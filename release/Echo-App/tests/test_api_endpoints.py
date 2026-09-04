import pytest
import datetime
import io

import server

app = server.app


# Basistestclient voor alle Flask-endpointtests.
@pytest.fixture()
def client():
    app.config.update(TESTING=True)
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def reset_pending_confirmation_state():
    # Houd tests geïsoleerd door globale pending/scheduler-state terug te zetten.
    originele_waarde = server.GESPREK_CONTEXT.get("wacht_op_bevestiging", "")
    originele_laatste_webactie = server.GESPREK_CONTEXT.get("laatste_webactie", "")
    origineel_laatste_commando = server.GESPREK_CONTEXT.get("laatste_commando", "")
    origineel_laatste_commando_norm = server.GESPREK_CONTEXT.get("laatste_commando_norm", "")
    origineel_laatste_commando_at = server.GESPREK_CONTEXT.get("laatste_commando_at", 0.0)
    origineel_laatste_spreek_norm = server.GESPREK_CONTEXT.get("laatste_spreektekst_norm", "")
    origineel_laatste_spreek_at = server.GESPREK_CONTEXT.get("laatste_spreektekst_at", 0.0)
    origineel_laatste_antwoord_norm = server.GESPREK_CONTEXT.get("laatste_assistent_antwoord_norm", "")
    origineel_laatste_antwoord_at = server.GESPREK_CONTEXT.get("laatste_assistent_antwoord_at", 0.0)
    origineel_automatisering_actief_tot = server.GESPREK_CONTEXT.get("automatisering_actief_tot", 0.0)
    originele_daily_enabled = server.instellingen.get("security_scan_daily_enabled")
    originele_daily_time = server.instellingen.get("security_scan_daily_time")
    originele_daily_state = dict(server.DAILY_SECURITY_SCAN_STATE)
    server.GESPREK_CONTEXT["wacht_op_bevestiging"] = ""
    try:
        yield
    finally:
        server.GESPREK_CONTEXT["wacht_op_bevestiging"] = originele_waarde
        server.GESPREK_CONTEXT["laatste_webactie"] = originele_laatste_webactie
        server.GESPREK_CONTEXT["laatste_commando"] = origineel_laatste_commando
        server.GESPREK_CONTEXT["laatste_commando_norm"] = origineel_laatste_commando_norm
        server.GESPREK_CONTEXT["laatste_commando_at"] = origineel_laatste_commando_at
        server.GESPREK_CONTEXT["laatste_spreektekst_norm"] = origineel_laatste_spreek_norm
        server.GESPREK_CONTEXT["laatste_spreektekst_at"] = origineel_laatste_spreek_at
        server.GESPREK_CONTEXT["laatste_assistent_antwoord_norm"] = origineel_laatste_antwoord_norm
        server.GESPREK_CONTEXT["laatste_assistent_antwoord_at"] = origineel_laatste_antwoord_at
        server.GESPREK_CONTEXT["automatisering_actief_tot"] = origineel_automatisering_actief_tot
        server.instellingen["security_scan_daily_enabled"] = originele_daily_enabled
        server.instellingen["security_scan_daily_time"] = originele_daily_time
        with server.DAILY_SECURITY_SCAN_LOCK:
            server.DAILY_SECURITY_SCAN_STATE.clear()
            server.DAILY_SECURITY_SCAN_STATE.update(originele_daily_state)


