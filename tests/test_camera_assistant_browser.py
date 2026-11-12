import threading
import time

import pytest
from werkzeug.serving import make_server

import echo_camera_assistant as coach
import server


@pytest.fixture()
def live_coach(monkeypatch, camera_observation):
    state = {"kind": "open", "lean": 0.0, "x": 0.5, "locked": False, "fail": False, "released": 0, "actions": [], "microphones": [], "reminders": []}
    monitor = coach.CameraAssistantMonitor(on_reminder=lambda: state["reminders"].append("posture"))
    monkeypatch.setattr(server, "CAMERA_ASSISTENT", monitor)
    monkeypatch.setattr(server, "ECHO_DEMO_MODE", False)
    monkeypatch.setattr(server, "ECHO_ENTERPRISE_MODE", False)
    monkeypatch.setitem(server.instellingen, "taal", "Nederlands")

    class Detector:
        def __init__(self, _settings, _stop=None):
            if state["fail"]:
                raise coach.CameraAssistantError("vision")

        def read(self):
            return camera_observation(state["kind"], state["lean"], state["x"])

        def close(self):
            state["released"] += 1

    def action(name, settings):
        state["actions"].append((name, settings.swipe_action, settings.microphone))
        return "mic-1" if name == "mute" else None

    def microphone(device=None, muted=None):
        if device is None:
            return [{"id": "mic-1", "name": "Testmicrofoon"}]
        state["microphones"].append((device, muted))
        return device

    monkeypatch.setattr(coach, "LandmarkDetector", Detector)
    monkeypatch.setattr(coach, "perform_action", action)
    monkeypatch.setattr(coach, "microphone_operation", microphone)
    monkeypatch.setattr(coach, "desktop_available", lambda: not state["locked"])
    http = make_server("127.0.0.1", 0, server.app, threaded=True)
    worker = threading.Thread(target=http.serve_forever, daemon=True)
    worker.start()
    try:
        yield f"http://127.0.0.1:{http.server_port}", monitor, state
    finally:
        monitor.stop()
        http.shutdown()
        worker.join(timeout=5)


@pytest.fixture()
def browser():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as runtime:
        instance = runtime.chromium.launch(headless=True)
        try:
            yield instance
        finally:
            instance.close()


def test_status_is_available_when_microphone_listing_hangs(live_coach, browser):
    from playwright.sync_api import expect
    url, monitor, state = live_coach
    page = browser.new_page()
    page.add_init_script("""(() => {
        const originalFetch = window.fetch;
        window.fetch = (input, options) => String(input).includes('/api/camera-assistent/microphones')
            ? new Promise(() => {}) : originalFetch(input, options);
    })()""")
    page.goto(url + "/camera-assistent")
    expect(page.locator("#coach-status")).to_contain_text("Uit.", timeout=3000)
    page.locator("#coach-consent").check()
    expect(page.locator("#coach-start")).to_be_enabled()
    assert not monitor.snapshot()["running"]
    assert not state["actions"]
    page.close()


def test_rejected_action_does_not_report_lost_connection(live_coach, browser):
    from playwright.sync_api import expect
    url, monitor, state = live_coach
    page = browser.new_page()
    page.add_init_script("""(() => {
        window.coachGuideChanges = [];
        document.addEventListener('DOMContentLoaded', () => {
            const guide = document.querySelector('#coach-guide');
            new MutationObserver(() => window.coachGuideChanges.push(guide.textContent))
                .observe(guide, {childList: true, characterData: true, subtree: true});
        });
    })()""")
    page.goto(url + "/camera-assistent")
    page.locator("#coach-consent").check()
    page.locator("#coach-start").click()
    expect(page.locator("#coach-status")).to_contain_text("Camera actief")
    page.route("**/api/camera-assistent/train", lambda route: route.fulfill(
        status=409, json={"status": "error", "message": "De handscan is geweigerd."}
    ))
    page.locator('[data-train="activate"]').click()
    expect(page.locator("#coach-status")).to_contain_text("De handscan is geweigerd.")
    expect(page.locator('[data-train="activate"]')).to_be_enabled(timeout=3000)
    assert all("niet bereikbaar" not in text for text in page.evaluate("window.coachGuideChanges"))
    assert monitor.snapshot()["running"] and not monitor.snapshot()["armed"]
    assert not state["actions"]
    page.locator("#coach-stop").click()
    page.close()


