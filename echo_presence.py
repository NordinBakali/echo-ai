"""Opt-in, local-only webcam presence monitoring. Never authenticates a user."""

import ctypes
import logging
import math
import sys
import threading
import time
from ctypes import wintypes
from dataclasses import dataclass
from pathlib import Path


LOGGER = logging.getLogger(__name__)
POLL_SECONDS = 0.5
FACE_STABLE_SECONDS = 2.0
CAMERA_FRAME_TIMEOUT = 2.0
CAMERA_CLOSE_TIMEOUT = 2.0
ERROR_MESSAGES = {
    "unsupported": ("Presence detection requires Windows.", "Aanwezigheidsdetectie vereist Windows."),
    "invalid_settings": (
        "Use a delay of 10-600 seconds, camera number 0-10 and a boolean sound setting.",
        "Gebruik een wachttijd van 10-600 seconden, cameranummer 0-10 en een geldige geluidsinstelling.",
    ),
    "already_running": ("Stop detection before changing settings.", "Stop de detectie voordat je instellingen wijzigt."),
    "camera_dependency": (
        "The camera dependency is unavailable. Restart with Start-Echo-App.bat to install requirements.",
        "Het camerapakket ontbreekt of kan niet laden. Herstart via Start-Echo-App.bat om de pakketten te installeren.",
    ),
    "camera_open": (
        "Cannot open the webcam. Close Camera Lab or other camera apps, check Windows camera permissions, or try another camera number.",
        "De webcam kan niet openen. Sluit Camera Lab of andere camera-apps, controleer de Windows-camerarechten of probeer een ander cameranummer.",
    ),
    "camera_read": (
        "Camera frames are unavailable. Detection has stopped; lock Windows manually and restart detection when the camera is available.",
        "Geen camerabeelden beschikbaar. Detectie is gestopt; vergrendel Windows zelf en start opnieuw zodra de camera beschikbaar is.",
    ),
    "camera_model": (
        "The local face detector could not load. Reinstall opencv-contrib-python.",
        "De lokale gezichtsdetector kan niet laden. Installeer opencv-contrib-python opnieuw.",
    ),
    "camera_processing": ("Camera processing failed; detection stopped.", "Cameraverwerking mislukt; detectie gestopt."),
    "camera_release": ("The webcam could not be released. Restart Echo.", "De webcam kon niet worden vrijgegeven. Herstart Echo."),
    "lock_failed": (
        "Windows rejected the lock request. Detection stopped; use Windows+L to lock manually.",
        "Windows heeft het vergrendelverzoek geweigerd. Detectie gestopt; vergrendel zelf met Windows+L.",
    ),
    "sound_failed": ("The return sound failed; detection stopped.", "Het terugkomstsignaal is mislukt; detectie gestopt."),
}


class PresenceError(Exception):
    def __init__(self, code: str, status: int = 503):
        self.code = code
        self.status = status
        super().__init__(ERROR_MESSAGES[code][0])

    def localized(self, dutch: bool) -> str:
        return ERROR_MESSAGES[self.code][1 if dutch else 0]


@dataclass(frozen=True)
class PresenceSettings:
    delay_seconds: int = 30
    camera_index: int = 0
    notify: bool = True

    @classmethod
    def from_payload(cls, payload: object) -> "PresenceSettings":
        if not isinstance(payload, dict) or set(payload) != {"delay_seconds", "camera_index", "notify"}:
            raise PresenceError("invalid_settings", 400)
        delay = payload["delay_seconds"]
        camera = payload["camera_index"]
        notify = payload["notify"]
        if (
            type(delay) is not int or not 10 <= delay <= 600
            or type(camera) is not int or not 0 <= camera <= 10
            or type(notify) is not bool
        ):
            raise PresenceError("invalid_settings", 400)
        return cls(delay, camera, notify)


