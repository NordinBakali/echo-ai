import threading
import time
from queue import Queue
from unittest.mock import Mock

import cv2
import numpy as np
import pytest

import echo_presence as presence


@pytest.fixture(autouse=True)
def forbid_real_camera(monkeypatch):
    monkeypatch.setattr(cv2, "VideoCapture", lambda *_args: pytest.fail("A test accessed the real webcam"))


def test_tracker_waits_for_stable_initial_face_and_exact_absence_timeout():
    tracker = presence.PresenceTracker(30)
    assert tracker.update(False, 0) is None
    assert tracker.update(False, 1000) is None
    assert tracker.phase == "waiting"
    tracker.update(True, 1001)
    tracker.update(False, 1002)
    assert not tracker.armed
    tracker.update(True, 1003)
    tracker.update(True, 1004.99)
    assert not tracker.armed
    assert tracker.update(True, 1005) is None
    assert tracker.armed
    tracker.update(False, 1006)
    assert tracker.remaining(1006) == 30
    assert tracker.update(False, 1035.999) is None
    assert tracker.remaining(1035.999) == 1
    assert tracker.update(False, 1036) == "lock"
    assert tracker.remaining(1036) is None
    assert tracker.update(False, 2000) is None


def test_tracker_cancels_countdown_and_only_signals_once_after_stable_return():
    tracker = presence.PresenceTracker(10)
    tracker.update(True, 0)
    tracker.update(True, 2)
    tracker.update(False, 3)
    tracker.update(True, 12)
    tracker.update(False, 13)
    assert tracker.update(False, 22.99) is None
    assert tracker.update(False, 23) == "lock"
    tracker.update(True, 24)
    tracker.update(False, 25)
    tracker.update(True, 26)
    assert tracker.update(True, 27.99) is None
    assert tracker.update(True, 28) == "returned"
    assert tracker.update(True, 30) is None
    tracker.update(False, 31)
    assert tracker.update(False, 41) == "lock"
    tracker.update(True, 42)
    assert tracker.update(True, 44) == "returned"


@pytest.mark.parametrize("payload", [
    None, [], {}, {"delay_seconds": 30},
    {"delay_seconds": True, "camera_index": 0, "notify": True},
    {"delay_seconds": 9, "camera_index": 0, "notify": True},
    {"delay_seconds": 601, "camera_index": 0, "notify": True},
    {"delay_seconds": 30.0, "camera_index": 0, "notify": True},
    {"delay_seconds": "30", "camera_index": 0, "notify": True},
    {"delay_seconds": 30, "camera_index": -1, "notify": True},
    {"delay_seconds": 30, "camera_index": 11, "notify": True},
    {"delay_seconds": 30, "camera_index": False, "notify": True},
    {"delay_seconds": 30, "camera_index": 0, "notify": "false"},
    {"delay_seconds": 30, "camera_index": 0, "notify": True, "unlock": True},
])
def test_settings_reject_invalid_types_ranges_and_unknown_fields(payload):
    with pytest.raises(presence.PresenceError) as error:
        presence.PresenceSettings.from_payload(payload)
    assert error.value.status == 400


@pytest.mark.parametrize(("delay", "camera"), [(10, 0), (600, 10)])
def test_settings_accept_range_boundaries(delay, camera):
    settings = presence.PresenceSettings.from_payload({
        "delay_seconds": delay, "camera_index": camera, "notify": False,
    })
    assert settings == presence.PresenceSettings(delay, camera, False)


def test_windows_lock_checks_the_actual_api_result(monkeypatch):
    monkeypatch.setattr(presence.sys, "platform", "win32")
    user32 = Mock()
    monkeypatch.setattr(presence.ctypes, "WinDLL", Mock(return_value=user32), raising=False)
    user32.LockWorkStation.return_value = True
    presence.lock_windows()
    user32.LockWorkStation.assert_called_once_with()
    user32.LockWorkStation.return_value = False
    monkeypatch.setattr(presence.ctypes, "get_last_error", lambda: 5, raising=False)
    monkeypatch.setattr(presence.ctypes, "WinError", lambda _code: OSError("Denied"), raising=False)
    with pytest.raises(presence.PresenceError, match="Windows rejected"):
        presence.lock_windows()


def test_unsupported_platform_never_opens_camera(monkeypatch):
    monkeypatch.setattr(presence.sys, "platform", "linux")
    monitor = presence.PresenceMonitor()
    assert not monitor.snapshot()["supported"]
    with pytest.raises(presence.PresenceError, match="requires Windows"):
        monitor.start(presence.PresenceSettings())
    with pytest.raises(presence.PresenceError, match="requires Windows"):
        presence.lock_windows()
    assert not monitor.snapshot()["running"]