def test_invalid_status_response_is_reported_as_server_error(live_coach, browser):
    from playwright.sync_api import expect
    url, monitor, state = live_coach
    page = browser.new_page()
    page.route("**/api/camera-assistent/status", lambda route: route.fulfill(
        json={"status": "success", "camera": {"phase": "monitoring"}}
    ))
    page.goto(url + "/camera-assistent")
    expect(page.locator("#coach-status")).to_contain_text("Ongeldige camerastatus.")
    expect(page.locator("#coach-guide")).to_contain_text("kon de camerastatus niet ophalen")
    expect(page.locator("#coach-state-camera")).to_have_text("Onbekend")
    expect(page.locator("#coach-start")).to_be_disabled()
    assert not monitor.snapshot()["running"] and not state["actions"]
    page.close()


def test_language_switch_is_local_to_page_and_does_not_restart_camera(live_coach, browser):
    from playwright.sync_api import expect
    url, monitor, state = live_coach
    page = browser.new_page()
    page.goto(url + "/camera-assistent?lang=nl")
    expect(page.locator("#coach-state-camera")).to_have_text("Uit")
    expect(page.locator("#coach-state-scan")).to_have_text("Nog niet gescand")
    expect(page.locator("#coach-state-actions")).to_have_text("Uit")
    page.locator("#coach-consent").check()
    page.locator("#coach-start").click()
    expect(page.locator("#coach-state-camera")).to_have_text("Aan")
    page.get_by_role("link", name="English", exact=True).click()
    expect(page.locator("html")).to_have_attribute("lang", "en")
    expect(page.locator("#coach-state-camera")).to_have_text("On")
    expect(page.locator("#coach-state-actions")).to_have_text("Off")
    assert server.instellingen["taal"] == "Nederlands"
    assert monitor.snapshot()["running"] and not monitor.snapshot()["armed"]
    assert state["released"] == 0 and not state["actions"]
    page.locator("#coach-stop").click()
    page.close()


@pytest.mark.parametrize("language", ["nl", "en"])
def test_pinch_volume_scan_practice_lock_and_visual_feedback(live_coach, browser, language):
    from playwright.sync_api import expect
    url, monitor, state = live_coach
    dutch = language == "nl"
    page = browser.new_page()
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(url + f"/camera-assistent?lang={language}")
    expect(page.get_by_text("Knijpen · volume" if dutch else "Pinch · volume", exact=True)).to_be_visible()
    page.locator("#coach-consent").check()
    page.locator("#coach-start").click()
    state["kind"] = "pinch"
    expect(page.locator("#coach-recognition")).to_contain_text("knijpgebaar" if dutch else "pinch")
    page.wait_for_timeout(650)
    state["kind"] = "pinch_wide"
    page.wait_for_timeout(500)
    assert not state["actions"] and not monitor.snapshot()["armed"]
    state["kind"] = "open"
    page.locator('[data-train="activate"]').click()
    expect(page.locator("#coach-state-actions")).to_have_text("Aan" if dutch else "On", timeout=6000)
    state["kind"] = "pinch"
    expect(page.locator("#coach-guide")).to_contain_text("0,4 seconden" if dutch else "0.4 seconds")
    page.wait_for_timeout(650)
    assert page.evaluate("""() => {
        const c = document.querySelector('#coach-preview');
        const pixel = c.getContext('2d').getImageData(Math.round(c.width * .455), Math.round(c.height * .58), 1, 1).data;
        return pixel[0] === 255 && pixel[1] === 255 && pixel[2] === 255 && pixel[3] === 255;
    }""")
    state["kind"] = "pinch_wide"
    expect(page.locator("#coach-action")).to_contain_text("volume omhoog" if dutch else "volume up")
    page.wait_for_timeout(800)
    assert [action[0] for action in state["actions"]] == ["volume_up"]
    state["kind"] = "pinch"
    expect(page.locator("#coach-action")).to_contain_text("volume omlaag" if dutch else "volume down")
    assert [action[0] for action in state["actions"]] == ["volume_up", "volume_down"]
    state["locked"] = True
    expect(page.locator("#coach-state-camera")).to_have_text("Gepauzeerd" if dutch else "Paused")
    expect(page.locator("#coach-state-actions")).to_have_text("Uit" if dutch else "Off")
    state["locked"] = False
    state["kind"] = "pinch_wide"
    expect(page.locator("#coach-state-camera")).to_have_text("Aan" if dutch else "On")
    page.wait_for_timeout(600)
    assert len(state["actions"]) == 2
    state["kind"] = "pinch"
    page.locator("#coach-arm").click()
    expect(page.locator("#coach-state-actions")).to_have_text("Aan" if dutch else "On")
    page.wait_for_timeout(650)
    state["kind"] = "pinch_close"
    expect(page.locator("#coach-action")).to_contain_text("Acties verstuurd: 3" if dutch else "Actions sent: 3")
    assert [action[0] for action in state["actions"]] == ["volume_up", "volume_down", "volume_down"]
    page.locator("#coach-stop").click()
    expect(page.locator("#coach-state-camera")).to_have_text("Uit" if dutch else "Off")
    assert state["released"] == 1 and not errors
    page.close()


