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

# ----- summary, call detection and automatic recording -----
import json

import echo_meeting_summary as summary
import echo_meeting_trigger as trigger


def fake_ollama(calls, items=None):
    def request(endpoint, payload, timeout=0):
        calls.append(payload)
        merge = "partial meeting notes" in payload["messages"][0]["content"]
        content = {
            "summary": "Totaal." if merge else f"Deel {len(calls)}.",
            "decisions": ["Release vrijdag"],
            "action_items": items if items is not None else [
                {"who": "Sanne", "what": "Rapport | sturen", "due": "vrijdag", "timestamp": "00:00:01"},
                {"who": "", "what": "Iets", "due": "", "timestamp": "09:99:99"},
                {"who": "X", "what": " ", "due": "", "timestamp": ""},
            ],
        }
        return {"done": True, "done_reason": "stop", "message": {"content": json.dumps(content)}}
    return request


def test_summary_validates_items_and_merges_long_transcripts():
    calls = []
    short = "Titel — 2026\n\n[00:00:01] Anderen: Sanne stuurt vrijdag het rapport.\n"
    report = summary.summarize(short, "llama3.1", True, request=fake_ollama(calls), verify=lambda name, minimum: 8192)
    assert len(calls) == 1 and calls[0]["options"]["num_ctx"] == 8192
    assert "UNTRUSTED" in calls[0]["messages"][0]["content"] and "Sanne stuurt" in calls[0]["messages"][1]["content"]
    assert report["action_items"] == [
        {"who": "Sanne", "what": "Rapport | sturen", "due": "vrijdag", "timestamp": "00:00:01"},
        {"who": "Onbekend", "what": "Iets", "due": "", "timestamp": ""},  # invented timestamp dropped
    ]
    md = summary.markdown(report, "Titel", "2026", True)
    assert "| Sanne | Rapport \\| sturen | vrijdag | 00:00:01 |" in md and "## Besluiten" in md

    calls.clear()
    long = "T\n\n" + "\n".join(f"[00:{i // 60:02d}:{i % 60:02d}] Jij: " + "woord " * 60 for i in range(100))
    progress = []
    report = summary.summarize(long, "llama3.1", True, progress=progress.append,
                               request=fake_ollama(calls), verify=lambda name, minimum: 8192)
    assert len(calls) == 4 and report["summary"] == "Totaal."  # 3 excerpts + 1 merge
    assert "Excerpt 1 of 3" in calls[0]["messages"][1]["content"]
    assert progress == sorted(progress) and progress[-1] < 1
    with pytest.raises(summary.local.AnalysisError):
        summary.summarize(short, "gpt-oss:20b-cloud", True, request=fake_ollama([]), verify=lambda n, m: 8192)


def test_transcribe_then_summarize_writes_minutes(recorder):
    seen = []

    def summarizer(text, model, dutch, progress):
        seen.append((model, dutch, "seg1" in text))
        progress(0.5)
        return {"model": model, "chunks": 1, "summary": "Kort.", "decisions": [],
                "action_items": [{"who": "Jij", "what": "Mailen", "due": "", "timestamp": ""}]}

    recorder.summarizer = summarizer
    meeting_id = recorder.start(True, microphone=False)
    recorder.fake.clock.now += 1
    recorder.stop()
    recorder.transcribe(meeting_id, "nl", False, background=False, summary_model="llama3.1")
    meta = recorder.meetings()[0]
    assert seen == [("llama3.1", True, True)] and meta["has_summary"] and meta["action_items"] == 1
    assert "| Jij | Mailen |" in recorder.transcript(meeting_id, "md").read_text(encoding="utf-8")

    recorder.summarizer = lambda *a, **k: (_ for _ in ()).throw(summary.local.AnalysisError("Ollama down", "Ollama uit", 503))
    recorder.summarize(meeting_id, "llama3.1", background=False)
    meta = recorder.meetings()[0]
    assert meta["summary_error"] == "Ollama down" and meta["status"] == "transcribed" and not recorder.jobs


