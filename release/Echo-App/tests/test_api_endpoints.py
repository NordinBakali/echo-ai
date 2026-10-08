import pytest
import datetime
import io
import copy
import sqlite3

import server

app = server.app


# Basistestclient voor alle Flask-endpointtests.
@pytest.fixture()
def client():
    app.config.update(TESTING=True)
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def isolate_company_knowledge_metrics(monkeypatch, tmp_path):
    monkeypatch.setattr(server, "BEDRIJFSDOCUMENT_METRICS_PAD", tmp_path / "company-metrics.json")


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
    originele_website_schedule_enabled = server.instellingen.get("website_audit_schedule_enabled")
    originele_website_schedule_frequency = server.instellingen.get("website_audit_schedule_frequency")
    originele_website_schedule_time = server.instellingen.get("website_audit_schedule_time")
    originele_website_schedule_target_url = server.instellingen.get("website_audit_schedule_target_url")
    originele_website_schedule_profile = server.instellingen.get("website_audit_schedule_profile")
    originele_website_schedule_alert_webhook = server.instellingen.get("website_audit_alert_webhook")
    originele_website_schedule_alert_score_drop = server.instellingen.get("website_audit_alert_score_drop")
    originele_website_schedule_alert_on_critical = server.instellingen.get("website_audit_alert_on_critical")
    origineel_instellingen_profiel = server.instellingen.get("instellingen_profiel")
    originele_instellingen_profielen = copy.deepcopy(server.instellingen.get("instellingen_profielen", {}))
    originele_daily_state = dict(server.DAILY_SECURITY_SCAN_STATE)
    originele_website_audit_state = copy.deepcopy(server.WEBSITE_AUDIT_STATE)
    originele_website_audit_schedule_state = dict(server.WEBSITE_AUDIT_SCHEDULE_STATE)
    origineel_quick_checker_module = server.QUICK_CHECKER_MODULE
    originele_quick_check_cache = copy.deepcopy(server.QUICK_CHECK_CACHE)
    originele_quick_check_client_requests = copy.deepcopy(server.QUICK_CHECK_CLIENT_REQUESTS)
    originele_quick_check_tasks = copy.deepcopy(server.QUICK_CHECK_TASKS)
    originele_quick_check_task_order = list(server.QUICK_CHECK_TASK_ORDER)
    originele_quick_check_client_latest = dict(server.QUICK_CHECK_CLIENT_LATEST_TASK)
    server.GESPREK_CONTEXT["wacht_op_bevestiging"] = ""
    with server.QUICK_CHECK_CACHE_LOCK:
        server.QUICK_CHECK_CACHE.clear()
    with server.QUICK_CHECK_RATE_LIMIT_LOCK:
        server.QUICK_CHECK_CLIENT_REQUESTS.clear()
    with server.QUICK_CHECK_TASK_LOCK:
        server.QUICK_CHECK_TASKS.clear()
        server.QUICK_CHECK_TASK_ORDER.clear()
        server.QUICK_CHECK_CLIENT_LATEST_TASK.clear()
    server.QUICK_CHECKER_MODULE = None
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
        server.instellingen["website_audit_schedule_enabled"] = originele_website_schedule_enabled
        server.instellingen["website_audit_schedule_frequency"] = originele_website_schedule_frequency
        server.instellingen["website_audit_schedule_time"] = originele_website_schedule_time
        server.instellingen["website_audit_schedule_target_url"] = originele_website_schedule_target_url
        server.instellingen["website_audit_schedule_profile"] = originele_website_schedule_profile
        server.instellingen["website_audit_alert_webhook"] = originele_website_schedule_alert_webhook
        server.instellingen["website_audit_alert_score_drop"] = originele_website_schedule_alert_score_drop
        server.instellingen["website_audit_alert_on_critical"] = originele_website_schedule_alert_on_critical
        server.instellingen["instellingen_profiel"] = origineel_instellingen_profiel
        server.instellingen["instellingen_profielen"] = copy.deepcopy(originele_instellingen_profielen)
        with server.DAILY_SECURITY_SCAN_LOCK:
            server.DAILY_SECURITY_SCAN_STATE.clear()
            server.DAILY_SECURITY_SCAN_STATE.update(originele_daily_state)
        with server.WEBSITE_AUDIT_LOCK:
            server.WEBSITE_AUDIT_STATE.clear()
            server.WEBSITE_AUDIT_STATE.update(copy.deepcopy(originele_website_audit_state))
        with server.WEBSITE_AUDIT_SCHEDULE_LOCK:
            server.WEBSITE_AUDIT_SCHEDULE_STATE.clear()
            server.WEBSITE_AUDIT_SCHEDULE_STATE.update(dict(originele_website_audit_schedule_state))
        with server.QUICK_CHECK_CACHE_LOCK:
            server.QUICK_CHECK_CACHE.clear()
            server.QUICK_CHECK_CACHE.update(copy.deepcopy(originele_quick_check_cache))
        with server.QUICK_CHECK_RATE_LIMIT_LOCK:
            server.QUICK_CHECK_CLIENT_REQUESTS.clear()
            server.QUICK_CHECK_CLIENT_REQUESTS.update(copy.deepcopy(originele_quick_check_client_requests))
        with server.QUICK_CHECK_TASK_LOCK:
            server.QUICK_CHECK_TASKS.clear()
            server.QUICK_CHECK_TASKS.update(copy.deepcopy(originele_quick_check_tasks))
            server.QUICK_CHECK_TASK_ORDER.clear()
            server.QUICK_CHECK_TASK_ORDER.extend(list(originele_quick_check_task_order))
            server.QUICK_CHECK_CLIENT_LATEST_TASK.clear()
            server.QUICK_CHECK_CLIENT_LATEST_TASK.update(dict(originele_quick_check_client_latest))
        server.QUICK_CHECKER_MODULE = origineel_quick_checker_module