def test_microphones_can_be_retried_and_selection_is_preserved(live_coach, browser):
    from playwright.sync_api import expect
    url, monitor, state = live_coach
    page = browser.new_page()
    calls = []

    def microphone_response(route):
        calls.append(route.request.url)
        if len(calls) == 1:
            route.fulfill(status=503, json={"status": "error", "message": "Testfout microfoon."})
        else:
            route.continue_()

    page.route("**/api/camera-assistent/microphones", microphone_response)
    page.goto(url + "/camera-assistent")
    expect(page.locator("#coach-status")).to_contain_text("Uit.")
    expect(page.locator("#coach-device-status")).to_contain_text("Testfout microfoon.")
    page.locator("#coach-settings summary").click()
    page.locator("#coach-refresh-microphones").click()
    expect(page.locator('#coach-microphone option[value="mic-1"]')).to_have_count(1)
    page.select_option("#coach-microphone", "mic-1")
    page.locator("#coach-refresh-microphones").click()
    expect(page.locator("#coach-refresh-microphones")).to_be_enabled()
    expect(page.locator("#coach-microphone")).to_have_value("mic-1")
    assert len(calls) == 3 and not monitor.snapshot()["running"] and not state["actions"]
    page.close()


def test_missing_saved_microphone_never_silently_switches_device(live_coach, browser):
    from playwright.sync_api import expect
    url, monitor, state = live_coach
    monitor._settings = coach.Settings(microphone="missing-mic")
    page = browser.new_page()
    page.goto(url + "/camera-assistent")
    expect(page.locator("#coach-microphone")).to_have_value("missing-mic")
    expect(page.locator("#coach-device-status")).to_contain_text("niet in de lijst")
    page.locator("#coach-consent").check()
    expect(page.locator("#coach-start")).to_be_disabled()
    page.locator("#coach-settings summary").click()
    page.locator("#coach-gestures").uncheck()
    expect(page.locator("#coach-start")).to_be_enabled()
    expect(page.locator("#coach-device-status")).to_contain_text("als je gebaren wilt gebruiken")
    page.locator("#coach-gestures").check()
    expect(page.locator("#coach-start")).to_be_disabled()
    page.select_option("#coach-microphone", "communications")
    expect(page.locator("#coach-device-status")).not_to_contain_text("niet in de lijst")
    expect(page.locator("#coach-start")).to_be_enabled()
    assert not monitor.snapshot()["running"] and not state["actions"]
    page.close()


def test_invalid_hidden_setting_opens_for_keyboard_correction(live_coach, browser):
    from playwright.sync_api import expect
    url, monitor, state = live_coach
    page = browser.new_page()
    page.goto(url + "/camera-assistent")
    expect(page.locator("#coach-status")).to_contain_text("Uit.")
    page.locator("#coach-consent").check()
    page.locator("#coach-delay").evaluate("(input) => { input.value = '5'; }")
    page.locator("#coach-start").focus()
    page.keyboard.press("Enter")
    expect(page.locator("#coach-settings")).to_have_attribute("open", "")
    expect(page.locator("#coach-delay")).to_be_focused()
    assert not monitor.snapshot()["running"] and not state["actions"]
    page.locator("#coach-settings summary").focus()
    page.keyboard.press("Enter")
    expect(page.locator("#coach-settings")).not_to_have_attribute("open", "")
    page.close()


