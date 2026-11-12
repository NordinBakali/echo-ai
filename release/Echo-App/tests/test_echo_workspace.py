import io
import json
import socket
import zipfile

import pytest

import echo_workspace as workspace
import server


@pytest.fixture()
def client(monkeypatch, tmp_path):
    server.app.config.update(TESTING=True)
    monkeypatch.setattr(server, "WERKRUIMTE_DATA_DIR", tmp_path)
    monkeypatch.setattr(server, "ECHO_DEMO_MODE", False)
    monkeypatch.setattr(server, "ECHO_ENTERPRISE_MODE", False)
    monkeypatch.setattr(server, "online_ai_beschikbaar", lambda: True)
    with server.app.test_client() as test_client:
        yield test_client


def test_workspace_is_linked_from_echo_and_available(client):
    assert b"/werkruimte" in client.get("/").data
    response = client.get("/werkruimte")
    assert response.status_code == 200
    assert b"/api/werkruimte" in response.data


def test_workspace_warns_when_no_ai_model_is_configured(client, monkeypatch):
    monkeypatch.setattr(server, "online_ai_beschikbaar", lambda: False)
    response = client.get("/werkruimte")
    assert response.status_code == 200
    assert b"model-warning" in response.data


@pytest.mark.parametrize(("language", "html_language"), [("Nederlands", b'lang="nl"'), ("English", b'lang="en"')])
def test_workspace_uses_echo_language_setting(client, monkeypatch, language, html_language):
    monkeypatch.setitem(server.instellingen, "taal", language)
    assert html_language in client.get("/werkruimte").data


def test_workspace_transcription_does_not_execute_voice_commands(client, monkeypatch):
    seen = {}

    def transcribe(path):
        seen["path"] = path
        return "open de browser en maak een notitie", "whisper"

    monkeypatch.setattr(server, "herken_audio_upload_tekst", transcribe)
    monkeypatch.setattr(server, "voer_commando_uit", lambda _text: pytest.fail("Voice was executed"))
    response = client.post(
        "/api/werkruimte/transcribeer",
        data={"audio": (io.BytesIO(b"audio"), "bericht.ogg")},
    )

    assert response.status_code == 200
    assert response.json["gesproken"] == "open de browser en maak een notitie"
    assert not seen["path"].exists()


def test_workspace_transcription_uses_selected_spoken_language(client, monkeypatch):
    seen = {}

    def transcribe(path, taalcode=None):
        seen["language"] = taalcode
        return "Een Nederlandstalige opname.", "whisper"

    monkeypatch.setattr(server, "herken_audio_upload_tekst", transcribe)
    response = client.post(
        "/api/werkruimte/transcribeer",
        data={"audio": (io.BytesIO(b"audio"), "bericht.ogg"), "language": "nl-NL"},
    )
    assert response.status_code == 200
    assert seen["language"] == "nl-NL"
    invalid = client.post(
        "/api/werkruimte/transcribeer",
        data={"audio": (io.BytesIO(b"audio"), "bericht.ogg"), "language": "invalid"},
    )
    assert invalid.status_code == 400


def test_whisper_receives_the_selected_language(monkeypatch, tmp_path):
    seen = {}

    class Segment:
        text = " Een Nederlandstalige opname."

    class Model:
        def transcribe(self, path, **options):
            seen.update(options)
            return [Segment()], None

    monkeypatch.setattr(server, "laad_whisper_model", lambda: Model())
    transcript = server.herken_audio_pad_via_whisper(tmp_path / "spraak.ogg", taalcode="nl-NL")
    assert transcript == "Een Nederlandstalige opname."
    assert seen["language"] == "nl"


def test_notes_use_the_transcript_without_treating_it_as_a_command(client, monkeypatch):
    messages = []

    def ask_ai(berichten, **_kwargs):
        messages.extend(berichten)
        return "# Overleg\n\n- Bespreek de planning."

    monkeypatch.setattr(server, "vraag_werkruimte_ai", ask_ai)
    response = client.post(
        "/api/werkruimte/verwerk",
        data={"action": "note", "text": "Bespreek morgen de planning."},
    )

    assert response.status_code == 200
    assert response.json["result"].startswith("# Overleg")
    assert any("Bespreek morgen de planning." in item["content"] for item in messages)
    assert "instruction" in messages[0]["content"].lower()