def test_index_route_returns_html(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"<html" in response.data.lower()


# API-shape validatie voor command- en settings-endpoints.
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


def test_api_commando_response_includes_cors_headers(client):
    response = client.post("/api/commando", json={"commando": "current time"})

    assert response.status_code == 200
    assert response.headers.get("Access-Control-Allow-Origin") == "*"
    assert "POST" in (response.headers.get("Access-Control-Allow-Methods") or "")


def test_execute_command_ignores_duplicate_voice_command(client):
    server.GESPREK_CONTEXT["laatste_commando_norm"] = server.normaliseer_vergelijktekst("hoe laat is het")
    server.GESPREK_CONTEXT["laatste_commando_at"] = server.time.time()

    response = client.post("/api/commando", json={
        "commando": "hoe laat is het",
        "source": "voice",
    })

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "success"
    assert payload["duplicate_ignored"] is True


def test_geavanceerde_besturing_geblokkeerd_auto_activeert_voor_discord_call(monkeypatch):
    monkeypatch.setitem(server.instellingen, "computerbesturing_toestaan", True)
    server.deactiveer_automatisering_modus()

    blokkade = server.geavanceerde_besturing_geblokkeerd("discord call::vriend max")

    assert blokkade == ""
    assert server.automatisering_actief() is True


def test_geavanceerde_besturing_geblokkeerd_blijft_blokkeren_voor_mouse_zonder_modus(monkeypatch):
    monkeypatch.setitem(server.instellingen, "computerbesturing_toestaan", True)
    server.deactiveer_automatisering_modus()

    blokkade = server.geavanceerde_besturing_geblokkeerd("mouse click left")

    assert isinstance(blokkade, str)
    assert blokkade.strip()
    assert "automation" in blokkade.lower()


def test_geavanceerde_besturing_geblokkeerd_auto_activeert_voor_discord_call_macro(monkeypatch):
    monkeypatch.setitem(server.instellingen, "computerbesturing_toestaan", True)
    monkeypatch.setattr(server, "AUTOMATISERING_BESCHIKBAAR", True)
    server.deactiveer_automatisering_modus()

    blokkade = server.geavanceerde_besturing_geblokkeerd("run macro discord-call-button")

    assert blokkade == ""
    assert server.automatisering_actief() is True


def test_geavanceerde_besturing_geblokkeerd_auto_activeert_voor_whatsapp_call(monkeypatch):
    monkeypatch.setitem(server.instellingen, "computerbesturing_toestaan", True)
    monkeypatch.setattr(server, "AUTOMATISERING_BESCHIKBAAR", True)
    server.deactiveer_automatisering_modus()

    blokkade = server.geavanceerde_besturing_geblokkeerd("whatsapp call::voice||vriend max")

    assert blokkade == ""
    assert server.automatisering_actief() is True


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


def test_dashboard_exposes_daily_security_scan_structure(client):
    response = client.get("/api/dashboard")

    assert response.status_code == 200
    payload = response.get_json()
    daily_scan = payload["security_daily_scan"]
    assert isinstance(daily_scan, dict)
    assert {
        "enabled",
        "scheduled_time",
        "next_run_at",
        "next_run_label",
        "monitor_running",
        "supported",
    }.issubset(set(daily_scan.keys()))


def test_mobile_access_endpoint_returns_expected_structure(client, monkeypatch):
    monkeypatch.setattr(server, "ECHO_RUNTIME_HOST", "0.0.0.0")
    monkeypatch.setattr(server, "ECHO_RUNTIME_PORT", 5090)
    monkeypatch.setattr(server, "haal_lokale_ipv4_adressen", lambda max_items=8: ["192.168.1.77"])

    response = client.get("/api/mobile-access")

    assert response.status_code == 200
    payload = response.get_json()
    assert {
        "enabled",
        "host",
        "port",
        "local_url",
        "network_urls",
        "primary_network_url",
        "same_network_required",
    }.issubset(set(payload.keys()))
    assert payload["enabled"] is True
    assert payload["primary_network_url"].startswith("http://192.168.1.77:5090")


def test_dashboard_exposes_mobile_access_structure(client):
    response = client.get("/api/dashboard")

    assert response.status_code == 200
    payload = response.get_json()
    mobile_access = payload["mobile_access"]
    assert isinstance(mobile_access, dict)
    assert {
        "enabled",
        "host",
        "port",
        "local_url",
        "network_urls",
        "primary_network_url",
        "same_network_required",
    }.issubset(set(mobile_access.keys()))


# Safety-confirmation flow voor destructieve/gevoelige acties.
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


def test_speech_upload_route_rejects_missing_audio_file(client):
    response = client.post("/api/spraak-upload", data={}, content_type="multipart/form-data")

    assert response.status_code == 400
    payload = response.get_json()
    assert payload["status"] == "error"
    assert payload.get("message")


def test_speech_upload_route_rejects_empty_audio_file(client):
    response = client.post(
        "/api/spraak-upload",
        data={"audio": (io.BytesIO(b""), "voice.webm")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    payload = response.get_json()
    assert payload["status"] == "error"
    assert payload.get("message")


def test_speech_upload_route_rejects_oversized_audio_file(client, monkeypatch):
    monkeypatch.setattr(server, "MAX_AUDIO_UPLOAD_BYTES", 10)

    response = client.post(
        "/api/spraak-upload",
        data={"audio": (io.BytesIO(b"01234567890"), "voice.webm")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 413
    payload = response.get_json()
    assert payload["status"] == "error"
    assert payload.get("message")


def test_speech_upload_route_transcribes_with_mocked_backend(client, monkeypatch):
    waargenomen = {}

    def fake_transcribe(audio_pad):
        waargenomen["suffix"] = audio_pad.suffix
        return "hey echo bereken 1 plus 1", "whisper"

    monkeypatch.setattr(server, "herken_audio_upload_tekst", fake_transcribe)

    response = client.post(
        "/api/spraak-upload",
        data={"audio": (io.BytesIO(b"webm-bytes"), "voice.webm")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "success"
    assert payload["gesproken"] == "hey echo bereken 1 plus 1"
    assert payload["provider"] == "whisper"
    assert waargenomen["suffix"] == ".webm"


# Parser-regressietests voor routing van natuurlijke taal naar acties.
def test_normaliseer_actie_parses_battery_check_phrase():
    assert server.normaliseer_actie("hoeveel batterij heb ik nog") == "battery status"


def test_normaliseer_actie_parses_wifi_quality_phrase():
    assert server.normaliseer_actie("is mijn wifi goed genoeg voor upload en download") == "wifi quality"


def test_normaliseer_actie_parses_brightness_set_phrase():
    assert server.normaliseer_actie("zet helderheid op 65 procent") == "brightness set 65"


def test_normaliseer_actie_parses_brightness_step_phrases():
    assert server.normaliseer_actie("maak scherm helderder") == "brightness up"
    assert server.normaliseer_actie("maak scherm donkerder") == "brightness down"


def test_normaliseer_actie_parses_security_threat_scan_phrase():
    assert server.normaliseer_actie("start malware scan") == "security threat scan start"


def test_normaliseer_actie_parses_security_cleanup_and_not_delete_path():
    assert server.normaliseer_actie("remove malware") == "security threat cleanup"


def test_normaliseer_actie_parses_phone_status_phrase():
    assert server.normaliseer_actie("phone status") == "mobile access status"


def test_normaliseer_actie_parses_phone_link_phrase():
    assert server.normaliseer_actie("test via telefoon") == "mobile access link"


def test_normaliseer_actie_parses_discord_send_phrase():
    actie = server.normaliseer_actie("stuur discord bericht naar general met Hallo team")
    assert actie == "discord send::general||Hallo team"


def test_voer_systeeminfo_uit_mobile_access_link_uses_detected_lan_url(monkeypatch):
    monkeypatch.setattr(server, "ECHO_RUNTIME_HOST", "0.0.0.0")
    monkeypatch.setattr(server, "ECHO_RUNTIME_PORT", 5101)
    monkeypatch.setattr(server, "haal_lokale_ipv4_adressen", lambda max_items=8: ["10.0.0.55"])

    bericht = server.voer_systeeminfo_uit("mobile access link")

    assert "10.0.0.55:5101" in bericht


def test_normaliseer_actie_parses_discord_dm_phrase():
    actie = server.normaliseer_actie("stuur 1 op 1 bericht naar vriend max op discord met yo bro")
    assert actie == "discord dm::vriend max||yo bro"


def test_normaliseer_actie_parses_discord_quick_dm_with_met_phrase():
    actie = server.normaliseer_actie("stuur naar max met kom je online")
    assert actie == "discord dm::max||kom je online"


def test_normaliseer_actie_parses_discord_quick_dm_single_target_phrase():
    actie = server.normaliseer_actie("stuur naar @kevin ben er over 5 min")
    assert actie == "discord dm::@kevin||ben er over 5 min"


def test_normaliseer_actie_parses_discord_call_phrase():
    actie = server.normaliseer_actie("bel naar max op discord")
    assert actie == "discord call::max"


def test_normaliseer_actie_parses_discord_call_simple_phrase():
    actie = server.normaliseer_actie("bel max op discord")
    assert actie == "discord call::max"


def test_normaliseer_actie_parses_discord_call_polite_phrase():
    actie = server.normaliseer_actie("kan je max bellen op discord")
    assert actie == "discord call::max"


def test_normaliseer_actie_parses_discord_call_prefixed_phrase():
    actie = server.normaliseer_actie("echo kan je voor me max bellen op discord")
    assert actie == "discord call::max"


def test_normaliseer_actie_parses_discord_call_discord_first_phrase():
    actie = server.normaliseer_actie("discord bel max")
    assert actie == "discord call::max"


def test_normaliseer_actie_parses_discord_call_button_macro_phrase():
    actie = server.normaliseer_actie("bel op discord")
    assert actie == "run macro discord-call-button"


def test_normaliseer_actie_parses_discord_vc_phrase():
    actie = server.normaliseer_actie("start een vc met krokonl op discord")
    assert actie == "discord call::voice||krokonl"


def test_normaliseer_actie_parses_discord_voice_call_phrase_with_colon_target():
    actie = server.normaliseer_actie("start een voice call op discord met :krokonl:")
    assert actie == "discord call::voice||krokonl"


def test_normaliseer_actie_parses_discord_video_call_phrase():
    actie = server.normaliseer_actie("start een videocall met krokonl op discord")
    assert actie == "discord call::video||krokonl"


def test_normaliseer_actie_parses_whatsapp_voice_call_phrase():
    actie = server.normaliseer_actie("start een voice call met max op whatsapp")
    assert actie == "whatsapp call::voice||max"


def test_normaliseer_actie_parses_whatsapp_video_call_phrase():
    actie = server.normaliseer_actie("start een video call met max op whatsapp")
    assert actie == "whatsapp call::video||max"


def test_normaliseer_actie_parses_whatsapp_open_phrase_app_first():
    assert server.normaliseer_actie("whatsapp openen") == "open app whatsapp"


def test_normaliseer_actie_parses_open_whatsapp_phrase():
    assert server.normaliseer_actie("open whatsapp") == "open app whatsapp"


def test_verwijder_directe_herhaling_uit_antwoord_schoont_tekst_op():
    bron = "Dit kan ik doen. Dit kan ik doen. Zeg wat je nodig hebt."

    assert server.verwijder_directe_herhaling_uit_antwoord(bron) == "Dit kan ik doen. Zeg wat je nodig hebt."


def test_normaliseer_actie_parses_specific_topic_help_phrase():
    actie = server.normaliseer_actie("wat kan je doen met discord")
    assert actie == "help topic::discord"


def test_normaliseer_discord_doel_uses_dm_aliases(monkeypatch):
    monkeypatch.setitem(
        server.instellingen,
        "discord_dm_vriend_aliases",
        {
            "max": "MaxPower",
            "beste vriend": "NordinMate",
        },
    )

    assert server.normaliseer_discord_doel("vriend max", dm_mode=True) == "@MaxPower"
    assert server.normaliseer_discord_doel("@beste vriend", dm_mode=True) == "@NordinMate"
    assert server.normaliseer_discord_doel("max", dm_mode=False) == "max"


def test_normaliseer_actie_parses_browser_click_link_phrase():
    assert server.normaliseer_actie("klik derde link") == "browser click link::index||3"
    assert server.normaliseer_actie("klik link met tekst echo docs") == "browser click link::text||echo docs"


def test_synchroniseer_taalinstellingen_normalizes_daily_security_scan_values():
    instellingen = dict(server.DEFAULT_SETTINGS)
    instellingen["security_scan_daily_enabled"] = "ja"
    instellingen["security_scan_daily_time"] = "7:05"

    gesynchroniseerd = server.synchroniseer_taalinstellingen(instellingen)

    assert gesynchroniseerd["security_scan_daily_enabled"] is True
    assert gesynchroniseerd["security_scan_daily_time"] == "07:05"


def test_synchroniseer_taalinstellingen_falls_back_for_invalid_daily_scan_time():
    instellingen = dict(server.DEFAULT_SETTINGS)
    instellingen["security_scan_daily_time"] = "99:88"

    gesynchroniseerd = server.synchroniseer_taalinstellingen(instellingen)

    assert gesynchroniseerd["security_scan_daily_time"] == "03:00"


def test_synchroniseer_taalinstellingen_normalizes_discord_dm_aliases():
    instellingen = dict(server.DEFAULT_SETTINGS)
    instellingen["discord_dm_vriend_aliases"] = {
        " Beste vriend ": " @Nordin Main ",
        "vriend max": "  Max Prime  ",
        "   ": "Leeg",
        "maat!": "Buddy-One",
        "zonder_doel": "",
    }

    gesynchroniseerd = server.synchroniseer_taalinstellingen(instellingen)

    assert gesynchroniseerd["discord_dm_vriend_aliases"] == {
        "beste vriend": "Nordin Main",
        "vriend max": "Max Prime",
        "maat": "Buddy-One",
    }


def test_verwerk_dagelijkse_security_scan_runs_once_per_day(monkeypatch):
    server.instellingen["security_scan_daily_enabled"] = True
    server.instellingen["security_scan_daily_time"] = "03:00"

    with server.DAILY_SECURITY_SCAN_LOCK:
        server.DAILY_SECURITY_SCAN_STATE.clear()
        server.DAILY_SECURITY_SCAN_STATE.update(server.standaard_dagelijkse_security_scan_data())

    monkeypatch.setattr(server.platform, "system", lambda: "Windows")

    calls = {"count": 0}

    def fake_start_security_scan():
        calls["count"] += 1
        return True, "Daily scan started"

    monkeypatch.setattr(server, "start_security_threat_scan", fake_start_security_scan)

    eerste_run = datetime.datetime(2026, 9, 1, 3, 1, 0).timestamp()
    zelfde_dag_later = datetime.datetime(2026, 9, 1, 18, 0, 0).timestamp()
    volgende_dag = datetime.datetime(2026, 9, 2, 3, 2, 0).timestamp()

    assert server.verwerk_dagelijkse_security_scan(nu_timestamp=eerste_run) is True
    assert server.verwerk_dagelijkse_security_scan(nu_timestamp=zelfde_dag_later) is False
    assert server.verwerk_dagelijkse_security_scan(nu_timestamp=volgende_dag) is True
    assert calls["count"] == 2


# Security-cleanup confirm-flow moet pending state correct beheren.
def test_security_cleanup_command_sets_pending_confirmation(client, monkeypatch):
    monkeypatch.setattr(server.platform, "system", lambda: "Windows")
    monkeypatch.setattr(server, "heeft_windows_adminrechten", lambda: True)
    monkeypatch.setattr(
        server,
        "haal_defender_threat_overzicht",
        lambda max_items=server.SECURITY_THREAT_SUMMARY_MAX_ITEMS: {
            "threat_count": 2,
            "detection_count": 2,
            "threat_ids": ["101", "202"],
            "threat_names": ["Demo.Threat.A", "Demo.Threat.B"],
        },
    )

    response = client.post("/api/commando", json={"commando": "remove malware"})

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "success"
    assert server.GESPREK_CONTEXT["wacht_op_bevestiging"] == "security threat cleanup"
    assert payload["pending_confirmation"]["pending"] is True
    assert payload["pending_confirmation"]["action_key"] == "security threat cleanup"


def test_confirm_pending_security_cleanup_executes_and_clears_state(client, monkeypatch):
    server.GESPREK_CONTEXT["wacht_op_bevestiging"] = "security threat cleanup"
    monkeypatch.setattr(server, "voer_security_threat_cleanup_uit", lambda: "Threat cleanup completed")

    response = client.post("/api/commando", json={"commando": "confirm pending action"})

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "success"
    assert payload["message"] == "Threat cleanup completed"
    assert server.GESPREK_CONTEXT["wacht_op_bevestiging"] == ""


def test_voer_enkele_actie_uit_dispatches_discord_send(monkeypatch):
    calls = {}

    def fake_discord_send(bestemming, bericht, dm_mode=False):
        calls["bestemming"] = bestemming
        calls["bericht"] = bericht
        calls["dm_mode"] = dm_mode
        return "Discord sent"

    monkeypatch.setattr(server, "voer_discord_bericht_actie_uit", fake_discord_send)

    resultaat = server.voer_enkele_actie_uit("discord send::general||hallo team")

    assert resultaat == "Discord sent"
    assert calls["bestemming"] == "general"
    assert calls["bericht"] == "hallo team"
    assert calls["dm_mode"] is False


def test_voer_enkele_actie_uit_dispatches_discord_dm(monkeypatch):
    calls = {}

    def fake_discord_send(bestemming, bericht, dm_mode=False):
        calls["bestemming"] = bestemming
        calls["bericht"] = bericht
        calls["dm_mode"] = dm_mode
        return "Discord dm sent"

    monkeypatch.setattr(server, "voer_discord_bericht_actie_uit", fake_discord_send)

    resultaat = server.voer_enkele_actie_uit("discord dm::vriend max||hallo")

    assert resultaat == "Discord dm sent"
    assert calls["bestemming"] == "vriend max"
    assert calls["bericht"] == "hallo"
    assert calls["dm_mode"] is True


def test_voer_enkele_actie_uit_dispatches_discord_call(monkeypatch):
    calls = {}

    def fake_discord_call(bestemming, beltype="voice"):
        calls["bestemming"] = bestemming
        calls["beltype"] = beltype
        return "Discord call started"

    monkeypatch.setattr(server, "voer_discord_bel_actie_uit", fake_discord_call)

    resultaat = server.voer_enkele_actie_uit("discord call::vriend max")

    assert resultaat == "Discord call started"
    assert calls["bestemming"] == "max"
    assert calls["beltype"] == "voice"


def test_voer_enkele_actie_uit_dispatches_discord_video_call(monkeypatch):
    calls = {}

    def fake_discord_call(bestemming, beltype="voice"):
        calls["bestemming"] = bestemming
        calls["beltype"] = beltype
        return "Discord video call started"

    monkeypatch.setattr(server, "voer_discord_bel_actie_uit", fake_discord_call)

    resultaat = server.voer_enkele_actie_uit("discord call::video||krokonl")

    assert resultaat == "Discord video call started"
    assert calls["bestemming"] == "krokonl"
    assert calls["beltype"] == "video"


def test_voer_enkele_actie_uit_dispatches_whatsapp_voice_call(monkeypatch):
    calls = {}

    def fake_whatsapp_call(bestemming, beltype="voice"):
        calls["bestemming"] = bestemming
        calls["beltype"] = beltype
        return "WhatsApp voice call started"

    monkeypatch.setattr(server, "voer_whatsapp_bel_actie_uit", fake_whatsapp_call)

    resultaat = server.voer_enkele_actie_uit("whatsapp call::voice||krokonl")

    assert resultaat == "WhatsApp voice call started"
    assert calls["bestemming"] == "krokonl"
    assert calls["beltype"] == "voice"


def test_voer_enkele_actie_uit_opent_whatsapp_desktop_via_start_command(monkeypatch):
    popen_calls = []

    class DummyPopen:
        def __init__(self, args):
            popen_calls.append(args)

    monkeypatch.setattr(server, "vind_gescande_app_voor_sleutel", lambda _sleutel, _details: None)
    monkeypatch.setattr(server.subprocess, "Popen", DummyPopen)
    monkeypatch.setattr(server, "gw", None)

    resultaat = server.voer_enkele_actie_uit("open app whatsapp")

    assert popen_calls
    assert any("whatsapp" in " ".join(str(part).lower() for part in call) for call in popen_calls)
    assert "whatsapp" in resultaat.lower()


def test_voer_enkele_actie_uit_opent_whatsapp_web_als_desktop_niet_start(monkeypatch):
    geopend = {"url": ""}

    monkeypatch.setattr(server, "vind_gescande_app_voor_sleutel", lambda _sleutel, _details: None)
    monkeypatch.setattr(server, "gw", object())
    monkeypatch.setattr(server.time, "sleep", lambda _seconds: None)
    monkeypatch.setattr(server, "activeer_venster", lambda _app, _probeer_start=True: False)
    monkeypatch.setattr(server.subprocess, "Popen", lambda _command: object())
    monkeypatch.setattr(server, "open_windows_doel", lambda _target: (_ for _ in ()).throw(RuntimeError("desktop launch failed")))

    def fake_open_doel_url_of_protocol(url):
        geopend["url"] = url
        return url.startswith("https://web.whatsapp.com")

    monkeypatch.setattr(server, "open_doel_url_of_protocol", fake_open_doel_url_of_protocol)

    resultaat = server.voer_enkele_actie_uit("open app whatsapp")

    assert geopend["url"].startswith("https://web.whatsapp.com")
    assert "whatsapp" in resultaat.lower()


def test_voer_discord_bel_actie_uit_gebruikt_discord_call_hotkey(monkeypatch):
    hotkey_calls = []

    class DummyPyAutoGui:
        def hotkey(self, *keys):
            hotkey_calls.append(keys)

    monkeypatch.setitem(server.instellingen, "computerbesturing_toestaan", True)
    server.activeer_automatisering_modus()
    monkeypatch.setattr(server, "pyautogui", DummyPyAutoGui())
    monkeypatch.setattr(server, "focus_of_open_app_voor_actie", lambda _app: (True, "discord", "Discord"))
    monkeypatch.setattr(server, "open_discord_doel_via_quickswitcher", lambda _bestemming, dm_mode=True: "@max")
    monkeypatch.setattr(server.time, "sleep", lambda _seconds: None)

    resultaat = server.voer_discord_bel_actie_uit("max")

    assert hotkey_calls
    assert hotkey_calls[-1] == server.DISCORD_CALL_HOTKEY
    assert server.DISCORD_CALL_HOTKEY == ("ctrl", "[")
    assert "max" in resultaat.lower()


def test_voer_discord_bel_actie_uit_klikt_op_call_knop(monkeypatch):
    move_calls = []
    click_calls = []
    hotkey_calls = []

    class DummyWindow:
        left = 20
        top = 12
        width = 1280
        height = 820
        isMinimized = False

        def activate(self):
            return None

    class DummyPyAutoGui:
        def moveTo(self, x, y, duration=0.0):
            move_calls.append((x, y, duration))

        def click(self):
            click_calls.append(True)

        def hotkey(self, *keys):
            hotkey_calls.append(keys)

    monkeypatch.setitem(server.instellingen, "computerbesturing_toestaan", True)
    server.activeer_automatisering_modus()
    monkeypatch.setattr(server, "pyautogui", DummyPyAutoGui())
    monkeypatch.setattr(server, "haal_actief_venster", lambda: DummyWindow())
    monkeypatch.setattr(server, "focus_of_open_app_voor_actie", lambda _app: (True, "discord", "Discord"))
    monkeypatch.setattr(server, "open_discord_doel_via_quickswitcher", lambda _bestemming, dm_mode=True: "@krokonl")
    monkeypatch.setattr(server.time, "sleep", lambda _seconds: None)

    resultaat = server.voer_discord_bel_actie_uit("krokonl", "voice")

    assert move_calls
    assert click_calls
    assert hotkey_calls == []
    assert "krokonl" in resultaat.lower()


def test_voer_enkele_actie_uit_geeft_specifieke_mogelijkheden_voor_topic():
    bericht = server.voer_enkele_actie_uit("help topic::discord")

    assert "discord" in bericht.lower()
    assert "1-op-1" in bericht.lower() or "1-on-1" in bericht.lower()


def test_voer_enkele_actie_uit_specifieke_help_onbekend_topic_geeft_suggesties():
    bericht = server.voer_enkele_actie_uit("help topic::fietsenmaker")

    assert "fietsenmaker" in bericht.lower()
    assert "discord" in bericht.lower()


def test_voer_browser_link_selectie_uit_opent_gekozen_index(monkeypatch):
    monkeypatch.setattr(server, "bron_url_voor_link_selectie", lambda: ("https://example.com/search", ""))
    monkeypatch.setattr(
        server,
        "haal_webpagina_html",
        lambda url: {"url": url, "title": "Search", "html": "<html></html>"},
    )
    monkeypatch.setattr(
        server,
        "extraheer_klikbare_links_uit_html",
        lambda html_tekst, basis_url, max_items=70: [
            {"index": 1, "url": "https://example.com/a", "text": "Alpha"},
            {"index": 2, "url": "https://example.com/b", "text": "Bravo"},
        ],
    )

    geopend = {}

    def fake_open(url):
        geopend["url"] = url
        return True

    monkeypatch.setattr(server, "open_doel_url_of_protocol", fake_open)

    bericht = server.voer_browser_link_selectie_uit("index||2")

    assert geopend["url"] == "https://example.com/b"
    assert "link 2" in bericht.lower()