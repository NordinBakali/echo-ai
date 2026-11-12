import time
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

import echo_resources as resources
from echo_system_care import CareError, Store, SystemCare


POLICY = {"apps": [resources.normalized_path(r"C:\Apps\example.exe")], "power_plan": "", "active_cooling": False}
GUID = "381b4222-f694-41f0-9685-ff5bb260df2e"


@pytest.fixture()
def setup(tmp_path, monkeypatch):
    store = Store(tmp_path / "care.sqlite3")
    store.set("policies", {"gaming": POLICY})
    process = Mock(pid=99999)
    process.name.return_value = "example.exe"
    process.exe.return_value = POLICY["apps"][0]
    process.username.return_value = "user"
    process.create_time.return_value = 10
    process.memory_info.return_value = SimpleNamespace(rss=1024)
    own = Mock()
    own.username.return_value = "user"
    monkeypatch.setattr(resources.psutil, "Process", lambda pid=None: own if pid is None else process)
    monkeypatch.setattr(resources, "protected_pids", lambda: {1, 2})
    monkeypatch.setattr(resources, "session_id", lambda pid: 1)
    monkeypatch.setattr(resources.psutil, "process_iter", lambda: [process])
    monkeypatch.setattr(resources.psutil, "wait_procs", lambda procs, timeout: (procs, []))
    monkeypatch.setattr(resources, "memory_status", lambda: {"available": 5000, "total": 10000, "percent": 50})
    monkeypatch.setattr(resources, "command", Mock(side_effect=AssertionError("No real system commands")))
    return store, process


@pytest.mark.parametrize("name", ["python.exe", "python3.14", "msedge.exe", "securityhealthservice.exe", "Code.exe", "sentinel.exe"])
def test_protected_names_never_selected(setup, name):
    _, process = setup
    process.name.return_value = name
    assert resources.processes()["items"] == []


def test_other_users_sessions_empty_executable_and_protected_pid(setup, monkeypatch):
    _, process = setup
    process.username.return_value = "someone-else"
    assert not resources.processes()["items"]
    process.username.return_value = "user"
    monkeypatch.setattr(resources.sys, "platform", "win32")
    monkeypatch.setattr(resources, "session_id", lambda pid: 2 if pid == 99999 else 1)
    assert not resources.processes()["items"]
    monkeypatch.setattr(resources, "session_id", lambda pid: 1)
    process.exe.return_value = ""
    assert not resources.processes()["items"]
    assert not resources.eligible(process, {99999}, "user")


def test_policy_accepts_only_observed_or_previously_approved_paths(setup):
    assert resources.validate_policy(POLICY, {}) == POLICY
    with pytest.raises(resources.ResourceError):
        resources.validate_policy({**POLICY, "apps": ["unseen.exe"]}, {})
    with pytest.raises(resources.ResourceError):
        resources.validate_policy({**POLICY, "active_cooling": "yes"}, {})


@pytest.mark.parametrize("change", ["pid_reuse", "exe_change", "owner_change", "protected", "expired", "policy_changed"])
def test_execution_revalidates_exact_identity_and_authorization(setup, change, monkeypatch):
    store, process = setup
    plan = resources.prepare("gaming", POLICY)
    if change == "pid_reuse":
        process.create_time.return_value = 11
    elif change == "exe_change":
        process.exe.return_value = r"C:\Apps\different.exe"
    elif change == "owner_change":
        process.username.return_value = "other"
    elif change == "protected":
        monkeypatch.setattr(resources, "protected_pids", lambda: {99999})
    elif change == "expired":
        plan["created"] = time.time() - 31
    else:
        store.set("policies", {"gaming": {**POLICY, "apps": []}})
    if change in ("expired", "policy_changed"):
        with pytest.raises(resources.ResourceError):
            resources.execute(plan, store)
    else:
        result = resources.execute(plan, store)
        assert result["status"] == "partial"
    process.terminate.assert_not_called()


def test_explicit_termination_and_actual_memory_difference(setup, monkeypatch):
    store, process = setup
    plan = resources.prepare("gaming", POLICY)
    monkeypatch.setattr(resources, "memory_status", lambda: {"available": 4500})
    result = resources.execute(plan, store)
    process.terminate.assert_called_once()
    assert result["status"] == "completed"
    assert result["available_change"] == -500


