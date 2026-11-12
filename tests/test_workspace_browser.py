import json
import threading
from pathlib import Path

import pytest
from werkzeug.serving import make_server

import echo_workspace as workspace
import server


@pytest.fixture()
def live_workspace(monkeypatch, tmp_path):
    monkeypatch.setattr(server, "WERKRUIMTE_DATA_DIR", tmp_path)
    monkeypatch.setattr(server, "ECHO_DEMO_MODE", False)
    monkeypatch.setattr(server, "ECHO_ENTERPRISE_MODE", False)
    monkeypatch.setattr(server, "online_ai_beschikbaar", lambda: True)
    monkeypatch.setitem(server.instellingen, "taal", "Nederlands")
    transcriptions = []

    def transcribe(path, taalcode=None):
        transcriptions.append({"bytes": path.stat().st_size, "language": taalcode})
        return "Morgen bespreken we de planning.", "whisper"

    def ask_ai(messages, **_kwargs):
        prompt = messages[0]["content"]
        if "JSON object" in prompt:
            return json.dumps({"title": "Artikel over energie", "summary": "De kern van het artikel.", "labels": ["energie", "nieuws"]})
        if "well-structured Markdown note" in prompt:
            return "# Overleg\n\n- Bespreek morgen de planning."
        if "Translate the source segment" in prompt:
            return "Dear customer, the delivery is tomorrow."
        return "- Het rapport noemt een belangrijke beslissing."

    monkeypatch.setattr(server, "herken_audio_upload_tekst", transcribe)
    monkeypatch.setattr(server, "vraag_werkruimte_ai", ask_ai)
    monkeypatch.setattr(
        workspace,
        "fetch_article",
        lambda url, dutch: {"url": url, "title": "Artikel", "text": "De inhoud van het artikel.", "warnings": []},
    )
    http_server = make_server("127.0.0.1", 0, server.app, threaded=True)
    worker = threading.Thread(target=http_server.serve_forever, daemon=True)
    worker.start()
    try:
        yield f"http://127.0.0.1:{http_server.server_port}", transcriptions
    finally:
        http_server.shutdown()
        worker.join(timeout=5)


@pytest.fixture()
def browser():
    playwright = pytest.importorskip("playwright.sync_api")
    with playwright.sync_playwright() as runtime:
        if not Path(runtime.chromium.executable_path).exists():
            pytest.skip("Playwright Chromium is not installed")
        instance = runtime.chromium.launch(
            headless=True,
            args=["--use-fake-device-for-media-stream", "--use-fake-ui-for-media-stream"],
        )
        try:
            yield instance
        finally:
            instance.close()


def test_workspace_browser_feature_flows_and_mobile_layout(live_workspace, browser, tmp_path):
    from playwright.sync_api import expect

    base_url, transcriptions = live_workspace
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(f"{base_url}/werkruimte")
    expect(page.locator("#panel-voice")).to_be_visible()
    page.select_option("#voice-language", "nl-NL")
    page.locator("#voice-file").set_input_files({
        "name": "bericht.ogg",
        "mimeType": "audio/ogg",
        "buffer": b"synthetic audio",
    })
    page.locator("#voice-form button[type=submit]").click()
    expect(page.locator("#voice-result")).to_have_value("# Overleg\n\n- Bespreek morgen de planning.")
    expect(page.locator("#note-preview h3")).to_have_text("Overleg")
    expect(page.locator("#note-preview li")).to_have_text("Bespreek morgen de planning.")
    assert transcriptions == [{"bytes": len(b"synthetic audio"), "language": "nl-NL"}]
    with page.expect_download() as download_info:
        page.locator('[data-download="voice-result"]').click()
    note = tmp_path / "notitie.md"
    download_info.value.save_as(str(note))
    assert "Bespreek morgen de planning." in note.read_text(encoding="utf-8")

    page.locator("#tab-reading").click()
    page.locator("#reading-url").fill("https://example.com/artikel")
    page.locator("#reading-form button[type=submit]").click()
    expect(page.locator(".reading-card")).to_have_count(1)
    expect(page.locator(".reading-card")).to_contain_text("De kern van het artikel.")
    expect(page.locator(".reading-label").first).to_have_text("energie")
    page.get_by_role("button", name="Markeer als gelezen").click()
    expect(page.locator(".reading-state")).to_have_text("Gelezen")
    page.reload()
    page.locator("#tab-reading").click()
    expect(page.locator(".reading-state")).to_have_text("Gelezen")
    page.locator("#reading-search").fill("energie")
    expect(page.locator(".reading-card")).to_have_count(1)
    page.once("dialog", lambda dialog: dialog.accept())
    page.get_by_role("button", name="Verwijderen").click()
    expect(page.locator(".reading-card")).to_have_count(0)

    page.locator("#tab-translate").click()
    page.locator("#translate-text").fill("Beste klant, de levering is morgen.")
    page.locator("#translate-context").fill("Formele e-mail")
    page.select_option("#translate-language", "en")
    page.locator("#translate-form button[type=submit]").click()
    expect(page.locator("#translate-result")).to_have_value("Dear customer, the delivery is tomorrow.")

    page.locator("#tab-summary").click()
    page.locator("#summary-text").fill("Een lang rapport met een belangrijke beslissing.")
    page.locator("#summary-form button[type=submit]").click()
    expect(page.locator("#summary-result")).to_have_value("- Het rapport noemt een belangrijke beslissing.")

    page.set_viewport_size({"width": 390, "height": 844})
    for tab in ("voice", "reading", "translate", "summary"):
        page.locator(f"#tab-{tab}").click()
        assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    assert errors == []
    page.close()


def test_workspace_browser_records_and_transcribes_audio(live_workspace, browser):
    from playwright.sync_api import expect

    base_url, transcriptions = live_workspace
    context = browser.new_context(permissions=["microphone"])
    page = context.new_page()
    page.goto(f"{base_url}/werkruimte")
    page.select_option("#voice-language", "nl-NL")
    page.locator("#record-start").click()
    expect(page.locator("#record-stop")).to_be_enabled()
    page.wait_for_timeout(1500)
    page.locator("#record-stop").click()
    expect(page.locator("#voice-preview")).to_be_visible()
    page.locator("#voice-form button[type=submit]").click()
    expect(page.locator("#voice-result")).to_have_value("# Overleg\n\n- Bespreek morgen de planning.")
    assert transcriptions and transcriptions[0]["bytes"] > 0
    assert transcriptions[0]["language"] == "nl-NL"
    context.close()
