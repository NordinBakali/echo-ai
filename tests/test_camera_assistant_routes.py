from dataclasses import asdict
from unittest.mock import Mock

import pytest

import echo_camera_assistant as coach
import server


@pytest.fixture()
def client(monkeypatch):
    monitor = coach.CameraAssistantMonitor()
    monkeypatch.setattr(server, "CAMERA_ASSISTENT", monitor)
    monkeypatch.setattr(server, "ECHO_DEMO_MODE", False)
    monkeypatch.setattr(server, "ECHO_ENTERPRISE_MODE", False)
    monkeypatch.setitem(server.instellingen, "taal", "Nederlands")
    monkeypatch.setattr(coach, "LandmarkDetector", lambda *_args: pytest.fail("No real camera allowed"))
    monkeypatch.setattr(coach, "perform_action", lambda *_args: pytest.fail("No real action allowed"))
    server.app.config.update(TESTING=True)
    with server.app.test_client() as client:
        yield client
    monitor.stop()


def test_link_page_language_initial_status_and_no_caching(client, monkeypatch):
    assert b"/camera-assistent" in client.get("/").data
    assert b"/camera-assistent" in client.get("/aanwezigheid").data
    page = client.get("/camera-assistent")
    assert page.status_code == 200 and b'lang="nl"' in page.data
    assert page.headers["Cache-Control"] == "no-store"
    assert b"Microfoon weer aan" in page.data
    assert b'id="coach-guide"' in page.data and b'id="coach-progress"' in page.data
    status = client.get("/api/camera-assistent/status")
    assert "Access-Control-Allow-Origin" not in status.headers
    assert status.json["camera"]["phase"] == "stopped"
    assert not status.json["camera"]["armed"]
    assert status.json["camera"]["hands"] == []
    assert status.json["camera"]["cooldown_seconds"] == 0
    monkeypatch.setitem(server.instellingen, "taal", "English")
    assert b'lang="en"' in client.get("/camera-assistent").data


def test_camera_page_language_can_change_without_changing_echo_preference(client):
    assert b'lang="en"' in client.get("/camera-assistent?lang=en").data
    assert b'lang="nl"' in client.get("/camera-assistent?lang=nl").data
    assert b'lang="nl"' in client.get("/camera-assistent?lang=invalid").data
    assert server.instellingen["taal"] == "Nederlands"

    headers = {
        "X-Echo-Presence-Token": server.AANWEZIGHEID_TOKEN,
        "X-Echo-UI-Language": "en",
    }
    response = client.post("/api/camera-assistent/train", json={"target": "activate"}, headers=headers)
    assert response.status_code == 409
    assert response.json["message"] == "Start the camera assistant first."
    headers["X-Echo-UI-Language"] = "nl"
    response = client.post("/api/camera-assistent/train", json={"target": "activate"}, headers=headers)
    assert response.status_code == 409
    assert response.json["message"] == "Start eerst de camera-assistent."
    headers["X-Echo-Presence-Token"] = "expired-token"
    response = client.post("/api/camera-assistent/train", json={"target": "activate"}, headers=headers)
    assert response.status_code == 403
    assert "Vernieuw" in response.json["message"] and "camera-assistent" in response.json["message"]
    headers["X-Echo-UI-Language"] = "en"
    response = client.post("/api/camera-assistent/train", json={"target": "activate"}, headers=headers)
    assert response.status_code == 403
    assert "Reload" in response.json["message"] and "camera assistant" in response.json["message"]
    assert server.instellingen["taal"] == "Nederlands"


