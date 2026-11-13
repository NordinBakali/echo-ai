"""Detect an active Teams/Zoom/Webex/Slack/Skype call from Windows' microphone-usage registry and drive the recorder."""

import json
import os
import threading
import time
from pathlib import Path

try:
    import winreg
except ImportError:  # pragma: no cover - Windows only
    winreg = None

CONSENT_STORE = r"Software\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\microphone"
PACKAGED_APPS = {"MSTeams_": "Microsoft Teams", "MicrosoftTeams_": "Microsoft Teams", "Zoom": "Zoom"}
DESKTOP_APPS = {
    "ms-teams.exe": "Microsoft Teams", "teams.exe": "Microsoft Teams",
    "zoom.exe": "Zoom", "cpthost.exe": "Zoom",
    "webex.exe": "Webex", "ciscocollabhost.exe": "Webex", "atmgr.exe": "Webex",
    "slack.exe": "Slack", "skype.exe": "Skype",
}
POLL_SECONDS = 5
START_AFTER_SECONDS = 10
ANNOUNCE_SECONDS = 15  # time between the spoken announcement and the first recorded audio
STOP_AFTER_SECONDS = 30
ANNOUNCEMENT_EN = "My AI assistant is listening in to take the minutes."
ANNOUNCEMENT_NL = "Mijn AI-assistent luistert mee om de notulen te maken."


def _in_use(key):
    try:
        start = winreg.QueryValueEx(key, "LastUsedTimeStart")[0]
        stop = winreg.QueryValueEx(key, "LastUsedTimeStop")[0]
    except OSError:
        return False
    return bool(start) and stop == 0


def active_call_apps(registry=None):
    """Names of meeting apps that are using the microphone right now (browsers are deliberately ignored)."""
    registry = registry or winreg
    if registry is None:
        return []
    found = set()

    def scan(path, match):
        try:
            root = registry.OpenKey(registry.HKEY_CURRENT_USER, path)
        except OSError:
            return
        with root:
            index = 0
            while True:
                try:
                    name = registry.EnumKey(root, index)
                except OSError:
                    break
                index += 1
                app = match(name)
                if app:
                    try:
                        with registry.OpenKey(root, name) as key:
                            if _in_use(key):
                                found.add(app)
                    except OSError:
                        pass

    scan(CONSENT_STORE, lambda name: next((app for prefix, app in PACKAGED_APPS.items() if name.startswith(prefix)), None))
    scan(CONSENT_STORE + r"\NonPackaged", lambda name: DESKTOP_APPS.get(name.replace("#", "\\").rsplit("\\", 1)[-1].lower()))
    return sorted(found)