class PresenceTracker:
    def __init__(self, delay_seconds: int):
        self.delay_seconds = delay_seconds
        self.armed = False
        self.lock_requested = False
        self.face_detected = False
        self.present_since: float | None = None
        self.absent_since: float | None = None
        self.phase = "waiting"

    def update(self, face_detected: bool, now: float) -> str | None:
        self.face_detected = face_detected
        if face_detected:
            self.absent_since = None
            if self.present_since is None:
                self.present_since = now
            if now - self.present_since < FACE_STABLE_SECONDS:
                self.phase = "confirming"
                return None
            self.phase = "present"
            self.armed = True
            if self.lock_requested:
                self.lock_requested = False
                return "returned"
        else:
            self.present_since = None
            if not self.armed:
                self.phase = "waiting"
            elif self.lock_requested:
                self.phase = "lock_requested"
            else:
                if self.absent_since is None:
                    self.absent_since = now
                self.phase = "away"
                if now - self.absent_since >= self.delay_seconds:
                    self.lock_requested = True
                    self.phase = "lock_requested"
                    return "lock"
        return None

    def remaining(self, now: float) -> int | None:
        if self.phase != "away" or self.absent_since is None:
            return None
        return max(0, math.ceil(self.delay_seconds - (now - self.absent_since)))


def lock_windows() -> None:
    if sys.platform != "win32":
        raise PresenceError("unsupported")
    try:
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        user32.LockWorkStation.argtypes = []
        user32.LockWorkStation.restype = wintypes.BOOL
        if not user32.LockWorkStation():
            raise ctypes.WinError(ctypes.get_last_error())
    except OSError as exc:
        raise PresenceError("lock_failed") from exc


def play_return_sound() -> None:
    import winsound

    try:
        winsound.Beep(880, 200)
    except RuntimeError as exc:
        raise PresenceError("sound_failed") from exc


class CameraSource:
    _lock = threading.RLock()
    _sources: dict[int, "CameraSource"] = {}

    @classmethod
    def acquire(cls, camera_index: int) -> "CameraSource":
        with cls._lock:
            previous = cls._sources.get(camera_index)
            if previous is not None and previous._users == 0:
                if previous._thread.is_alive():
                    raise PresenceError("camera_release")
                del cls._sources[camera_index]
            if camera_index not in cls._sources:
                cls._sources[camera_index] = cls(camera_index)
            source = cls._sources[camera_index]
            source._users += 1
            return source

    def __init__(self, camera_index: int):
        try:
            import cv2
        except (ImportError, OSError) as exc:
            raise PresenceError("camera_dependency") from exc
        self.cv2 = cv2
        self._index = camera_index
        self._users = 0
        self._condition = threading.Condition()
        self._stop = threading.Event()
        self._frame = None
        self._sequence = 0
        self._error: PresenceError | None = None
        self._release_error: PresenceError | None = None
        try:
            self.capture = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
        except cv2.error as exc:
            raise PresenceError("camera_open") from exc
        try:
            if not self.capture.isOpened():
                raise PresenceError("camera_open")
            for setting, value in ((cv2.CAP_PROP_FRAME_WIDTH, 640), (cv2.CAP_PROP_FRAME_HEIGHT, 480), (cv2.CAP_PROP_FPS, 30)):
                if not self.capture.set(setting, value):
                    LOGGER.debug("Camera %s does not support capture setting %s=%s", camera_index, setting, value)
        except (cv2.error, PresenceError) as exc:
            try:
                self.capture.release()
            except cv2.error as release_error:
                raise PresenceError("camera_release") from release_error
            raise PresenceError("camera_open") from exc
        self._thread = threading.Thread(target=self._capture, name=f"echo-camera-{camera_index}", daemon=True)
        try:
            self._thread.start()
        except RuntimeError as exc:
            try:
                self.capture.release()
            except cv2.error as release_error:
                raise PresenceError("camera_release") from release_error
            raise PresenceError("camera_open") from exc

    def _capture(self) -> None:
        cv2 = self.cv2
        try:
            while not self._stop.is_set():
                ok, frame = self.capture.read()
                if self._stop.is_set():
                    break
                if not ok or frame is None or frame.size == 0:
                    raise PresenceError("camera_read")
                height, width = frame.shape[:2]
                if width > 640:
                    frame = cv2.resize(frame, (640, max(1, round(height * 640 / width))))
                with self._condition:
                    # Replace, never queue: a slow detector must not replay old gestures.
                    self._frame = frame.copy()
                    self._sequence += 1
                    self._condition.notify_all()
                self._stop.wait(0.001)
        except (PresenceError, cv2.error) as exc:
            LOGGER.exception("Shared camera capture failed")
            with self._condition:
                self._error = exc if isinstance(exc, PresenceError) else PresenceError("camera_processing")
        finally:
            try:
                self.capture.release()
            except cv2.error:
                LOGGER.exception("Shared camera release failed")
                with self._condition:
                    self._release_error = PresenceError("camera_release")
            with self._condition:
                self._frame = None
                self._stop.set()
                self._condition.notify_all()

    def read(self):
        with self._condition:
            return self.read_newer(self._sequence)[0]

    def read_newer(self, after: int):
        """Return the latest frame newer than `after` without waiting if one is already pending."""
        with self._condition:
            ready = self._condition.wait_for(
                lambda: self._sequence > after or self._error is not None or self._stop.is_set(),
                timeout=CAMERA_FRAME_TIMEOUT,
            )
            if self._error is not None:
                raise PresenceError(self._error.code) from self._error
            if not ready or self._stop.is_set() or self._frame is None:
                raise PresenceError("camera_read")
            return self._frame.copy(), self._sequence

    def close(self) -> None:
        with self._lock:
            self._users -= 1
            if self._users == 0:
                with self._condition:
                    self._stop.set()
                    self._condition.notify_all()
                self._thread.join(timeout=CAMERA_CLOSE_TIMEOUT)
                if self._thread.is_alive():
                    raise PresenceError("camera_release")
                del self._sources[self._index]
                if self._release_error is not None:
                    raise self._release_error


