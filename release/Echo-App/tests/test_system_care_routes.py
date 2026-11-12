import copy
from unittest.mock import Mock

import pytest

import echo_system_care as care
import server


@pytest.fixture()
def client(monkeypatch, tmp_path):
    monitor = care.SystemCare(care.Store(tmp_path / "care.sqlite3"))
    monkeypatch.setattr(server, "SYSTEEMZORG", monitor)
    monkeypatch.setattr(server, "ECHO_DEMO_MODE", False)
    monkeypatch.setattr(server, "ECHO_ENTERPRISE_MODE", False)
    monkeypatch.setattr(server, "instellingen", copy.deepcopy(server.instellingen))
    monkeypatch.setitem(server.instellingen, "taal", "Nederlands")
    monkeypatch.setattr(server, "sla_instellingen_op", Mock())
    monkeypatch.setattr(care, "scan_lan", lambda *_: pytest.fail("No real LAN scan"))
    monkeypatch.setattr(care.resources, "execute", lambda *_: pytest.fail("No real OS actions"))
    server.app.config.update(TESTING=True)
    with server.app.test_client() as client:
        yield client
    monitor.stop()


def test_page_profiles_and_no_side_effects(client):
    assert b"/systeemzorg" in client.get("/").data
    page = client.get("/systeemzorg")
    assert page.status_code == 200 and b'lang="nl"' in page.data
    assert page.headers["Cache-Control"] == "no-store"
    response = client.get("/api/systeemzorg/status")
    assert not response.json["care"]["running"]
    assert "Access-Control-Allow-Origin" not in response.headers
    result = client.post("/api/instellingen", json={"instellingen_profiel": "gaming"}).json
    assert result["settings_profile"] == "gaming"
    assert "heavy_work" in result["settings_profiles"]
    assert result["hardware_job"] == ""


@pytest.mark.parametrize("path", [
    "/systeemzorg", "/api/systeemzorg/status", "/api/systeemzorg/resources", "/api/systeemzorg/automatic",
    "/api/systeemzorg/local-ai/models", "/api/systeemzorg/local-ai/analyze",
    "/api/systeemzorg/pressure-start", "/api/systeemzorg/pressure-stop",
])
@pytest.mark.parametrize("attack", ["remote", "host", "origin", "cross_site"])
def test_local_boundaries(client, path, attack):
    options = {}
    headers = {"X-Echo-System-Token": server.SYSTEEMZORG_TOKEN}
    if attack == "remote":
        options["environ_overrides"] = {"REMOTE_ADDR": "192.168.1.2"}
        headers["X-Forwarded-For"] = "127.0.0.1"
    elif attack == "host":
        options["base_url"] = "http://hostile.example"
    elif attack == "origin":
        headers["Origin"] = "http://hostile.example"
    else:
        headers["Sec-Fetch-Site"] = "cross-site"
    response = client.open(path, method="POST" if path.endswith(("automatic", "analyze", "pressure-start", "pressure-stop")) else "GET",
                           json={"enabled": True}, headers=headers, **options)
    assert response.status_code == 403
    assert "Access-Control-Allow-Origin" not in response.headers


@pytest.mark.parametrize("action", ["start", "stop", "trust", "policy", "preview", "execute", "automatic", "restore",
                                  "pressure-start", "pressure-stop"])
def test_all_mutations_need_token_and_object(client, action):
    path = "/api/systeemzorg/" + action
    assert client.post(path, json={}).status_code == 403
    headers = {"X-Echo-System-Token": server.SYSTEEMZORG_TOKEN}
    assert client.post(path, data="{}", headers=headers, content_type="text/plain").status_code == 415
    assert client.post(path, json=[], headers=headers).status_code == 400


@pytest.mark.parametrize("mode", ["ECHO_DEMO_MODE", "ECHO_ENTERPRISE_MODE"])
@pytest.mark.parametrize("path", ["/systeemzorg", "/api/systeemzorg/local-ai/models", "/api/systeemzorg/local-ai/analyze",
                                 "/api/systeemzorg/pressure-start", "/api/systeemzorg/pressure-stop"])
