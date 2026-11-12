import copy
from unittest.mock import Mock

import pytest

import echo_osint as osint
import echo_web_automation as web
import server

WATCH = {
    "name": "Console", "url": "https://shop.example/p/1", "mode": "notify", "interval": 300,
    "in_stock_text": [], "out_of_stock_text": [], "max_price": None,
    "elements": {"stock_indicator": {"selector": "#stock", "text": ""}}, "checkout_url": "", "authorized": False,
}


@pytest.fixture()
def client(monkeypatch, tmp_path):
    shop = Mock()
    shop.snapshot.return_value = {"open": False, "busy": False, "host": "", "error": "", "running": False}
    automation = web.WebAutomation(web.Store(tmp_path / "web.sqlite3"), Mock(), shop=shop)
    session = Mock()
    session.get.side_effect = AssertionError("No real network")
    checker = osint.Osint(osint.Store(tmp_path / "osint.sqlite3"), Mock(), session=session)
    monkeypatch.delenv("HIBP_API_KEY", raising=False)
    monkeypatch.setattr(server, "WEBAUTOMATISERING", automation)
    monkeypatch.setattr(server, "OSINT", checker)
    monkeypatch.setattr(server, "ECHO_DEMO_MODE", False)
    monkeypatch.setattr(server, "ECHO_ENTERPRISE_MODE", False)
    monkeypatch.setattr(server, "instellingen", copy.deepcopy(server.instellingen))
    monkeypatch.setitem(server.instellingen, "taal", "Nederlands")
    server.app.config.update(TESTING=True)
    with server.app.test_client() as test_client:
        yield test_client
    automation.stop()
    checker.shutdown()


def headers():
    return {"X-Echo-Web-Token": server.WEBAUTOMATISERING_TOKEN}


def test_page_renders_token_and_dashboard_link(client):
    assert b"/webautomatisering" in client.get("/").data
    page = client.get("/webautomatisering")
    assert page.status_code == 200 and b'lang="nl"' in page.data
    assert server.WEBAUTOMATISERING_TOKEN.encode() in page.data
    assert page.headers["Cache-Control"] == "no-store"
    status = client.get("/api/webautomatisering/status", headers=headers())
    assert status.status_code == 200 and not status.json["web"]["running"]
    assert status.json["osint"]["key_source"] == ""
    assert "Access-Control-Allow-Origin" not in status.headers
    assert client.get("/api/webautomatisering/unknown", headers=headers()).status_code == 404


@pytest.mark.parametrize("path", ["/webautomatisering", "/api/webautomatisering/status", "/api/webautomatisering/save", "/api/webautomatisering/osint/add"])
@pytest.mark.parametrize("attack", ["remote", "host", "origin", "cross_site", "no_token"])
def test_local_boundaries(client, path, attack):
    options, request_headers = {}, headers()
    if attack == "remote":
        options["environ_overrides"] = {"REMOTE_ADDR": "192.168.1.2"}
        request_headers["X-Forwarded-For"] = "127.0.0.1"
    elif attack == "host":
        options["base_url"] = "http://hostile.example"
    elif attack == "origin":
        request_headers["Origin"] = "http://hostile.example"
    elif attack == "cross_site":
        request_headers["Sec-Fetch-Site"] = "cross-site"
    else:
        if path == "/webautomatisering":
            pytest.skip("The page itself carries the token")
        request_headers = {"X-Echo-Web-Token": "wrong"}
    method = "GET" if path in ("/webautomatisering", "/api/webautomatisering/status") else "POST"
    response = client.open(path, method=method, json={"id": "", "watch": WATCH}, headers=request_headers, **options)
    assert response.status_code == 403
    assert "Access-Control-Allow-Origin" not in response.headers
    assert server.WEBAUTOMATISERING.store.watches() == []


@pytest.mark.parametrize("mode", ["ECHO_DEMO_MODE", "ECHO_ENTERPRISE_MODE"])
def test_shared_modes_cannot_use_web_automation(client, monkeypatch, mode):
    monkeypatch.setattr(server, mode, True)
    assert client.get("/webautomatisering").status_code in (403, 503)
    assert client.get("/api/webautomatisering/status", headers=headers()).status_code in (403, 503)
    for path in ("/webautomatisering", "/api/webautomatisering/status"):
        with server.app.test_request_context(path, headers=headers(), environ_base={"REMOTE_ADDR": "127.0.0.1"}):
            assert server.beveilig_webautomatisering()[1] == 403


@pytest.mark.parametrize("path", ["/api/webautomatisering/save", "/api/webautomatisering/osint/add"])
def test_mutations_need_json_objects_with_exact_keys(client, path):
    assert client.post(path, data="{}", headers=headers(), content_type="text/plain").status_code == 415
    assert client.post(path, json=[], headers=headers()).status_code == 400
    assert client.post(path, json={"unexpected": True}, headers=headers()).status_code == 400


