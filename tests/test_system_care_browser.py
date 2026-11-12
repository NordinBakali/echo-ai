import copy
import threading
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from werkzeug.serving import make_server

import echo_system_care as care
import server


@pytest.fixture()
def live_care(tmp_path, monkeypatch):
    monitor = care.SystemCare(
        care.Store(tmp_path / "care.sqlite3"),
        profile_provider=lambda: server.instellingen.get("instellingen_profiel", "normal"),
    )
    monkeypatch.setattr(server, "SYSTEEMZORG", monitor)
    monkeypatch.setattr(server, "ECHO_DEMO_MODE", False)
    monkeypatch.setattr(server, "ECHO_ENTERPRISE_MODE", False)
    monkeypatch.setattr(server, "instellingen", copy.deepcopy(server.instellingen))
    monkeypatch.setitem(server.instellingen, "taal", "Nederlands")
    monkeypatch.setattr(server, "sla_instellingen_op", lambda _: None)
    adapter = {"name": "Testwifi", "address": "192.168.8.1", "network": "192.168.8.0/29", "supported": True}
    monkeypatch.setattr(care, "adapters", lambda: [adapter])
    monkeypatch.setattr(care, "scan_lan", lambda *_: ("wifi", [{"ip": "192.168.8.2", "mac": "02:00:00:00:00:02"}]))
    monkeypatch.setattr(care, "windows_events", lambda channel, cursor: {"events": [], "cursor": 42, "error": "Access denied" if channel == "Security" else ""})
    exe = care.resources.normalized_path(r"C:\Apps\example.exe")
    process = {"pid": 99999, "created": 10, "exe": exe, "name": "Example", "memory": 1024}
    monkeypatch.setattr(care.resources, "processes", lambda: {"items": [process], "inaccessible": 1})
    monkeypatch.setattr(care.resources, "power_capabilities", lambda: {"supported": False, "plans": [], "active_cooling": False})
    monkeypatch.setattr(care.resources, "memory_status", lambda: {"available": 4096, "total": 8192, "percent": 50})
    executions = []

    def execute(plan, _store, *, guard=None):
        if guard and not guard(SimpleNamespace(pid=99999, exe=lambda: exe)):
            return {"status": "partial", "processes": [{"pid": 99999, "name": "Example", "status": "skipped_foreground_or_permission"}]}
        executions.append(plan)
        return {"status": "completed", "processes": [{"pid": 99999, "name": "Example", "status": "terminated"}],
                "memory": {"available": 8192}, "available_change": 4096}

    monkeypatch.setattr(care.resources, "execute", execute)
    http = make_server("127.0.0.1", 0, server.app, threaded=True)
    worker = threading.Thread(target=http.serve_forever, daemon=True)
    worker.start()
    try:
        yield f"http://127.0.0.1:{http.server_port}", monitor, executions, exe
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


def test_cpu_ram_watch_policy_consent_load_voice_profile_change_and_stop(live_care, browser, monkeypatch):
    from playwright.sync_api import expect
    url, monitor, executions, exe = live_care
    monkeypatch.setitem(server.instellingen, "instellingen_profiel", "gaming")
    monkeypatch.setattr(monitor, "_pressure_loop", lambda: None)
    monkeypatch.setattr(care.resources, "foreground_protection", lambda: (set(), set()))
    voice = Mock()
    monkeypatch.setattr(care.resources, "local_pressure_speech", voice)
    monkeypatch.setattr(care.resources, "load_sample", lambda _previous, _now: ({
        "cpu": 85, "ram": 50, "inaccessible": 0, "candidates": [{
            "pid": 99999, "created": 10, "exe": exe, "name": "Example", "memory": 1024, "cpu": 10,
        }],
    }, {}))
    page = browser.new_page(viewport={"width": 390, "height": 844})
    page.on("dialog", lambda dialog: dialog.accept())
    page.goto(url + "/systeemzorg")
    expect(page.locator("#care-pressure-status")).to_contain_text("UIT")
    expect(page.locator("#care-apps option")).to_have_count(1)
    expect(page.locator("#care-pressure-start")).to_be_disabled()
    page.select_option("#care-apps", [exe])
    page.locator("#care-save").click()
    page.select_option("#care-pressure-profile", "gaming")
    page.locator("#care-pressure-consent").check()
    page.locator("#care-pressure-start").click()
    expect(page.locator("#care-pressure-status")).to_contain_text("AAN")
    voice.assert_called_once_with(True, check_only=True)
    assert not executions
    for now in [0, 5, 10, 15]:
        monitor.pressure_once(now)
        if monitor.resource_worker:
            monitor.resource_worker.join(3)
    expect(page.locator("#care-pressure-status")).to_contain_text("85.0%")
    expect(page.locator("#care-job")).to_contain_text("terminated")
    assert len(executions) == 1
    voice.assert_called_with(True)
    page.locator("#care-pressure-stop").click()
    expect(page.locator("#care-pressure-status")).to_contain_text("UIT")
    assert not monitor.pressure["enabled"]
    page.locator("#care-pressure-start").click()
    expect(page.locator("#care-pressure-status")).to_contain_text("AAN")
    monkeypatch.setitem(server.instellingen, "instellingen_profiel", "normal")
    care.SystemCare._pressure_loop(monitor)
    expect(page.locator("#care-pressure-status")).to_contain_text("UIT")
    expect(page.locator("#care-pressure-error")).to_contain_text("profile changed")
    assert len(executions) == 1
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    page.close()