def test_translation_processes_all_chunks_with_previous_context(client, monkeypatch):
    prompts = []
    monkeypatch.setattr(workspace, "AI_CHUNK_CHARS", 80)

    def ask_ai(berichten, **_kwargs):
        prompts.append(berichten[-1]["content"])
        return f"Translated part {len(prompts)}."

    monkeypatch.setattr(server, "vraag_werkruimte_ai", ask_ai)
    text = "Eerste deel met context. " * 8 + "UNIEK_LAATSTE_DEEL"
    response = client.post(
        "/api/werkruimte/verwerk",
        data={
            "action": "translate",
            "text": text,
            "target_language": "English",
            "context": "Het gaat om een zakelijke e-mail.",
        },
    )

    assert response.status_code == 200
    assert len(prompts) > 1
    assert "UNIEK_LAATSTE_DEEL" in prompts[-1]
    assert "zakelijke e-mail" in prompts[0]
    assert "Translated part 1." in prompts[1]
    assert f"Translated part {len(prompts)}." in response.json["result"]


def test_chunking_keeps_every_source_character(monkeypatch):
    monkeypatch.setattr(workspace, "AI_CHUNK_CHARS", 23)
    original = "Een lange zin met meerdere woorden.\n\n" + "é" * 74 + "\nLaatste regel."
    assert "".join(workspace.split_text(original)) == original


def test_translation_keeps_paragraph_boundaries_when_splitting(monkeypatch):
    monkeypatch.setattr(workspace, "AI_CHUNK_CHARS", 35)
    original = "Een zin met meerdere woorden en voldoende context.\n\nEen tweede alinea met meerdere woorden."
    translated = workspace.translate_text(
        original,
        "en",
        "",
        lambda messages: messages[-1]["content"].split("Source segment:\n", 1)[1],
    )
    assert translated == original


def test_long_summary_includes_the_final_chunk(client, monkeypatch):
    prompts = []
    monkeypatch.setattr(workspace, "AI_CHUNK_CHARS", 100)

    def ask_ai(berichten, **_kwargs):
        prompt = berichten[-1]["content"]
        prompts.append(prompt)
        if "UNIEK_LAATSTE_DEEL" in prompt or "Laatste punt." in prompt:
            return "Laatste punt."
        return "Belangrijk punt."

    monkeypatch.setattr(server, "vraag_werkruimte_ai", ask_ai)
    response = client.post(
        "/api/werkruimte/verwerk",
        data={"action": "summary", "text": "Een lange bronzin. " * 20 + "UNIEK_LAATSTE_DEEL"},
    )

    assert response.status_code == 200
    assert any("UNIEK_LAATSTE_DEEL" in prompt for prompt in prompts)
    assert len(prompts) > 2
    assert "Laatste punt." in prompts[-1]


def test_unavailable_ai_and_invalid_sources_report_errors(client, monkeypatch):
    monkeypatch.setattr(server, "online_ai_beschikbaar", lambda: False)
    response = client.post("/api/werkruimte/verwerk", data={"action": "note", "text": "Tekst"})
    assert response.status_code == 503
    assert response.json["status"] == "error"

    monkeypatch.setattr(server, "online_ai_beschikbaar", lambda: True)
    response = client.post(
        "/api/werkruimte/verwerk",
        data={"action": "summary", "text": "Tekst", "url": "https://example.com"},
    )
    assert response.status_code == 400
    assert response.json["status"] == "error"


def test_truncated_ai_response_is_reported_instead_of_returning_partial_text(client, monkeypatch):
    calls = []

    def ask_ai(berichten, **kwargs):
        calls.append(kwargs)
        return {"choices": [{"finish_reason": "length", "message": {"content": "Onvolledig"}}]}

    monkeypatch.setattr(server, "vraag_online_ai_bericht", ask_ai)
    response = client.post(
        "/api/werkruimte/verwerk",
        data={"action": "translate", "text": "Volledige brontekst.", "target_language": "en"},
    )
    assert response.status_code == 502
    assert response.json["status"] == "error"
    assert "result" not in response.json
    assert calls[0]["return_raw"] is True


def test_translation_retries_truncated_chunks_without_losing_source(client, monkeypatch):
    completed_chunks = []
    calls = []

    def ask_ai(berichten, **_kwargs):
        source = berichten[-1]["content"].split("Source segment:\n", 1)[1]
        calls.append(source)
        if len(source) > 900:
            return {"choices": [{"finish_reason": "length", "message": {"content": "Onvolledig"}}]}
        completed_chunks.append(source)
        return {"choices": [{"finish_reason": "stop", "message": {"content": f"Part {len(completed_chunks)}"}}]}

    monkeypatch.setattr(server, "vraag_online_ai_bericht", ask_ai)
    original = "Een zin voor vertaling met context. " * 70
    response = client.post(
        "/api/werkruimte/verwerk",
        data={"action": "translate", "text": original, "target_language": "en"},
    )
    assert response.status_code == 200
    assert len(calls) > len(completed_chunks) > 1
    assert "".join(completed_chunks) == original.strip()
    assert "Part 1" in response.json["result"]
    assert f"Part {len(completed_chunks)}" in response.json["result"]