def test_partial_results_never_claim_success(setup, monkeypatch):
    store, process = setup
    monkeypatch.setattr(resources.psutil, "wait_procs", lambda procs, timeout: ([], procs))
    result = resources.execute(resources.prepare("gaming", POLICY), store)
    assert result["status"] == "partial" and result["processes"][0]["status"] == "still_running"
    process.terminate.side_effect = resources.psutil.AccessDenied(99999)
    result = resources.execute(resources.prepare("gaming", POLICY), store)
    assert result["processes"][0]["status"] == "error"


def test_power_recovery_saved_before_changes_and_retained_on_failure(setup, monkeypatch):
    store, process = setup
    monkeypatch.setattr(resources, "power_capabilities", lambda: {"active": GUID, "plans": [{"id": GUID}]})
    monkeypatch.setattr(resources, "cooling_index", lambda _: 0)

    def fail(_args):
        assert store.get("power_recovery", None) == {"active": GUID, "cooling": {GUID: 0}}
        raise resources.ResourceError("Permission denied")

    monkeypatch.setattr(resources, "command", fail)
    policy = {**POLICY, "active_cooling": True}
    store.set("policies", {"gaming": policy})
    with pytest.raises(resources.ResourceError):
        resources.execute(resources.prepare("gaming", policy), store)
    process.terminate.assert_not_called()
    assert store.get("power_recovery", None)
    monkeypatch.setattr(resources, "command", Mock(return_value=""))
    monkeypatch.setattr(resources, "active_scheme", lambda: GUID)
    resources.restore_power(store)
    assert store.get("power_recovery", None) is None


def test_preview_is_single_use_and_auto_actions_are_session_authorized(setup, monkeypatch):
    store, process = setup
    service = SystemCare(store)
    assert service.profile_changed("gaming", True) == "manual_confirmation_required"
    service.automatic = True
    assert service.profile_changed("gaming", False) == "manual_confirmation_required"
    preview = service.preview("gaming")
    service.execute_preview(preview["token"])
    service.resource_worker.join(3)
    assert service.last_resource["status"] == "completed"
    with pytest.raises(CareError):
        service.execute_preview(preview["token"])
    assert SystemCare(Store(store.path)).automatic is False
    process.terminate.assert_called_once()


@pytest.mark.parametrize("recovery", ["invalid", {"active": 5}, {"active": GUID, "cooling": {GUID: 2}}])
def test_invalid_recovery_never_changes_os(setup, recovery):
    store, _ = setup
    store.set("power_recovery", recovery)
    with pytest.raises(resources.ResourceError):
        resources.restore_power(store)
    resources.command.assert_not_called()


def test_power_readback_failure_keeps_recovery(setup, monkeypatch):
    store, process = setup
    monkeypatch.setattr(resources, "power_capabilities", lambda: {"active": GUID, "plans": [{"id": GUID}]})
    monkeypatch.setattr(resources, "command", Mock(return_value=""))
    monkeypatch.setattr(resources, "active_scheme", lambda: GUID)
    monkeypatch.setattr(resources, "cooling_index", lambda _: 0)
    with pytest.raises(resources.ResourceError, match="verification"):
        resources.apply_power({**POLICY, "active_cooling": True}, store)
    assert store.get("power_recovery", None) is not None
    process.terminate.assert_not_called()


def test_nonwindows_power_policy_is_explicitly_unsupported(setup, monkeypatch):
    monkeypatch.setattr(resources.sys, "platform", "linux")
    with pytest.raises(resources.ResourceError, match="require Windows"):
        resources.validate_policy({**POLICY, "active_cooling": True}, {})


@pytest.fixture()
def pressure_setup(setup, monkeypatch):
    store, process = setup
    active = ["gaming"]
    service = SystemCare(store, profile_provider=lambda: active[0])
    monkeypatch.setattr(service, "_pressure_loop", lambda: None)
    monkeypatch.setattr(resources, "foreground_protection", lambda: (set(), set()))
    voice = Mock()
    monkeypatch.setattr(resources, "local_pressure_speech", voice)
    sample = {"cpu": 85, "ram": 50, "inaccessible": 0, "candidates": [
        {"pid": 99999, "created": 10, "exe": POLICY["apps"][0], "name": "example.exe",
         "memory": 256 * 1024 * 1024, "cpu": 10},
    ]}
    monkeypatch.setattr(resources, "load_sample", lambda _previous, _now: (sample, {}))
    try:
        yield service, process, sample, active, voice
    finally:
        service.stop()
        if service.resource_worker:
            service.resource_worker.join(3)