def test_at_least_one_feature_must_be_enabled_before_start(live_coach, browser):
    from playwright.sync_api import expect
    url, monitor, state = live_coach
    page = browser.new_page()
    page.goto(url + "/camera-assistent")
    expect(page.locator("#coach-status")).to_contain_text("Uit.")
    page.locator("#coach-settings summary").click()
    page.locator("#coach-posture").uncheck()
    page.locator("#coach-gestures").uncheck()
    page.locator("#coach-settings summary").click()
    page.locator("#coach-consent").check()
    page.locator("#coach-start").click()
    expect(page.locator("#coach-settings")).to_have_attribute("open", "")
    expect(page.locator("#coach-gestures")).to_be_focused()
    expect(page.locator("#coach-status")).to_contain_text("Schakel houdingsherinneringen of handgebaren in")
    assert not monitor.snapshot()["running"] and not state["actions"]
    page.locator("#coach-gestures").check()
    expect(page.locator("#coach-status")).to_contain_text("Uit.")
    page.close()


def test_disconnection_marks_each_state_unknown_and_recovers(live_coach, browser):
    from playwright.sync_api import expect
    url, monitor, state = live_coach
    page = browser.new_page()
    page.goto(url + "/camera-assistent")
    page.locator("#coach-consent").check()
    page.locator("#coach-start").click()
    expect(page.locator("#coach-state-camera")).to_have_text("Aan")
    page.locator('[data-train="activate"]').click()
    expect(page.locator("#coach-state-actions")).to_have_text("Aan", timeout=6000)
    page.route("**/api/camera-assistent/status", lambda route: route.abort("failed"))
    for label in ["camera", "scan", "actions"]:
        expect(page.locator(f"#coach-state-{label}")).to_have_text("Onbekend", timeout=3000)
    expect(page.locator("#coach-guide")).to_contain_text("niet bereikbaar")
    expect(page.locator("#coach-action")).to_contain_text("onbekend")
    assert monitor.snapshot()["armed"] and not state["actions"]
    page.unroute("**/api/camera-assistent/status")
    expect(page.locator("#coach-state-actions")).to_have_text("Aan", timeout=4000)
    page.locator("#coach-disarm").click()
    page.locator("#coach-stop").click()
    page.close()


def test_live_guidance_does_not_repeat_unchanged_announcements(live_coach, browser):
    from playwright.sync_api import expect
    url, _monitor, state = live_coach
    state["kind"] = "none"
    page = browser.new_page()
    page.goto(url + "/camera-assistent")
    page.locator("#coach-consent").check()
    page.locator("#coach-start").click()
    expect(page.locator("#coach-guide")).to_contain_text("Geen hand zichtbaar")
    page.evaluate("""() => {
        window.guideMutations = 0;
        const observer = new MutationObserver(() => window.guideMutations++);
        observer.observe(document.querySelector('#coach-guide'), {childList: true, characterData: true, subtree: true});
    }""")
    page.wait_for_timeout(600)
    assert page.evaluate("window.guideMutations") == 0
    page.locator("#coach-stop").click()
    page.close()


def test_camera_page_layout_and_consent_across_screen_sizes(live_coach, browser):
    from playwright.sync_api import expect
    url, monitor, state = live_coach
    page = browser.new_page()
    page.goto(url + "/camera-assistent?lang=nl")
    expect(page.locator("#coach-state-camera")).to_have_text("Uit")
    expect(page.locator("#coach-preview-placeholder")).to_be_visible()
    expect(page.locator("#coach-consent")).not_to_be_checked()
    expect(page.locator("#coach-start")).to_be_disabled()
    for width in [320, 390, 768, 1280]:
        page.set_viewport_size({"width": width, "height": 844})
        assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
        for selector in ["#coach-swipe", "#coach-start", '[data-train="activate"]', "#coach-disarm"]:
            assert page.locator(selector).evaluate(
                "(node) => { const r = node.getBoundingClientRect(); return r.left >= 0 && r.right <= innerWidth; }"
            )
    assert page.evaluate("""() => {
        const ids = Array.from(document.querySelectorAll('[id]'), node => node.id);
        return ids.length === new Set(ids).size;
    }""")
    assert not monitor.snapshot()["running"] and not state["actions"]
    page.close()


