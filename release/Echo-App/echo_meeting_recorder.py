"""Local meeting recorder: speaker loopback + optional microphone, transcribed on this PC with Whisper."""

import json
import os
import re
import secrets
import shutil
import threading
import time
import wave
from datetime import datetime
from pathlib import Path

import numpy as np

try:
    import pyaudiowpatch as pyaudio
except Exception:  # pragma: no cover - depends on the Windows audio stack
    pyaudio = None

DATA_DIR = Path(os.environ.get("LOCALAPPDATA", str(Path.home() / ".local" / "share"))) / "Echo" / "meetings"
RATE = 16000
MAX_SECONDS = 4 * 60 * 60
MIN_FREE_BYTES = 1024 ** 3
GAP_SECONDS = 0.25
TRACKS = {"speakers": ("Others", "Anderen"), "microphone": ("You", "Jij")}
LANGUAGES = {"auto", "nl", "en"}
ID_PATTERN = re.compile(r"^\d{8}-\d{6}-[0-9a-f]{6}$")
GPU_ERROR = re.compile(r"cublas|cudnn|cuda|cudart", re.IGNORECASE)


class MeetingError(Exception):
    def __init__(self, en, nl=None, status=400):
        super().__init__(en)
        self.en, self.nl, self.status = en, nl or en, status

    def localized(self, nederlands):
        return self.nl if nederlands else self.en


def to_mono_16k(raw, channels, rate):
    samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32)
    if channels > 1:
        samples = samples[: len(samples) - len(samples) % channels].reshape(-1, channels).mean(axis=1)
    if rate != RATE and len(samples):
        length = max(1, round(len(samples) * RATE / rate))
        samples = np.interp(np.linspace(0, len(samples) - 1, length), np.arange(len(samples)), samples)
    return np.clip(samples, -32768, 32767).astype(np.int16)


class TrackWriter:
    """Writes one 16 kHz mono track and fills silence gaps so all tracks share one timeline."""

    def __init__(self, path, started, clock):
        self.path, self.started, self.clock = Path(path), started, clock
        self.lock = threading.Lock()
        self.frames = 0
        self.wav = wave.open(str(self.path), "wb")
        self.wav.setnchannels(1)
        self.wav.setsampwidth(2)
        self.wav.setframerate(RATE)

    def _pad_to(self, target):
        missing = target - self.frames
        if missing > 0:
            self.wav.writeframes(np.zeros(missing, dtype=np.int16).tobytes())
            self.frames += missing

    def feed(self, raw, channels, rate):
        samples = to_mono_16k(raw, channels, rate)
        with self.lock:
            if self.wav is None:
                return
            expected = int((self.clock() - self.started) * RATE)
            if expected - self.frames - len(samples) > GAP_SECONDS * RATE:
                self._pad_to(expected - len(samples))
            self.wav.writeframes(samples.tobytes())
            self.frames += len(samples)

    def close(self, end_frames=None):
        with self.lock:
            if self.wav is None:
                return
            if end_frames is not None:
                self._pad_to(end_frames)
            self.wav.close()
            self.wav = None