def feed_pressure(service, times):
    for now in times:
        service.pressure_once(now)
        if service.resource_worker:
            service.resource_worker.join(3)


def test_cpu_pressure_requires_ten_seconds_after_warmup_and_stops_once(pressure_setup):
    service, process, _sample, _active, voice = pressure_setup
    service.start_pressure("gaming", True, False)
    feed_pressure(service, [0, 5, 10, 14.999])
    process.terminate.assert_not_called()
    feed_pressure(service, [15])
    process.terminate.assert_called_once()
    assert service.last_resource["status"] == "completed"
    assert service.pressure["last_action"]
    feed_pressure(service, range(20, 150, 5))
    process.terminate.assert_called_once()
    voice.assert_not_called()


def test_exact_eighty_percent_and_short_spikes_do_not_stop_apps(pressure_setup):
    service, process, sample, _active, _voice = pressure_setup
    service.start_pressure("gaming", True, False)
    sample.update(cpu=80, ram=80)
    feed_pressure(service, [0, 5, 10, 15, 20])
    process.terminate.assert_not_called()
    sample["cpu"] = 81
    feed_pressure(service, [25, 30])
    sample["cpu"] = 79
    feed_pressure(service, [35])
    sample["cpu"] = 81
    feed_pressure(service, [40, 45])
    process.terminate.assert_not_called()
    feed_pressure(service, [50])
    process.terminate.assert_called_once()


def test_ram_pressure_matches_memory_not_unrelated_cpu_load(pressure_setup):
    service, process, sample, _active, _voice = pressure_setup
    service.start_pressure("gaming", True, False)
    sample.update(cpu=10, ram=81)
    sample["candidates"][0].update(memory=128 * 1024 * 1024 - 1, cpu=90)
    feed_pressure(service, [0, 5, 10, 15])
    process.terminate.assert_not_called()
    sample["candidates"][0]["memory"] += 1
    feed_pressure(service, [20])
    process.terminate.assert_called_once()


def test_cpu_pressure_does_not_target_a_memory_only_process(pressure_setup):
    service, process, sample, _active, _voice = pressure_setup
    service.start_pressure("gaming", True, False)
    sample["candidates"][0]["cpu"] = 4.99
    sample["candidates"].append({**sample["candidates"][0], "pid": 88888, "cpu": 70,
                                 "exe": resources.normalized_path(r"C:\Apps\not-approved.exe")})
    feed_pressure(service, [0, 5, 10, 15])
    process.terminate.assert_not_called()
    sample["candidates"][0]["cpu"] = 5
    feed_pressure(service, [20])
    process.terminate.assert_called_once()


def test_foreground_identity_is_rechecked_after_selection(pressure_setup, monkeypatch):
    service, process, _sample, _active, _voice = pressure_setup
    service.start_pressure("gaming", True, False)
    monkeypatch.setattr(resources, "foreground_protection", Mock(side_effect=[
        (set(), set()), ({99999}, {POLICY["apps"][0]}),
    ]))
    feed_pressure(service, [0, 5, 10, 15])
    process.terminate.assert_not_called()
    assert service.last_resource["processes"][0]["status"] == "skipped_foreground_or_permission"


def test_other_instance_of_foreground_application_is_protected(pressure_setup, monkeypatch):
    service, process, _sample, _active, _voice = pressure_setup
    service.start_pressure("gaming", True, False)
    monkeypatch.setattr(resources, "foreground_protection", lambda: ({12345}, {POLICY["apps"][0]}))
    feed_pressure(service, [0, 5, 10, 15, 20])
    process.terminate.assert_not_called()


def test_pressure_cooldown_covers_new_process_identities(pressure_setup):
    service, process, sample, _active, _voice = pressure_setup
    service.start_pressure("gaming", True, False)
    feed_pressure(service, [0, 5, 10, 15])
    process.create_time.return_value = 11
    sample["candidates"][0]["created"] = 11
    feed_pressure(service, range(20, 75, 5))
    assert process.terminate.call_count == 1
    feed_pressure(service, [75])
    assert process.terminate.call_count == 2