class CameraDetector:
    def __init__(self, camera_index: int):
        self.source = CameraSource.acquire(camera_index)
        self.cv2 = self.source.cv2
        try:
            self.detector = self.cv2.CascadeClassifier(
                str(Path(self.cv2.data.haarcascades) / "haarcascade_frontalface_default.xml")
            )
            if self.detector.empty():
                raise PresenceError("camera_model")
        except (self.cv2.error, PresenceError) as exc:
            self.source.close()
            raise PresenceError("camera_model") from exc

    def read(self) -> bool:
        cv2 = self.cv2
        frame = self.source.read()
        try:
            gray = cv2.equalizeHist(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
            faces = self.detector.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40)
            )
            return len(faces) > 0
        except cv2.error as exc:
            raise PresenceError("camera_processing") from exc

    def close(self) -> None:
        self.source.close()


class PresenceMonitor:
    def __init__(self):
        self._lock = threading.RLock()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._settings = PresenceSettings()
        self._tracker = PresenceTracker(self._settings.delay_seconds)
        self._phase = "stopped"
        self._error = ""
        self._returns = 0

    def snapshot(self) -> dict:
        with self._lock:
            running = self._thread is not None and self._thread.is_alive()
            return {
                "supported": sys.platform == "win32",
                "running": running,
                "phase": self._phase,
                "error_code": self._error,
                "face_detected": self._tracker.face_detected if running else False,
                "seconds_remaining": self._tracker.remaining(time.monotonic()) if self._phase == "away" else None,
                "return_count": self._returns,
                "delay_seconds": self._settings.delay_seconds,
                "camera_index": self._settings.camera_index,
                "notify": self._settings.notify,
            }

    def start(self, settings: PresenceSettings) -> None:
        if sys.platform != "win32":
            raise PresenceError("unsupported")
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                raise PresenceError("already_running", 409)
            self._settings = settings
            self._tracker = PresenceTracker(settings.delay_seconds)
            self._phase = "starting"
            self._error = ""
            self._returns = 0
            self._stop.clear()
            self._thread = threading.Thread(target=self._run, name="echo-presence", daemon=True)
            self._thread.start()

    def stop(self) -> None:
        with self._lock:
            self._stop.set()
            worker = self._thread
            if worker is not None and worker.is_alive() and not self._error:
                self._phase = "stopping"
        if worker is not None:
            worker.join(timeout=3)

    def _record_error(self, error: PresenceError) -> None:
        LOGGER.exception("Presence detection failed: %s", error.code)
        with self._lock:
            self._error = error.code
            self._phase = "error"
            self._stop.set()

    def _run(self) -> None:
        camera = None
        try:
            camera = CameraDetector(self._settings.camera_index)
            while not self._stop.is_set():
                face_detected = camera.read()
                with self._lock:
                    if self._stop.is_set():
                        break
                    action = self._tracker.update(face_detected, time.monotonic())
                    self._phase = self._tracker.phase
                    if action == "lock":
                        lock_windows()
                    elif action == "returned":
                        self._returns += 1
                        if self._settings.notify:
                            play_return_sound()
                self._stop.wait(POLL_SECONDS)
        except PresenceError as exc:
            self._record_error(exc)
        finally:
            if camera is not None:
                try:
                    camera.close()
                except PresenceError as exc:
                    self._record_error(exc)
            with self._lock:
                if not self._error:
                    self._phase = "stopped"