class FakeRegistry:
    HKEY_CURRENT_USER = "HKCU"

    def __init__(self, tree):
        self.tree = tree

    def OpenKey(self, parent, name):
        path = name if parent == "HKCU" else parent.path + "\\" + name
        if path not in self.tree:
            raise OSError(path)
        registry = self

        class Key:
            def __init__(self):
                self.path = path

            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False

        key = Key()
        key.registry = registry
        return key

    def EnumKey(self, key, index):
        children = sorted(k[len(key.path) + 1:] for k in self.tree
                          if k.startswith(key.path + "\\") and "\\" not in k[len(key.path) + 1:])
        if index >= len(children):
            raise OSError("done")
        return children[index]


def test_active_call_apps_reads_microphone_usage(monkeypatch):
    base = trigger.CONSENT_STORE
    tree = {
        base: {}, base + "\\NonPackaged": {},
        base + "\\MSTeams_8wekyb3d8bbwe": {"LastUsedTimeStart": 5, "LastUsedTimeStop": 0},
        base + "\\SpotifyAB.SpotifyMusic_x": {"LastUsedTimeStart": 5, "LastUsedTimeStop": 0},
        base + "\\NonPackaged\\C:#Program Files#Zoom#bin#Zoom.exe": {"LastUsedTimeStart": 5, "LastUsedTimeStop": 9},
        base + "\\NonPackaged\\C:#Program Files#Google#Chrome#chrome.exe": {"LastUsedTimeStart": 5, "LastUsedTimeStop": 0},
    }
    registry = FakeRegistry(tree)

    def query(key, name):
        values = tree[key.path]
        if name not in values:
            raise OSError(name)
        return values[name], 4

    monkeypatch.setattr(trigger, "winreg", type("W", (), {"QueryValueEx": staticmethod(query)}))
    assert trigger.active_call_apps(registry) == ["Microsoft Teams"]
    tree[base + "\\NonPackaged\\C:#Program Files#Zoom#bin#Zoom.exe"]["LastUsedTimeStop"] = 0
    assert trigger.active_call_apps(registry) == ["Microsoft Teams", "Zoom"]


def test_auto_recorder_starts_and_finishes_calls(recorder, tmp_path):
    apps, notes, finished = [], [], []
    auto = trigger.AutoRecorder(recorder, tmp_path / "auto.json", detector=lambda: list(apps),
                                clock=recorder.fake.clock, notify=lambda en, nl, speak=False: notes.append((nl, speak)))
    auto.start = lambda: None  # tests drive poll() directly
    with pytest.raises(meeting.MeetingError):
        auto.configure(False, True, False, "nl", False, "llama3.1")
    auto.configure(True, True, False, "nl", False, "llama3.1")
    assert json.loads((tmp_path / "auto.json").read_text())["model"] == "llama3.1"
    recorder.transcribe = lambda *a, **k: finished.append((a, k))

    apps.append("Microsoft Teams")
    auto.poll()
    recorder.fake.clock.now += 5
    auto.poll()
    assert recorder.snapshot()["recording"] is None and notes == []  # not before 10 seconds in a call
    recorder.fake.clock.now += 5
    auto.poll()
    # The announcement comes first; nothing is recorded until participants have been told.
    assert recorder.snapshot()["recording"] is None
    assert len(notes) == 1 and "Mijn AI-assistent luistert mee" in notes[0][0] and notes[0][1] is True
    assert auto.snapshot()["starts_in"] == trigger.ANNOUNCE_SECONDS
    recorder.fake.clock.now += trigger.ANNOUNCE_SECONDS - 1
    auto.poll()
    assert recorder.snapshot()["recording"] is None
    recorder.fake.clock.now += 1
    auto.poll()
    meeting_id = recorder.snapshot()["recording"]["id"]
    assert auto.snapshot()["auto_meeting"] == meeting_id and len(notes) == 2 and notes[1][1] is False
    apps.clear()
    auto.poll()
    recorder.fake.clock.now += 29
    auto.poll()
    assert recorder.snapshot()["recording"]  # short drop-outs do not end the recording
    recorder.fake.clock.now += 1
    auto.poll()
    assert recorder.snapshot()["recording"] is None
    assert finished == [((meeting_id, "nl", False), {"summary_model": "llama3.1"})]

    manual = recorder.start(True, microphone=False)  # a manual recording is never stopped automatically
    apps.append("Zoom")
    recorder.fake.clock.now += 20
    auto.poll()
    apps.clear()
    recorder.fake.clock.now += 60
    auto.poll()
    auto.poll()
    assert recorder.snapshot()["recording"]["id"] == manual
    assert trigger.AutoRecorder(recorder, tmp_path / "auto.json").settings["enabled"] is True