def test_dashboard_shortcut_is_filterable_and_opens_without_starting_camera(live_coach, browser):
    from playwright.sync_api import expect
    url, monitor, state = live_coach
    page = browser.new_page(viewport={"width": 1280, "height": 900})

    def api_response(route):
        if route.request.url.endswith("/api/instellingen"):
            route.fulfill(json={"naam": "Echo", "taal": "Nederlands", "spraak_uitgang": False})
        else:
            route.fulfill(status=503, json={"status": "error", "message": "Test service unavailable."})

    page.route("**/api/**", api_response)
    page.goto(url + "/")
    page.wait_for_function("!document.body.classList.contains('booting')", timeout=10000)
    camera = page.locator('#commandCenterPanel a[href="/camera-assistent"]')
    workspace = page.locator('#commandCenterPanel a[href="/werkruimte"]')
    expect(camera).to_be_visible(timeout=7000)
    expect(page.locator("html")).to_have_attribute("lang", "nl")
    expect(camera.locator('strong [lang="nl"]')).to_be_visible()
    expect(camera.locator('strong [lang="en"]')).to_be_hidden()
    page.locator("#actionFilterInput").fill("Spotify")
    expect(camera).to_be_visible()
    expect(workspace).to_be_hidden()
    page.locator("#actionFilterInput").press("Escape")
    expect(workspace).to_be_visible()
    assert page.evaluate("document.body.classList.contains('dashboard-active')")
    page.locator("#languageToggleBtn").click()
    expect(page.locator("html")).to_have_attribute("lang", "en")
    expect(camera.locator('strong [lang="nl"]')).to_be_hidden()
    expect(camera.locator('strong [lang="en"]')).to_be_visible()
    page.locator("#actionFilterInput").fill("gebaren")
    expect(camera).to_be_visible()
    page.locator("#actionFilterInput").press("Escape")
    assert page.evaluate("document.body.classList.contains('dashboard-active')")
    with page.expect_popup() as popup_info:
        camera.click()
    popup = popup_info.value
    expect(popup.locator("#coach-state-camera")).to_have_text("Uit")
    assert not monitor.snapshot()["running"] and not state["actions"]
    popup.close()
    page.set_viewport_size({"width": 390, "height": 844})
    assert page.locator("#commandCenterPanel").evaluate(
        "(node) => { const r = node.getBoundingClientRect(); return r.left >= 0 && r.right <= innerWidth; }"
    )
    page.close()