def read_track(path):
    with wave.open(str(path), "rb") as wav:
        return np.frombuffer(wav.readframes(wav.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0


def stamp(seconds):
    seconds = max(0, int(seconds))
    return f"{seconds // 3600:02d}:{seconds % 3600 // 60:02d}:{seconds % 60:02d}"


def srt_stamp(seconds):
    ms = max(0, int(round(seconds * 1000)))
    return f"{ms // 3600000:02d}:{ms % 3600000 // 60000:02d}:{ms % 60000 // 1000:02d},{ms % 1000:03d}"


class MeetingRecorder:
    def __init__(self, data_dir=DATA_DIR, model_loader=None, audio=None, clock=time.monotonic, notify=None,
                 fallback_loader=None, summarizer=None):
        self.data_dir = Path(data_dir)
        self.summarizer = summarizer
        self.model_loader = model_loader
        self.fallback_loader = fallback_loader
        self.audio = audio if audio is not None else pyaudio
        self.clock = clock
        self.notify = notify or (lambda en, nl: None)
        self.lock = threading.RLock()
        self.recording = None
        self.jobs = {}

    # ----- storage -----
    def _dir(self, meeting_id):
        if not isinstance(meeting_id, str) or not ID_PATTERN.match(meeting_id):
            raise MeetingError("Unknown meeting.", "Onbekende vergadering.", 404)
        path = self.data_dir / meeting_id
        if not (path / "meta.json").is_file():
            raise MeetingError("Unknown meeting.", "Onbekende vergadering.", 404)
        return path

    def _meta(self, path):
        return json.loads((Path(path) / "meta.json").read_text(encoding="utf-8"))

    def _save_meta(self, path, meta):
        tmp = Path(path) / "meta.json.tmp"
        tmp.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp, Path(path) / "meta.json")

    def meetings(self):
        if not self.data_dir.is_dir():
            return []
        items = []
        for path in sorted(self.data_dir.iterdir(), reverse=True):
            if not ID_PATTERN.match(path.name) or not (path / "meta.json").is_file():
                continue
            try:
                meta = self._meta(path)
            except (OSError, ValueError):
                continue
            job = self.jobs.get(path.name)
            if job:
                meta.update(status=job["status"], progress=job["progress"])
            meta["has_transcript"] = (path / "transcript.txt").is_file()
            meta["has_summary"] = (path / "summary.md").is_file()
            items.append(meta)
        return items

    def transcript(self, meeting_id, kind="txt"):
        name = {"srt": "transcript.srt", "md": "summary.md"}.get(kind, "transcript.txt")
        path = self._dir(meeting_id) / name
        if not path.is_file():
            if kind == "md":
                raise MeetingError("No summary yet.", "Nog geen samenvatting.", 404)
            raise MeetingError("No transcript yet.", "Nog geen transcriptie.", 404)
        return path

    def delete(self, meeting_id):
        path = self._dir(meeting_id)
        with self.lock:
            if self.recording and self.recording["id"] == meeting_id:
                raise MeetingError("Stop the recording first.", "Stop eerst de opname.", 409)
            if meeting_id in self.jobs:
                raise MeetingError("Wait until transcription or summary finishes.",
                                   "Wacht tot de transcriptie of samenvatting klaar is.", 409)
            self.jobs.pop(meeting_id, None)
        shutil.rmtree(path)

    # ----- recording -----
    def snapshot(self):
        with self.lock:
            rec = self.recording
            current = None
            if rec:
                current = {
                    "id": rec["id"], "microphone": rec["microphone"],
                    "elapsed": round(self.clock() - rec["started"], 1),
                    "max_seconds": MAX_SECONDS,
                    "speakers_device": rec["devices"].get("speakers"),
                    "microphone_device": rec["devices"].get("microphone"),
                }
            return {"available": self.audio is not None, "recording": current, "meetings": self.meetings()}

    def _open(self, pa, kind):
        if kind == "speakers":
            device = pa.get_default_wasapi_loopback()
        else:
            wasapi = pa.get_host_api_info_by_type(self.audio.paWASAPI)
            index = wasapi.get("defaultInputDevice", -1)
            if index is None or index < 0:
                raise MeetingError("No microphone found.", "Geen microfoon gevonden.")
            device = pa.get_device_info_by_index(index)
        channels = max(1, min(2, int(device.get("maxInputChannels") or 1)))
        rate = int(device.get("defaultSampleRate") or 48000)
        return device, channels, rate

    def start(self, authorized, microphone=True, title=""):
        if authorized is not True:
            raise MeetingError(
                "Confirm that all participants know the meeting is being recorded.",
                "Bevestig dat alle deelnemers weten dat de vergadering wordt opgenomen.",
            )
        if type(microphone) is not bool or not isinstance(title, str) or len(title) > 120:
            raise MeetingError("Invalid recording options.", "Ongeldige opname-opties.")
        if self.audio is None:
            raise MeetingError(
                "Windows loopback audio is unavailable (install PyAudioWPatch).",
                "Windows-loopbackaudio is niet beschikbaar (installeer PyAudioWPatch).", 503,
            )
        with self.lock:
            if self.recording:
                raise MeetingError("A recording is already running.", "Er loopt al een opname.", 409)
            self.data_dir.mkdir(parents=True, exist_ok=True)
            if shutil.disk_usage(self.data_dir).free < MIN_FREE_BYTES:
                raise MeetingError("Less than 1 GB disk space free.", "Minder dan 1 GB schijfruimte vrij.", 507)
            meeting_id = f"{datetime.now():%Y%m%d-%H%M%S}-{secrets.token_hex(3)}"
            folder = self.data_dir / meeting_id
            folder.mkdir()
            pa = self.audio.PyAudio()
            streams, writers, devices = [], {}, {}
            started = self.clock()
            try:
                for kind in ["speakers"] + (["microphone"] if microphone else []):
                    device, channels, rate = self._open(pa, kind)
                    writer = TrackWriter(folder / f"{kind}.wav", started, self.clock)
                    writers[kind] = writer

                    def callback(data, frames, info, status, writer=writer, channels=channels, rate=rate):
                        writer.feed(data, channels, rate)
                        return (None, self.audio.paContinue)

                    streams.append(pa.open(
                        format=self.audio.paInt16, channels=channels, rate=rate, input=True,
                        input_device_index=device["index"], frames_per_buffer=max(1, rate // 100),
                        stream_callback=callback,
                    ))
                    devices[kind] = str(device.get("name", ""))
            except MeetingError:
                self._close(pa, streams, writers)
                shutil.rmtree(folder, ignore_errors=True)
                raise
            except Exception as exc:
                self._close(pa, streams, writers)
                shutil.rmtree(folder, ignore_errors=True)
                raise MeetingError(
                    f"Could not open audio: {exc}", f"Audio kon niet worden geopend: {exc}", 503,
                ) from exc
            meta = {
                "id": meeting_id, "title": title.strip() or meeting_id,
                "started_at": datetime.now().isoformat(timespec="seconds"),
                "duration": 0, "microphone": microphone, "tracks": list(writers),
                "devices": devices, "status": "recording", "progress": 0, "language": None, "error": None,
            }
            self._save_meta(folder, meta)
            timer = threading.Timer(MAX_SECONDS, self._auto_stop, args=(meeting_id,))
            timer.daemon = True
            timer.start()
            self.recording = {
                "id": meeting_id, "folder": folder, "pa": pa, "streams": streams, "writers": writers,
                "started": started, "microphone": microphone, "devices": devices, "timer": timer,
            }
        self.notify("Meeting recording started.", "Vergaderopname gestart.")
        return meeting_id

    def _close(self, pa, streams, writers, end_frames=None):
        for stream in streams:
            try:
                stream.stop_stream()
                stream.close()
            except Exception:
                pass
        for writer in writers.values():
            writer.close(end_frames)
        try:
            pa.terminate()
        except Exception:
            pass

    def _auto_stop(self, meeting_id):
        with self.lock:
            if self.recording and self.recording["id"] == meeting_id:
                self.stop()

    def stop(self):
        with self.lock:
            rec = self.recording
            if not rec:
                raise MeetingError("No recording is running.", "Er loopt geen opname.", 409)
            self.recording = None
            rec["timer"].cancel()
            duration = self.clock() - rec["started"]
            self._close(rec["pa"], rec["streams"], rec["writers"], int(duration * RATE))
            meta = self._meta(rec["folder"])
            meta.update(duration=round(duration, 1), status="recorded")
            self._save_meta(rec["folder"], meta)
        self.notify("Meeting recording saved.", "Vergaderopname opgeslagen.")
        return rec["id"]

    def shutdown(self):
        try:
            self.stop()
        except MeetingError:
            pass

    # ----- transcription -----
    def transcribe(self, meeting_id, language="auto", separate=False, background=True, summary_model=None):
        folder = self._dir(meeting_id)
        if language not in LANGUAGES or type(separate) is not bool:
            raise MeetingError("Invalid transcription options.", "Ongeldige transcriptie-opties.")
        if self.model_loader is None:
            raise MeetingError("Whisper is not available.", "Whisper is niet beschikbaar.", 503)
        with self.lock:
            if self.recording and self.recording["id"] == meeting_id:
                raise MeetingError("Stop the recording first.", "Stop eerst de opname.", 409)
            if meeting_id in self.jobs:
                raise MeetingError("This meeting is already being processed.", "Deze vergadering wordt al verwerkt.", 409)
            if any(job["status"] == "transcribing" for job in self.jobs.values()):
                raise MeetingError("Another transcription is running.", "Er loopt al een transcriptie.", 409)
            self.jobs[meeting_id] = {"status": "transcribing", "progress": 0}
        args = (folder, language, separate, summary_model)
        if background:
            threading.Thread(target=self._transcribe, args=args, daemon=True).start()
        else:
            self._transcribe(*args)

    def summarize(self, meeting_id, model, background=True):
        folder = self._dir(meeting_id)
        if not isinstance(model, str) or not model.strip():
            raise MeetingError("Choose a local Ollama model.", "Kies een lokaal Ollama-model.")
        if self.summarizer is None:
            raise MeetingError("Summaries are not available.", "Samenvatten is niet beschikbaar.", 503)
        if not (folder / "transcript.txt").is_file():
            raise MeetingError("Transcribe the meeting first.", "Schrijf de vergadering eerst uit.", 409)
        with self.lock:
            if meeting_id in self.jobs:
                raise MeetingError("This meeting is already being processed.", "Deze vergadering wordt al verwerkt.", 409)
            if any(job["status"] == "summarizing" for job in self.jobs.values()):
                raise MeetingError("Another summary is running.", "Er loopt al een samenvatting.", 409)
            self.jobs[meeting_id] = {"status": "summarizing", "progress": 0}
        if background:
            threading.Thread(target=self._summarize_job, args=(folder, model.strip()), daemon=True).start()
        else:
            self._summarize_job(folder, model.strip())

    def _summarize_job(self, folder, model):
        try:
            self._summarize(folder, model, self.jobs[folder.name])
        finally:
            with self.lock:
                self.jobs.pop(folder.name, None)

    def _summarize(self, folder, model, job):
        meta = self._meta(folder)
        job.update(status="summarizing", progress=0)
        try:
            dutch = meta.get("language") != "en"
            transcript = (folder / "transcript.txt").read_text(encoding="utf-8")
            report = self.summarizer(
                transcript, model, dutch, progress=lambda fraction: job.update(progress=min(99, int(fraction * 100))),
            )
            from echo_meeting_summary import markdown
            (folder / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
            (folder / "summary.md").write_text(markdown(report, meta["title"], meta["started_at"], dutch), encoding="utf-8")
            meta.update(summary_model=report["model"], summary_error=None, action_items=len(report["action_items"]))
            self.notify("Meeting summary and action items are ready.", "Samenvatting en actiepunten van de vergadering zijn klaar.")
        except Exception as exc:
            localized = getattr(exc, "localized", None)
            message = localized(False) if callable(localized) else str(exc)
            meta.update(summary_error=message[:300])
        finally:
            self._save_meta(folder, meta)

    def _run_model(self, model, sources, language, total, job):
        done, segments, detected = 0.0, [], None
        for kind, audio in sources.items():
            parts, info = model.transcribe(
                audio, language=None if language == "auto" else language, beam_size=5, vad_filter=True,
            )
            detected = detected or getattr(info, "language", None)
            for part in parts:
                text = str(getattr(part, "text", "") or "").strip()
                if text:
                    segments.append((float(part.start), float(part.end), kind, text))
                job["progress"] = min(99, int((done + float(part.end)) / total * 100))
            done += len(audio) / RATE
        return segments, detected

    def _transcribe(self, folder, language, separate, summary_model=None):
        meeting_id = folder.name
        meta = self._meta(folder)
        job = self.jobs[meeting_id]
        transcribed = False
        try:
            tracks = {kind: read_track(folder / f"{kind}.wav") for kind in meta["tracks"] if (folder / f"{kind}.wav").is_file()}
            if not tracks:
                raise MeetingError("The recording has no audio.", "De opname bevat geen audio.")
            length = max(len(a) for a in tracks.values())
            if not separate or len(tracks) == 1:
                mixed = np.zeros(length, dtype=np.float32)
                for audio in tracks.values():
                    mixed[: len(audio)] += audio
                peak = float(np.max(np.abs(mixed))) if length else 0.0
                if peak > 1.0:
                    mixed /= peak
                sources = {None: mixed}
            else:
                sources = tracks
            model = self.model_loader()
            total = max(1e-6, (length / RATE) * len(sources))
            try:
                segments, detected = self._run_model(model, sources, language, total, job)
            except Exception as exc:
                if self.fallback_loader is None or not GPU_ERROR.search(str(exc)):
                    raise
                # GPU libraries (cuBLAS/cuDNN) are missing: redo everything on the CPU.
                job["progress"] = 0
                segments, detected = self._run_model(self.fallback_loader(), sources, language, total, job)
            segments.sort(key=lambda item: (item[0], item[2] or ""))
            nederlands = (detected or language) == "nl"
            label = lambda kind: "" if kind is None else TRACKS[kind][1 if nederlands else 0] + ": "
            lines = [f"{meta['title']} — {meta['started_at']}", ""]
            lines += [f"[{stamp(start)}] {label(kind)}{text}" for start, _, kind, text in segments]
            (folder / "transcript.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
            srt = [
                f"{i}\n{srt_stamp(start)} --> {srt_stamp(end)}\n{label(kind)}{text}\n"
                for i, (start, end, kind, text) in enumerate(segments, 1)
            ]
            (folder / "transcript.srt").write_text("\n".join(srt), encoding="utf-8")
            meta.update(status="transcribed", progress=100, language=detected or language, error=None,
                        segments=len(segments), separate=separate and len(tracks) > 1)
            self.notify("Meeting transcript is ready.", "Vergadertranscriptie is klaar.")
            transcribed = True
        except Exception as exc:
            message = exc.localized(False) if isinstance(exc, MeetingError) else str(exc)
            meta.update(status="error", error=message[:300])
        finally:
            self._save_meta(folder, meta)
            try:
                if transcribed and summary_model and self.summarizer is not None:
                    self._summarize(folder, summary_model, job)
            finally:
                with self.lock:
                    self.jobs.pop(meeting_id, None)
