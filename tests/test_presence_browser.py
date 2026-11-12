import threading
from pathlib import Path

import pytest
from werkzeug.serving import make_server

import echo_presence as presence
import server


@pytest.fixture()
def live_presence(monkeypatch):
    monitor = presence.PresenceMonitor()
    monkeypatch.setattr(server, "AANWEZIGHEID_MONITOR", monitor)
    monkeypatch.setattr(server, "ECHO_DEMO_MODE", False)
    monkeypatch.setattr(server, "ECHO_ENTERPRISE_MODE", False)
    monkeypatch.setitem(server.instellingen, "taal", "Nederlands")
    monkeypatch.setattr(presence.sys, "platform", "win32")
    monkeypatch.setattr(presence, "lock_windows", lambda: pytest.fail("Browser test tried to lock Windows"))
    monkeypatch.setattr(presence, "play_return_sound", lambda: pytest.fail("Browser test tried to play sound"))
    monkeypatch.setattr(presence, "FACE_STABLE_SECONDS", 0)
    camera_state = {"fail": False, "released": 0}

    class Camera:
        def __init__(self, _index):
            if camera_state["fail"]:
                raise presence.PresenceError("camera_open")

        def read(self):
            return True

        def close(self):
            camera_state["released"] += 1

    monkeypatch.setattr(presence, "CameraDetector", Camera)
    http_server = make_server("127.0.0.1", 0, server.app, threaded=True)
    worker = threading.Thread(target=http_server.serve_forever, daemon=True)
    worker.start()
    try:
        yield f"http://127.0.0.1:{http_server.server_port}", monitor, camera_state
    finally:
        monitor.stop()
        http_server.shutdown()
        worker.join(timeout=5)


@pytest.fixture()
def browser():
    from playwright.sync_api import sync_playwright

    with sync_playwright() as runtime:
        assert Path(runtime.chromium.executable_path).exists(), "Install Playwright Chromium to run presence browser tests"
        instance = runtime.chromium.launch(headless=True)
        try:
            yield instance
        finally:
            instance.close()


def test_presence_ui_opt_in_start_reload_stop_camera_error_and_mobile(live_presence, browser):
    from playwright.sync_api import expect

    base_url, monitor, camera = live_presence
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    response = page.goto(f"{base_url}/aanwezigheid")
    assert response.status == 200
    expect(page.locator("#presence-status")).to_contain_text("Uit.")
    expect(page.locator("#presence-start")).to_be_disabled()
    assert not monitor.snapshot()["running"]
    page.locator("#presence-delay").fill("45")
    page.locator("#presence-notify").select_option("false")
    page.locator("#presence-consent").check()
    page.locator("#presence-start").click()
    expect(page.locator("#presence-status")).to_contain_text("De bewaking is actief")
    expect(page.locator("#presence-delay")).to_be_disabled()
    assert monitor.snapshot()["delay_seconds"] == 45
    assert monitor.snapshot()["notify"] is False
    page.reload()
    expect(page.locator("#presence-status")).to_contain_text("De bewaking is actief")
    expect(page.locator("#presence-delay")).to_have_value("45")
    page.locator("#presence-stop").click()
    expect(page.locator("#presence-status")).to_contain_text("Uit.")
    assert camera["released"] == 1
    assert not monitor.snapshot()["running"]

    camera["fail"] = True
    page.locator("#presence-consent").check()
    page.locator("#presence-start").click()
    expect(page.locator("#presence-status")).to_contain_text("De webcam kan niet openen")
    assert not monitor.snapshot()["running"]
    page.set_viewport_size({"width": 390, "height": 844})
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    assert errors == []
    page.close()


def test_presence_ui_reports_lost_connection_and_stale_token(live_presence, browser, monkeypatch):
    from playwright.sync_api import expect

    base_url, monitor, _camera = live_presence
    page = browser.new_page()
    page.goto(f"{base_url}/aanwezigheid")
    expect(page.locator("#presence-status")).to_contain_text("Uit.")
    page.route("**/api/aanwezigheid/status", lambda route: route.abort())
    expect(page.locator("#presence-status")).to_contain_text("Status onzeker", timeout=6000)
    expect(page.locator("#presence-start")).to_be_disabled()
    page.unroute("**/api/aanwezigheid/status")
    expect(page.locator("#presence-status")).to_contain_text("Uit.", timeout=6000)
    monkeypatch.setattr(server, "AANWEZIGHEID_TOKEN", "rotated-for-browser-test")
    page.locator("#presence-consent").check()
    page.locator("#presence-start").click()
    expect(page.locator("#presence-status")).to_contain_text("Vernieuw de aanwezigheidspagina")
    assert not monitor.snapshot()["running"]
    page.close()