def test_long_summary_retries_truncated_intermediate_chunks(client, monkeypatch):
    monkeypatch.setattr(workspace, "AI_CHUNK_CHARS", 1_500)
    completed_chunks = []

    def ask_ai(berichten, **_kwargs):
        source = berichten[-1]["content"]
        if source.startswith("Source:\n"):
            return {"choices": [{"finish_reason": "stop", "message": {"content": "De belangrijkste punten."}}]}
        chunk = source.split(":\n", 1)[1]
        if len(chunk) > 900:
            return {"choices": [{"finish_reason": "length", "message": {"content": "Onvolledig"}}]}
        completed_chunks.append(chunk)
        return {"choices": [{"finish_reason": "stop", "message": {"content": "Kern van dit deel."}}]}

    monkeypatch.setattr(server, "vraag_online_ai_bericht", ask_ai)
    original = "Een lang rapport met belangrijke inhoud. " * 100
    response = client.post("/api/werkruimte/verwerk", data={"action": "summary", "text": original})
    assert response.status_code == 200
    assert len(completed_chunks) > 3
    assert "".join(completed_chunks) == original.strip()


def test_successful_raw_ai_response_is_used(client, monkeypatch):
    monkeypatch.setattr(
        server,
        "vraag_online_ai_bericht",
        lambda *_args, **_kwargs: {"choices": [{"finish_reason": "stop", "message": {"content": "# Notitie\nInhoud."}}]},
    )
    response = client.post("/api/werkruimte/verwerk", data={"action": "note", "text": "Inhoud."})
    assert response.status_code == 200
    assert response.json["result"] == "# Notitie\nInhoud."


def test_docx_and_email_extraction_preserve_text_and_context():
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr(
            "word/document.xml",
            b'<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            b"<w:body><w:p><w:r><w:t>Belangrijke titel</w:t></w:r></w:p>"
            b"<w:p><w:r><w:t>Tweede alinea.</w:t></w:r></w:p></w:body></w:document>",
        )
    document = workspace.extract_document(buffer.getvalue(), "rapport.docx", dutch=True)
    assert "Belangrijke titel" in document["text"]
    assert "Tweede alinea." in document["text"]

    message = (
        b"From: sender@example.com\r\nTo: receiver@example.com\r\n"
        b"Subject: Vergadering\r\nContent-Type: text/plain; charset=utf-8\r\n\r\n"
        b"De vergadering is morgen."
    )
    email = workspace.extract_document(message, "mail.eml", dutch=True)
    assert "Vergadering" in email["text"]
    assert "sender@example.com" in email["text"]
    assert "De vergadering is morgen." in email["text"]


def test_real_pdf_extracts_all_text_and_warns_about_scanned_or_blank_pages(client, monkeypatch):
    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=12)
    pdf.cell(text="Unieke tekst op pagina een.")
    pdf.add_page()
    pdf.cell(text="Unieke tekst op pagina twee.")
    pdf.add_page()
    captured = []

    def ask_ai(berichten, **_kwargs):
        captured.append(berichten[-1]["content"])
        return "De kern van het rapport."

    monkeypatch.setattr(server, "vraag_werkruimte_ai", ask_ai)
    response = client.post(
        "/api/werkruimte/verwerk",
        data={"action": "summary", "document": (io.BytesIO(bytes(pdf.output())), "rapport.pdf")},
    )
    assert response.status_code == 200
    assert "Unieke tekst op pagina een." in captured[0]
    assert "Unieke tekst op pagina twee." in captured[0]
    assert len(response.json["warnings"]) == 2
    assert any("OCR" in warning for warning in response.json["warnings"])


def test_scanned_pdf_without_selectable_text_fails_clearly(client):
    from pypdf import PdfWriter

    pdf = PdfWriter()
    pdf.add_blank_page(width=200, height=200)
    buffer = io.BytesIO()
    pdf.write(buffer)
    response = client.post(
        "/api/werkruimte/verwerk",
        data={"action": "summary", "document": (io.BytesIO(buffer.getvalue()), "scan.pdf")},
    )
    assert response.status_code == 422
    assert "OCR" in response.json["message"]


