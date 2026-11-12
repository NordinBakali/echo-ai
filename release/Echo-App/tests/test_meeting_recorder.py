import wave
from types import SimpleNamespace

import numpy as np
import pytest

import echo_meeting_recorder as meeting
import server


class FakeClock:
    def __init__(self):
        self.now = 100.0

    def __call__(self):
        return self.now


class FakeStream:
    def __init__(self, callback):
        self.callback = callback
        self.closed = False

    def stop_stream(self):
        pass

    def close(self):
        self.closed = True


class FakeAudio:
    paWASAPI, paInt16, paContinue = 13, 8, 0

    def __init__(self):
        self.streams = []
        audio = self

        class PyAudio:
            def get_default_wasapi_loopback(self):
                return {"index": 1, "name": "Speakers [Loopback]", "maxInputChannels": 2, "defaultSampleRate": 48000.0}

            def get_host_api_info_by_type(self, _):
                return {"defaultInputDevice": 2}

            def get_device_info_by_index(self, index):
                return {"index": index, "name": "Mic", "maxInputChannels": 1, "defaultSampleRate": 44100.0}

            def open(self, **kwargs):
                stream = FakeStream(kwargs["stream_callback"])
                stream.kwargs = kwargs
                audio.streams.append(stream)
                return stream

            def terminate(self):
                pass

        self.PyAudio = PyAudio


class FakeModel:
    def __init__(self):
        self.calls = []

    def transcribe(self, audio, **kwargs):
        self.calls.append((len(audio), kwargs))
        loud = float(np.abs(audio[:16000]).max()) > 0.1
        segment = SimpleNamespace(start=0.5 if loud else 1.5, end=2.0, text=f" seg{len(self.calls)} ")
        return iter([segment]), SimpleNamespace(language="nl")


def tone(seconds, rate, channels, amplitude=8000):
    samples = np.full(int(seconds * rate) * channels, amplitude, dtype=np.int16)
    return samples.tobytes()


def frames(path):
    with wave.open(str(path), "rb") as wav:
        assert wav.getframerate() == 16000 and wav.getnchannels() == 1
        return wav.getnframes()


@pytest.fixture()
def recorder(tmp_path):
    clock, audio, model = FakeClock(), FakeAudio(), FakeModel()
    rec = meeting.MeetingRecorder(tmp_path, model_loader=lambda: model, audio=audio, clock=clock)
    rec.fake = SimpleNamespace(clock=clock, audio=audio, model=model)
    yield rec
    rec.shutdown()


def test_start_requires_consent(recorder):
    with pytest.raises(meeting.MeetingError):
        recorder.start(False)
    assert recorder.snapshot()["recording"] is None and not recorder.meetings()


def test_tracks_are_resampled_aligned_and_gaps_filled(recorder, tmp_path):
    meeting_id = recorder.start(True, microphone=True, title="Stand-up")
    speakers, mic = recorder.fake.audio.streams
    assert speakers.kwargs["channels"] == 2 and mic.kwargs["rate"] == 44100
    recorder.fake.clock.now += 1
    speakers.callback(tone(1, 48000, 2), 0, None, 0)
    mic.callback(tone(1, 44100, 1), 0, None, 0)
    # Loopback delivers nothing during silence; the next chunk must land at the right time.
    recorder.fake.clock.now += 3
    speakers.callback(tone(1, 48000, 2), 0, None, 0)
    recorder.fake.clock.now += 1
    recorder.stop()
    folder = tmp_path / meeting_id
    assert frames(folder / "speakers.wav") == frames(folder / "microphone.wav") == 5 * 16000
    meta = recorder.meetings()[0]
    assert meta["status"] == "recorded" and meta["duration"] == 5 and meta["title"] == "Stand-up"
    assert all(stream.closed for stream in recorder.fake.audio.streams)
    with pytest.raises(meeting.MeetingError):
        recorder.stop()