def test_watch_and_identifier_round_trip(client):
    saved = client.post("/api/webautomatisering/save", json={"id": "", "watch": WATCH}, headers=headers())
    assert saved.status_code == 200 and saved.json["id"]
    watch = saved.json["web"]["watches"][0]
    assert watch["config"]["name"] == "Console" and watch["selectors"]["stock_indicator"][0]["reason"] == "configured"
    unsafe = {**WATCH, "mode": "cart", "authorized": True, "elements": {"add_to_cart": {"selector": "", "text": "Nu betalen"}}}
    rejected = client.post("/api/webautomatisering/save", json={"id": "", "watch": unsafe}, headers=headers())
    assert rejected.status_code == 400 and "never" in rejected.json["message"]
    paused = client.post("/api/webautomatisering/pause", json={"id": saved.json["id"]}, headers=headers())
    assert paused.json["web"]["watches"][0]["state"]["paused"]
    added = client.post("/api/webautomatisering/osint/add", json={"kind": "domain", "value": "Example.COM", "owned": True}, headers=headers())
    assert added.status_code == 200 and added.json["osint"]["identifiers"][0]["value"] == "example.com"
    password = client.post("/api/webautomatisering/osint/password_range", json={"prefix": "nothex"}, headers=headers())
    assert password.status_code == 400
    deleted = client.post("/api/webautomatisering/delete", json={"id": saved.json["id"]}, headers=headers())
    assert deleted.json["web"]["watches"] == []


def test_start_requires_consent_and_storage_errors_are_503(client, monkeypatch):
    refused = client.post("/api/webautomatisering/start", json={"authorized": False, "sound": False}, headers=headers())
    assert refused.status_code == 400 and not server.WEBAUTOMATISERING.snapshot()["running"]
    monkeypatch.setattr(server.WEBAUTOMATISERING.store, "watches", Mock(side_effect=OSError("disk")))
    assert client.get("/api/webautomatisering/status", headers=headers()).status_code == 503


def test_password_range_returns_only_lines(client, monkeypatch):
    monkeypatch.setattr(server.OSINT, "password_range", lambda prefix: [f"{'A' * 35}:2"])
    response = client.post("/api/webautomatisering/osint/password_range", json={"prefix": "ABCDE"}, headers=headers())
    assert response.json == {"status": "success", "lines": [f"{'A' * 35}:2"]}


def test_notifications_are_generic_and_never_spoken(client, monkeypatch):
    voice = Mock()
    monkeypatch.setattr(server, "spreek_uit", voice)
    monkeypatch.setattr(server, "GESPREK_CONTEXT", {})
    sound = Mock()
    sound.MessageBeep.side_effect = RuntimeError("Unavailable")
    monkeypatch.setattr(server, "winsound", sound)
    server.webautomatisering_notificatie("action_done", True)
    server.webautomatisering_notificatie("osint_alert", False)
    voice.assert_not_called()
    messages = [item["message"] for item in server.GESPREK_CONTEXT["notificaties"]]
    assert "Rond de betaling zelf af" in messages[0] and "Datalekcheck" in messages[1]
    sound.MessageBeep.assert_called_once()


def test_transaction_mode_requires_separate_consent_and_round_trips(client):
    watch = {
        **WATCH, "mode": "reserve", "authorized": True, "max_price": 500,
        "transaction": {
            "authorized": False, "currency": "EUR",
            "button": {"selector": "#reserve", "text": "Reservering bevestigen"},
            "confirmation": {"selector": "#confirmed", "text": "Reservering bevestigd"},
            "item": {"selector": ".item", "text": "Console"},
            "quantity": {"selector": ".qty", "text": "1"},
            "total": {"selector": "#total", "text": ""},
        },
    }
    data = {"id": "", "watch": watch}
    assert client.post("/api/webautomatisering/save", json=data).status_code == 403
    response = client.post("/api/webautomatisering/save", json=data, headers=headers())
    assert response.status_code == 400 and "authorization" in response.json["message"]
    watch["transaction"]["authorized"] = True
    response = client.post("/api/webautomatisering/save", json=data, headers=headers())
    assert response.status_code == 200
    assert response.json["web"]["watches"][0]["config"]["transaction"] == watch["transaction"]
    assert response.json["web"]["watches"][0]["transaction"] is None
    server.WEBAUTOMATISERING.shop.submit.assert_not_called()


def test_confirmed_and_unknown_transactions_have_distinct_local_notifications(client, monkeypatch):
    monkeypatch.setattr(server, "GESPREK_CONTEXT", {})
    voice = Mock()
    monkeypatch.setattr(server, "spreek_uit", voice)
    for kind in ("order_confirmed", "reservation_confirmed", "transaction_uncertain"):
        server.webautomatisering_notificatie(kind, False)
    messages = [row["message"] for row in server.GESPREK_CONTEXT["notificaties"]]
    assert "bestelling bevestigd" in messages[0]
    assert "reservering bevestigd" in messages[1]
    assert "onbekend" in messages[2]
    voice.assert_not_called()