def test_web_fetch_rejects_private_and_mixed_dns_results(monkeypatch):
    monkeypatch.setattr(
        workspace.socket,
        "getaddrinfo",
        lambda *_args, **_kwargs: [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443)),
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 443)),
        ],
    )
    with pytest.raises(workspace.WorkspaceError):
        workspace.resolve_public_addresses("example.com", 443)


@pytest.mark.parametrize("url", ["http://example.com:0/", "ftp://example.com/", "https://user:password@example.com/"])
def test_web_fetch_rejects_invalid_url_forms(url):
    with pytest.raises(workspace.WorkspaceError):
        workspace.normalize_url(url)


def test_web_fetch_rejects_ipv6_to_private_ipv4_translation(monkeypatch):
    monkeypatch.setattr(
        workspace.socket,
        "getaddrinfo",
        lambda *_args, **_kwargs: [
            (socket.AF_INET6, socket.SOCK_STREAM, 6, "", ("64:ff9b::c0a8:101", 443, 0, 0))
        ],
    )
    with pytest.raises(workspace.WorkspaceError):
        workspace.resolve_public_addresses("example.com", 443)


def test_web_fetch_pins_public_ip_and_uses_original_https_hostname(monkeypatch):
    seen = {}

    class FakeSocket:
        def close(self):
            pass

    class FakeTLS:
        def wrap_socket(self, sock, server_hostname):
            seen["tls_hostname"] = server_hostname
            return sock

    class FakeResponse:
        status = 200

        def getheader(self, name):
            return {"Content-Type": "text/html; charset=utf-8"}.get(name)

        def read(self, _limit):
            return b"<html><head><title>Nieuws</title></head><body><nav>Menu</nav><article><h1>Titel</h1><p>Artikeltekst.</p></article></body></html>"

    class FakeConnection:
        def __init__(self, host, port, timeout):
            seen["connection_host"] = host
            self.sock = None

        def request(self, method, path, headers):
            seen["method"] = method
            seen["path"] = path
            seen["host_header"] = headers["Host"]

        def getresponse(self):
            return FakeResponse()

        def close(self):
            self.sock.close()

    monkeypatch.setattr(workspace, "resolve_public_addresses", lambda host, port: ["93.184.216.34"])
    monkeypatch.setattr(
        workspace.socket,
        "create_connection",
        lambda address, timeout: seen.update({"address": address}) or FakeSocket(),
    )
    monkeypatch.setattr(workspace.ssl, "create_default_context", lambda: FakeTLS())
    monkeypatch.setattr(workspace.http.client, "HTTPConnection", FakeConnection)
    article = workspace.fetch_article("https://example.com/artikel?q=1", dutch=True)

    assert seen["address"] == ("93.184.216.34", 443)
    assert seen["tls_hostname"] == seen["connection_host"] == seen["host_header"] == "example.com"
    assert seen["path"] == "/artikel?q=1"
    assert article["title"] == "Titel"
    assert "Artikeltekst." in article["text"]
    assert "Menu" not in article["text"]


def test_web_redirect_is_revalidated_before_connecting(monkeypatch):
    original_fetch = workspace._fetch_once

    def redirect_then_fetch(url):
        if url.startswith("https://example.com/"):
            return 302, "http://127.0.0.1/admin", "", b""
        return original_fetch(url)

    monkeypatch.setattr(workspace, "_fetch_once", redirect_then_fetch)
    monkeypatch.setattr(
        workspace.socket,
        "getaddrinfo",
        lambda *_args, **_kwargs: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 80))],
    )
    monkeypatch.setattr(workspace.socket, "create_connection", lambda *_args, **_kwargs: pytest.fail("Connected to private host"))
    with pytest.raises(workspace.WorkspaceError):
        workspace.fetch_article("https://example.com/nieuws")


def test_reading_list_persists_labels_summary_and_read_state(client, monkeypatch):
    monkeypatch.setattr(
        workspace,
        "fetch_article",
        lambda url, dutch: {
            "url": url,
            "title": "Artikel",
            "text": "Een artikel met relevante feiten.",
            "warnings": [],
        },
    )
    monkeypatch.setattr(
        server,
        "vraag_werkruimte_ai",
        lambda *_args, **_kwargs: json.dumps({
            "title": "Artikel",
            "summary": "De belangrijkste feiten.",
            "labels": ["technologie", "nieuws"],
        }),
    )

    created = client.post("/api/werkruimte/leeslijst", json={"url": "https://example.com/artikel"})
    assert created.status_code == 201
    item = created.json["item"]
    assert item["labels"] == ["technologie", "nieuws"]
    assert item["summary"] == "De belangrijkste feiten."
    assert item["read"] is False
    assert client.get("/api/werkruimte/leeslijst").json["items"][0]["id"] == item["id"]

    updated = client.patch(f'/api/werkruimte/leeslijst/{item["id"]}', json={"read": True})
    assert updated.status_code == 200
    assert client.get("/api/werkruimte/leeslijst").json["items"][0]["read"] is True
    assert client.post("/api/werkruimte/leeslijst", json={"url": "https://example.com/artikel"}).status_code == 409
    assert client.delete(f'/api/werkruimte/leeslijst/{item["id"]}').status_code == 200
    assert client.get("/api/werkruimte/leeslijst").json["items"] == []


