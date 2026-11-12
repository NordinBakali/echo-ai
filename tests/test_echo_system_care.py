import socket
import threading
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

import echo_system_care as care


@pytest.fixture()
def monitor(tmp_path):
    return care.SystemCare(care.Store(tmp_path / "care.sqlite3"), notify=Mock())


@pytest.mark.parametrize("address,mask,supported", [
    ("192.168.10.2", "255.255.255.0", True),
    ("10.0.0.2", "255.255.0.0", False),
    ("172.16.0.2", "255.255.255.252", True),
    ("172.16.0.2", "255.255.255.254", False),
])
def test_adapter_scope_bounds(monkeypatch, address, mask, supported):
    monkeypatch.setattr(care.psutil, "net_if_stats", lambda: {"wifi": SimpleNamespace(isup=True)})
    monkeypatch.setattr(care.psutil, "net_if_addrs", lambda: {"wifi": [SimpleNamespace(family=socket.AF_INET, address=address, netmask=mask)]})
    assert care.adapters()[0]["supported"] is supported
    if supported:
        assert care.selected_adapter(address)["address"] == address
    else:
        with pytest.raises(care.CareError):
            care.selected_adapter(address)


@pytest.mark.parametrize("address", ["127.0.0.1", "8.8.8.8", "169.254.1.2", "100.64.1.2", "224.0.0.1"])
def test_nonprivate_addresses_never_offered(monkeypatch, address):
    monkeypatch.setattr(care.psutil, "net_if_stats", lambda: {"wifi": SimpleNamespace(isup=True)})
    monkeypatch.setattr(care.psutil, "net_if_addrs", lambda: {"wifi": [SimpleNamespace(family=socket.AF_INET, address=address, netmask="255.255.255.0")]})
    assert care.adapters() == []


def test_lan_scan_is_bound_and_ignores_stale_unobserved_neighbors(monkeypatch):
    adapter = {"name": "wifi", "address": "192.168.1.1", "network": "192.168.1.0/29", "supported": True}
    monkeypatch.setattr(care, "adapters", lambda: [adapter])
    seen = []

    def ping(host, source, stop):
        seen.append((host, source))
        return host == "192.168.1.2"

    monkeypatch.setattr(care, "ping_host", ping)
    monkeypatch.setattr(care, "neighbors", lambda _: [
        {"ip": "192.168.1.2", "mac": "02-AA-00-00-00-02", "state": "stale"},
        {"ip": "192.168.1.3", "mac": "02-AA-00-00-00-03", "state": "stale"},
        {"ip": "192.168.1.4", "mac": "02-AA-00-00-00-04", "state": "reachable"},
        {"ip": "192.168.2.5", "mac": "02-AA-00-00-00-05", "state": "reachable"},
        {"ip": "192.168.1.6", "mac": "FF-FF-FF-FF-FF-FF", "state": "reachable"},
        {"ip": "192.168.1.5", "mac": "02-AA-00-00-00-05", "state": "permanent"},
    ])
    scope, devices = care.scan_lan("192.168.1.1", threading.Event())
    assert scope == "wifi|192.168.1.0/29"
    assert [p["ip"] for p in devices] == ["192.168.1.2", "192.168.1.4"]
    assert devices[0]["mac"] == "02:aa:00:00:00:02"
    assert len(seen) == 5 and all(source == "192.168.1.1" for _, source in seen)
    with pytest.raises(care.CareError):
        care.scan_lan("192.168.2.1", threading.Event())


def test_ping_binds_selected_source_and_missing_tool_is_explicit(monkeypatch):
    run = Mock(return_value=SimpleNamespace(returncode=0, stdout="Reply: bytes=32 time<1ms TTL=64", stderr=""))
    monkeypatch.setattr(care.subprocess, "run", run)
    monkeypatch.setattr(care.sys, "platform", "win32")
    assert care.ping_host("192.168.1.2", "192.168.1.1", threading.Event())
    assert run.call_args.args[0][-3:] == ["-S", "192.168.1.1", "192.168.1.2"]
    run.return_value.stdout = "Destination host unreachable"
    assert not care.ping_host("192.168.1.2", "192.168.1.1", threading.Event())
    run.return_value.returncode = 2
    with pytest.raises(care.CareError):
        care.ping_host("192.168.1.2", "192.168.1.1", threading.Event())
    run.side_effect = FileNotFoundError("missing ping")
    with pytest.raises(care.CareError):
        care.ping_host("192.168.1.2", "192.168.1.1", threading.Event())


def test_linux_ping_uses_numeric_addresses_and_selected_interface(monkeypatch):
    monkeypatch.setattr(care.sys, "platform", "linux")
    run = Mock(return_value=SimpleNamespace(returncode=0, stdout="64 bytes ttl=64 time=1ms", stderr=""))
    monkeypatch.setattr(care.subprocess, "run", run)
    assert care.ping_host("192.168.1.2", "192.168.1.1", threading.Event())
    assert run.call_args.args[0] == ["ping", "-n", "-c", "1", "-W", "1", "-I", "192.168.1.1", "192.168.1.2"]
    with pytest.raises(care.CareError, match="requires Windows"):
        care.validate_config({**care.DEFAULT_CONFIG, "logs": True, "sound": True})