@pytest.mark.parametrize("failure", ["foreground", "profile", "policy"])
def test_pressure_failures_disarm_without_termination(pressure_setup, monkeypatch, failure):
    service, process, _sample, active, _voice = pressure_setup
    service.start_pressure("gaming", True, False)
    if failure == "foreground":
        monkeypatch.setattr(resources, "foreground_protection", Mock(side_effect=resources.ResourceError("Desktop locked")))
        feed_pressure(service, [0, 5, 10])
        service.pressure_last_sample = time.monotonic() - 5
        service.pressure_since = time.monotonic() - 10
    elif failure == "profile":
        active[0] = "normal"
    else:
        service.store.set("policies", {})
    SystemCare._pressure_loop(service)
    assert not service.pressure["enabled"] and service.pressure["error"]
    process.terminate.assert_not_called()


def test_stopping_revokes_pending_pressure_guard_and_survives_restart(pressure_setup):
    service, process, _sample, _active, _voice = pressure_setup
    service.start_pressure("gaming", True, False)
    service.stop_pressure()
    feed_pressure(service, [0, 5, 10, 15])
    assert not service._pressure_guard(process)
    process.terminate.assert_not_called()
    assert not SystemCare(Store(service.store.path)).snapshot()["pressure"]["enabled"]


def test_pressure_authorization_and_policy_are_session_scoped(pressure_setup):
    service, _process, _sample, active, _voice = pressure_setup
    for auth in [False, 1, "true"]:
        with pytest.raises(CareError):
            service.start_pressure("gaming", auth, False)
    active[0] = "normal"
    with pytest.raises(CareError, match="Apply this profile"):
        service.start_pressure("gaming", True, False)
    active[0] = "gaming"
    service.start_pressure("gaming", True, False)
    with pytest.raises(CareError, match="Stop CPU/RAM"):
        service.save_policy("gaming", POLICY)


def test_local_speech_only_after_confirmed_termination(pressure_setup):
    service, process, _sample, _active, voice = pressure_setup
    service.start_pressure("gaming", True, True, True)
    voice.assert_called_once_with(True, check_only=True)
    voice.reset_mock()
    feed_pressure(service, [0, 5, 10, 15])
    process.terminate.assert_called_once()
    voice.assert_called_once_with(True)


def test_speech_failure_preserves_termination_result_and_disarms(pressure_setup):
    service, process, _sample, _active, voice = pressure_setup
    service.start_pressure("gaming", True, True)
    voice.side_effect = resources.ResourceError("Local voice failed")
    feed_pressure(service, [0, 5, 10, 15])
    process.terminate.assert_called_once()
    assert service.last_resource["processes"][0]["status"] == "terminated"
    assert service.last_resource["status"] == "error"
    assert not service.pressure["enabled"] and "voice failed" in service.pressure["error"]


def test_pressure_never_applies_power_policy(pressure_setup, monkeypatch):
    service, process, _sample, _active, _voice = pressure_setup
    power = Mock(side_effect=AssertionError("Pressure monitoring must not change power settings"))
    monkeypatch.setattr(resources, "apply_power", power)
    service.start_pressure("gaming", True, False)
    feed_pressure(service, [0, 5, 10, 15])
    process.terminate.assert_called_once()
    power.assert_not_called()


def test_load_sampler_uses_deltas_and_normalizes_all_cpu_cores(setup, monkeypatch):
    _store, process = setup
    monkeypatch.setattr(resources.psutil, "cpu_percent", lambda **_kwargs: 85)
    monkeypatch.setattr(resources.psutil, "cpu_count", lambda: 4)
    process.cpu_times.return_value = SimpleNamespace(user=10, system=2)
    sample, prior = resources.load_sample({}, 0)
    assert sample["candidates"][0]["cpu"] == 0
    process.cpu_times.return_value = SimpleNamespace(user=12, system=2)
    sample, _prior = resources.load_sample(prior, 5)
    assert sample["candidates"][0]["cpu"] == pytest.approx(10)


def test_pressure_execution_rechecks_identity_and_requires_guard(setup):
    store, process = setup
    plan = {**resources.prepare("gaming", POLICY), "pressure": True}
    with pytest.raises(resources.ResourceError, match="require a live"):
        resources.execute(plan, store)
    process.create_time.return_value = 11
    assert resources.execute(plan, store, guard=lambda _process: True)["status"] == "partial"
    process.terminate.assert_not_called()


def test_missing_samples_reset_sustained_pressure_window(pressure_setup):
    service, process, _sample, _active, _voice = pressure_setup
    service.start_pressure("gaming", True, False)
    feed_pressure(service, [0, 5, 10, 30, 35, 40])
    process.terminate.assert_not_called()
    feed_pressure(service, [45])
    process.terminate.assert_called_once()