def test_full_posture_training_gesture_mute_and_stop_flows(live_coach, browser):
    from playwright.sync_api import expect
    url, monitor, state = live_coach
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    assert page.goto(url + "/camera-assistent").status == 200
    expect(page.locator("#coach-status")).to_contain_text("Uit.")
    expect(page.locator("#coach-guide")).to_contain_text("Start")
    expect(page.locator("#coach-start")).to_be_disabled()
    page.locator("#coach-settings summary").click()
    page.locator("#coach-delay").fill("10")
    expect(page.locator('#coach-microphone option[value="mic-1"]')).to_have_count(1)
    page.select_option("#coach-microphone", "mic-1")
    page.locator("#coach-consent").check()
    page.locator("#coach-start").click()
    expect(page.locator("#coach-status")).to_contain_text("Camera actief")
    expect(page.locator("#coach-performance")).to_contain_text("fps")
    expect(page.locator("#coach-guide")).to_contain_text("Hand scannen en gebaren activeren")
    page.wait_for_function("""() => {
        const canvas = document.querySelector('#coach-preview');
        return canvas.getContext('2d').getImageData(320, 360, 1, 1).data[3] > 0;
    }""")
    expect(page.locator("#coach-arm")).to_be_disabled()
    page.locator('[data-train="posture"]').click()
    expect(page.locator("#coach-status")).to_contain_text("Kalibratie bewaard", timeout=6000)
    assert monitor.snapshot()["posture_calibrated"]
    state["kind"] = "none"
    page.locator('[data-train="activate"]').click()
    expect(page.locator("#coach-guide")).to_contain_text("Geen hand")
    state["kind"] = "open+open"
    expect(page.locator("#coach-guide")).to_contain_text("één hand")
    state["kind"] = "open"
    expect(page.locator("#coach-training")).to_contain_text("open hand")
    expect(page.locator("#coach-progress")).to_be_visible()
    expect(page.locator("#coach-recognition")).to_contain_text("Handscan: klaar", timeout=6000)
    expect(page.locator("#coach-action")).to_contain_text("Acties AAN.")
    assert monitor.snapshot()["armed"] and not monitor.snapshot()["trained"]
    assert state["actions"] == []
    state["kind"] = "fist"
    expect(page.locator("#coach-action")).to_contain_text("gemutet", timeout=6000)
    expect(page.locator("#coach-guide")).to_contain_text("al uitgevoerd")
    assert state["actions"] == [("mute", "media", "mic-1")]
    with page.expect_response(lambda response: response.url.endswith("/api/camera-assistent/unmute") and response.request.method == "POST"):
        page.locator("#coach-unmute").click()
    assert state["microphones"] == [("mic-1", False)]
    state["kind"], state["x"] = "open", 0.25
    page.wait_for_timeout(2200)
    state["x"] = 0.6
    expect(page.locator("#coach-action")).to_contain_text("Acties verstuurd: 2", timeout=5000)
    expect(page.locator("#coach-action")).to_contain_text("Laatste actie: volgend nummer")
    assert state["actions"][-1] == ("right", "media", "mic-1")
    state["kind"], state["x"] = "point+open", 0.5
    expect(page.locator("#coach-recognition")).to_contain_text("links: wijsvinger, rechts: open hand", timeout=5000)
    expect(page.locator("#coach-action")).to_contain_text("Acties verstuurd: 3", timeout=6000)
    expect(page.locator("#coach-action")).to_contain_text("Laatste actie: afspelen/pauzeren")
    assert state["actions"][-1] == ("play_pause", "media", "mic-1")
    assert monitor.snapshot()["settings"]["extra_gestures"] is True
    page.locator("#coach-disarm").click()
    expect(page.locator("#coach-action")).to_contain_text("Oefenstand")
    state["lean"] = 0.1
    expect(page.locator("#coach-status")).to_contain_text("Ontspan je schouders", timeout=14000)
    assert state["reminders"] == ["posture"]
    page.reload()
    expect(page.locator("#coach-status")).to_contain_text("Ontspan je schouders")
    expect(page.locator("#coach-delay")).to_have_value("10")
    page.set_viewport_size({"width": 390, "height": 844})
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    page.locator("#coach-stop").click()
    expect(page.locator("#coach-status")).to_contain_text("Uit.")
    expect(page.locator("#coach-state-scan")).to_have_text("Opnieuw scannen")
    expect(page.locator("#coach-recognition")).to_contain_text("opnieuw scannen na het starten")
    expect(page.locator("#coach-performance")).to_have_text("")
    assert not monitor.snapshot()["running"]
    assert state["released"] == 1
    assert errors == []
    page.close()


def test_english_guidance_and_camera_unavailable_message(live_coach, browser, monkeypatch):
    from playwright.sync_api import expect
    url, _monitor, state = live_coach
    monkeypatch.setitem(server.instellingen, "taal", "English")
    page = browser.new_page()
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(url + "/camera-assistent")
    expect(page.locator("#coach-guide")).to_contain_text("Start the camera assistant")
    state["kind"] = "none"
    page.locator("#coach-consent").check()
    page.locator("#coach-start").click()
    expect(page.locator("#coach-guide")).to_contain_text("No hand visible")
    state["kind"] = "open"
    expect(page.locator("#coach-guide")).to_contain_text("Scan hand and enable gestures")
    page.locator("#coach-stop").click()
    expect(page.locator("#coach-guide")).to_contain_text("Start the camera assistant")
    assert errors == []
    page.close()


def test_scan_can_be_cancelled_before_it_arms(live_coach, browser):
    from playwright.sync_api import expect
    url, monitor, state = live_coach
    state["kind"] = "none"
    page = browser.new_page()
    page.goto(url + "/camera-assistent")
    page.locator("#coach-consent").check()
    page.locator("#coach-start").click()
    expect(page.locator("#coach-guide")).to_contain_text("Geen hand")
    page.locator('[data-train="activate"]').click()
    expect(page.locator("#coach-progress")).to_be_visible()
    expect(page.locator("#coach-disarm")).to_have_text("Handscan stoppen")
    expect(page.locator("#coach-disarm")).to_be_enabled()
    page.locator("#coach-disarm").click()
    expect(page.locator("#coach-status")).to_contain_text("Handscan gestopt")
    assert not monitor.snapshot()["training"]
    state["kind"] = "open"
    page.wait_for_timeout(1500)
    assert not monitor.snapshot()["armed"] and not monitor.snapshot()["gesture_ready"]
    assert state["actions"] == []
    page.locator("#coach-stop").click()
    page.close()