def test_mac_trust_persists_but_dhcp_reuse_is_unknown(monitor):
    store = monitor.store
    a = {"ip": "192.168.1.2", "mac": "02:00:00:00:00:02"}
    assert store.observe_devices("wifi", [a], 100) == [a]
    assert not store.observe_devices("wifi", [a], 101)
    store.trust("wifi", a["mac"], True)
    assert care.Store(store.path).rows()["devices"][0]["trusted"] == 1
    moved = {**a, "ip": "192.168.1.3"}
    assert not store.observe_devices("wifi", [moved], 102)
    stranger = {**a, "mac": "02:00:00:00:00:09"}
    assert store.observe_devices("wifi", [stranger], 103) == [stranger]
    unverified = {"ip": "192.168.1.5", "mac": ""}
    store.observe_devices("wifi", [unverified], 104)
    with pytest.raises(care.CareError):
        store.trust("wifi", "ip:192.168.1.5", True)
    store.trust("wifi", a["mac"], False)
    assert store.observe_devices("wifi", [moved], 105) == [moved]


def test_alerts_are_bounded_deduplicated_and_local(monitor):
    for i in range(220):
        monitor.emit(str(i), "system_error", "A local summary")
    monitor.emit("219", "system_error", "Duplicate")
    with monitor.store.connection() as db:
        assert db.execute("SELECT COUNT(*) FROM alerts").fetchone()[0] == 200
    assert monitor.notify.call_count == 220
    assert monitor.store.rows()["alerts"][0]["profile"] == "security"
    monitor.stop()
    monitor.emit("late", "system_error", "No late alert")
    assert monitor.notify.call_count == 220


def test_windows_logs_checkpoint_permission_error_and_restart(monitor, monkeypatch):
    monkeypatch.setattr(care.sys, "platform", "win32")
    event = {"id": 4625, "record": 42, "provider": "Security", "time": "2026-01-01T10:00:00Z"}
    calls = []

    def read(channel, cursor):
        calls.append((channel, cursor))
        if channel == "Application":
            return {"error": "Access denied"}
        return {"events": [event], "cursor": 42, "reset": False, "backlog": False}

    monkeypatch.setattr(care, "windows_events", read)
    monitor.logs_once()
    assert monitor.errors == {"Application": "Access denied"}
    assert monitor.store.get("log:System", 0) == 42
    assert monitor.store.get("log:Application", 0) == 0
    monitor.logs_once()
    assert len(monitor.store.rows()["alerts"]) == 2
    assert ("System", 42) in calls
    replacement = care.SystemCare(care.Store(monitor.store.path))
    assert not replacement.snapshot()["running"] and not replacement.automatic
    assert replacement.store.get("log:System", 0) == 42


def test_stop_during_log_read_cannot_emit_or_advance(monitor, monkeypatch):
    monkeypatch.setattr(care.sys, "platform", "win32")

    def read(*_):
        monitor.stop()
        return {"events": [{"id": 1, "record": 3, "provider": "test", "time": "now"}], "cursor": 3}

    monkeypatch.setattr(care, "windows_events", read)
    monitor.logs_once()
    assert not monitor.store.rows()["alerts"]
    assert monitor.store.get("log:System", 0) == 0


def test_syslog_incremental_rotation_truncation_and_no_raw_persistence(tmp_path):
    path = tmp_path / "auth.log"
    path.write_bytes(b"info: hello\nFailed password for PRIVATE_USER\npartial")
    first = care.syslog_events(path, {})
    assert first["events"][0]["kind"] == "failed_login"
    assert "PRIVATE_USER" not in str(first)
    assert care.syslog_events(path, first["cursor"])["events"] == []
    with path.open("ab") as stream:
        stream.write(b" error\n")
    second = care.syslog_events(path, first["cursor"])
    assert second["events"][0]["kind"] == "system_error"
    path.write_bytes(b"segfault\n")
    third = care.syslog_events(path, second["cursor"])
    assert third["reset"] and third["events"][0]["kind"] == "crash"
    path.rename(tmp_path / "old.log")
    path.write_bytes(b"authentication failure\n")
    assert care.syslog_events(path, third["cursor"])["reset"]


def test_syslog_copytruncate_regrowth_has_new_identity(tmp_path):
    path = tmp_path / "syslog"
    path.write_bytes(b"error first\n")
    first = care.syslog_events(path, {})
    path.write_bytes(b"error another event after copytruncate\nerror first\n")
    second = care.syslog_events(path, first["cursor"])
    assert second["reset"] and len(second["events"]) == 2
    assert second["events"][0]["key"] != first["events"][0]["key"]


def test_scheduler_start_stop_and_failures_are_visible(monitor, monkeypatch):
    ran = threading.Event()

    def failure():
        ran.set()
        raise care.CareError("Readable error")

    monkeypatch.setattr(monitor, "logs_once", failure)
    monitor.start({**care.DEFAULT_CONFIG, "logs": True})
    assert ran.wait(2)
    monitor.stop()
    assert not monitor.snapshot()["running"]
    assert monitor.errors["logs"] == "Readable error"
    assert monitor.store.get("monitor_config", {})["logs"]


@pytest.mark.parametrize("update", [{"network_interval": 0}, {"log_interval": 1}, {"logs": "true"}, {"alert_profile": "other"}])
def test_invalid_monitor_settings(update):
    with pytest.raises(care.CareError):
        care.validate_config({**care.DEFAULT_CONFIG, "logs": True, **update})