def test_local_analysis_explicit_files_safe_render_clear_and_failure(live_care, browser, monkeypatch):
    from playwright.sync_api import expect
    url, monitor, executions, _exe = live_care
    calls = []

    def local_request(endpoint, payload=None, timeout=5):
        calls.append((endpoint, payload))
        if endpoint == "tags":
            return {"models": [{"name": "qwen2.5:3b", "size": 123}]}
        if endpoint == "show":
            return {"model_info": {"general.architecture": "qwen2", "qwen2.context_length": 32768},
                    "capabilities": ["completion"]}
        return {"done": True, "done_reason": "stop", "message": {"content": '{"summary":"Review this log.","findings":[{"file":"sample.log","line":2,"evidence":"<script>window.pwned=1</script>","explanation":"Untrusted log content.","next_step":"Review manually."}]}'}}

    monkeypatch.setattr(server.lokale_analyse, "local_request", local_request)
    page = browser.new_page(viewport={"width": 390, "height": 844})
    page.goto(url + "/systeemzorg")
    expect(page.locator("#local-ai-submit")).to_be_disabled()
    assert not calls
    page.locator("#local-ai-refresh").click()
    expect(page.locator("#local-ai-model option")).to_have_count(2)
    page.select_option("#local-ai-model", "qwen2.5:3b")
    page.locator("#local-ai-files").set_input_files({
        "name": "sample.log", "mimeType": "text/plain",
        "buffer": b"Startup\n<script>window.pwned=1</script>\nERROR",
    })
    expect(page.locator("#local-ai-submit")).to_be_disabled()
    page.locator("#local-ai-consent").check()
    page.locator("#local-ai-submit").click()
    expect(page.locator("#local-ai-report")).to_be_visible()
    expect(page.locator("#local-ai-findings")).to_contain_text("sample.log:2")
    expect(page.locator("#local-ai-findings")).to_contain_text("<script>")
    assert page.evaluate("window.pwned") is None
    assert calls[-1][0] == "chat"
    assert not monitor.snapshot()["running"] and not executions
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    page.locator("#local-ai-clear").click()
    expect(page.locator("#local-ai-report")).to_be_hidden()
    expect(page.locator("#local-ai-consent")).not_to_be_checked()
    assert page.locator("#local-ai-files").evaluate("node => node.files.length") == 0
    def offline(*_args, **_kwargs):
        raise server.lokale_analyse.AnalysisError("Offline", "Niet bereikbaar", 503)

    monkeypatch.setattr(server.lokale_analyse, "local_request", offline)
    page.locator("#local-ai-refresh").click()
    expect(page.locator("#local-ai-error")).to_have_text("Niet bereikbaar")
    page.close()


