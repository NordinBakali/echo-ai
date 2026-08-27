import pytest

import server

app = server.app


@pytest.fixture()
def client():
    app.config.update(TESTING=True)
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def reset_pending_confirmation_state():
    originele_waarde = server.GESPREK_CONTEXT.get("wacht_op_bevestiging", "")
    server.GESPREK_CONTEXT["wacht_op_bevestiging"] = ""
    try:
        yield
    finally:
        server.GESPREK_CONTEXT["wacht_op_bevestiging"] = originele_waarde


def test_index_route_returns_html(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"<html" in response.data.lower()


def test_execute_command_rejects_invalid_json_shape(client):
    response = client.post("/api/commando", data="[]", content_type="application/json")

    assert response.status_code == 400
    payload = response.get_json()
    assert payload["status"] == "error"
    assert "payload" in payload["message"].lower()


def test_execute_command_rejects_empty_command(client):
    response = client.post("/api/commando", json={"commando": ""})

    assert response.status_code == 400
    payload = response.get_json()
    assert payload["status"] == "error"


def test_execute_command_accepts_valid_payload(client):
    response = client.post("/api/commando", json={"commando": "bereken 2+2"})

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "success"
    assert payload.get("message")


def test_update_settings_rejects_invalid_json_shape(client):
    response = client.post("/api/instellingen", data="[]", content_type="application/json")

    assert response.status_code == 400
    payload = response.get_json()
    assert payload["status"] == "error"
    assert "payload" in payload["message"].lower()


def test_dashboard_route_returns_expected_structure(client):
    response = client.get("/api/dashboard")

    assert response.status_code == 200
    payload = response.get_json()
    expected_keys = {
        "generated_at",
        "generated_at_label",
        "runtime",
        "routing",
        "modes",
        "ai",
        "memory",
        "planner",
        "workspace",
        "pending_confirmation",
    }
    assert expected_keys.issubset(set(payload.keys()))


def test_dangerous_command_sets_pending_confirmation_state(client):
    response = client.post("/api/commando", json={"commando": "shutdown computer"})

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "success"
    assert server.GESPREK_CONTEXT["wacht_op_bevestiging"] == "shutdown computer"

    pending = payload["pending_confirmation"]
    assert pending["pending"] is True
    assert pending["action_key"] == "shutdown computer"
    assert pending["confirm_command"] == "confirm pending action"
    assert pending["cancel_command"] == "cancel pending action"


def test_dashboard_exposes_pending_confirmation_details(client):
    server.GESPREK_CONTEXT["wacht_op_bevestiging"] = "shutdown computer"

    response = client.get("/api/dashboard")

    assert response.status_code == 200
    payload = response.get_json()
    pending = payload["pending_confirmation"]
    assert pending["pending"] is True
    assert pending["action_key"] == "shutdown computer"
    assert pending["kind"] == "system"
    assert pending["prompt_en"]
    assert pending["prompt_nl"]


def test_confirm_pending_action_executes_and_clears_pending_state(client, tmp_path):
    doelbestand = tmp_path / "pending_confirm.txt"
    doelbestand.write_text("oude tekst", encoding="utf-8")
    server.GESPREK_CONTEXT["wacht_op_bevestiging"] = f"overwrite file::{doelbestand}||nieuwe tekst"

    response = client.post("/api/commando", json={"commando": "confirm pending action"})

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "success"
    assert server.GESPREK_CONTEXT["wacht_op_bevestiging"] == ""
    assert doelbestand.read_text(encoding="utf-8") == "nieuwe tekst"

    dashboard_response = client.get("/api/dashboard")
    dashboard_payload = dashboard_response.get_json()
    assert dashboard_payload["pending_confirmation"]["pending"] is False


def test_cancel_pending_action_clears_pending_state(client):
    server.GESPREK_CONTEXT["wacht_op_bevestiging"] = "shutdown computer"

    response = client.post("/api/commando", json={"commando": "cancel pending action"})

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "success"
    assert server.GESPREK_CONTEXT["wacht_op_bevestiging"] == ""
    assert payload["pending_confirmation"]["pending"] is False


def test_speech_route_returns_error_when_speech_unavailable(client, monkeypatch):
    monkeypatch.setattr(server, "SPRAAK_BESCHIKBAAR", False)

    response = client.post("/api/spraak")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "error"
    assert payload.get("message")


def test_speech_route_uses_mocked_recognition_flow(client, monkeypatch):
    monkeypatch.setattr(server, "SPRAAK_BESCHIKBAAR", True)
    monkeypatch.setattr(server, "herken_spraak", lambda: "bereken 1+1")
    monkeypatch.setattr(server, "voer_commando_uit", lambda tekst: "Result: 2")

    response = client.post("/api/spraak")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "success"
    assert payload["gesproken"] == "bereken 1+1"
    assert payload["message"] == "Result: 2"


def test_normaliseer_actie_parses_battery_check_phrase():
    assert server.normaliseer_actie("hoeveel batterij heb ik nog") == "battery status"


def test_normaliseer_actie_parses_wifi_quality_phrase():
    assert server.normaliseer_actie("is mijn wifi goed genoeg voor upload en download") == "wifi quality"


def test_normaliseer_actie_parses_brightness_set_phrase():
    assert server.normaliseer_actie("zet helderheid op 65 procent") == "brightness set 65"


def test_normaliseer_actie_parses_brightness_step_phrases():
    assert server.normaliseer_actie("maak scherm helderder") == "brightness up"
    assert server.normaliseer_actie("maak scherm donkerder") == "brightness down"