def test_invalid_ai_labels_do_not_create_reading_list_entry(client, monkeypatch):
    monkeypatch.setattr(
        workspace,
        "fetch_article",
        lambda url, dutch: {"url": url, "title": "Artikel", "text": "Tekst", "warnings": []},
    )
    monkeypatch.setattr(server, "vraag_werkruimte_ai", lambda *_args, **_kwargs: "Geen geldige JSON")
    response = client.post("/api/werkruimte/leeslijst", json={"url": "https://example.com/artikel"})
    assert response.status_code == 502
    assert client.get("/api/werkruimte/leeslijst").json["items"] == []


def test_workspace_blocks_cross_origin_changes_and_does_not_expose_reading_list(client):
    response = client.post(
        "/api/werkruimte/leeslijst",
        json={"url": "https://example.com"},
        headers={"Origin": "https://other.example"},
    )
    assert response.status_code == 403
    assert "Access-Control-Allow-Origin" not in client.get("/api/werkruimte/leeslijst").headers


def test_workspace_keeps_enterprise_reading_lists_separate(monkeypatch, tmp_path):
    secret = "test-enterprise-sessiesleutel-met-minimaal-32-tekens"
    monkeypatch.setattr(server, "ECHO_DEMO_MODE", False)
    monkeypatch.setattr(server, "ECHO_ENTERPRISE_MODE", True)
    monkeypatch.setattr(server, "ECHO_ENTERPRISE_ADMIN_USERNAME", "platform-admin")
    monkeypatch.setattr(server, "ECHO_ENTERPRISE_ADMIN_PASSWORD", "platform-admin-wachtwoord")
    monkeypatch.setattr(server, "ECHO_ENTERPRISE_DATA_DIR", tmp_path / "enterprise-data")
    monkeypatch.setattr(server, "ECHO_ENTERPRISE_DATABASE", tmp_path / "enterprise.sqlite3")
    monkeypatch.setattr(server, "ECHO_SESSION_SECRET", secret)
    monkeypatch.setattr(server.app, "secret_key", secret)
    monkeypatch.setitem(server.app.config, "SESSION_COOKIE_SECURE", False)
    monkeypatch.setattr(server, "online_ai_beschikbaar", lambda: True)
    monkeypatch.setattr(
        workspace,
        "fetch_article",
        lambda url, dutch: {"url": url, "title": "Artikel", "text": "Bron", "warnings": []},
    )
    monkeypatch.setattr(
        server,
        "vraag_werkruimte_ai",
        lambda *_args, **_kwargs: json.dumps({"title": "Artikel", "summary": "Kern.", "labels": ["nieuws"]}),
    )
    server.initialize_enterprise_database()
    company_id, first_id, second_id = "a" * 32, "b" * 32, "c" * 32
    with server.enterprise_db_connect() as connection:
        connection.execute("INSERT INTO companies (id, name, created_at) VALUES (?, ?, ?)", (company_id, "Bedrijf", "2026"))
        for user_id in (first_id, second_id):
            connection.execute(
                "INSERT INTO users (id, company_id, username, password_hash, role, enabled, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (user_id, company_id, user_id, "unused", "member", 1, "2026"),
            )
    first = server.app.test_client()
    second = server.app.test_client()
    for test_client, user_id in ((first, first_id), (second, second_id)):
        with test_client.session_transaction() as browser_session:
            browser_session["echo_enterprise_user_id"] = user_id
            browser_session["echo_enterprise_auth_version"] = 0

    assert first.get("/werkruimte").status_code == 200
    created = first.post("/api/werkruimte/leeslijst", json={"url": "https://example.com/artikel"})
    assert created.status_code == 201
    item_id = created.json["item"]["id"]
    assert len(first.get("/api/werkruimte/leeslijst").json["items"]) == 1
    assert second.get("/api/werkruimte/leeslijst").json["items"] == []
    assert second.delete(f"/api/werkruimte/leeslijst/{item_id}").status_code == 404
    assert len(first.get("/api/werkruimte/leeslijst").json["items"]) == 1