def test_real_local_classifier_loads_and_processes_synthetic_frames(monkeypatch):
    capture = Mock()
    capture.read.return_value = (True, np.zeros((720, 1280, 3), dtype=np.uint8))
    monkeypatch.setattr(cv2, "VideoCapture", Mock(return_value=capture))
    camera = presence.CameraDetector(0)
    assert camera.read() is False
    capture.read.return_value = (False, None)
    with pytest.raises(presence.PresenceError, match="Camera frames"):
        camera.read()
    camera.close()
    capture.release.assert_called_once()


def test_camera_open_failure_releases_handle(monkeypatch):
    capture = Mock()
    capture.isOpened.return_value = False
    monkeypatch.setattr(cv2, "VideoCapture", Mock(return_value=capture))
    with pytest.raises(presence.PresenceError, match="Cannot open"):
        presence.CameraDetector(0)
    capture.release.assert_called_once()


def test_shared_camera_drains_old_frames_without_waiting_for_a_consumer(monkeypatch):
    frames = Queue()
    drained = threading.Event()
    for value in range(1, 21):
        frames.put((True, np.full((2, 2, 3), value, dtype=np.uint8)))
    capture = Mock()

    def read():
        result = frames.get(timeout=3)
        if result[0] and int(result[1][0, 0, 0]) == 20:
            drained.set()
        return result

    capture.read.side_effect = read
    monkeypatch.setattr(cv2, "VideoCapture", Mock(return_value=capture))
    source = presence.CameraSource.acquire(0)
    producer = None
    try:
        assert drained.wait(1), "Capture must drain the driver even while inference/UI is idle"
        producer = threading.Timer(0.03, lambda: frames.put((True, np.full((2, 2, 3), 21, dtype=np.uint8))))
        producer.start()
        frame = source.read()
        assert int(frame[0, 0, 0]) >= 20
    finally:
        if producer:
            producer.join(timeout=1)
        frames.put((False, None))
        source.close()
    capture.release.assert_called_once()


def test_camera_never_reuses_a_cached_frame_when_capture_stalls(monkeypatch):
    frames = Queue()
    frames.put((True, np.zeros((2, 2, 3), dtype=np.uint8)))
    capture = Mock()
    capture.read.side_effect = lambda: frames.get(timeout=3)
    monkeypatch.setattr(cv2, "VideoCapture", Mock(return_value=capture))
    monkeypatch.setattr(presence, "CAMERA_FRAME_TIMEOUT", 0.03)
    source = presence.CameraSource.acquire(0)
    try:
        with source._condition:
            assert source._condition.wait_for(lambda: source._sequence == 1, timeout=1)
        with pytest.raises(presence.PresenceError, match="Camera frames"):
            source.read()
    finally:
        frames.put((False, None))
        source.close()
    capture.release.assert_called_once()


def test_reader_gets_a_pending_newer_frame_without_waiting_but_never_the_same_frame_twice(monkeypatch):
    frames = Queue()
    frames.put((True, np.full((2, 2, 3), 7, dtype=np.uint8)))
    capture = Mock()
    capture.read.side_effect = lambda: frames.get(timeout=3)
    monkeypatch.setattr(cv2, "VideoCapture", Mock(return_value=capture))
    monkeypatch.setattr(presence, "CAMERA_FRAME_TIMEOUT", 0.2)
    source = presence.CameraSource.acquire(0)
    try:
        with source._condition:
            assert source._condition.wait_for(lambda: source._sequence == 1, timeout=1)
        started = time.monotonic()
        frame, sequence = source.read_newer(0)
        assert time.monotonic() - started < 0.1
        assert (int(frame[0, 0, 0]), sequence) == (7, 1)
        with pytest.raises(presence.PresenceError, match="Camera frames"):
            source.read_newer(sequence)
    finally:
        frames.put((False, None))
        source.close()
    capture.release.assert_called_once()


def test_camera_close_timeout_prevents_second_handle_and_releases_on_reader_exit(monkeypatch):
    reading, unblock = threading.Event(), threading.Event()
    capture = Mock()

    def read():
        reading.set()
        assert unblock.wait(3)
        return True, np.zeros((2, 2, 3), dtype=np.uint8)

    capture.read.side_effect = read
    factory = Mock(return_value=capture)
    monkeypatch.setattr(cv2, "VideoCapture", factory)
    monkeypatch.setattr(presence, "CAMERA_CLOSE_TIMEOUT", 0.03)
    source = presence.CameraSource.acquire(0)
    try:
        assert reading.wait(1)
        with pytest.raises(presence.PresenceError, match="released"):
            source.close()
        with pytest.raises(presence.PresenceError, match="released"):
            presence.CameraSource.acquire(0)
        factory.assert_called_once()
        capture.release.assert_not_called()
    finally:
        unblock.set()
        source._thread.join(timeout=1)
    capture.release.assert_called_once()
    replacement = presence.CameraSource.acquire(0)
    replacement.close()
    assert factory.call_count == 2
    assert capture.release.call_count == 2