def test_index_route_returns_html(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"<html" in response.data.lower()
    assert b"Vraag de bedrijfsdocumenten" in response.data


def test_company_knowledge_command_answers_with_document_citations(client, monkeypatch, tmp_path):
    (tmp_path / "beleid.md").write_text(
        "# Retourbeleid\nKlanten kunnen ongebruikte producten binnen 30 dagen retourneren.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(server, "BEDRIJFSDOCUMENTEN_PAD", tmp_path)
    monkeypatch.setattr(server, "online_ai_beschikbaar", lambda: True)
    ai_calls = []

    def fake_ai(messages, temperatuur=0.4, **_kwargs):
        ai_calls.append(messages)
        return "Klanten mogen binnen 30 dagen retourneren [1] [9]."

    monkeypatch.setattr(server, "vraag_online_ai_bericht", fake_ai)

    response = client.post(
        "/api/commando",
        json={"commando": "vraag bedrijfsdocumenten: wat is het retourbeleid?"},
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "success"
    assert payload["route"]["tool"] == "company_knowledge"
    assert payload["route"]["metrics"]["knowledge_status"] == "answered"
    assert len(payload["route"]["metrics"]["feedback_id"]) == 32
    assert "binnen 30 dagen" in payload["message"]
    assert "[1] beleid.md:1-2" in payload["message"]
    assert "[9]" not in payload["message"]
    assert len(ai_calls) == 1
    prompt = ai_calls[0][1]["content"]
    assert "beleid.md:1-2" in prompt
    assert "ongebruikte producten binnen 30 dagen" in prompt


def test_company_knowledge_example_document_can_answer_demo_question(monkeypatch, tmp_path):
    (tmp_path / "voorbeeld-bedrijf.md").write_text(
        "# Retourbeleid\nOngebruikte producten mogen binnen 30 kalenderdagen retour.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(server, "BEDRIJFSDOCUMENTEN_PAD", tmp_path)
    monkeypatch.setattr(server, "online_ai_beschikbaar", lambda: True)
    monkeypatch.setattr(
        server,
        "vraag_online_ai_bericht",
        lambda *_args, **_kwargs: "Ongebruikte producten mogen binnen 30 kalenderdagen retour [1].",
    )

    antwoord = server.vraag_bedrijfsdocumenten("wat is het retourbeleid?")

    assert "30 kalenderdagen" in antwoord["answer"]
    assert "[1] voorbeeld-bedrijf.md:" in antwoord["answer"]
    assert antwoord["status"] == "answered"


def test_company_knowledge_metrics_and_feedback_are_aggregated_without_text(client, monkeypatch, tmp_path):
    (tmp_path / "beleid.md").write_text(
        "# Retourbeleid\nKlanten kunnen ongebruikte producten binnen 30 dagen retourneren.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(server, "BEDRIJFSDOCUMENTEN_PAD", tmp_path)
    monkeypatch.setattr(server, "online_ai_beschikbaar", lambda: True)
    monkeypatch.setattr(server, "vraag_online_ai_bericht", lambda *_args, **_kwargs: "Retour binnen 30 dagen.")

    answer_response = client.post(
        "/api/commando",
        json={"commando": "vraag bedrijfsdocumenten: wat is het retourbeleid?"},
    )
    feedback_id = answer_response.get_json()["route"]["metrics"]["feedback_id"]
    feedback_response = client.post(
        "/api/company-knowledge/feedback",
        json={"feedback_id": feedback_id, "rating": "positive"},
    )
    duplicate_response = client.post(
        "/api/company-knowledge/feedback",
        json={"feedback_id": feedback_id, "rating": "negative"},
    )
    metrics_response = client.get("/api/company-knowledge/metrics")

    assert answer_response.status_code == 200
    assert feedback_response.status_code == 200
    assert duplicate_response.status_code == 409
    assert metrics_response.status_code == 200
    assert metrics_response.get_json()["answered"] == 1
    assert metrics_response.get_json()["positive_feedback"] == 1
    assert metrics_response.get_json()["positive_feedback_percent"] == 100.0
    opgeslagen_metrics = (server.BEDRIJFSDOCUMENT_METRICS_PAD).read_text(encoding="utf-8")
    assert "wat is het retourbeleid" not in opgeslagen_metrics
    assert "Retour binnen 30 dagen" not in opgeslagen_metrics
    assert "beleid.md" not in opgeslagen_metrics


def test_company_knowledge_feedback_rejects_invalid_payloads(client):
    invalid_rating = client.post(
        "/api/company-knowledge/feedback",
        json={"feedback_id": "a" * 32, "rating": "maybe"},
    )
    malformed_id = client.post(
        "/api/company-knowledge/feedback",
        json={"feedback_id": "../metrics", "rating": "positive"},
    )

    assert invalid_rating.status_code == 400
    assert malformed_id.status_code == 400


def test_company_knowledge_does_not_guess_without_matching_source(client, monkeypatch, tmp_path):
    (tmp_path / "beleid.md").write_text(
        "Retouren kunnen binnen 30 dagen worden gemeld.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(server, "BEDRIJFSDOCUMENTEN_PAD", tmp_path)
    ai_calls = []
    monkeypatch.setattr(server, "vraag_online_ai_bericht", lambda *_args, **_kwargs: ai_calls.append(True))

    response = client.post(
        "/api/commando",
        json={"commando": "vraag bedrijfsdocumenten: wat is de garantieperiode voor laptops?"},
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "success"
    assert "matching passage" in payload["message"].lower() or "passend fragment" in payload["message"].lower()
    assert ai_calls == []


def configureer_demo_modus(monkeypatch):
    wachtwoord = "veilige-echo-demo-code"
    sessiesleutel = "test-sessiesleutel-met-minimaal-32-tekens"
    monkeypatch.setattr(server, "ECHO_DEMO_MODE", True)
    monkeypatch.setattr(server, "ECHO_DEMO_PASSWORD", wachtwoord)
    monkeypatch.setattr(server, "ECHO_SESSION_SECRET", sessiesleutel)
    monkeypatch.setattr(server.app, "secret_key", sessiesleutel)
    monkeypatch.setitem(server.app.config, "SESSION_COOKIE_SECURE", False)
    with server.DEMO_LOGIN_ATTEMPTS_LOCK:
        server.DEMO_LOGIN_ATTEMPTS.clear()
    return wachtwoord


def configureer_enterprise_modus(monkeypatch, tmp_path):
    sessiesleutel = "test-enterprise-sessiesleutel-met-minimaal-32-tekens"
    monkeypatch.setattr(server, "ECHO_ENTERPRISE_MODE", True)
    monkeypatch.setattr(server, "ECHO_ENTERPRISE_ADMIN_USERNAME", "platform-admin")
    monkeypatch.setattr(server, "ECHO_ENTERPRISE_ADMIN_PASSWORD", "platform-admin-wachtwoord")
    monkeypatch.setattr(server, "ECHO_ENTERPRISE_DATA_DIR", tmp_path / "enterprise-data")
    monkeypatch.setattr(server, "ECHO_ENTERPRISE_DATABASE", tmp_path / "enterprise.sqlite3")
    monkeypatch.setattr(server, "ECHO_SESSION_SECRET", sessiesleutel)
    monkeypatch.setattr(server.app, "secret_key", sessiesleutel)
    monkeypatch.setitem(server.app.config, "SESSION_COOKIE_SECURE", False)
    with server.ENTERPRISE_LOGIN_ATTEMPTS_LOCK:
        server.ENTERPRISE_LOGIN_ATTEMPTS.clear()


def login_enterprise(client, username, password):
    return client.post("/login", data={"username": username, "password": password})


def create_enterprise_company(client, name, username, password):
    return client.post(
        "/api/admin/companies",
        json={
            "company_name": name,
            "admin_username": username,
            "admin_password": password,
        },
    )


def test_enterprise_mode_requires_named_account_and_restricts_personal_api(client, monkeypatch, tmp_path):
    configureer_enterprise_modus(monkeypatch, tmp_path)

    page_response = client.get("/")
    settings_response = client.get("/api/instellingen")
    admin_response = client.get("/api/admin/companies")
    login_page = client.get("/login")

    assert page_response.status_code == 302
    assert page_response.headers["Location"].endswith("/login")
    assert settings_response.status_code == 401
    assert admin_response.status_code == 401
    assert b"Gebruikersnaam" in login_page.data
    assert b"Toegangscode" not in login_page.data


def test_enterprise_platform_admin_creates_company_and_company_scoped_users(client, monkeypatch, tmp_path):
    configureer_enterprise_modus(monkeypatch, tmp_path)
    login = login_enterprise(client, "platform-admin", "platform-admin-wachtwoord")
    admin_page = client.get("/admin")
    created = create_enterprise_company(
        client,
        "Bedrijf Een",
        "bedrijf-een-admin",
        "bedrijf-een-admin-wachtwoord",
    )
    company_id = created.get_json()["company"]["id"]
    members = client.post(
        "/api/admin/users",
        json={
            "username": "company-member",
            "password": "company-member-wachtwoord",
            "company_id": company_id,
            "role": "company_admin",
        },
    )

    assert login.status_code == 302
    assert login.headers["Location"].endswith("/admin")
    assert admin_page.status_code == 200
    assert b"createCompanyForm" in admin_page.data
    assert created.status_code == 201
    assert created.get_json()["company"]["name"] == "Bedrijf Een"
    assert created.get_json()["admin"]["username"] == "bedrijf-een-admin"
    assert members.status_code == 201
    assert members.get_json()["user"]["role"] == "company_admin"
    assert client.get("/api/admin/companies").get_json()["companies"][0]["user_count"] == 2


def test_enterprise_company_documents_and_metrics_are_isolated(client, monkeypatch, tmp_path):
    configureer_enterprise_modus(monkeypatch, tmp_path)
    login_enterprise(client, "platform-admin", "platform-admin-wachtwoord")
    company_a = create_enterprise_company(
        client, "Bedrijf Een", "bedrijf-een-admin", "bedrijf-een-admin-wachtwoord",
    ).get_json()["company"]["id"]
    company_b = create_enterprise_company(
        client, "Bedrijf Twee", "bedrijf-twee-admin", "bedrijf-twee-admin-wachtwoord",
    ).get_json()["company"]["id"]
    docs_a = server.enterprise_documents_path(company_a)
    docs_a.mkdir(parents=True, exist_ok=True)
    (docs_a / "beleid.md").write_text(
        "# Retourbeleid\nRetourtermijn voor het zilveren product is 47 dagen.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(server, "online_ai_beschikbaar", lambda: True)
    monkeypatch.setattr(server, "vraag_online_ai_bericht", lambda *_args, **_kwargs: "De retourtermijn is 47 dagen [1].")

    company_a_client = server.app.test_client()
    company_b_client = server.app.test_client()
    login_a = login_enterprise(company_a_client, "bedrijf-een-admin", "bedrijf-een-admin-wachtwoord")
    with company_a_client.session_transaction() as company_a_session:
        company_a_user = server.enterprise_get_user(company_a_session.get("echo_enterprise_user_id"))
    answer_a = company_a_client.post(
        "/api/company-knowledge/query",
        json={"question": "Wat is de retourtermijn van het zilveren product?"},
    )
    login_b = login_enterprise(company_b_client, "bedrijf-twee-admin", "bedrijf-twee-admin-wachtwoord")
    answer_b = company_b_client.post(
        "/api/company-knowledge/query",
        json={"question": "Wat is de retourtermijn van het zilveren product?"},
    )
    documents_b = company_b_client.get("/api/company-knowledge/documents").get_json()
    metrics_a = company_a_client.get("/api/company-knowledge/metrics").get_json()
    metrics_b = company_b_client.get("/api/company-knowledge/metrics").get_json()

    assert login_a.status_code == 302
    assert login_b.status_code == 302
    assert company_a_user["username"] == "bedrijf-een-admin"
    assert company_a_user["company_id"] == company_a
    assert answer_a.status_code == 200, answer_a.get_json()
    assert "47 dagen" in answer_a.get_json()["answer"]
    assert answer_a.get_json()["knowledge_status"] == "answered"
    assert b"enterpriseDocumentsList" in company_a_client.get("/").data
    assert answer_b.status_code == 200
    assert answer_b.get_json()["knowledge_status"] == "no_sources"
    assert "47 dagen" not in answer_b.get_json()["answer"]
    assert documents_b["documents"] == []
    assert metrics_a["answered"] == 1
    assert metrics_b["no_sources"] == 1


def test_enterprise_company_admin_can_upload_list_and_delete_safe_documents(client, monkeypatch, tmp_path):
    configureer_enterprise_modus(monkeypatch, tmp_path)
    login_enterprise(client, "platform-admin", "platform-admin-wachtwoord")
    company_id = create_enterprise_company(
        client, "Bedrijf Een", "bedrijf-een-admin", "bedrijf-een-admin-wachtwoord",
    ).get_json()["company"]["id"]
    login_enterprise(client, "bedrijf-een-admin", "bedrijf-een-admin-wachtwoord")

    uploaded = client.post(
        "/api/company-knowledge/documents",
        data={"document": (io.BytesIO(b"# Retourbeleid\nBinnen 30 dagen.\n"), "../../beleid.md")},
        content_type="multipart/form-data",
    )
    listed = client.get("/api/company-knowledge/documents")
    duplicate = client.post(
        "/api/company-knowledge/documents",
        data={"document": (io.BytesIO(b"Vervangende tekst"), "beleid.md")},
        content_type="multipart/form-data",
    )
    deleted = client.delete("/api/company-knowledge/documents/beleid.md")
    listing_after_delete = client.get("/api/company-knowledge/documents").get_json()
    audit_log = client.get("/api/admin/audit-log")
    audit_events = audit_log.get_json()["events"]

    assert uploaded.status_code == 201
    assert uploaded.get_json()["document"]["name"] == "beleid.md"
    assert uploaded.get_json()["document"]["size_bytes"] == len(b"# Retourbeleid\nBinnen 30 dagen.\n")
    assert listed.status_code == 200
    assert listed.get_json()["documents"][0]["name"] == "beleid.md"
    assert "Binnen 30 dagen" not in listed.get_data(as_text=True)
    assert duplicate.status_code == 409
    assert deleted.status_code == 200
    assert listing_after_delete["documents"] == []
    assert not (tmp_path / "beleid.md").exists()
    assert not (server.enterprise_documents_path(company_id) / "beleid.md").exists()
    assert audit_log.status_code == 200
    assert [event["action"] for event in audit_events[:2]] == ["document_deleted", "document_uploaded"]
    assert all(event["actor_username"] == "bedrijf-een-admin" for event in audit_events[:2])
    assert all(event["target"] == "beleid.md" for event in audit_events[:2])
    assert "Binnen 30 dagen" not in audit_log.get_data(as_text=True)
    with pytest.raises(ValueError):
        server.enterprise_safe_document_path(company_id, "../outside.md")


def test_enterprise_document_upload_rejects_unsupported_invalid_and_oversized_content(client, monkeypatch, tmp_path):
    configureer_enterprise_modus(monkeypatch, tmp_path)
    login_enterprise(client, "platform-admin", "platform-admin-wachtwoord")
    create_enterprise_company(client, "Bedrijf Een", "bedrijf-een-admin", "bedrijf-een-admin-wachtwoord")
    login_enterprise(client, "bedrijf-een-admin", "bedrijf-een-admin-wachtwoord")

    unsupported = client.post(
        "/api/company-knowledge/documents",
        data={"document": (io.BytesIO(b"no"), "beleid.pdf")},
        content_type="multipart/form-data",
    )
    invalid_utf8 = client.post(
        "/api/company-knowledge/documents",
        data={"document": (io.BytesIO(b"\xff\xfe"), "beleid.txt")},
        content_type="multipart/form-data",
    )
    oversized = client.post(
        "/api/company-knowledge/documents",
        data={"document": (io.BytesIO(b"x" * (server.MAX_BEDRIJFSDOCUMENT_GROOTTE + 1)), "groot.md")},
        content_type="multipart/form-data",
    )

    assert unsupported.status_code == 400
    assert invalid_utf8.status_code == 400
    assert oversized.status_code == 413
    assert client.get("/api/company-knowledge/documents").get_json()["documents"] == []


def test_enterprise_document_upload_enforces_company_document_count(client, monkeypatch, tmp_path):
    configureer_enterprise_modus(monkeypatch, tmp_path)
    login_enterprise(client, "platform-admin", "platform-admin-wachtwoord")
    company_id = create_enterprise_company(
        client, "Bedrijf Een", "bedrijf-een-admin", "bedrijf-een-admin-wachtwoord",
    ).get_json()["company"]["id"]
    login_enterprise(client, "bedrijf-een-admin", "bedrijf-een-admin-wachtwoord")
    document_root = server.enterprise_documents_path(company_id)
    document_root.mkdir(parents=True, exist_ok=True)
    for index in range(server.MAX_BEDRIJFSDOCUMENTEN):
        (document_root / f"policy-{index}.md").write_text("Policy text.", encoding="utf-8")

    response = client.post(
        "/api/company-knowledge/documents",
        data={"document": (io.BytesIO(b"New policy."), "new-policy.md")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 409
    assert len(client.get("/api/company-knowledge/documents").get_json()["documents"]) == 100


def test_enterprise_members_can_list_but_cannot_change_company_documents(client, monkeypatch, tmp_path):
    configureer_enterprise_modus(monkeypatch, tmp_path)
    login_enterprise(client, "platform-admin", "platform-admin-wachtwoord")
    create_enterprise_company(client, "Bedrijf Een", "bedrijf-een-admin", "bedrijf-een-admin-wachtwoord")
    login_enterprise(client, "bedrijf-een-admin", "bedrijf-een-admin-wachtwoord")
    created_member = client.post(
        "/api/admin/users",
        json={"username": "gebruiker-een", "password": "gebruiker-een-wachtwoord"},
    )
    admin_logout = client.post("/logout")
    member_client = server.app.test_client()
    login_member = login_enterprise(member_client, "gebruiker-een", "gebruiker-een-wachtwoord")
    listed = member_client.get("/api/company-knowledge/documents")
    upload = member_client.post(
        "/api/company-knowledge/documents",
        data={"document": (io.BytesIO(b"tekst"), "nieuw.txt")},
        content_type="multipart/form-data",
    )
    delete = member_client.delete("/api/company-knowledge/documents/nieuw.txt")

    assert created_member.status_code == 201
    assert admin_logout.status_code == 302
    assert login_member.status_code == 302
    assert listed.status_code == 200
    assert upload.status_code == 403
    assert delete.status_code == 403


def test_enterprise_company_admin_cannot_create_accounts_in_another_company(client, monkeypatch, tmp_path):
    configureer_enterprise_modus(monkeypatch, tmp_path)
    login_enterprise(client, "platform-admin", "platform-admin-wachtwoord")
    create_enterprise_company(client, "Bedrijf Een", "bedrijf-een-admin", "bedrijf-een-admin-wachtwoord")
    login_enterprise(client, "bedrijf-een-admin", "bedrijf-een-admin-wachtwoord")
    admin_page = client.get("/admin")

    response = client.post(
        "/api/admin/users",
        json={
            "username": "foreign-member",
            "password": "foreign-member-wachtwoord",
            "company_id": "a" * 32,
        },
    )

    assert admin_page.status_code == 200
    assert b"createUserForm" in admin_page.data
    assert b"uploadCompanyDocumentForm" in admin_page.data
    assert b"enterpriseAuditLog" in client.get("/admin").data
    assert response.status_code == 403
    assert response.get_json()["status"] == "error"


def test_enterprise_member_cannot_manage_users_and_logout_revokes_access(client, monkeypatch, tmp_path):
    configureer_enterprise_modus(monkeypatch, tmp_path)
    login_enterprise(client, "platform-admin", "platform-admin-wachtwoord")
    created = create_enterprise_company(
        client, "Bedrijf Een", "bedrijf-een-admin", "bedrijf-een-admin-wachtwoord",
    )
    login_enterprise(client, "bedrijf-een-admin", "bedrijf-een-admin-wachtwoord")
    created_member = client.post(
        "/api/admin/users",
        json={"username": "gebruiker-een", "password": "gebruiker-een-wachtwoord"},
    )
    logout_admin = client.post("/logout")
    login_member = login_enterprise(client, "gebruiker-een", "gebruiker-een-wachtwoord")
    admin_page = client.get("/admin")
    member_portal = client.get("/")
    account_list = client.get("/api/admin/users")
    logout_member = client.post("/logout")
    after_logout = client.get("/api/company-knowledge/metrics")

    assert created.status_code == 201
    assert created_member.status_code == 201
    assert logout_admin.status_code == 302
    assert login_member.status_code == 302
    assert admin_page.status_code == 403
    assert member_portal.status_code == 200
    assert account_list.status_code == 403
    assert logout_member.status_code == 302
    assert after_logout.status_code == 401


def test_enterprise_company_admin_can_disable_own_member(client, monkeypatch, tmp_path):
    configureer_enterprise_modus(monkeypatch, tmp_path)
    login_enterprise(client, "platform-admin", "platform-admin-wachtwoord")
    create_enterprise_company(
        client, "Bedrijf Een", "bedrijf-een-admin", "bedrijf-een-admin-wachtwoord",
    )
    login_enterprise(client, "bedrijf-een-admin", "bedrijf-een-admin-wachtwoord")
    created_member = client.post(
        "/api/admin/users",
        json={"username": "uit-te-schakelen", "password": "lid-wachtwoord-langer-dan-12"},
    )
    member = next(
        user for user in client.get("/api/admin/users").get_json()["users"]
        if user["username"] == "uit-te-schakelen"
    )
    member_client = server.app.test_client()
    login_member = login_enterprise(member_client, "uit-te-schakelen", "lid-wachtwoord-langer-dan-12")
    disabled = client.patch(
        f"/api/admin/users/{member['id']}/status",
        json={"enabled": False},
    )
    audit_events = client.get("/api/admin/audit-log").get_json()["events"]
    member_access = member_client.get("/api/company-knowledge/metrics")

    assert created_member.status_code == 201
    assert login_member.status_code == 302
    assert disabled.status_code == 200
    assert disabled.get_json()["enabled"] is False
    assert member_access.status_code == 401
    assert [event["action"] for event in audit_events[:2]] == ["account_disabled", "account_created"]
    assert [event["target"] for event in audit_events[:2]] == ["uit-te-schakelen", "uit-te-schakelen"]


def test_enterprise_audit_log_is_company_admin_only_and_company_scoped(client, monkeypatch, tmp_path):
    configureer_enterprise_modus(monkeypatch, tmp_path)
    login_enterprise(client, "platform-admin", "platform-admin-wachtwoord")
    create_enterprise_company(client, "Bedrijf Een", "bedrijf-een-admin", "bedrijf-een-admin-wachtwoord")
    create_enterprise_company(client, "Bedrijf Twee", "bedrijf-twee-admin", "bedrijf-twee-admin-wachtwoord")

    company_a_client = server.app.test_client()
    login_enterprise(company_a_client, "bedrijf-een-admin", "bedrijf-een-admin-wachtwoord")
    created = company_a_client.post(
        "/api/admin/users",
        json={"username": "audit-member", "password": "audit-member-wachtwoord"},
    )
    events_a = company_a_client.get("/api/admin/audit-log").get_json()["events"]
    events_with_ignored_company_id = company_a_client.get(
        "/api/admin/audit-log?company_id=not-a-company"
    ).get_json()["events"]

    member_client = server.app.test_client()
    login_enterprise(member_client, "audit-member", "audit-member-wachtwoord")
    denied = member_client.get("/api/admin/audit-log")

    company_b_client = server.app.test_client()
    login_enterprise(company_b_client, "bedrijf-twee-admin", "bedrijf-twee-admin-wachtwoord")
    events_b = company_b_client.get("/api/admin/audit-log").get_json()["events"]

    assert created.status_code == 201
    assert events_a[0]["target"] == "audit-member"
    assert events_with_ignored_company_id == events_a
    assert denied.status_code == 403
    assert client.get("/api/admin/audit-log").status_code == 403
    assert all(event["target"] != "audit-member" for event in events_b)


def test_enterprise_admin_password_reset_requires_password_change_and_revokes_sessions(client, monkeypatch, tmp_path):
    configureer_enterprise_modus(monkeypatch, tmp_path)
    login_enterprise(client, "platform-admin", "platform-admin-wachtwoord")
    create_enterprise_company(client, "Bedrijf Een", "bedrijf-een-admin", "bedrijf-een-admin-wachtwoord")
    login_enterprise(client, "bedrijf-een-admin", "bedrijf-een-admin-wachtwoord")
    created = client.post(
        "/api/admin/users",
        json={"username": "wachtwoord-lid", "password": "oud-lid-wachtwoord"},
    )
    member = next(
        user for user in client.get("/api/admin/users").get_json()["users"]
        if user["username"] == "wachtwoord-lid"
    )
    member_client = server.app.test_client()
    login_enterprise(member_client, "wachtwoord-lid", "oud-lid-wachtwoord")

    reset = client.post(f"/api/admin/users/{member['id']}/password-reset", json={})
    temporary_password = reset.get_json()["temporary_password"]
    old_session_access = member_client.get("/api/company-knowledge/metrics")
    old_password_login = login_enterprise(member_client, "wachtwoord-lid", "oud-lid-wachtwoord")
    temporary_login = login_enterprise(member_client, "wachtwoord-lid", temporary_password)
    blocked_api = member_client.get("/api/company-knowledge/metrics")
    change_page = member_client.get("/account/change-password")
    mismatched = member_client.post(
        "/account/change-password",
        data={"password": "nieuw-lid-wachtwoord", "confirm_password": "ander-lid-wachtwoord"},
    )
    changed = member_client.post(
        "/account/change-password",
        data={"password": "nieuw-lid-wachtwoord-veilig", "confirm_password": "nieuw-lid-wachtwoord-veilig"},
    )
    temporary_password_login = login_enterprise(
        server.app.test_client(), "wachtwoord-lid", temporary_password,
    )
    new_password_client = server.app.test_client()
    new_password_login = login_enterprise(
        new_password_client, "wachtwoord-lid", "nieuw-lid-wachtwoord-veilig",
    )
    audit_actions = [
        event["action"]
        for event in client.get("/api/admin/audit-log").get_json()["events"]
    ]

    assert created.status_code == 201
    assert reset.status_code == 200
    assert reset.get_json()["must_change_password"] is True
    assert len(temporary_password) >= 24
    assert old_session_access.status_code == 401
    assert old_password_login.status_code == 401
    assert temporary_login.status_code == 302
    assert temporary_login.headers["Location"].endswith("/account/change-password")
    assert blocked_api.status_code == 403
    assert change_page.status_code == 200
    assert b"Stel je nieuwe wachtwoord in" in change_page.data
    assert mismatched.status_code == 200
    assert b"komen niet overeen" in mismatched.data
    assert changed.status_code == 302
    assert temporary_password_login.status_code == 401
    assert new_password_login.status_code == 302
    assert "password_changed" in audit_actions
    assert "password_reset" in audit_actions

    with server.enterprise_db_connect() as connection:
        stored_hash = connection.execute(
            "SELECT password_hash, must_change_password FROM users WHERE id = ?",
            (member["id"],),
        ).fetchone()
    assert stored_hash["must_change_password"] == 0
    assert server.check_password_hash(stored_hash["password_hash"], temporary_password) is False
    assert server.check_password_hash(stored_hash["password_hash"], "nieuw-lid-wachtwoord-veilig")


def test_enterprise_admin_password_reset_is_limited_to_managed_accounts(client, monkeypatch, tmp_path):
    configureer_enterprise_modus(monkeypatch, tmp_path)
    login_enterprise(client, "platform-admin", "platform-admin-wachtwoord")
    company_a_id = create_enterprise_company(
        client, "Bedrijf Een", "bedrijf-een-admin", "bedrijf-een-admin-wachtwoord",
    ).get_json()["company"]["id"]
    company_b_id = create_enterprise_company(
        client, "Bedrijf Twee", "bedrijf-twee-admin", "bedrijf-twee-admin-wachtwoord",
    ).get_json()["company"]["id"]
    member_b = client.post(
        "/api/admin/users",
        json={
            "username": "ander-bedrijfslid",
            "password": "ander-bedrijfslid-wachtwoord",
            "company_id": company_b_id,
            "role": "member",
        },
    )
    member_b_id = next(
        user["id"]
        for user in client.get(f"/api/admin/users?company_id={company_b_id}").get_json()["users"]
        if user["username"] == "ander-bedrijfslid"
    )
    company_a_admin_id = next(
        user["id"]
        for user in client.get(f"/api/admin/users?company_id={company_a_id}").get_json()["users"]
        if user["username"] == "bedrijf-een-admin"
    )
    with server.enterprise_db_connect() as connection:
        platform_admin_id = connection.execute(
            "SELECT id FROM users WHERE role = 'superadmin'"
        ).fetchone()["id"]

    company_admin = server.app.test_client()
    login_enterprise(company_admin, "bedrijf-een-admin", "bedrijf-een-admin-wachtwoord")
    cross_company_reset = company_admin.post(
        f"/api/admin/users/{member_b_id}/password-reset",
        json={},
    )
    own_reset = company_admin.post(
        f"/api/admin/users/{company_a_admin_id}/password-reset",
        json={},
    )
    platform_admin_self_reset = client.post(
        f"/api/admin/users/{platform_admin_id}/password-reset",
        json={},
    )

    assert member_b.status_code == 201
    assert cross_company_reset.status_code == 403
    assert own_reset.status_code == 403
    assert platform_admin_self_reset.status_code == 403


def test_enterprise_database_migrates_existing_accounts_and_audit_log(monkeypatch, tmp_path):
    configureer_enterprise_modus(monkeypatch, tmp_path)
    database = server.ECHO_ENTERPRISE_DATABASE
    with sqlite3.connect(database) as connection:
        connection.executescript(
            """
            CREATE TABLE companies (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE users (
                id TEXT PRIMARY KEY,
                company_id TEXT REFERENCES companies(id) ON DELETE CASCADE,
                username TEXT NOT NULL UNIQUE COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('superadmin', 'company_admin', 'member')),
                enabled INTEGER NOT NULL DEFAULT 1 CHECK (enabled IN (0, 1)),
                created_at TEXT NOT NULL
            );
            CREATE TABLE enterprise_audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id TEXT NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
                actor_username TEXT NOT NULL,
                action TEXT NOT NULL CHECK (action IN (
                    'company_created', 'member_created', 'member_enabled',
                    'member_disabled', 'document_uploaded', 'document_deleted'
                )),
                target TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            INSERT INTO companies VALUES ('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', 'Bedrijf Een', '2026-01-01T00:00:00+00:00');
            INSERT INTO users VALUES ('admin-id', 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', 'bedrijf-admin', 'hash', 'company_admin', 1, '2026-01-01T00:00:00+00:00');
            INSERT INTO enterprise_audit_log (company_id, actor_username, action, target, created_at)
            VALUES ('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', 'bedrijf-admin', 'member_created', 'oud-lid', '2026-01-01T00:00:00+00:00');
            """
        )

    server.initialize_enterprise_database()
    server.initialize_enterprise_database()
    with server.enterprise_db_connect() as connection:
        user_columns = {
            row["name"] for row in connection.execute("PRAGMA table_info(users)").fetchall()
        }
        audit_rows = connection.execute(
            "SELECT action, target FROM enterprise_audit_log"
        ).fetchall()

    assert {"must_change_password", "auth_version"}.issubset(user_columns)
    assert [(row["action"], row["target"]) for row in audit_rows] == [("account_created", "oud-lid")]


def test_enterprise_mode_requires_secure_cookie_for_network_bind(client, monkeypatch, tmp_path):
    configureer_enterprise_modus(monkeypatch, tmp_path)
    monkeypatch.setenv("ECHO_HOST", "0.0.0.0")
    monkeypatch.setitem(server.app.config, "SESSION_COOKIE_SECURE", False)

    response = client.get("/")

    assert response.status_code == 503
    assert b"ECHO_COOKIE_SECURE=true" in response.data


def test_enterprise_mode_rejects_cross_origin_account_changes(client, monkeypatch, tmp_path):
    configureer_enterprise_modus(monkeypatch, tmp_path)
    login_enterprise(client, "platform-admin", "platform-admin-wachtwoord")

    response = client.post(
        "/api/admin/companies",
        json={
            "company_name": "Aanval",
            "admin_username": "attacker-admin",
            "admin_password": "attacker-admin-password",
        },
        headers={"Origin": "https://evil.example"},
    )

    assert response.status_code == 403
    assert response.get_json()["status"] == "error"


def test_demo_mode_requires_login_for_pages_and_api(client, monkeypatch):
    configureer_demo_modus(monkeypatch)

    page_response = client.get("/")
    api_response = client.get("/api/dashboard")

    assert page_response.status_code == 302
    assert page_response.headers["Location"].endswith("/login")
    assert api_response.status_code == 401
    assert api_response.get_json()["login_url"] == "/login"


def test_demo_mode_login_and_logout_protect_api(client, monkeypatch):
    wachtwoord = configureer_demo_modus(monkeypatch)

    login_page = client.get("/login")
    failed_login = client.post("/login", data={"password": "verkeerde-code"})
    login = client.post("/login", data={"password": wachtwoord})

    assert login_page.status_code == 200
    assert b"Toegangscode" in login_page.data
    assert failed_login.status_code == 401
    assert b"De toegangscode klopt niet" in failed_login.data
    assert login.status_code == 302
    assert "HttpOnly" in login.headers["Set-Cookie"]
    assert "SameSite=Lax" in login.headers["Set-Cookie"]
    assert client.get("/api/dashboard").status_code == 200

    logout = client.post("/logout")

    assert logout.status_code == 302
    assert client.get("/api/dashboard").status_code == 401


def test_demo_mode_fails_closed_without_secure_configuration(client, monkeypatch):
    monkeypatch.setattr(server, "ECHO_DEMO_MODE", True)
    monkeypatch.setattr(server, "ECHO_DEMO_PASSWORD", "")
    monkeypatch.setattr(server, "ECHO_SESSION_SECRET", "")

    response = client.get("/")

    assert response.status_code == 503
    assert b"ECHO_DEMO_PASSWORD" in response.data
    assert client.get("/api/dashboard").status_code == 503


def test_demo_mode_limits_failed_login_attempts(client, monkeypatch):
    configureer_demo_modus(monkeypatch)

    for _ in range(server.DEMO_LOGIN_MAX_ATTEMPTS):
        response = client.post("/login", data={"password": "verkeerde-code"})
        assert response.status_code == 401

    limited_response = client.post("/login", data={"password": "verkeerde-code"})

    assert limited_response.status_code == 429


def test_demo_mode_blocks_cross_origin_and_computer_control(client, monkeypatch):
    wachtwoord = configureer_demo_modus(monkeypatch)
    client.post("/login", data={"password": wachtwoord})
    monkeypatch.setattr(server, "sla_instellingen_op", lambda _instellingen: None)

    cross_origin = client.post(
        "/api/commando",
        json={"commando": "bereken 2+2"},
        headers={"Origin": "https://evil.example"},
    )
    update = client.post("/api/instellingen", json={
        "instellingen_profiel": "streaming",
        "apply_profile": True,
    })

    assert cross_origin.status_code == 403
    assert "Access-Control-Allow-Origin" not in cross_origin.headers
    assert update.status_code == 200
    assert server.instellingen["computerbesturing_toestaan"] is False
    assert server.instellingen["instellingen_profielen"]["streaming"]["computerbesturing_toestaan"] is False


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


def test_execute_command_rejects_too_long_command(client, monkeypatch):
    monkeypatch.setattr(server, "MAX_COMMAND_TEXT_CHARS", 12)

    response = client.post("/api/commando", json={"commando": "x" * 13})

    assert response.status_code == 413
    payload = response.get_json()
    assert payload["status"] == "error"


def test_execute_command_accepts_valid_payload(client):
    response = client.post("/api/commando", json={"commando": "bereken 2+2"})

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "success"
    assert payload.get("message")
    assert "artifacts" in payload
    assert "screenshot" in payload["artifacts"]


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


def test_update_settings_applies_named_profile(client, monkeypatch):
    monkeypatch.setattr(server, "sla_instellingen_op", lambda _instellingen: None)

    response = client.post("/api/instellingen", json={
        "instellingen_profiel": "streaming",
        "apply_profile": True,
    })

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "success"
    assert payload["settings_profile"] == "streaming"
    assert payload["profile_applied"] is True
    assert "streaming" in payload["settings_profiles"]
    assert server.instellingen["computerbesturing_toestaan"] is True
    assert server.instellingen["spraak_uitgang"] is False
    assert server.instellingen["spraak_input_provider"] == "whisper"


def test_update_settings_can_skip_profile_apply(client, monkeypatch):
    monkeypatch.setattr(server, "sla_instellingen_op", lambda _instellingen: None)
    server.instellingen["computerbesturing_toestaan"] = False

    response = client.post("/api/instellingen", json={
        "instellingen_profiel": "streaming",
        "apply_profile": False,
    })

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "success"
    assert payload["settings_profile"] == "streaming"
    assert payload["profile_applied"] is False
    assert server.instellingen["computerbesturing_toestaan"] is False


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


def test_dashboard_exposes_website_audit_structure(client):
    response = client.get("/api/dashboard")

    assert response.status_code == 200
    payload = response.get_json()
    audit = payload["website_audit"]
    assert isinstance(audit, dict)
    assert {
        "running",
        "state",
        "progress_percent",
        "profile",
        "target_url",
        "score",
        "grade",
        "checks_passed",
        "checks_warn",
        "checks_failed",
        "findings_top",
        "severity_totals",
    }.issubset(set(audit.keys()))


def test_dashboard_exposes_website_audit_schedule_structure(client):
    response = client.get("/api/dashboard")

    assert response.status_code == 200
    payload = response.get_json()
    schedule = payload["website_audit_schedule"]
    assert isinstance(schedule, dict)
    assert {
        "enabled",
        "frequency",
        "scheduled_time",
        "target_url",
        "profile",
        "next_run_at",
        "next_run_label",
        "monitor_running",
        "alert_score_drop",
        "alert_on_critical",
    }.issubset(set(schedule.keys()))


def test_website_audit_status_endpoint_returns_expected_structure(client):
    response = client.get("/api/website-audit/status")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "success"
    assert isinstance(payload.get("message"), str)
    assert isinstance(payload.get("audit"), dict)
    assert isinstance(payload.get("schedule"), dict)


def test_website_audit_schedule_endpoint_returns_expected_structure(client):
    response = client.get("/api/website-audit/schedule")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "success"
    assert isinstance(payload.get("message"), str)
    assert isinstance(payload.get("schedule"), dict)


def test_website_audit_schedule_update_endpoint_rejects_invalid_json_shape(client):
    response = client.post("/api/website-audit/schedule", data="[]", content_type="application/json")

    assert response.status_code == 400
    payload = response.get_json()
    assert payload["status"] == "error"


def test_website_audit_schedule_update_endpoint_persists_values(client, monkeypatch):
    monkeypatch.setattr(server, "sla_instellingen_op", lambda _instellingen: None)

    response = client.post("/api/website-audit/schedule", json={
        "enabled": True,
        "frequency": "weekly",
        "scheduled_time": "7:5",
        "target_url": "https://example.com",
        "profile": "security",
        "alert_webhook": "https://hooks.example.com/echo",
        "alert_score_drop": 18,
        "alert_on_critical": False,
    })

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "success"
    schema = payload["schedule"]
    assert schema["enabled"] is True
    assert schema["frequency"] == "weekly"
    assert schema["scheduled_time"] == "07:05"
    assert schema["target_url"] == "https://example.com"
    assert schema["profile"] == "security"
    assert schema["alert_score_drop"] == 18
    assert schema["alert_on_critical"] is False


def test_website_audit_start_endpoint_rejects_invalid_json_shape(client):
    response = client.post("/api/website-audit/start", data="[]", content_type="application/json")

    assert response.status_code == 400
    payload = response.get_json()
    assert payload["status"] == "error"


def test_website_audit_start_endpoint_starts_scan(client, monkeypatch):
    waargenomen = {}

    def fake_start(url, profiel="standard"):
        waargenomen["url"] = url
        waargenomen["profile"] = profiel
        return True, "Website audit started"

    monkeypatch.setattr(server, "start_website_audit", fake_start)
    monkeypatch.setattr(server, "huidige_website_audit_payload", lambda: {"running": True, "state": "running"})

    response = client.post("/api/website-audit/start", json={
        "url": "https://example.com",
        "profile": "security",
    })

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "success"
    assert waargenomen["url"] == "https://example.com"
    assert waargenomen["profile"] == "security"
    assert payload["audit"]["running"] is True


def test_quick_check_run_rejects_invalid_json_shape(client):
    response = client.post("/api/quick-check/run", data="[]", content_type="application/json")

    assert response.status_code == 400
    payload = response.get_json()
    assert payload["status"] == "error"


def test_quick_check_run_rejects_invalid_url(client):
    response = client.post("/api/quick-check/run", json={"url": "https://example.com/\nmalformed"})

    assert response.status_code == 400
    payload = response.get_json()
    assert payload["status"] == "error"


def test_quick_check_run_returns_cached_result_on_repeat(client, monkeypatch):
    calls = {"count": 0}

    class DummyQuickChecker:
        @staticmethod
        def run_scan(url, mode):
            calls["count"] += 1
            return {
                "summary": {
                    "score": 91,
                },
                "target_url": url,
                "mode": mode,
            }

        @staticmethod
        def report_to_text(report):
            return f"score={report.get('summary', {}).get('score', 0)}"

        @staticmethod
        def build_client_message(report):
            return f"Audit score {report.get('summary', {}).get('score', 0)}"

    monkeypatch.setattr(server, "laad_quick_checker_module", lambda: DummyQuickChecker)

    eerste = client.post("/api/quick-check/run", json={"url": "https://example.com", "mode": "quick"})
    tweede = client.post("/api/quick-check/run", json={"url": "https://example.com", "mode": "quick"})

    assert eerste.status_code == 200
    eerste_payload = eerste.get_json()
    assert eerste_payload["status"] == "success"
    assert eerste_payload["from_cache"] is False

    assert tweede.status_code == 200
    tweede_payload = tweede.get_json()
    assert tweede_payload["status"] == "success"
    assert tweede_payload["from_cache"] is True
    assert isinstance(tweede_payload.get("cache_age_seconds"), int)
    assert calls["count"] == 1


def test_quick_check_run_enforces_rate_limit(client, monkeypatch):
    class DummyQuickChecker:
        @staticmethod
        def run_scan(url, mode):
            return {
                "summary": {
                    "score": 88,
                },
                "target_url": url,
                "mode": mode,
            }

    monkeypatch.setattr(server, "laad_quick_checker_module", lambda: DummyQuickChecker)
    monkeypatch.setattr(server, "QUICK_CHECK_RATE_LIMIT_MAX_REQUESTS", 1)
    monkeypatch.setattr(server, "QUICK_CHECK_RATE_LIMIT_WINDOW_SECONDS", 60)

    eerste = client.post("/api/quick-check/run", json={"url": "https://example.com"})
    tweede = client.post("/api/quick-check/run", json={"url": "https://example.com"})

    assert eerste.status_code == 200
    assert tweede.status_code == 429
    payload = tweede.get_json()
    assert payload["status"] == "error"
    assert isinstance(payload.get("retry_after_seconds"), int)
    assert tweede.headers.get("Retry-After")


def test_quick_check_run_returns_timeout_error(client, monkeypatch):
    monkeypatch.setattr(server, "laad_quick_checker_module", lambda: object())

    def fake_timeout(_module, _url, _mode):
        raise TimeoutError("timeout")

    monkeypatch.setattr(server, "voer_quick_checker_scan_met_timeout", fake_timeout)

    response = client.post("/api/quick-check/run", json={"url": "https://example.com"})

    assert response.status_code == 504
    payload = response.get_json()
    assert payload["status"] == "error"


def test_quick_check_start_rejects_invalid_json_shape(client):
    response = client.post("/api/quick-check/start", data="[]", content_type="application/json")

    assert response.status_code == 400
    payload = response.get_json()
    assert payload["status"] == "error"


def test_quick_check_start_returns_task_payload(client, monkeypatch):
    fake_task = server.standaard_quick_check_task_data("quick-check-test-1", "https://example.com", "quick", "127.0.0.1")
    fake_task.update({
        "status": "running",
        "running": True,
        "stage": "queued",
        "progress_percent": 4,
        "message": "Quick checker gestart",
    })

    monkeypatch.setattr(server, "start_quick_checker_scan_taak", lambda _url, _mode, _client: fake_task)

    response = client.post("/api/quick-check/start", json={"url": "https://example.com", "mode": "quick"})

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "success"
    assert payload["task"]["id"] == "quick-check-test-1"
    assert payload["task"]["running"] is True
    assert payload["task"]["status"] == "running"


def test_quick_check_status_endpoint_returns_completed_task_with_result(client):
    task_data = server.standaard_quick_check_task_data("quick-check-test-2", "https://example.com", "quick", "127.0.0.1")
    task_data.update({
        "status": "completed",
        "running": False,
        "stage": "completed",
        "progress_percent": 100,
        "message": "Quick checker scan afgerond.",
        "payload": {
            "report": {
                "target": "https://example.com",
                "scan_type": "quick",
            },
            "text_report": "ok",
            "client_message": "done",
        },
    })
    server.registreer_quick_check_taak(task_data)

    response = client.get("/api/quick-check/status/quick-check-test-2")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "success"
    assert payload["task"]["status"] == "completed"
    assert payload["task"]["result"]["report"]["target"] == "https://example.com"


def test_quick_check_status_endpoint_returns_404_for_unknown_task(client):
    response = client.get("/api/quick-check/status/quick-check-missing")

    assert response.status_code == 404
    payload = response.get_json()
    assert payload["status"] == "error"


def test_website_functional_check_run_rejects_invalid_json_shape(client):
    response = client.post("/api/website-functional-check/run", data="[]", content_type="application/json")

    assert response.status_code == 400
    payload = response.get_json()
    assert payload["status"] == "error"


def test_website_functional_check_run_returns_report_payload(client, monkeypatch):
    monkeypatch.setattr(server, "run_website_functional_visual_check", lambda _url: {
        "scan_id": "functional-check-abc123def456",
        "target_url": "https://example.com",
        "scanned_at": "2026-10-02T09:00:00+00:00",
        "summary": {
            "overall_status": "ok",
            "links_total": 3,
        },
        "report_path": "reports/website-audits/functional-check-abc123def456.html",
        "report_url": "/api/website-functional-check/report/functional-check-abc123def456",
    })

    response = client.post("/api/website-functional-check/run", json={"url": "https://example.com"})

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "success"
    assert payload["check"]["scan_id"] == "functional-check-abc123def456"
    assert payload["check"]["report_url"].endswith("/api/website-functional-check/report/functional-check-abc123def456")


def test_website_functional_check_start_returns_task_payload(client, monkeypatch):
    monkeypatch.setattr(server, "start_website_functional_check_taak", lambda _url, _client: {
        "id": "functional-task-test-1",
        "status": "running",
        "running": True,
        "stage": "links",
        "progress_percent": 42,
        "message": "Testing links",
        "target_url": "https://example.com",
        "current_test": {
            "type": "link",
            "id": "link-2",
            "target": "https://example.com/about",
        },
    })

    response = client.post("/api/website-functional-check/start", json={"url": "https://example.com"})

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "success"
    assert payload["task"]["id"] == "functional-task-test-1"
    assert payload["task"]["running"] is True
    assert payload["task"]["stage"] == "links"


def test_website_functional_check_status_returns_completed_task_with_result(client):
    task_data = server.standaard_website_functional_check_task_data(
        "functional-task-test-2",
        "https://example.com",
        "127.0.0.1",
    )
    task_data.update({
        "status": "completed",
        "running": False,
        "stage": "completed",
        "progress_percent": 100,
        "message": "Visual functional check completed.",
        "payload": {
            "scan_id": "functional-check-abc123def456",
            "report_url": "/api/website-functional-check/report/functional-check-abc123def456",
            "summary": {
                "overall_status": "ok",
                "links_total": 2,
            },
        },
    })
    server.registreer_website_functional_check_taak(task_data)

    response = client.get("/api/website-functional-check/status/functional-task-test-2")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "success"
    assert payload["task"]["status"] == "completed"
    assert payload["task"]["result"]["scan_id"] == "functional-check-abc123def456"


def test_website_functional_check_status_returns_404_for_unknown_task(client):
    response = client.get("/api/website-functional-check/status/functional-task-missing")

    assert response.status_code == 404
    payload = response.get_json()
    assert payload["status"] == "error"


def test_website_functional_check_report_endpoint_returns_html_file(client, monkeypatch, tmp_path):
    report_dir = tmp_path / "website-audits"
    report_dir.mkdir(parents=True, exist_ok=True)

    report_id = "functional-check-abc123def456"
    report_pad = report_dir / f"{report_id}.html"
    report_pad.write_text("<html><body>functional check</body></html>", encoding="utf-8")

    monkeypatch.setattr(server, "WEBSITE_AUDIT_REPORT_DIR", report_dir)

    response = client.get(f"/api/website-functional-check/report/{report_id}")

    assert response.status_code == 200
    assert response.headers.get("Content-Type", "").startswith("text/html")
    assert b"functional check" in response.data


def test_website_functional_check_report_endpoint_rejects_invalid_id(client):
    response = client.get("/api/website-functional-check/report/not-valid")

    assert response.status_code == 404
    payload = response.get_json()
    assert payload["status"] == "error"


def test_website_audit_report_latest_endpoint_returns_404_without_report(client, monkeypatch):
    monkeypatch.setattr(server, "laad_laatste_website_audit_rapport", lambda: None)

    response = client.get("/api/website-audit/report/latest")

    assert response.status_code == 404
    payload = response.get_json()
    assert payload["status"] == "error"


def test_website_audit_report_latest_endpoint_returns_report(client, monkeypatch):
    rapport = {
        "scan_id": "audit-abc123",
        "summary": {
            "score": 88,
            "grade": "B",
            "checks_failed": 1,
            "checks_warn": 2,
        },
    }
    monkeypatch.setattr(server, "laad_laatste_website_audit_rapport", lambda: rapport)
    monkeypatch.setattr(server, "website_audit_rapport_bericht", lambda scan_id="latest": f"report {scan_id}")

    response = client.get("/api/website-audit/report/latest")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "success"
    assert payload["report"]["scan_id"] == "audit-abc123"
    assert payload["report"]["download_paths"]["json"].endswith("/api/website-audit/report/audit-abc123/download/json")
    assert payload["report"]["download_paths"]["markdown"].endswith("/api/website-audit/report/audit-abc123/download/markdown")
    assert payload["report"]["download_paths"]["pdf"].endswith("/api/website-audit/report/audit-abc123/download/pdf")


def test_website_audit_report_by_id_endpoint_returns_404_without_report(client, monkeypatch):
    monkeypatch.setattr(server, "laad_website_audit_rapport", lambda _scan_id: None)

    response = client.get("/api/website-audit/report/audit-missing")

    assert response.status_code == 404
    payload = response.get_json()
    assert payload["status"] == "error"
    assert payload["scan_id"] == "audit-missing"


def test_website_audit_report_by_id_endpoint_returns_report(client, monkeypatch):
    rapport = {
        "scan_id": "audit-xyz789",
        "summary": {
            "score": 74,
            "grade": "C",
            "checks_failed": 3,
            "checks_warn": 1,
        },
    }
    monkeypatch.setattr(server, "laad_website_audit_rapport", lambda _scan_id: rapport)
    monkeypatch.setattr(server, "website_audit_rapport_bericht", lambda scan_id="latest": f"report {scan_id}")

    response = client.get("/api/website-audit/report/audit-xyz789")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "success"
    assert payload["report"]["scan_id"] == "audit-xyz789"
    assert payload["report"]["download_paths"]["json"].endswith("/api/website-audit/report/audit-xyz789/download/json")


def test_website_audit_latest_download_endpoint_returns_report_file(client, monkeypatch, tmp_path):
    report_dir = tmp_path / "website-audits"
    report_dir.mkdir(parents=True, exist_ok=True)

    json_pad = report_dir / "audit-abc123.json"
    json_pad.write_text('{"ok": true}', encoding="utf-8")

    monkeypatch.setattr(server, "WEBSITE_AUDIT_REPORT_DIR", report_dir)
    monkeypatch.setattr(server, "laad_laatste_website_audit_rapport", lambda: {
        "scan_id": "audit-abc123",
        "report_files": {
            "json": str(json_pad),
        },
    })

    response = client.get("/api/website-audit/report/latest/download/json")

    assert response.status_code == 200
    assert response.headers.get("Content-Type", "").startswith("application/json")
    assert b'"ok": true' in response.data


def test_website_audit_scan_download_endpoint_returns_markdown_file(client, monkeypatch, tmp_path):
    report_dir = tmp_path / "website-audits"
    report_dir.mkdir(parents=True, exist_ok=True)

    md_pad = report_dir / "audit-xyz789.md"
    md_pad.write_text("# Demo report", encoding="utf-8")

    monkeypatch.setattr(server, "WEBSITE_AUDIT_REPORT_DIR", report_dir)
    monkeypatch.setattr(server, "laad_website_audit_rapport", lambda _scan_id: {
        "scan_id": "audit-xyz789",
        "report_files": {
            "markdown": str(md_pad),
        },
    })

    response = client.get("/api/website-audit/report/audit-xyz789/download/markdown")

    assert response.status_code == 200
    assert response.headers.get("Content-Type", "").startswith("text/markdown")
    assert b"Demo report" in response.data


def test_website_audit_download_endpoint_returns_404_for_missing_format(client, monkeypatch):
    monkeypatch.setattr(server, "laad_laatste_website_audit_rapport", lambda: {
        "scan_id": "audit-no-files",
        "report_files": {},
    })

    response = client.get("/api/website-audit/report/latest/download/pdf")

    assert response.status_code == 404
    payload = response.get_json()
    assert payload["status"] == "error"


def test_latest_screenshot_endpoint_returns_unavailable_without_files(client, monkeypatch, tmp_path):
    screenshot_dir = tmp_path / "screenshots"
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(server, "screenshot_map_pad", lambda: screenshot_dir)

    response = client.get("/api/screenshot/latest")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["available"] is False


def test_latest_screenshot_and_download_routes_work(client, monkeypatch, tmp_path):
    screenshot_dir = tmp_path / "screenshots"
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    screenshot_file = screenshot_dir / "echo-screenshot-20260904-153000.png"
    screenshot_file.write_bytes(b"PNGDATA")

    monkeypatch.setattr(server, "screenshot_map_pad", lambda: screenshot_dir)
    monkeypatch.setattr(
        server,
        "maak_mobiele_toegang_payload",
        lambda poort=None, host=None: {
            "enabled": True,
            "host": "0.0.0.0",
            "port": 5000,
            "local_url": "http://127.0.0.1:5000",
            "network_urls": ["http://192.168.1.77:5000"],
            "primary_network_url": "http://192.168.1.77:5000",
            "same_network_required": True,
            "access_hint_en": "",
            "access_hint_nl": "",
        },
    )

    latest_response = client.get("/api/screenshot/latest")
    assert latest_response.status_code == 200
    latest_payload = latest_response.get_json()
    assert latest_payload["available"] is True
    assert latest_payload["filename"] == "echo-screenshot-20260904-153000.png"
    assert latest_payload["download_path"].endswith("echo-screenshot-20260904-153000.png")

    download_response = client.get(latest_payload["download_path"])
    assert download_response.status_code == 200
    assert download_response.data == b"PNGDATA"
    assert "attachment" in (download_response.headers.get("Content-Disposition") or "")


def test_screenshot_download_route_rejects_invalid_filename(client):
    response = client.get("/api/screenshots/not-valid-name.png")

    assert response.status_code == 404
    payload = response.get_json()
    assert payload["status"] == "error"


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


def test_normaliseer_actie_parses_stream_start_phrase():
    assert server.normaliseer_actie("ga live op obs") == "stream start"


def test_normaliseer_actie_parses_stream_stop_phrase():
    assert server.normaliseer_actie("stop stream") == "stream stop"


def test_normaliseer_actie_parses_stream_recording_phrase():
    assert server.normaliseer_actie("start recording op obs") == "stream recording start"


def test_normaliseer_actie_parses_stream_scene_brb_phrase():
    assert server.normaliseer_actie("wissel scene naar brb") == "stream scene brb"


def test_normaliseer_actie_parses_stream_marker_phrase():
    assert server.normaliseer_actie("maak clip marker in obs") == "stream marker"


def test_normaliseer_actie_parses_stream_help_phrase():
    assert server.normaliseer_actie("stream help") == "stream help"


def test_normaliseer_actie_parses_website_audit_scan_phrase():
    actie = server.normaliseer_actie("scan website https://example.com op security")
    assert actie == "website audit start::security||https://example.com"


def test_normaliseer_actie_parses_website_audit_status_phrase():
    assert server.normaliseer_actie("website audit status") == "website audit status"


def test_normaliseer_actie_parses_website_audit_report_phrase():
    assert server.normaliseer_actie("website audit report") == "website audit report latest"


def test_normaliseer_actie_parses_website_audit_schedule_status_phrase():
    assert server.normaliseer_actie("website audit schedule status") == "website audit schedule status"


def test_voer_enkele_actie_uit_dispatches_website_audit_start(monkeypatch):
    waargenomen = {}

    def fake_start(url, profiel="standard"):
        waargenomen["url"] = url
        waargenomen["profile"] = profiel
        return True, "Website audit started"

    monkeypatch.setattr(server, "start_website_audit", fake_start)

    resultaat = server.voer_enkele_actie_uit("website audit start::full||https://example.com")

    assert resultaat == "Website audit started"
    assert waargenomen["url"] == "https://example.com"
    assert waargenomen["profile"] == "full"


def test_voer_enkele_actie_uit_dispatches_website_audit_schedule_status(monkeypatch):
    monkeypatch.setattr(server, "website_audit_schedule_status_bericht", lambda: "schedule active")

    resultaat = server.voer_enkele_actie_uit("website audit schedule status")

    assert resultaat == "schedule active"


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


def test_analyseer_verzoek_routering_returns_scores_and_confidence():
    routering = server.analyseer_verzoek_routering("open youtube")

    assert routering["intent"] == "action"
    assert routering["tool"] == "local_plan"
    assert isinstance(routering.get("scores"), dict)
    assert {"action", "answer", "hybrid"}.issubset(set(routering["scores"].keys()))
    assert isinstance(routering.get("confidence"), float)
    assert 0.0 <= routering["confidence"] <= 1.0
    assert isinstance(routering.get("fallback_order"), list)


def test_analyseer_verzoek_routering_classifies_hybrid_question_action_mix():
    routering = server.analyseer_verzoek_routering("open youtube en leg uit waarom deze video handig is")

    assert routering["intent"] == "hybrid"
    assert routering["question_like"] is True
    assert routering["action_like"] is True
    assert routering["tool"] in {"local_plan", "builtin_answer", "online_action_planner"}


def test_synchroniseer_taalinstellingen_normalizes_daily_security_scan_values():
    instellingen = dict(server.DEFAULT_SETTINGS)
    instellingen["security_scan_daily_enabled"] = "ja"
    instellingen["security_scan_daily_time"] = "7:05"

    gesynchroniseerd = server.synchroniseer_taalinstellingen(instellingen)

    assert gesynchroniseerd["security_scan_daily_enabled"] is True
    assert gesynchroniseerd["security_scan_daily_time"] == "07:05"


def test_synchroniseer_taalinstellingen_normalizes_settings_profiles():
    instellingen = dict(server.DEFAULT_SETTINGS)
    instellingen["instellingen_profiel"] = "onbekend"
    instellingen["instellingen_profielen"] = {
        "Security": {
            "online_ai_modus": "nee",
            "computerbesturing_toestaan": "ja",
            "spraak_input_provider": "whisper",
            "website_audit_schedule_profile": "SECURITY",
        },
    }

    gesynchroniseerd = server.synchroniseer_taalinstellingen(instellingen)

    assert gesynchroniseerd["instellingen_profiel"] == "normal"
    assert {"normal", "streaming", "security"}.issubset(set(gesynchroniseerd["instellingen_profielen"].keys()))
    assert gesynchroniseerd["instellingen_profielen"]["security"]["online_ai_modus"] is False
    assert gesynchroniseerd["instellingen_profielen"]["security"]["computerbesturing_toestaan"] is True
    assert gesynchroniseerd["instellingen_profielen"]["security"]["spraak_input_provider"] == "whisper"
    assert gesynchroniseerd["instellingen_profielen"]["security"]["website_audit_schedule_profile"] == "security"


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


def test_evalueer_website_audit_alerts_triggert_bij_critical_en_score_drop(monkeypatch):
    with server.WEBSITE_AUDIT_SCHEDULE_LOCK:
        server.WEBSITE_AUDIT_SCHEDULE_STATE.clear()
        server.WEBSITE_AUDIT_SCHEDULE_STATE.update(server.standaard_website_audit_scheduler_data())
        server.WEBSITE_AUDIT_SCHEDULE_STATE["last_completed_score"] = 93

    monkeypatch.setitem(server.instellingen, "website_audit_alert_score_drop", 10)
    monkeypatch.setitem(server.instellingen, "website_audit_alert_on_critical", True)
    monkeypatch.setitem(server.instellingen, "website_audit_alert_webhook", "https://hooks.example.com/echo")

    webhook_calls = {}

    def fake_webhook(payload, url):
        webhook_calls["payload"] = payload
        webhook_calls["url"] = url
        return True, "ok"

    monkeypatch.setattr(server, "verstuur_website_audit_alert_webhook", fake_webhook)
    monkeypatch.setattr(server, "registreer_notificatie", lambda _melding: None)

    resultaat = server.evalueer_website_audit_alerts({
        "scan_id": "audit-alert-1",
        "target_url": "https://example.com",
        "profile": "security",
        "summary": {
            "score": 72,
            "grade": "C",
            "exposure_level": "high",
            "checks_failed": 4,
            "checks_warn": 2,
            "severity_totals": {
                "critical": 1,
            },
        },
    }, trigger_source="scheduled")

    assert resultaat["triggered"] is True
    assert resultaat["sent"] is True
    assert resultaat["score_drop"] == 21
    assert resultaat["critical"] == 1
    assert webhook_calls["url"] == "https://hooks.example.com/echo"
    assert webhook_calls["payload"]["scan_id"] == "audit-alert-1"
    assert webhook_calls["payload"]["trigger_source"] == "scheduled"


def test_evalueer_website_audit_alerts_blijft_stil_zonder_triggers(monkeypatch):
    with server.WEBSITE_AUDIT_SCHEDULE_LOCK:
        server.WEBSITE_AUDIT_SCHEDULE_STATE.clear()
        server.WEBSITE_AUDIT_SCHEDULE_STATE.update(server.standaard_website_audit_scheduler_data())
        server.WEBSITE_AUDIT_SCHEDULE_STATE["last_completed_score"] = 80

    monkeypatch.setitem(server.instellingen, "website_audit_alert_score_drop", 20)
    monkeypatch.setitem(server.instellingen, "website_audit_alert_on_critical", True)
    monkeypatch.setitem(server.instellingen, "website_audit_alert_webhook", "")
    monkeypatch.setattr(server, "registreer_notificatie", lambda _melding: None)

    resultaat = server.evalueer_website_audit_alerts({
        "scan_id": "audit-alert-2",
        "target_url": "https://example.com",
        "summary": {
            "score": 79,
            "severity_totals": {
                "critical": 0,
            },
        },
    })

    assert resultaat["triggered"] is False
    assert resultaat["sent"] is False
    assert resultaat["score_drop"] == 1


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


def test_is_meedenk_vraag_detecteert_expliciete_denkvraag():
    assert server.is_meedenk_vraag("denk mee over mijn planning") is True
    assert server.is_meedenk_vraag("hoe werkt wifi") is False


def test_is_doorvraag_verzoek_detecteert_expliciete_triggers():
    assert server.is_doorvraag_verzoek("vraag door over mijn project") is True
    assert server.is_doorvraag_verzoek("ask follow-up questions about my code") is True
    assert server.is_doorvraag_verzoek("wat is een api") is False


def test_maak_best_mogelijke_antwoordtekst_kiest_doorvragen_voor_online(monkeypatch):
    monkeypatch.setitem(server.instellingen, "agent_modus", True)
    monkeypatch.setattr(server, "maak_inhoudelijk_antwoord", lambda tekst, uitgevoerde_resultaten=None: "")
    monkeypatch.setattr(server, "maak_online_ai_antwoord", lambda tekst, uitgevoerde_resultaten=None: "online fallback")

    tool, antwoord = server.maak_best_mogelijke_antwoordtekst("vraag door over mijn planning")

    assert tool == "guided_followup"
    assert antwoord
    assert "1." in antwoord and "2." in antwoord and "3." in antwoord


def test_maak_online_ai_antwoord_slaat_cache_hergebruik_op(monkeypatch):
    calls = {"count": 0}

    def fake_online_chat(tekst, uitgevoerde_resultaten=None):
        calls["count"] += 1
        return "Cached answer"

    monkeypatch.setattr(server, "online_ai_beschikbaar", lambda: True)
    monkeypatch.setattr(server, "is_meedenk_vraag", lambda _tekst: False)
    monkeypatch.setattr(server, "is_doorvraag_verzoek", lambda _tekst: False)
    monkeypatch.setattr(server, "vraag_online_ai_chat", fake_online_chat)

    with server.ONLINE_ANTWOORD_CACHE_LOCK:
        server.ONLINE_ANTWOORD_CACHE.clear()

    try:
        eerste = server.maak_online_ai_antwoord("what is caching")
        tweede = server.maak_online_ai_antwoord("what is caching")
    finally:
        with server.ONLINE_ANTWOORD_CACHE_LOCK:
            server.ONLINE_ANTWOORD_CACHE.clear()

    assert eerste == "Cached answer"
    assert tweede == "Cached answer"
    assert calls["count"] == 1


def test_maak_online_ai_antwoord_slaat_over_bij_doorvraag(monkeypatch):
    calls = {"count": 0}

    def fake_online_chat(tekst, uitgevoerde_resultaten=None):
        calls["count"] += 1
        return "Should not be used"

    monkeypatch.setattr(server, "online_ai_beschikbaar", lambda: True)
    monkeypatch.setattr(server, "is_meedenk_vraag", lambda _tekst: False)
    monkeypatch.setattr(server, "is_doorvraag_verzoek", lambda _tekst: True)
    monkeypatch.setattr(server, "vraag_online_ai_chat", fake_online_chat)

    antwoord = server.maak_online_ai_antwoord("vraag door over dit onderwerp")

    assert antwoord == ""
    assert calls["count"] == 0