@pytest.mark.parametrize("path", ["/camera-assistent", "/api/camera-assistent/status", "/api/camera-assistent/microphones", "/api/camera-assistent/arm"])
@pytest.mark.parametrize("attack", ["remote", "host", "origin"])
def test_camera_actions_and_data_require_local_origin(client, path, attack):
    options = {}
    headers = {"X-Echo-Presence-Token": server.AANWEZIGHEID_TOKEN}
    if attack == "remote":
        options["environ_overrides"] = {"REMOTE_ADDR": "192.168.1.40"}
        headers["X-Forwarded-For"] = "127.0.0.1"
    elif attack == "host":
        options["base_url"] = "http://untrusted.example"
    else:
        headers["Origin"] = "http://untrusted.example"
    response = client.open(path, method="POST" if path.endswith("/arm") else "GET",
                           json={"enabled": True}, headers=headers, **options)
    assert response.status_code == 403
    assert "Access-Control-Allow-Origin" not in response.headers


@pytest.mark.parametrize("action", ["start", "stop", "train", "arm", "unmute"])
def test_every_action_requires_csrf_token_and_json(client, action):
    path = "/api/camera-assistent/" + action
    assert client.post(path, json={}).status_code == 403
    headers = {"X-Echo-Presence-Token": server.AANWEZIGHEID_TOKEN}
    assert client.post(path, data="{}", headers=headers, content_type="text/plain").status_code == 415
    assert client.post(path, json=[], headers=headers).status_code == 400


def test_training_action_validation_and_cannot_arm_before_training(client):
    headers = {"X-Echo-Presence-Token": server.AANWEZIGHEID_TOKEN}
    assert client.post("/api/camera-assistent/arm", json={"enabled": True}, headers=headers).status_code == 409
    assert client.post("/api/camera-assistent/arm", json={"enabled": "true"}, headers=headers).status_code == 400
    assert client.post("/api/camera-assistent/train", json={"target": []}, headers=headers).status_code == 400
    assert client.post("/api/camera-assistent/execute", json={"keys": "anything"}, headers=headers).status_code == 400


def test_one_scan_requires_opt_in_then_enables_without_second_pose(client, camera_observation):
    monitor = server.CAMERA_ASSISTENT
    monitor._phase = "monitoring"
    headers = {"X-Echo-Presence-Token": server.AANWEZIGHEID_TOKEN}
    path = "/api/camera-assistent/train"
    assert client.post(path, json={"target": "activate"}).status_code == 403
    assert not monitor.snapshot()["armed"]
    response = client.post(path, json={"target": "activate"}, headers=headers)
    assert response.status_code == 200
    assert response.json["camera"]["training"] == "activate"
    assert not response.json["camera"]["armed"]
    start = monitor._training.last
    body, hands = camera_observation("open")
    for i in range(11):
        monitor._observe(body, hands, start + i / 10)
    status = client.get("/api/camera-assistent/status").json["camera"]
    assert status["gesture_ready"] and status["armed"]
    assert status["notice"] == "scan_complete"
    assert status["trained"] == []


def test_start_reports_async_model_error_and_stop_still_works(client, monkeypatch):
    monkeypatch.setattr(coach, "LandmarkDetector", Mock(side_effect=coach.CameraAssistantError("models")))
    headers = {"X-Echo-Presence-Token": server.AANWEZIGHEID_TOKEN}
    assert client.post("/api/camera-assistent/start", json=asdict(coach.Settings()), headers=headers).status_code == 200
    server.CAMERA_ASSISTENT._thread.join(timeout=3)
    status = client.get("/api/camera-assistent/status").json["camera"]
    assert status["phase"] == "error"
    assert "modellen" in status["error_message"]
    english = client.get("/api/camera-assistent/status", headers={"X-Echo-UI-Language": "en"}).json["camera"]
    assert "models" in english["error_message"]
    assert client.post("/api/camera-assistent/stop", json={}, headers=headers).status_code == 200


@pytest.mark.parametrize("mode", ["ECHO_DEMO_MODE", "ECHO_ENTERPRISE_MODE"])
def test_shared_modes_block_new_camera_features(client, monkeypatch, mode):
    monkeypatch.setattr(server, mode, True)
    with server.app.test_request_context("/camera-assistent", environ_base={"REMOTE_ADDR": "127.0.0.1"}):
        assert server.beveilig_aanwezigheid()[1] == 403