def test_shared_modes_cannot_use_system_care(client, monkeypatch, mode, path):
    monkeypatch.setattr(server, mode, True)
    with server.app.test_request_context(path, environ_base={"REMOTE_ADDR": "127.0.0.1"}):
        assert server.beveilig_systeemzorg()[1] == 403


def test_dashboard_hardware_hook_requires_local_token_and_manual_flag(client, monkeypatch):
    hook = Mock(return_value="running")
    monkeypatch.setattr(server.SYSTEEMZORG, "profile_changed", hook)
    data = {"instellingen_profiel": "heavy_work", "apply_profile": True}
    assert client.post("/api/instellingen", json=data).status_code == 200
    hook.assert_not_called()
    data["hardware_profile_apply"] = True
    client.post("/api/instellingen", json=data)
    assert hook.call_args.kwargs["authorized"] is False
    headers = {"X-Echo-System-Token": server.SYSTEEMZORG_TOKEN}
    client.post("/api/instellingen", json=data, headers=headers)
    assert hook.call_args.kwargs["authorized"] is True
    client.post("/api/instellingen", json=data, headers=headers, environ_overrides={"REMOTE_ADDR": "192.168.1.2"})
    assert hook.call_args.kwargs["authorized"] is False
    assert server.SYSTEEMZORG_TOKEN.encode() not in client.get("/", environ_overrides={"REMOTE_ADDR": "192.168.1.2"}).data


def test_notifications_never_invoke_cloud_speech(client, monkeypatch):
    voice = Mock()
    monkeypatch.setattr(server, "spreek_uit", voice)
    monkeypatch.setattr(server, "GESPREK_CONTEXT", {})
    server.systeemzorg_notificatie("security", "failed_login", "Local log signal", False)
    voice.assert_not_called()
    message = server.GESPREK_CONTEXT["notificaties"][0]["message"]
    assert message.startswith("[security]")
    assert "Local log signal" not in message


def test_pressure_routes_require_explicit_permission_and_use_local_speech_only(client, monkeypatch):
    headers = {"X-Echo-System-Token": server.SYSTEEMZORG_TOKEN}
    path = "/api/systeemzorg/pressure-start"
    foreground = Mock(side_effect=AssertionError("Unapproved start must not inspect or act"))
    monkeypatch.setattr(care.resources, "foreground_protection", foreground)
    assert client.post(path, json={"profile": "gaming", "speech": True}, headers=headers).status_code == 400
    data = {"profile": "gaming", "authorized": False, "speech": True}
    assert client.post(path, json=data, headers=headers).status_code == 400
    foreground.assert_not_called()
    start = Mock()
    stop = Mock()
    cloud_voice = Mock(side_effect=AssertionError("No cloud-capable speech"))
    monkeypatch.setattr(server.SYSTEEMZORG, "start_pressure", start)
    monkeypatch.setattr(server.SYSTEEMZORG, "stop_pressure", stop)
    monkeypatch.setattr(server, "spreek_uit", cloud_voice)
    data["authorized"] = True
    response = client.post(path, json=data, headers=headers)
    assert response.status_code == 200 and not response.json["care"]["pressure"]["enabled"]
    start.assert_called_once_with("gaming", True, True, True)
    assert client.post("/api/systeemzorg/pressure-stop", json={}, headers=headers).status_code == 200
    stop.assert_called_once()
    monkeypatch.setattr(server, "GESPREK_CONTEXT", {})
    server.systeemzorg_notificatie("gaming", "resource_pressure", "Private process path", False)
    cloud_voice.assert_not_called()
    assert "Private process path" not in server.GESPREK_CONTEXT["notificaties"][0]["message"]