def test_camera_reader_start_failure_releases_handle(monkeypatch):
    capture = Mock()
    monkeypatch.setattr(cv2, "VideoCapture", Mock(return_value=capture))
    monkeypatch.setattr(threading.Thread, "start", Mock(side_effect=RuntimeError("Cannot create thread")))
    with pytest.raises(presence.PresenceError, match="Cannot open"):
        presence.CameraSource.acquire(0)
    capture.release.assert_called_once()
    assert 0 not in presence.CameraSource._sources


@pytest.mark.parametrize("notify", [True, False])
def test_monitor_full_away_return_cycle_uses_settings_and_releases_camera(monkeypatch, notify):
    monkeypatch.setattr(presence.sys, "platform", "win32")
    monkeypatch.setattr(presence, "POLL_SECONDS", 0)
    clock = Mock()
    monkeypatch.setattr(presence, "time", clock)
    frames = iter([(0, True), (2, True), (3, False), (12.999, False), (13, False),
                   (14, False), (15, True), (17, True), (18, True)])
    monitor = presence.PresenceMonitor()
    camera = Mock()

    def read():
        item = next(frames, None)
        if item is None:
            monitor._stop.set()
            return True
        now, face = item
        clock.monotonic.return_value = now
        return face

    camera.read.side_effect = read
    factory = Mock(return_value=camera)
    lock = Mock()
    sound = Mock()
    monkeypatch.setattr(presence, "CameraDetector", factory)
    monkeypatch.setattr(presence, "lock_windows", lock)
    monkeypatch.setattr(presence, "play_return_sound", sound)
    monitor.start(presence.PresenceSettings(10, 2, notify))
    monitor._thread.join(timeout=3)
    assert not monitor.snapshot()["running"]
    assert monitor.snapshot()["return_count"] == 1
    assert monitor.snapshot()["error_code"] == ""
    factory.assert_called_once_with(2)
    lock.assert_called_once_with()
    assert sound.call_count == int(notify)
    camera.close.assert_called_once()


@pytest.mark.parametrize("error_code", ["camera_open", "camera_read", "lock_failed", "sound_failed", "camera_release"])
def test_monitor_surfaces_failures_and_stops(monkeypatch, error_code):
    monkeypatch.setattr(presence.sys, "platform", "win32")
    monkeypatch.setattr(presence, "POLL_SECONDS", 0)
    camera = Mock()
    camera.read.return_value = False
    factory = Mock(return_value=camera)
    lock = Mock()
    sound = Mock()
    monitor = presence.PresenceMonitor()
    monkeypatch.setattr(presence, "CameraDetector", factory)
    monkeypatch.setattr(presence, "lock_windows", lock)
    monkeypatch.setattr(presence, "play_return_sound", sound)
    error = presence.PresenceError(error_code)
    if error_code == "camera_open":
        factory.side_effect = error
    elif error_code == "camera_read":
        camera.read.side_effect = error
    elif error_code == "camera_release":
        camera.read.side_effect = lambda: monitor._stop.set()
        camera.close.side_effect = error
    else:
        action = "lock" if error_code == "lock_failed" else "returned"
        monkeypatch.setattr(presence.PresenceTracker, "update", lambda *_args: action)
        (lock if action == "lock" else sound).side_effect = error
    monitor.start(presence.PresenceSettings())
    monitor._thread.join(timeout=3)
    snapshot = monitor.snapshot()
    assert snapshot["phase"] == "error"
    assert snapshot["error_code"] == error_code
    assert not snapshot["running"]
    if error_code != "camera_open":
        camera.close.assert_called_once()
    if error_code.startswith("camera"):
        lock.assert_not_called()
        sound.assert_not_called()


def test_stop_prevents_late_frame_from_locking_and_allows_restart(monkeypatch):
    monkeypatch.setattr(presence.sys, "platform", "win32")
    monitor = presence.PresenceMonitor()
    reading = threading.Event()
    camera = Mock()
    lock = Mock()

    def read():
        reading.set()
        assert monitor._stop.wait(timeout=3)
        return False

    camera.read.side_effect = read
    monkeypatch.setattr(presence, "CameraDetector", Mock(return_value=camera))
    monkeypatch.setattr(presence.PresenceTracker, "update", lambda *_args: "lock")
    monkeypatch.setattr(presence, "lock_windows", lock)
    for _ in range(2):
        reading.clear()
        monitor.start(presence.PresenceSettings())
        assert reading.wait(timeout=3)
        with pytest.raises(presence.PresenceError) as error:
            monitor.start(presence.PresenceSettings())
        assert error.value.status == 409
        monitor.stop()
        assert not monitor.snapshot()["running"]
        assert monitor.snapshot()["phase"] == "stopped"
    assert camera.close.call_count == 2
    lock.assert_not_called()