def test_monitor_trust_profile_preview_confirm_and_persist(live_care, browser):
    from playwright.sync_api import expect
    url, monitor, executions, exe = live_care
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.on("dialog", lambda dialog: dialog.accept())
    page.goto(url + "/systeemzorg")
    expect(page.locator("#care-status")).to_contain_text("Bewaking uit")
    expect(page.locator("#care-apps option")).to_have_count(1)
    expect(page.locator("#care-start")).to_be_disabled()
    assert page.request.post(url + "/api/systeemzorg/automatic", data={"enabled": True}).status == 403
    page.locator("#care-network").check()
    page.locator("#care-logs").check()
    page.select_option("#care-adapter", "192.168.8.1")
    page.locator("#care-consent").check()
    page.locator("#care-start").click()
    expect(page.locator("#care-status")).to_contain_text("Bewaking aan")
    expect(page.locator("#care-devices")).to_contain_text("Onbekend")
    expect(page.locator("#care-coverage")).to_contain_text("Security: Access denied")
    page.locator("#care-devices button").click()
    expect(page.locator("#care-devices")).to_contain_text("Vertrouwd")
    page.locator("#care-stop").click()
    expect(page.locator("#care-status")).to_contain_text("Bewaking uit")
    page.select_option("#care-apps", [exe])
    page.locator("#care-preview-button").click()
    expect(page.locator("#care-preview")).to_contain_text("PID 99999")
    assert executions == []
    page.locator("#care-execute").click()
    expect(page.locator("#care-job")).to_contain_text("completed")
    assert len(executions) == 1
    page.reload()
    expect(page.locator("#care-devices")).to_contain_text("Vertrouwd")
    expect(page.locator("#care-apps")).to_have_values([exe])
    page.locator("#care-auto-on").click()
    expect(page.locator("#care-auto-status")).to_contain_text("aan voor deze sessie")
    assert monitor.automatic
    page.locator("#care-auto-off").click()
    expect(page.locator("#care-auto-status")).to_contain_text("uit")
    page.set_viewport_size({"width": 390, "height": 844})
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    assert errors == []
    page.close()


def test_manual_dashboard_profiles_are_wired_but_intent_switches_are_not(live_care, browser):
    from playwright.sync_api import expect
    url, monitor, executions, _ = live_care
    policy = {"apps": [], "power_plan": "", "active_cooling": False}
    monitor.store.set("policies", {"gaming": policy, "heavy_work": policy})
    monitor.automatic = True
    page = browser.new_page()
    page.goto(url)
    page.wait_for_function("typeof applySettingsProfiel === 'function' && !appState.settingsProfileApplying")
    expect(page.locator("#settingsProfileSelect option[value=gaming]")).to_have_count(1)
    expect(page.locator("#settingsProfileSelect option[value=heavy_work]")).to_have_count(1)
    assert page.evaluate("applySettingsProfiel(null, {forcedProfile: 'gaming', silent: true})")
    assert executions == []
    assert page.evaluate("applySettingsProfiel(null, {forcedProfile: 'heavy_work'})")
    monitor.resource_worker.join(3)
    assert len(executions) == 1 and executions[0]["profile"] == "heavy_work"
    page.close()


def test_native_readonly_preview_empty_execution_and_persistence(tmp_path, monkeypatch, browser):
    from playwright.sync_api import expect
    store = care.Store(tmp_path / "native-care.sqlite3")
    monitor = care.SystemCare(store)
    monkeypatch.setattr(server, "SYSTEEMZORG", monitor)
    monkeypatch.setattr(server, "ECHO_DEMO_MODE", False)
    monkeypatch.setattr(server, "ECHO_ENTERPRISE_MODE", False)
    monkeypatch.setitem(server.instellingen, "taal", "Nederlands")
    http = make_server("127.0.0.1", 0, server.app, threaded=True)
    worker = threading.Thread(target=http.serve_forever, daemon=True)
    worker.start()
    page = browser.new_page()
    page.on("dialog", lambda dialog: dialog.accept())
    try:
        url = f"http://127.0.0.1:{http.server_port}"
        page.goto(url + "/systeemzorg")
        expect(page.locator("#care-capabilities")).to_contain_text("Beschikbaar RAM:", timeout=30000)
        assert page.request.post(url + "/api/systeemzorg/execute", data={"token": "invalid"}).status == 403
        assert page.locator("#care-apps").evaluate("(el) => el.selectedOptions.length") == 0
        page.locator("#care-preview-button").click()
        expect(page.locator("#care-preview")).to_contain_text("0 processen")
        assert list(monitor.previews.values())[0]["policy"] == {"apps": [], "power_plan": "", "active_cooling": False}
        page.locator("#care-execute").click()
        expect(page.locator("#care-job")).to_contain_text("completed")
        assert monitor.last_resource["processes"] == []
        assert care.Store(store.path).get("policies", {})["gaming"]["apps"] == []
        assert not store.get("power_recovery", None)
        assert not monitor.snapshot()["running"]
        page.reload()
        expect(page.locator("#care-status")).to_contain_text("Bewaking uit")
        expect(page.locator("#care-error")).to_be_empty()
    finally:
        page.close()
        monitor.stop()
        if monitor.resource_worker:
            monitor.resource_worker.join(5)
        http.shutdown()
        worker.join(timeout=5)