def test_local_ai_route_is_separate_from_chat_and_needs_permission(client, monkeypatch):
    analyze = Mock(return_value={"summary": "Synthetic report", "findings": []})
    chat = Mock(side_effect=AssertionError("Must not use normal AI/chat"))
    monkeypatch.setattr(server.lokale_analyse, "analyze", analyze)
    monkeypatch.setattr(server.lokale_analyse, "installed_models", lambda: ["qwen2.5:3b"])
    monkeypatch.setattr(server, "vraag_online_ai_bericht", chat)
    models = client.get("/api/systeemzorg/local-ai/models")
    assert models.json["models"] == ["qwen2.5:3b"]
    assert models.headers["Cache-Control"] == "no-store"
    assert "Access-Control-Allow-Origin" not in models.headers
    data = {"model": "qwen2.5:3b", "files": [{"name": "example.log", "text": "ERROR"}], "authorized": True}
    path = "/api/systeemzorg/local-ai/analyze"
    assert client.post(path, json=data).status_code == 403
    headers = {"X-Echo-System-Token": server.SYSTEEMZORG_TOKEN}
    assert client.post(path, data="{}", headers=headers, content_type="text/plain").status_code == 415
    for bad in [None, [], {}, {"files": []}]:
        assert client.post(path, json=bad, headers=headers).status_code in {400, 415}
    analyze.assert_not_called()
    result = client.post(path, json=data, headers=headers)
    assert result.status_code == 200 and result.json["report"]["summary"] == "Synthetic report"
    analyze.assert_called_once_with(data["files"], "qwen2.5:3b", True, True)
    chat.assert_not_called()
    assert result.headers["Cache-Control"] == "no-store"


def test_local_ai_unavailable_is_localized_and_large_request_is_rejected(client, monkeypatch):
    error = server.lokale_analyse.AnalysisError("Offline", "Niet bereikbaar", 503)
    analyze = Mock(side_effect=error)
    monkeypatch.setattr(server.lokale_analyse, "analyze", analyze)
    monkeypatch.setattr(server.lokale_analyse, "installed_models", Mock(side_effect=error))
    assert client.get("/api/systeemzorg/local-ai/models").json["message"] == "Niet bereikbaar"
    path = "/api/systeemzorg/local-ai/analyze"
    headers = {"X-Echo-System-Token": server.SYSTEEMZORG_TOKEN}
    data = {"files": [], "model": "x", "authorized": True}
    result = client.post(path, json=data, headers=headers)
    assert result.status_code == 503 and result.json["message"] == "Niet bereikbaar"
    analyze.reset_mock()
    data["files"] = [{"name": "x.log", "text": "x" * (512 * 1024)}]
    assert client.post(path, json=data, headers=headers).status_code == 413
    analyze.assert_not_called()


def test_sound_failure_is_explicit_and_never_switches_to_cloud_tts(client, monkeypatch):
    monkeypatch.setattr(server, "GESPREK_CONTEXT", {})
    voice = Mock()
    monkeypatch.setattr(server, "spreek_uit", voice)
    sound = Mock()
    sound.MessageBeep.side_effect = RuntimeError("Unavailable")
    monkeypatch.setattr(server, "winsound", sound)
    with pytest.raises(care.CareError, match="notification sound"):
        server.systeemzorg_notificatie("security", "failed_login", "Private details", True)
    voice.assert_not_called()


def test_policy_trust_round_trip_and_invalid_payloads(client, monkeypatch):
    headers = {"X-Echo-System-Token": server.SYSTEEMZORG_TOKEN}
    monkeypatch.setattr(care.resources, "processes", lambda: {"items": [], "inaccessible": 0})
    policy = {"apps": [], "power_plan": "", "active_cooling": False}
    assert client.post("/api/systeemzorg/policy", json={"profile": "gaming", "policy": policy}, headers=headers).status_code == 200
    assert client.get("/api/systeemzorg/status").json["care"]["policies"]["gaming"] == policy
    assert client.post("/api/systeemzorg/execute", json={"token": "unknown"}, headers=headers).status_code == 400
    assert client.post("/api/systeemzorg/policy", json={"profile": [], "policy": policy}, headers=headers).status_code == 400
    device = {"ip": "192.168.1.2", "mac": "02:00:00:00:00:02"}
    server.SYSTEEMZORG.store.observe_devices("wifi", [device], 100)
    result = client.post("/api/systeemzorg/trust", json={"scope": "wifi", "identity": device["mac"], "trusted": True}, headers=headers)
    assert result.json["care"]["devices"][0]["trusted"] == 1