def test_auto_recorder_skip_prevents_recording_until_next_call(recorder, tmp_path):
    apps = []
    auto = trigger.AutoRecorder(recorder, tmp_path / "auto.json", detector=lambda: list(apps), clock=recorder.fake.clock)
    auto.start = lambda: None
    auto.configure(True, True, False, "nl", False, "")
    with pytest.raises(meeting.MeetingError):
        auto.skip()  # no call yet
    apps.append("Zoom")
    auto.poll()
    recorder.fake.clock.now += 10
    auto.poll()
    assert auto.snapshot()["announced"] is True
    auto.skip()  # someone objected after the announcement
    recorder.fake.clock.now += 60
    auto.poll()
    assert recorder.snapshot()["recording"] is None and auto.snapshot()["skipped"] is True
    apps.clear()
    auto.poll()  # call ended: the next call is handled normally again
    apps.append("Zoom")
    auto.poll()
    recorder.fake.clock.now += 10
    auto.poll()
    recorder.fake.clock.now += trigger.ANNOUNCE_SECONDS
    auto.poll()
    assert recorder.snapshot()["recording"] is not None


def test_routes_summary_models_and_auto(client, recorder, monkeypatch, tmp_path):
    headers = {"X-Echo-Meeting-Token": server.VERGADERING_TOKEN}
    auto = trigger.AutoRecorder(recorder, tmp_path / "auto.json", detector=lambda: [])
    auto.start = lambda: None
    monkeypatch.setattr(server, "VERGADER_AUTO", auto)
    monkeypatch.setattr(server.lokale_analyse, "installed_models", lambda: ["llama3.1"])
    assert client.get("/api/vergadering/models").json["models"] == ["llama3.1"]
    status = client.get("/api/vergadering/status").json["meeting"]
    assert status["auto"]["enabled"] is False
    body = {"authorized": False, "enabled": True, "microphone": True, "language": "nl", "separate": False, "model": ""}
    assert client.post("/api/vergadering/auto", json=body, headers=headers).status_code == 400
    assert client.post("/api/vergadering/auto", json=dict(body, authorized=True)).status_code == 403
    saved = client.post("/api/vergadering/auto", json=dict(body, authorized=True), headers=headers)
    assert saved.status_code == 200 and saved.json["meeting"]["auto"]["enabled"] is True
    assert client.post("/api/vergadering/skip", json={}, headers=headers).status_code == 409  # no call to skip

    recorder.summarizer = lambda text, model, dutch, progress: {
        "model": model, "chunks": 1, "summary": "Kort.", "decisions": ["Ja"], "action_items": []}
    meeting_id = recorder.start(True, microphone=False)
    recorder.fake.clock.now += 1
    recorder.stop()
    assert client.post("/api/vergadering/summarize", json={"id": meeting_id, "model": "llama3.1"}, headers=headers).status_code == 409
    recorder.transcribe(meeting_id, "nl", False, background=False)
    monkeypatch.setattr(recorder, "summarize", lambda mid, model: recorder.__class__.summarize(recorder, mid, model, background=False))
    done = client.post("/api/vergadering/summarize", json={"id": meeting_id, "model": "llama3.1"}, headers=headers)
    assert done.status_code == 200 and done.json["meeting"]["meetings"][0]["has_summary"]
    md = client.get(f"/api/vergadering/transcript/{meeting_id}.md")
    assert md.status_code == 200 and "- Ja" in md.get_data(as_text=True)
