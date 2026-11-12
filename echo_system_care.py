"""Opt-in LAN discovery, local log analysis and guarded resource jobs."""

import hashlib
import ipaddress
import json
import logging
import os
import re
import secrets
import socket
import sqlite3
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from contextlib import closing
from pathlib import Path

import psutil

import echo_resources as resources


LOGGER = logging.getLogger(__name__)
DATA_DIR = Path(os.environ.get("LOCALAPPDATA", str(Path.home() / ".local" / "share"))) / "Echo" / "system-care"
PRIVATE_RANGES = tuple(ipaddress.ip_network(value) for value in ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"))
MAC = re.compile(r"(?:[0-9a-f]{2}:){5}[0-9a-f]{2}")
SYSLOG_PATHS = ("/var/log/syslog", "/var/log/messages", "/var/log/auth.log", "/var/log/secure")
CHANNELS = ("System", "Application", "Security")
DEFAULT_CONFIG = {
    "network": False, "logs": False, "address": "", "network_interval": 300,
    "log_interval": 60, "alert_profile": "security", "sound": False, "desktop": False,
}


class CareError(Exception):
    pass


class Store:
    def __init__(self, path: Path):
        self.path = path

    @contextmanager
    def connection(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(self.path, timeout=10)) as db, db:
            db.row_factory = sqlite3.Row
            db.executescript("""
                CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS devices (
                    scope TEXT, identity TEXT, ip TEXT, mac TEXT, trusted INTEGER DEFAULT 0,
                    last_seen REAL, last_alert REAL DEFAULT 0, present INTEGER DEFAULT 1,
                    PRIMARY KEY(scope, identity));
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, event_key TEXT UNIQUE,
                    kind TEXT, profile TEXT, summary TEXT, created REAL);
            """)
            yield db

    def get(self, key: str, default):
        with self.connection() as db:
            row = db.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return json.loads(row["value"]) if row else default

    def set(self, key: str, value) -> None:
        with self.connection() as db:
            db.execute("INSERT OR REPLACE INTO settings VALUES (?,?)", (key, json.dumps(value)))

    def alert(self, key: str, kind: str, profile: str, summary: str) -> bool:
        with self.connection() as db:
            result = db.execute(
                "INSERT OR IGNORE INTO alerts(event_key,kind,profile,summary,created) VALUES(?,?,?,?,?)",
                (key, kind, profile, summary[:600], time.time()),
            )
            db.execute("DELETE FROM alerts WHERE id NOT IN (SELECT id FROM alerts ORDER BY id DESC LIMIT 200)")
            return result.rowcount == 1

    def rows(self) -> dict:
        with self.connection() as db:
            return {
                "devices": [dict(row) for row in db.execute("SELECT * FROM devices ORDER BY last_seen DESC LIMIT 1000")],
                "alerts": [dict(row) for row in db.execute("SELECT * FROM alerts ORDER BY id DESC LIMIT 100")],
            }

    def trust(self, scope: str, identity: str, trusted: bool) -> None:
        if type(trusted) is not bool:
            raise CareError("Trust must be a boolean.")
        with self.connection() as db:
            row = db.execute("SELECT mac FROM devices WHERE scope=? AND identity=?", (scope, identity)).fetchone()
            if not row or not MAC.fullmatch(row["mac"] or ""):
                raise CareError("Only a discovered device with a MAC address can be trusted. IP-only identity is unsafe with DHCP.")
            db.execute("UPDATE devices SET trusted=?,last_alert=0 WHERE scope=? AND identity=?", (int(trusted), scope, identity))

    def observe_devices(self, scope: str, devices: list[dict], now: float) -> list[dict]:
        unknown = []
        with self.connection() as db:
            db.execute("UPDATE devices SET present=0 WHERE scope=?", (scope,))
            for device in devices:
                identity = device["mac"] or "ip:" + device["ip"]
                row = db.execute("SELECT * FROM devices WHERE scope=? AND identity=?", (scope, identity)).fetchone()
                trusted = bool(row and row["trusted"])
                last_alert = row["last_alert"] if row else 0
                should_alert = not trusted and (last_alert == 0 or now - last_alert >= 86400)
                db.execute("""
                    INSERT INTO devices(scope,identity,ip,mac,trusted,last_seen,last_alert,present)
                    VALUES(?,?,?,?,?,?,?,1)
                    ON CONFLICT(scope,identity) DO UPDATE SET ip=excluded.ip,mac=excluded.mac,
                    last_seen=excluded.last_seen,last_alert=excluded.last_alert,present=1
                """, (scope, identity, device["ip"], device["mac"], int(trusted), now, now if should_alert else last_alert))
                if should_alert:
                    unknown.append(device)
            db.execute("DELETE FROM devices WHERE trusted=0 AND last_seen<?", (now - 30 * 86400,))
        return unknown


def adapters() -> list[dict]:
    result = []
    stats = psutil.net_if_stats()
    for name, addresses in psutil.net_if_addrs().items():
        if name not in stats or not stats[name].isup:
            continue
        for item in addresses:
            if item.family != socket.AF_INET or not item.netmask:
                continue
            address = ipaddress.ip_address(item.address)
            network = ipaddress.ip_network(f"{address}/{item.netmask}", strict=False)
            if not any(address in private and network.subnet_of(private) for private in PRIVATE_RANGES):
                continue
            result.append({"name": name, "address": str(address), "network": str(network),
                           "supported": 4 <= network.num_addresses <= 256})
    return result


def selected_adapter(address: str) -> dict:
    match = next((item for item in adapters() if item["address"] == address), None)
    if not match or not match["supported"]:
        raise CareError("Choose an active private IPv4 LAN adapter with a subnet of /24 to /30. Larger networks are not silently partially scanned.")
    return match


def ping_host(address: str, source: str, stop: threading.Event) -> bool:
    if stop.is_set():
        return False
    args = ["ping.exe", "-n", "1", "-w", "350", "-S", source, address] if sys.platform == "win32" else [
        "ping", "-n", "-c", "1", "-W", "1", "-I", source, address,
    ]
    try:
        result = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=2,
                                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
        if result.returncode == 2:
            raise CareError(f"ICMP discovery failed: {result.stderr.strip()[:200]}")
        return result.returncode == 0 and bool(re.search(r"\bttl[=\s]\d+", result.stdout, re.I))
    except subprocess.TimeoutExpired:
        return False
    except OSError as exc:
        raise CareError(f"ICMP discovery could not start: {exc}") from exc


def powershell_json(script: str):
    prefix = "[Console]::OutputEncoding=[System.Text.UTF8Encoding]::new(); $ErrorActionPreference='Stop'; "
    output = resources.command(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", prefix + script], timeout=25)
    try:
        return json.loads(output.lstrip("\ufeff"))
    except json.JSONDecodeError as exc:
        raise CareError("Windows returned invalid monitoring data.") from exc


def neighbors(adapter: dict) -> list[dict]:
    if sys.platform == "win32":
        address = str(ipaddress.IPv4Address(adapter["address"]))
        data = powershell_json(
            f"$iface=Get-NetIPAddress -IPAddress '{address}' -AddressFamily IPv4 | Select-Object -First 1; "
            "if (-not $iface) { throw 'LAN adapter disappeared' }; "
            "$rows=@(Get-NetNeighbor -InterfaceIndex $iface.InterfaceIndex -AddressFamily IPv4 | "
            "Select-Object IPAddress,LinkLayerAddress,@{n='State';e={$_.State.ToString()}}); "
            "ConvertTo-Json -InputObject $rows -Compress"
        )
        return [{"ip": row["IPAddress"], "mac": row["LinkLayerAddress"], "state": row["State"].lower()} for row in data]
    output = resources.command(["ip", "-j", "neigh", "show", "dev", adapter["name"]])
    return [{"ip": row["dst"], "mac": row.get("lladdr", ""), "state": " ".join(row.get("state", [])).lower()}
            for row in json.loads(output)]


def scan_lan(address: str, stop: threading.Event) -> tuple[str, list[dict]]:
    adapter = selected_adapter(address)
    network = ipaddress.ip_network(adapter["network"])
    hosts = [str(host) for host in network.hosts() if str(host) != address]
    with ThreadPoolExecutor(max_workers=16, thread_name_prefix="echo-lan") as pool:
        outcomes = list(pool.map(lambda host: ping_host(host, address, stop), hosts))
    if stop.is_set():
        return adapter["network"], []
    reachable = {host for host, alive in zip(hosts, outcomes) if alive}
    found = {host: {"ip": host, "mac": ""} for host in reachable}
    for row in neighbors(adapter):
        try:
            ip = ipaddress.IPv4Address(row["ip"])
        except ipaddress.AddressValueError:
            continue
        mac = str(row["mac"]).lower().replace("-", ":")
        if (
            ip not in network or str(ip) == address or ip in (network.network_address, network.broadcast_address)
            or not MAC.fullmatch(mac) or mac in {"00:00:00:00:00:00", "ff:ff:ff:ff:ff:ff"}
            or int(mac[:2], 16) & 1
        ):
            continue
        if str(ip) in reachable or row["state"] == "reachable":
            found[str(ip)] = {"ip": str(ip), "mac": mac}
    scope = adapter["name"] + "|" + adapter["network"]
    return scope, sorted(found.values(), key=lambda item: int(ipaddress.IPv4Address(item["ip"])))


def windows_events(channel: str, cursor: int) -> dict:
    if channel not in CHANNELS or type(cursor) is not int or cursor < 0:
        raise CareError("Invalid event-log cursor.")
    predicate = "(EventID=4625 or EventID=4740 or EventID=1102)" if channel == "Security" else "(Level=1 or Level=2 or Level=3)"
    script = (
        f"$channel='{channel}'; $cursor={cursor}; "
        "try { "
        "$latest=Get-WinEvent -LogName $channel -MaxEvents 1; "
        "$reset=$cursor -gt $latest.RecordId; if ($reset) {$cursor=0}; "
        f"$condition='{predicate}'; "
        "if ($cursor -gt 0) {$query=\"*[System[EventRecordID > $cursor and $condition]]\"} "
        "else {$query=\"*[System[TimeCreated[timediff(@SystemTime) <= 900000] and $condition]]\"}; "
        "$events=@(); try {$events=@(Get-WinEvent -LogName $channel -FilterXPath $query -Oldest -MaxEvents 200)} "
        "catch {if ($_.FullyQualifiedErrorId -notlike 'NoMatchingEventsFound*') {throw}}; "
        "$rows=@($events | ForEach-Object { @{id=$_.Id;record=$_.RecordId;provider=$_.ProviderName;time=$_.TimeCreated.ToUniversalTime().ToString('o')} }); "
        "$next=if($events.Count -eq 200){$events[-1].RecordId}else{$latest.RecordId}; "
        "@{events=$rows;cursor=$next;reset=$reset;backlog=($events.Count -eq 200);error=''} | ConvertTo-Json -Depth 4 -Compress "
        "} catch { "
        "if ($_.FullyQualifiedErrorId -like 'NoMatchingEventsFound*') "
        "{@{events=@();cursor=$cursor;reset=$false;backlog=$false;error=''} | ConvertTo-Json -Compress} "
        "else {@{error=$_.Exception.Message} | ConvertTo-Json -Compress} }"
    )
    return powershell_json(script)


def classify_line(line: str) -> str:
    if re.search(r"failed password|authentication failure|invalid user|failed login", line, re.I):
        return "failed_login"
    if re.search(r"segfault|core dumped|kernel panic|oom-kill|out of memory", line, re.I):
        return "crash"
    if re.search(r"\b(error|fatal|critical)\b", line, re.I):
        return "system_error"
    return ""


def syslog_events(path: Path, cursor: dict) -> dict:
    with path.open("rb") as stream:
        stat = os.fstat(stream.fileno())
        offset = cursor.get("offset", max(0, stat.st_size - 65536))
        reset = cursor.get("inode", stat.st_ino) != stat.st_ino or offset > stat.st_size
        if not reset and cursor.get("anchor"):
            stream.seek(max(0, offset - 64))
            reset = hashlib.sha256(stream.read(min(64, offset))).hexdigest() != cursor["anchor"]
        generation = cursor.get("generation", 0) + int(reset)
        if reset:
            offset = 0
        stream.seek(offset)
        if not cursor and offset:
            stream.readline(65536)
            offset = stream.tell()
        data = stream.read(65536)
        complete = data.rfind(b"\n") + 1
        if complete == 0 and len(data) == 65536:
            complete = len(data)
        end = offset + complete
        stream.seek(max(0, end - 64))
        anchor = hashlib.sha256(stream.read(min(64, end))).hexdigest()
    warning = ""
    if b"\n" not in data and len(data) == 65536:
        warning = "A log line exceeded 64 KB and was skipped."
        lines = []
    else:
        lines = data[:complete].splitlines(keepends=True)
    events = []
    position = offset
    for line in lines:
        kind = classify_line(line.decode("utf-8", errors="replace"))
        if kind:
            key = hashlib.sha256(f"{path}:{stat.st_ino}:{generation}:{position}:".encode() + line).hexdigest()
            events.append({"key": key, "kind": kind, "summary": f"{path.name}: {kind}; byte offset {position}"})
        position += len(line)
    return {"events": events, "cursor": {"inode": stat.st_ino, "offset": offset + complete,
                                       "generation": generation, "anchor": anchor},
            "backlog": offset + complete < stat.st_size, "warning": warning, "reset": reset}


def validate_config(data: object) -> dict:
    if not isinstance(data, dict) or set(data) != set(DEFAULT_CONFIG):
        raise CareError("Invalid monitoring settings.")
    if any(type(data[key]) is not bool for key in ("network", "logs", "sound", "desktop")):
        raise CareError("Monitoring switches must be booleans.")
    if (
        type(data["network_interval"]) is not int or not 60 <= data["network_interval"] <= 3600
        or type(data["log_interval"]) is not int or not 15 <= data["log_interval"] <= 600
        or data["alert_profile"] not in resources.PROFILES or not isinstance(data["address"], str)
        or not (data["network"] or data["logs"])
    ):
        raise CareError("Choose a monitoring source, valid intervals and an alert profile.")
    if data["network"]:
        selected_adapter(data["address"])
    if data["sound"] and sys.platform != "win32":
        raise CareError("Local sound requires Windows. Use browser notifications on this platform.")
    return dict(data)


class SystemCare:
    def __init__(self, store: Store, notify=None, profile_provider=None):
        self.store = store
        self.notify = notify
        self.lock = threading.RLock()
        self.stop_event = threading.Event()
        self.worker: threading.Thread | None = None
        self.resource_worker: threading.Thread | None = None
        self.automatic = False
        self.config = dict(DEFAULT_CONFIG)
        self.errors: dict[str, str] = {}
        self.last_network = None
        self.last_logs = None
        self.last_resource: dict = {"status": "idle"}
        self.previews: dict[str, dict] = {}
        self.last_sound = 0.0
        self.profile_provider = profile_provider or (lambda: "normal")
        self.pressure_stop = threading.Event()
        self.pressure_worker: threading.Thread | None = None
        self.pressure = {"enabled": False, "profile": "", "speech": False, "cpu": None, "ram": None,
                         "error": "", "last_action": None, "inaccessible": 0}
        self.pressure_since: float | None = None
        self.pressure_previous: dict = {}
        self.pressure_last_sample: float | None = None
        self.pressure_next_action = 0.0
        self.pressure_attempted: set[tuple[int, float]] = set()
        self.pressure_policy: dict = {}
        self.pressure_dutch = False

    def snapshot(self) -> dict:
        with self.lock:
            return {
                **self.store.rows(), "config": self.store.get("monitor_config", DEFAULT_CONFIG),
                "running": bool(self.worker and self.worker.is_alive()), "stopping": self.stop_event.is_set(),
                "errors": dict(self.errors), "last_network": self.last_network, "last_logs": self.last_logs,
                "automatic_resources": self.automatic, "resource": dict(self.last_resource),
                "policies": self.store.get("policies", {}), "can_restore_power": self.store.get("power_recovery", None) is not None,
                "pressure": {**self.pressure, "active_profile": self.profile_provider(),
                             "running": bool(self.pressure_worker and self.pressure_worker.is_alive()),
                             "holding_seconds": max(0, time.monotonic() - self.pressure_since) if self.pressure_since is not None else 0},
            }

    def emit(self, key: str, kind: str, summary: str) -> None:
        with self.lock:
            if self.stop_event.is_set():
                return
            profile = self.config["alert_profile"]
            if self.store.alert(key, kind, profile, summary) and self.notify:
                sound = self.config["sound"] and time.monotonic() - self.last_sound >= 30
                if sound:
                    self.last_sound = time.monotonic()
                self.notify(profile, kind, summary, sound)

    def network_once(self) -> None:
        scope, devices = scan_lan(self.config["address"], self.stop_event)
        if self.stop_event.is_set():
            return
        now = time.time()
        unknown = self.store.observe_devices(scope, devices, now)
        if unknown:
            self.emit(f"lan:{scope}:{now}", "unknown_device", f"{len(unknown)} unknown LAN device(s): " + ", ".join(item["ip"] for item in unknown[:12]))
        with self.lock:
            self.last_network = now
            self.errors.pop("network", None)

    def logs_once(self) -> None:
        sources = list(CHANNELS) if sys.platform == "win32" else [p for p in SYSLOG_PATHS if Path(p).exists()]
        if not sources:
            raise CareError("No readable syslog files were found. This reader supports syslog/auth.log/messages/secure, not a journal-only installation.")
        for source in sources:
            if self.stop_event.is_set():
                return
            key = "log:" + source
            try:
                if sys.platform == "win32":
                    result = windows_events(source, self.store.get(key, 0))
                    if not isinstance(result, dict):
                        raise CareError("Invalid Windows event-log response.")
                    if result.get("error"):
                        raise CareError(result["error"])
                    if not isinstance(result.get("events"), list) or type(result.get("cursor")) is not int:
                        raise CareError("Invalid Windows event-log records or cursor.")
                    for event in result["events"]:
                        if (
                            not isinstance(event, dict) or type(event.get("id")) is not int
                            or type(event.get("record")) is not int or not isinstance(event.get("time"), str)
                            or not isinstance(event.get("provider"), str)
                        ):
                            raise CareError("Invalid Windows event-log record.")
                        event_key = f"windows:{source}:{event['record']}:{event['time']}"
                        kind = "failed_login" if event["id"] in (4625, 4740) else "log_cleared" if event["id"] == 1102 else "system_error"
                        self.emit(event_key, kind, f"{source}: {event['provider'][:100]} / event {event['id']} / {event['time']}")
                else:
                    result = syslog_events(Path(source), self.store.get(key, {}))
                    for event in result["events"]:
                        self.emit(event["key"], event["kind"], event["summary"])
                if self.stop_event.is_set():
                    return
                self.store.set(key, result["cursor"])
                notes = []
                if result.get("backlog"):
                    notes.append("Backlog remains; the next poll continues reading.")
                if result.get("reset"):
                    notes.append("The log was cleared or rotated; the cursor was reset.")
                if result.get("warning"):
                    notes.append(result["warning"])
                with self.lock:
                    if notes:
                        self.errors[source] = " ".join(notes)
                    else:
                        self.errors.pop(source, None)
            except (CareError, resources.ResourceError, OSError, ValueError) as exc:
                LOGGER.warning("Log source unavailable: %s: %s", source, exc)
                with self.lock:
                    self.errors[source] = str(exc)[:400]
        with self.lock:
            self.last_logs = time.time()

    def start(self, config: dict) -> None:
        config = validate_config(config)
        with self.lock:
            if self.worker and self.worker.is_alive():
                raise CareError("Monitoring is already running. Stop before changing settings.")
            self.store.set("monitor_config", config)
            self.config = config
            self.errors.clear()
            self.stop_event.clear()
            self.worker = threading.Thread(target=self._run, name="echo-system-care", daemon=True)
            self.worker.start()

    def stop(self) -> None:
        self.stop_pressure()
        with self.lock:
            self.stop_event.set()
        if self.worker:
            self.worker.join(timeout=3)

    def _run(self) -> None:
        next_network = next_logs = 0.0
        while not self.stop_event.is_set():
            now = time.monotonic()
            for name, enabled, due, function in (
                ("network", self.config["network"], next_network, self.network_once),
                ("logs", self.config["logs"], next_logs, self.logs_once),
            ):
                if enabled and now >= due and not self.stop_event.is_set():
                    try:
                        function()
                    except (CareError, resources.ResourceError, OSError, sqlite3.Error, ValueError) as exc:
                        LOGGER.exception("System monitoring failed: %s", name)
                        with self.lock:
                            self.errors[name] = str(exc)[:400]
                    if name == "network":
                        next_network = time.monotonic() + self.config["network_interval"]
                    else:
                        next_logs = time.monotonic() + self.config["log_interval"]
            self.stop_event.wait(1)

    def save_policy(self, profile: str, policy: dict) -> None:
        if profile not in resources.PROFILES:
            raise CareError("Unknown profile.")
        with self.lock:
            if self.pressure["enabled"] and profile == self.pressure["profile"]:
                raise CareError("Stop CPU/RAM protection before changing its approved policy.")
            if self.resource_worker and self.resource_worker.is_alive():
                raise CareError("Wait for the current hardware job before changing policy.")
            policies = self.store.get("policies", {})
            policies[profile] = resources.validate_policy(policy, policies.get(profile, {}))
            self.store.set("policies", policies)
            self.previews.clear()

    def preview(self, profile: str) -> dict:
        policy = self.store.get("policies", {}).get(profile)
        if policy is None:
            raise CareError("Save a hardware policy for this profile first.")
        plan = resources.prepare(profile, policy)
        with self.lock:
            self.previews = {key: value for key, value in self.previews.items() if time.time() - value["created"] <= 30}
            if len(self.previews) >= 10:
                raise CareError("Too many pending previews. Wait 30 seconds.")
            token = secrets.token_urlsafe(24)
            self.previews[token] = plan
        return {"token": token, **plan}

    def execute_preview(self, token: str) -> None:
        with self.lock:
            if self.resource_worker and self.resource_worker.is_alive():
                raise CareError("A hardware job is already running.")
            plan = self.previews.pop(token, None)
            if plan is None or time.time() - plan["created"] > 30:
                raise CareError("Preview missing or expired. Preview again.")
            self._launch_resource_job(plan)

    def _launch_resource_job(self, plan: dict) -> None:
        if self.resource_worker and self.resource_worker.is_alive():
            raise CareError("A hardware job is already running.")
        self.last_resource = {"status": "running", "profile": plan["profile"]}
        self.resource_worker = threading.Thread(target=self._resource_job, args=(plan,), name="echo-resource-profile", daemon=True)
        self.resource_worker.start()

    def _resource_job(self, plan: dict) -> None:
        result: dict = {}
        try:
            if plan.get("pressure"):
                with self.lock:
                    result = resources.execute(plan, self.store, guard=self._pressure_guard)
                    terminated = any(item["status"] == "terminated" for item in result["processes"])
                    if terminated:
                        self.pressure["last_action"] = time.time()
                    notify = self.pressure["enabled"] and not self.pressure_stop.is_set() and terminated
                    speech = notify and self.pressure["speech"]
                if notify:
                    if self.notify:
                        self.notify(plan["profile"], "resource_pressure", "Approved background app stopped after sustained high load.", False)
                    if speech:
                        resources.local_pressure_speech(self.pressure_dutch)
            else:
                result = resources.execute(plan, self.store)
        except (resources.ResourceError, psutil.Error, OSError, sqlite3.Error, ValueError) as exc:
            LOGGER.exception("Hardware profile failed")
            result = {**result, "status": "error", "error": str(exc)[:500]}
            if plan.get("pressure"):
                with self.lock:
                    self._pressure_failed(exc)
        with self.lock:
            self.last_resource = {**result, "profile": plan["profile"]}

    def start_pressure(self, profile: str, authorized: bool, speech: bool, dutch: bool = False) -> None:
        if authorized is not True or type(speech) is not bool or not isinstance(profile, str) or profile not in resources.PROFILES:
            raise CareError("Choose a profile and explicitly authorize automatic background-app termination.")
        with self.lock:
            if self.pressure["enabled"] or (self.pressure_worker and self.pressure_worker.is_alive()):
                raise CareError("CPU/RAM protection is already running or stopping.")
            if self.resource_worker and self.resource_worker.is_alive():
                raise CareError("Wait for the current hardware job.")
            policy = self.store.get("policies", {}).get(profile)
            if not policy or not policy.get("apps"):
                raise CareError("Save a profile policy with approved background applications first.")
            if self.profile_provider() != profile:
                raise CareError("Apply this profile in the Echo dashboard before enabling CPU/RAM protection.")
            resources.foreground_protection()
            if speech:
                resources.local_pressure_speech(dutch, check_only=True)
            psutil.cpu_percent(interval=None)
            self.pressure = {"enabled": True, "profile": profile, "speech": speech, "cpu": None, "ram": None,
                             "error": "", "last_action": None, "inaccessible": 0}
            self.pressure_policy = policy
            self.pressure_dutch = dutch
            self.pressure_previous = {}
            self.pressure_last_sample = self.pressure_since = None
            self.pressure_next_action = 0
            self.pressure_attempted.clear()
            self.pressure_stop.clear()
            self.pressure_worker = threading.Thread(target=self._pressure_loop, name="echo-resource-watch", daemon=True)
            self.pressure_worker.start()

    def stop_pressure(self) -> None:
        with self.lock:
            self.pressure["enabled"] = False
            self.pressure_stop.set()
            self.pressure_since = None
        if self.pressure_worker and self.pressure_worker is not threading.current_thread():
            self.pressure_worker.join(timeout=3)

    def _pressure_failed(self, error: Exception) -> None:
        self.pressure.update(enabled=False, error=str(error)[:500])
        self.pressure_stop.set()
        self.pressure_since = None

    def _pressure_guard(self, process) -> bool:
        with self.lock:
            if (
                not self.pressure["enabled"] or self.pressure_stop.is_set()
                or self.profile_provider() != self.pressure["profile"]
                or self.store.get("policies", {}).get(self.pressure["profile"]) != self.pressure_policy
            ):
                return False
            pids, paths = resources.foreground_protection()
            return process.pid not in pids and resources.normalized_path(process.exe()) not in paths

    def pressure_once(self, now: float) -> None:
        with self.lock:
            if not self.pressure["enabled"] or self.pressure_stop.is_set():
                return
            profile = self.pressure["profile"]
            if self.profile_provider() != profile:
                raise CareError("Active profile changed. CPU/RAM protection is disabled; enable it again explicitly.")
            if self.store.get("policies", {}).get(profile) != self.pressure_policy:
                raise CareError("The approved policy changed. Enable CPU/RAM protection again.")
            sample, previous = resources.load_sample(self.pressure_previous, now)
            self.pressure_previous = previous
            self.pressure.update(cpu=sample["cpu"], ram=sample["ram"], inaccessible=sample["inaccessible"])
            if self.pressure_last_sample is None or now - self.pressure_last_sample > 10:
                self.pressure_since = None
                self.pressure_last_sample = now
                return
            self.pressure_last_sample = now
            if sample["cpu"] <= 80 and sample["ram"] <= 80:
                self.pressure_since = None
                return
            if self.pressure_since is None:
                self.pressure_since = now
            if now - self.pressure_since < 10 or now < self.pressure_next_action:
                return
            if self.resource_worker and self.resource_worker.is_alive():
                return
            pids, paths = resources.foreground_protection()
            candidates = [item for item in sample["candidates"]
                          if item["exe"] in self.pressure_policy["apps"]
                          and (item["pid"], item["created"]) not in self.pressure_attempted
                          and item["pid"] not in pids and item["exe"] not in paths
                          and ((sample["cpu"] > 80 and item["cpu"] >= 5)
                               or (sample["ram"] > 80 and item["memory"] >= 128 * 1024 * 1024))]
            if not candidates:
                return
            candidate = max(candidates, key=lambda item: (
                item["cpu"] if sample["cpu"] > 80 else 0, item["memory"] if sample["ram"] > 80 else 0,
            ))
            plan = resources.prepare(profile, self.pressure_policy)
            plan["processes"] = [item for item in plan["processes"]
                                 if (item["pid"], item["created"], item["exe"]) == (candidate["pid"], candidate["created"], candidate["exe"])]
            if not plan["processes"]:
                return
            plan["pressure"] = True
            self.pressure_attempted.add((candidate["pid"], candidate["created"]))
            self.pressure_next_action = now + 60
            self._launch_resource_job(plan)

    def _pressure_loop(self) -> None:
        while not self.pressure_stop.is_set():
            try:
                self.pressure_once(time.monotonic())
            except (CareError, resources.ResourceError, psutil.Error, OSError, sqlite3.Error, ValueError) as exc:
                LOGGER.exception("CPU/RAM protection stopped")
                with self.lock:
                    self._pressure_failed(exc)
            self.pressure_stop.wait(5)

    def profile_changed(self, profile: str, authorized: bool) -> str:
        if not authorized or not self.automatic:
            return "manual_confirmation_required"
        if profile not in self.store.get("policies", {}):
            return "no_policy"
        preview = self.preview(profile)
        self.execute_preview(preview["token"])
        return "running"

    def restore(self) -> None:
        with self.lock:
            if self.resource_worker and self.resource_worker.is_alive():
                raise CareError("Wait for the hardware job to finish before restoring power settings.")
            resources.restore_power(self.store)