def test_lock_cancels_scan_and_requires_manual_reactivation(live_coach, browser):
    from playwright.sync_api import expect
    url, monitor, state = live_coach
    state["kind"] = "none"
    page = browser.new_page()
    page.goto(url + "/camera-assistent")
    page.locator("#coach-consent").check()
    page.locator("#coach-start").click()
    expect(page.locator("#coach-guide")).to_contain_text("Geen hand")
    page.locator('[data-train="activate"]').click()
    expect(page.locator("#coach-progress")).to_be_visible()
    state["locked"] = True
    expect(page.locator("#coach-status")).to_contain_text("Gepauzeerd")
    assert not monitor.snapshot()["training"] and not monitor.snapshot()["armed"]
    state["locked"], state["kind"] = False, "open"
    expect(page.locator("#coach-guide")).to_contain_text("Hand scannen en gebaren activeren")
    page.wait_for_timeout(1200)
    assert not monitor.snapshot()["armed"]
    page.locator('[data-train="activate"]').click()
    expect(page.locator("#coach-action")).to_contain_text("Acties AAN.", timeout=6000)
    state["locked"] = True
    expect(page.locator("#coach-status")).to_contain_text("Gepauzeerd")
    assert not monitor.snapshot()["armed"]
    state["locked"] = False
    expect(page.locator("#coach-arm")).to_be_enabled()
    expect(page.locator("#coach-status")).not_to_contain_text("Gebaaracties staan nu AAN")
    assert not monitor.snapshot()["armed"]
    page.locator("#coach-arm").click()
    expect(page.locator("#coach-action")).to_contain_text("Acties AAN.")
    assert state["actions"] == []
    page.locator("#coach-stop").click()
    page.close()


def test_active_preview_polls_promptly_without_overlapping_requests(live_coach, browser):
    from playwright.sync_api import expect
    url, monitor, _state = live_coach
    page = browser.new_page()
    page.goto(url + "/camera-assistent")
    expect(page.locator("#coach-status")).to_contain_text("Uit.")
    page.locator("#coach-consent").check()
    page.locator("#coach-start").click()
    expect(page.locator("#coach-status")).to_contain_text("Camera actief")
    samples = []
    pending = set()
    overlaps = []

    def requested(request):
        if request.url.endswith("/api/camera-assistent/status"):
            if pending:
                overlaps.append(request.url)
            pending.add(request)
            samples.append(time.monotonic())

    page.on("request", requested)
    page.on("requestfinished", lambda request: pending.discard(request))
    page.on("requestfailed", lambda request: pending.discard(request))
    page.wait_for_timeout(1200)
    assert len(samples) >= 10, "The active sketch must refresh substantially faster than the old 350 ms poll"
    assert not overlaps
    assert monitor.snapshot()["fps"] > 10
    page.locator("#coach-stop").click()
    expect(page.locator("#coach-status")).to_contain_text("Uit.")
    page.close()


def test_camera_error_and_lock_screen_are_visible(live_coach, browser):
    from playwright.sync_api import expect
    url, monitor, state = live_coach
    page = browser.new_page()
    page.goto(url + "/camera-assistent")
    expect(page.locator("#coach-status")).to_contain_text("Uit.")
    page.locator("#coach-consent").check()
    state["fail"] = True
    page.locator("#coach-start").click()
    expect(page.locator("#coach-status")).to_contain_text("Lokale herkenning mislukt")
    state["fail"], state["locked"] = False, True
    page.locator("#coach-start").click()
    expect(page.locator("#coach-status")).to_contain_text("Gepauzeerd")
    assert not monitor.snapshot()["armed"]
    assert not state["actions"]
    page.locator("#coach-stop").click()
    expect(page.locator("#coach-status")).to_contain_text("Uit.")
    page.close()
