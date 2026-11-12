import threading
from unittest.mock import Mock

import pytest

import echo_presence as presence
import server


@pytest.fixture()
def client(monkeypatch):
    monitor = presence.PresenceMonitor()
    monkeypatch.setattr(server, "AANWEZIGHEID_MONITOR", monitor)
    monkeypatch.setattr(server, "ECHO_DEMO_MODE", False)
    monkeypatch.setattr(server, "ECHO_ENTERPRISE_MODE", False)
    monkeypatch.setitem(server.instellingen, "taal", "Nederlands")
    monkeypatch.setattr(presence.sys, "platform", "win32")
    monkeypatch.setattr(presence, "CameraDetector", lambda *_args: pytest.fail("Unexpected camera access"))
    monkeypatch.setattr(presence, "lock_windows", lambda: pytest.fail("Unexpected lock"))
    server.app.config.update(TESTING=True)
    try:
        with server.app.test_client() as test_client:
            yield test_client
    finally:
        monitor.stop()


def headers(**extra):
    return {"X-Echo-Presence-Token": server.AANWEZIGHEID_TOKEN, **extra}


def test_page_link_localization_and_default_off_status(client, monkeypatch):
    assert b"/aanwezigheid" in client.get("/").data
    response = client.get("/aanwezigheid")
    assert response.status_code == 200
    assert b'lang="nl"' in response.data
    assert server.AANWEZIGHEID_TOKEN.encode() in response.data
    assert "no-store" in response.headers["Cache-Control"]
    snapshot = client.get("/api/aanwezigheid/status").json["presence"]
    assert snapshot["phase"] == "stopped"
    assert snapshot["running"] is False
    assert snapshot["delay_seconds"] == 30
    monkeypatch.setitem(server.instellingen, "taal", "English")
    assert b'lang="en"' in client.get("/aanwezigheid").data


@pytest.mark.parametrize("path", ["/aanwezigheid", "/api/aanwezigheid/status", "/api/aanwezigheid/start", "/api/aanwezigheid/stop"])
@pytest.mark.parametrize("attack", ["remote", "host", "origin", "scheme", "null_origin", "cross_site"])
def test_presence_is_local_only_and_rejects_cross_origin(client, path, attack):
    options = {}
    request_headers = headers()
    if attack == "remote":
        options["environ_overrides"] = {"REMOTE_ADDR": "192.168.1.40"}
        request_headers["X-Forwarded-For"] = "127.0.0.1"
    elif attack == "host":
        options["base_url"] = "http://attacker.example"
    elif attack == "origin":
        request_headers["Origin"] = "http://attacker.example"
    elif attack == "scheme":
        request_headers["Origin"] = "https://localhost"
    elif attack == "null_origin":
        request_headers["Origin"] = "null"
    else:
        request_headers["Sec-Fetch-Site"] = "cross-site"
    method = "POST" if path.endswith(("/start", "/stop")) else "GET"
    response = client.open(path, method=method, headers=request_headers, json={}, **options)
    assert response.status_code == 403
    assert "Access-Control-Allow-Origin" not in response.headers


@pytest.mark.parametrize("mode", ["ECHO_DEMO_MODE", "ECHO_ENTERPRISE_MODE"])
def test_presence_blocked_in_shared_modes(client, monkeypatch, mode):
    monkeypatch.setattr(server, mode, True)
    with server.app.test_request_context("/aanwezigheid", environ_base={"REMOTE_ADDR": "127.0.0.1"}):
        response, status = server.beveilig_aanwezigheid()
        assert status == 403
        assert response.json["status"] == "error"


@pytest.mark.parametrize("action", ["start", "stop"])
def test_control_requires_token_and_json(client, action):
    path = f"/api/aanwezigheid/{action}"
    assert client.post(path, json={}).status_code == 403
    assert client.post(path, json={}, headers={"X-Echo-Presence-Token": "invalid"}).status_code == 403
    assert client.post(path, data="{}", headers=headers(), content_type="text/plain").status_code == 415


def test_start_rejects_bad_json_and_unknown_options(client):
    response = client.post("/api/aanwezigheid/start", headers=headers(), data="{", content_type="application/json")
    assert response.status_code == 400
    assert response.json["status"] == "error"
    response = client.post("/api/aanwezigheid/start", headers=headers(), json={"enabled": True})
    assert response.status_code == 400


def test_start_readback_duplicate_stop_and_reset(client, monkeypatch):
    monitor = server.AANWEZIGHEID_MONITOR
    camera = Mock()
    reading = threading.Event()

    def read():
        reading.set()
        monitor._stop.wait(timeout=3)
        return True

    camera.read.side_effect = read
    factory = Mock(return_value=camera)
    monkeypatch.setattr(presence, "CameraDetector", factory)
    settings = {"delay_seconds": 45, "camera_index": 1, "notify": False}
    response = client.post("/api/aanwezigheid/start", json=settings, headers=headers(Origin="http://localhost"))
    assert response.status_code == 200
    assert reading.wait(timeout=3)
    snapshot = client.get("/api/aanwezigheid/status").json["presence"]
    assert snapshot["running"]
    for key, value in settings.items():
        assert snapshot[key] == value
    assert client.post("/api/aanwezigheid/start", json=settings, headers=headers()).status_code == 409
    response = client.post("/api/aanwezigheid/stop", json={}, headers=headers())
    assert response.json["presence"]["phase"] == "stopped"
    assert not response.json["presence"]["running"]
    camera.close.assert_called_once()
    assert presence.PresenceMonitor().snapshot()["phase"] == "stopped"


def test_async_camera_error_is_visible_and_localized(client, monkeypatch):
    monkeypatch.setattr(presence, "CameraDetector", Mock(side_effect=presence.PresenceError("camera_open")))
    client.post("/api/aanwezigheid/start", headers=headers(),
                json={"delay_seconds": 30, "camera_index": 0, "notify": True})
    server.AANWEZIGHEID_MONITOR._thread.join(timeout=3)
    snapshot = client.get("/api/aanwezigheid/status").json["presence"]
    assert snapshot["phase"] == "error"
    assert "De webcam kan niet openen" in snapshot["error_message"]


def test_existing_manual_lock_uses_checked_windows_helper(monkeypatch):
    lock = Mock()
    monkeypatch.setattr(presence, "lock_windows", lock)
    server.voer_bevestigde_systeemactie_uit("lock computer")
    lock.assert_called_once()