def test_separate_transcript_has_speaker_labels_and_srt(recorder, tmp_path):
    meeting_id = recorder.start(True, microphone=True)
    speakers, mic = recorder.fake.audio.streams
    recorder.fake.clock.now += 1
    speakers.callback(tone(1, 48000, 2), 0, None, 0)
    mic.callback(tone(1, 44100, 1, amplitude=0), 0, None, 0)
    recorder.fake.clock.now += 1
    recorder.stop()
    recorder.transcribe(meeting_id, "nl", True, background=False)
    text = recorder.transcript(meeting_id).read_text(encoding="utf-8").splitlines()
    assert text[2:] == ["[00:00:00] Anderen: seg1", "[00:00:01] Jij: seg2"]
    assert "00:00:00,500 --> 00:00:02,000" in recorder.transcript(meeting_id, "srt").read_text(encoding="utf-8")
    meta = recorder.meetings()[0]
    assert meta["status"] == "transcribed" and meta["has_transcript"] and meta["segments"] == 2
    assert recorder.fake.model.calls[0][1]["language"] == "nl"


def test_mixed_transcript_and_errors(recorder):
    meeting_id = recorder.start(True, microphone=False)
    recorder.fake.clock.now += 2
    recorder.stop()
    recorder.transcribe(meeting_id, "auto", False, background=False)
    assert recorder.fake.model.calls == [(32000, {"language": None, "beam_size": 5, "vad_filter": True})]
    assert "Jij" not in recorder.transcript(meeting_id).read_text(encoding="utf-8")
    with pytest.raises(meeting.MeetingError):
        recorder.transcribe(meeting_id, "de", False)
    for bad in ["../x", "20260101-000000-zzzzzz", 5]:
        with pytest.raises(meeting.MeetingError):
            recorder.delete(bad)
    recorder.delete(meeting_id)
    assert recorder.meetings() == []


def test_missing_gpu_libraries_fall_back_to_cpu(recorder):
    class BrokenGpu:
        def transcribe(self, audio, **kwargs):
            def parts():
                raise RuntimeError("Library cublas64_12.dll is not found or cannot be loaded")
                yield
            return parts(), SimpleNamespace(language="nl")

    recorder.model_loader = BrokenGpu
    recorder.fallback_loader = lambda: recorder.fake.model
    meeting_id = recorder.start(True, microphone=False)
    recorder.fake.clock.now += 1
    recorder.stop()
    recorder.transcribe(meeting_id, "nl", False, background=False)
    assert recorder.meetings()[0]["status"] == "transcribed"
    assert "seg1" in recorder.transcript(meeting_id).read_text(encoding="utf-8")


@pytest.fixture()
def client(monkeypatch, recorder):
    monkeypatch.setattr(server, "VERGADERING", recorder)
    monkeypatch.setattr(server, "ECHO_DEMO_MODE", False)
    monkeypatch.setattr(server, "ECHO_ENTERPRISE_MODE", False)
    server.app.config.update(TESTING=True)
    with server.app.test_client() as client:
        yield client


def test_routes_require_local_token_and_run_full_flow(client, recorder):
    assert b"/vergadering" in client.get("/").data
    page = client.get("/vergadering")
    assert page.status_code == 200 and page.headers["Cache-Control"] == "no-store"
    assert client.post("/api/vergadering/start", json={"authorized": True}).status_code == 403
    assert client.get("/api/vergadering/status", environ_base={"REMOTE_ADDR": "10.0.0.5"}).status_code == 403
    headers = {"X-Echo-Meeting-Token": server.VERGADERING_TOKEN}
    assert client.post("/api/vergadering/start", json={"authorized": False}, headers=headers).status_code == 400
    started = client.post("/api/vergadering/start", json={"authorized": True, "microphone": False}, headers=headers)
    assert started.status_code == 200 and started.json["meeting"]["recording"]
    recorder.fake.clock.now += 1
    meeting_id = client.post("/api/vergadering/stop", json={}, headers=headers).json["meeting"]["meetings"][0]["id"]
    recorder.transcribe(meeting_id, "nl", False, background=False)
    transcript = client.get(f"/api/vergadering/transcript/{meeting_id}.txt")
    assert transcript.status_code == 200 and "seg1" in transcript.get_data(as_text=True)
    assert client.get("/api/vergadering/transcript/..%2Fx.txt").status_code == 404
    assert client.post("/api/vergadering/delete", json={"id": meeting_id}, headers=headers).json["meeting"]["meetings"] == []