def test_only_the_largest_approved_cpu_process_is_stopped_per_minute(pressure_setup, monkeypatch):
    service, process, sample, _active, _voice = pressure_setup
    other = Mock(pid=99998)
    for method in ("name", "exe", "username", "create_time", "memory_info"):
        getattr(other, method).return_value = getattr(process, method)()
    original_factory = resources.psutil.Process
    monkeypatch.setattr(resources.psutil, "Process", lambda pid=None: other if pid == 99998 else original_factory(pid))
    monkeypatch.setattr(resources.psutil, "process_iter", lambda: [process, other])
    sample["candidates"].append({**sample["candidates"][0], "pid": 99998, "cpu": 50})
    service.start_pressure("gaming", True, False)
    feed_pressure(service, [0, 5, 10, 15, *range(20, 75, 5)])
    other.terminate.assert_called_once()
    process.terminate.assert_not_called()
    feed_pressure(service, [75])
    process.terminate.assert_called_once()


def test_termination_not_confirmed_does_not_speak_or_force_kill(pressure_setup, monkeypatch):
    service, process, _sample, _active, voice = pressure_setup
    service.start_pressure("gaming", True, True)
    voice.reset_mock()
    monkeypatch.setattr(resources.psutil, "wait_procs", lambda procs, timeout: ([], procs))
    feed_pressure(service, [0, 5, 10, 15])
    assert service.last_resource["processes"][0]["status"] == "still_running"
    assert service.pressure["last_action"] is None
    voice.assert_not_called()
    process.kill.assert_not_called()


@pytest.fixture()
def win_foreground(setup, monkeypatch):
    _store, process = setup
    native = Mock()
    native.OpenInputDesktop.return_value = 42
    native.GetForegroundWindow.return_value = 123
    process.parents.return_value = []
    process.children.return_value = []
    process.is_running.return_value = True

    def desktop_info(_desktop, _index, name, _size, _needed):
        name.value = "Default"
        return True

    def window_pid(_window, pointer):
        resources.ctypes.cast(pointer, resources.ctypes.POINTER(resources.wintypes.DWORD)).contents.value = process.pid
        return 1

    native.GetUserObjectInformationW.side_effect = desktop_info
    native.GetWindowThreadProcessId.side_effect = window_pid
    monkeypatch.setattr(resources.sys, "platform", "win32")
    monkeypatch.setattr(resources.ctypes, "WinDLL", Mock(return_value=native))
    return native, process


def test_native_foreground_guard_protects_siblings_and_ancestors_without_reading_system_exe(win_foreground):
    native, process = win_foreground
    sibling = Mock(pid=22222)
    sibling.exe.return_value = r"C:\Apps\app-renderer.exe"
    parent = Mock(pid=33333)
    parent.exe.return_value = r"C:\Apps\app-host.exe"
    parent.name.return_value = "app-host.exe"
    parent.username.return_value = "user"
    parent.children.return_value = [process, sibling]
    shell = Mock(pid=44444)
    shell.name.return_value = "explorer.exe"
    shell.exe.side_effect = resources.psutil.AccessDenied(shell.pid)
    process.parents.return_value = [parent, shell]
    pids, paths = resources.foreground_protection()
    assert pids == {process.pid, sibling.pid, parent.pid, shell.pid}
    assert paths == {POLICY["apps"][0], resources.normalized_path(sibling.exe()), resources.normalized_path(parent.exe())}
    shell.exe.assert_not_called()
    native.CloseDesktop.assert_called_once_with(42)


@pytest.mark.parametrize("failure", ["locked", "no_window", "changed_window", "access_denied", "empty_exe"])
def test_native_foreground_guard_fails_closed_and_closes_desktop(win_foreground, failure):
    native, process = win_foreground
    if failure == "locked":
        def locked(_desktop, _index, name, _size, _needed):
            name.value = "Winlogon"
            return True
        native.GetUserObjectInformationW.side_effect = locked
    elif failure == "no_window":
        native.GetForegroundWindow.return_value = 0
    elif failure == "changed_window":
        native.GetForegroundWindow.side_effect = [123, 456]
    elif failure == "access_denied":
        process.exe.side_effect = resources.psutil.AccessDenied(process.pid)
    else:
        process.exe.return_value = ""
    with pytest.raises(resources.ResourceError):
        resources.foreground_protection()
    native.CloseDesktop.assert_called_once_with(42)