class AutoRecorder:
    """Starts a recording when a call is detected and stops, transcribes and summarises it when the call ends."""

    def __init__(self, recorder, settings_path, detector=active_call_apps, clock=time.monotonic, notify=None):
        self.recorder = recorder
        self.settings_path = Path(settings_path)
        self.detector = detector
        self.clock = clock
        self.notify = notify or (lambda en, nl, speak=False: None)
        self.lock = threading.Lock()
        self.settings = self._load()
        self.call_since = self.quiet_since = self.announced_at = None
        self.skipped = False
        self.apps, self.meeting_id, self.error = [], None, None
        self.thread = None
        self.halt = threading.Event()

    def _load(self):
        defaults = {"enabled": False, "microphone": True, "language": "nl", "separate": False, "model": ""}
        try:
            data = json.loads(self.settings_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                defaults.update({k: data[k] for k in defaults if k in data and type(data[k]) is type(defaults[k])})
        except (OSError, ValueError):
            pass
        return defaults

    def configure(self, authorized, enabled, microphone, language, separate, model):
        from echo_meeting_recorder import LANGUAGES, MeetingError
        if (type(enabled) is not bool or type(microphone) is not bool or type(separate) is not bool
                or language not in LANGUAGES or not isinstance(model, str) or len(model) > 120):
            raise MeetingError("Invalid automatic recording settings.", "Ongeldige instellingen voor automatisch opnemen.")
        if enabled and authorized is not True:
            raise MeetingError(
                "Confirm that you will tell participants at the start of every call that Echo records it.",
                "Bevestig dat je deelnemers aan het begin van elke call vertelt dat Echo meeluistert.",
            )
        with self.lock:
            self.settings = {"enabled": enabled, "microphone": microphone, "language": language,
                             "separate": separate and microphone, "model": model.strip()}
            self.settings_path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.settings_path.with_suffix(".tmp")
            tmp.write_text(json.dumps(self.settings, indent=2), encoding="utf-8")
            os.replace(tmp, self.settings_path)
            self.call_since = self.quiet_since = self.announced_at = None
            self.skipped = False
            if not enabled:
                self.meeting_id, self.apps = None, []  # a running recording stays; stop it by hand
        if enabled:
            self.start()
        else:
            self.stop()

    def snapshot(self):
        with self.lock:
            starts_in = None
            if self.announced_at is not None and self.meeting_id is None and not self.skipped:
                starts_in = max(0, round(ANNOUNCE_SECONDS - (self.clock() - self.announced_at)))
            return {**self.settings, "running": bool(self.thread and self.thread.is_alive()),
                    "call_apps": list(self.apps), "auto_meeting": self.meeting_id, "error": self.error,
                    "announced": self.announced_at is not None, "starts_in": starts_in, "skipped": self.skipped,
                    "supported": winreg is not None or self.detector is not active_call_apps}

    def skip(self):
        """Do not record the current call (e.g. someone objected); recording resumes for the next call."""
        from echo_meeting_recorder import MeetingError
        with self.lock:
            if not self.apps or self.meeting_id is not None:
                raise MeetingError("There is no pending automatic recording to skip.",
                                   "Er is geen automatische opname die nog moet starten.", 409)
            self.skipped = True

    def start(self):
        with self.lock:
            self.halt.clear()
            if self.thread and self.thread.is_alive():
                return
            self.thread = threading.Thread(target=self._loop, name="echo-meeting-auto", daemon=True)
            self.thread.start()

    def stop(self):
        self.halt.set()

    def _loop(self):
        while not self.halt.is_set():
            self.poll()
            self.halt.wait(POLL_SECONDS)

    def poll(self):
        """One detection step; safe to call directly from tests."""
        from echo_meeting_recorder import MeetingError
        with self.lock:
            settings = dict(self.settings)
        if not settings["enabled"]:
            with self.lock:
                self.apps, self.call_since, self.quiet_since, self.announced_at = [], None, None, None
                self.skipped = False
            return
        try:
            apps = self.detector()
        except Exception as exc:  # keep watching; show the problem in the UI
            with self.lock:
                self.error = str(exc)[:200]
            return
        now = self.clock()
        with self.lock:
            self.apps, self.error = apps, None
            if apps:
                self.quiet_since = None
                self.call_since = self.call_since if self.call_since is not None else now
            else:
                self.call_since = self.announced_at = None
                self.skipped = False
                self.quiet_since = self.quiet_since if self.quiet_since is not None else now
            ours = self.meeting_id
            current = self.recorder.snapshot()["recording"]
            idle = bool(apps) and ours is None and current is None and not self.skipped
            should_announce = (idle and self.announced_at is None
                               and now - self.call_since >= START_AFTER_SECONDS)
            should_start = (idle and self.announced_at is not None
                            and now - self.announced_at >= ANNOUNCE_SECONDS)
            if should_announce:
                self.announced_at = now
            should_stop = (not apps and ours is not None and now - self.quiet_since >= STOP_AFTER_SECONDS)
        if ours is not None and (current is None or current["id"] != ours):
            # Stopped by hand (or the 4-hour limit): never take over a recording we did not start.
            with self.lock:
                self.meeting_id = None
                self.skipped = True  # do not restart within the same call
            return
        if should_announce:
            # Nothing is recorded yet: participants are told first and can object before audio is captured.
            self.notify(
                f"{apps[0]} call detected. Tell the participants now: \"{ANNOUNCEMENT_EN}\" "
                f"Echo starts recording in {ANNOUNCE_SECONDS} seconds; choose 'Do not record' if someone objects.",
                f"{apps[0]}-call gedetecteerd. Zeg nu tegen de deelnemers: \"{ANNOUNCEMENT_NL}\" "
                f"Echo begint over {ANNOUNCE_SECONDS} seconden met opnemen; kies 'Niet opnemen' als iemand bezwaar heeft.",
                True,
            )
        elif should_start:
            try:
                meeting_id = self.recorder.start(True, settings["microphone"], f"{apps[0]} — auto")
            except MeetingError as exc:
                with self.lock:
                    self.error = exc.localized(False)
                return
            with self.lock:
                self.meeting_id = meeting_id
            self.notify(f"Echo is now recording the {apps[0]} call.",
                        f"Echo neemt de {apps[0]}-call nu op.", False)
        elif should_stop:
            with self.lock:
                self.meeting_id = None
            try:
                self.recorder.stop()
                self.recorder.transcribe(ours, settings["language"], settings["separate"],
                                         summary_model=settings["model"] or None)
            except MeetingError as exc:
                with self.lock:
                    self.error = exc.localized(False)
