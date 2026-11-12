"""Breach and footprint checks for identifiers you own (Have I Been Pwned + public profile lookups)."""

import base64
import ctypes
import html
import json
import logging
import os
import re
import secrets
import sqlite3
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing, contextmanager
from pathlib import Path
from urllib.parse import quote

import requests


LOGGER = logging.getLogger(__name__)
DATA_DIR = Path(os.environ.get("LOCALAPPDATA", str(Path.home() / ".local" / "share"))) / "Echo" / "osint"
HIBP_BASE = "https://haveibeenpwned.com/api/v3"
PWNED_RANGE = "https://api.pwnedpasswords.com/range/"
DOMAIN_DASHBOARD = "https://haveibeenpwned.com/Dashboard/Redirect/Domains"
API_KEY_PAGE = "https://haveibeenpwned.com/API/Key"
USER_AGENT = "Echo-AI-local-breach-check/1.0"
KINDS = ("email", "username", "domain")
MAX_IDENTIFIERS, MIN_HOURS, MAX_HOURS = 20, 6, 168
KEY_RE = re.compile(r"[0-9a-fA-F]{32}")
EMAIL_RE = re.compile(r"[^@\s\"<>()\[\],;:\\/]{1,64}@(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}")
DOMAIN_RE = re.compile(r"(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z][a-z0-9-]{0,61}[a-z0-9]")
USERNAME_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,38}")
DPAPI_ENTROPY = b"Echo OSINT HIBP key v1"
SITES = (
    ("GitHub", "https://api.github.com/users/{u}", "https://github.com/{u}", "status"),
    ("GitLab", "https://gitlab.com/api/v4/users?username={u}", "https://gitlab.com/{u}", "json_list"),
    ("Docker Hub", "https://hub.docker.com/v2/users/{u}/", "https://hub.docker.com/u/{u}", "status"),
    ("PyPI", "https://pypi.org/user/{u}/", "https://pypi.org/user/{u}/", "status"),
    ("Keybase", "https://keybase.io/_/api/1.0/user/lookup.json?usernames={u}", "https://keybase.io/{u}", "keybase"),
    ("DEV", "https://dev.to/api/users/by_username?url={u}", "https://dev.to/{u}", "status"),
    ("Chess.com", "https://api.chess.com/pub/player/{u}", "https://www.chess.com/member/{u}", "status"),
    ("Lichess", "https://lichess.org/api/user/{u}", "https://lichess.org/@/{u}", "status"),
    ("Reddit", "https://www.reddit.com/user/{u}/about.json", "https://www.reddit.com/user/{u}", "status"),
    ("Hacker News", "https://hacker-news.firebaseio.com/v0/user/{u}.json", "https://news.ycombinator.com/user?id={u}", "json_null"),
)


class OsintError(Exception):
    pass


class _Blob(ctypes.Structure):
    _fields_ = [("cbData", ctypes.c_uint32), ("pbData", ctypes.POINTER(ctypes.c_char))]


def _dpapi(data: bytes, *, protect: bool) -> bytes:
    if os.name != "nt":
        raise OsintError("Encrypted key storage requires Windows; set HIBP_API_KEY instead.")
    crypt32 = ctypes.WinDLL("crypt32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    function = crypt32.CryptProtectData if protect else crypt32.CryptUnprotectData
    blob_pointer = ctypes.POINTER(_Blob)
    function.argtypes = [blob_pointer, ctypes.c_void_p, blob_pointer, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32, blob_pointer]
    function.restype = ctypes.c_int
    kernel32.LocalFree.argtypes = [ctypes.c_void_p]
    kernel32.LocalFree.restype = ctypes.c_void_p
    source_buffer = ctypes.create_string_buffer(data, len(data))
    entropy_buffer = ctypes.create_string_buffer(DPAPI_ENTROPY, len(DPAPI_ENTROPY))
    source = _Blob(len(data), ctypes.cast(source_buffer, ctypes.POINTER(ctypes.c_char)))
    entropy = _Blob(len(DPAPI_ENTROPY), ctypes.cast(entropy_buffer, ctypes.POINTER(ctypes.c_char)))
    output = _Blob()
    # 0x1 = CRYPTPROTECT_UI_FORBIDDEN
    if not function(ctypes.byref(source), None, ctypes.byref(entropy), None, None, 0x1, ctypes.byref(output)):
        raise OsintError("Windows could not encrypt or decrypt the stored key.")
    try:
        return ctypes.string_at(output.pbData, output.cbData)
    finally:
        kernel32.LocalFree(ctypes.cast(output.pbData, ctypes.c_void_p))


def protect(text: str) -> str:
    return base64.b64encode(_dpapi(text.encode(), protect=True)).decode()


def unprotect(token: str) -> str:
    return _dpapi(base64.b64decode(token), protect=False).decode()


def clean_html(value, size: int = 300) -> str:
    text = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", str(value or "")))).strip()
    return text[:size]


def validate_identifier(kind, value) -> str:
    if kind not in KINDS or not isinstance(value, str):
        raise OsintError("Unknown identifier type.")
    value = value.strip()
    if kind == "email":
        value = value.lower()
        if len(value) > 254 or not EMAIL_RE.fullmatch(value):
            raise OsintError("Enter a valid e-mail address.")
    elif kind == "domain":
        value = value.lower().removeprefix("www.").rstrip(".")
        try:
            value = value.encode("idna").decode("ascii")
        except UnicodeError:
            raise OsintError("Enter a valid domain name, without http:// or a path.") from None
        if not DOMAIN_RE.fullmatch(value):
            raise OsintError("Enter a valid domain name, without http:// or a path.")
    elif not USERNAME_RE.fullmatch(value):
        raise OsintError("Usernames may contain 1-39 letters, digits, dots, dashes and underscores.")
    return value


def summarize_breach(breach: dict) -> dict:
    return {
        "name": str(breach.get("Name") or "")[:100], "title": str(breach.get("Title") or breach.get("Name") or "")[:120],
        "domain": str(breach.get("Domain") or "")[:120], "date": str(breach.get("BreachDate") or "")[:10],
        "added": str(breach.get("AddedDate") or "")[:20], "count": breach.get("PwnCount") if isinstance(breach.get("PwnCount"), int) else None,
        "data": [str(item)[:60] for item in (breach.get("DataClasses") or [])[:20]],
        "verified": bool(breach.get("IsVerified")), "sensitive": bool(breach.get("IsSensitive")),
        "description": clean_html(breach.get("Description")),
    }


class Store:
    def __init__(self, path: Path):
        self.path = path
        self.write_lock = threading.RLock()

    @contextmanager
    def connection(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(self.path, timeout=10)) as db, db:
            db.row_factory = sqlite3.Row
            db.executescript("""
                CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS identifiers (
                    id TEXT PRIMARY KEY, kind TEXT NOT NULL, value TEXT NOT NULL, created REAL, result TEXT,
                    UNIQUE(kind, value));
            """)
            yield db

    def setting(self, key: str, default=None):
        with self.connection() as db:
            row = db.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return json.loads(row["value"]) if row else default

    def set_setting(self, key: str, value) -> None:
        with self.write_lock, self.connection() as db:
            if value is None:
                db.execute("DELETE FROM settings WHERE key=?", (key,))
            else:
                db.execute("INSERT OR REPLACE INTO settings VALUES(?,?)", (key, json.dumps(value)))

    def identifiers(self) -> list[dict]:
        with self.connection() as db:
            return [
                {"id": row["id"], "kind": row["kind"], "value": row["value"], "created": row["created"],
                 "result": json.loads(row["result"]) if row["result"] else None}
                for row in db.execute("SELECT * FROM identifiers ORDER BY created")
            ]

    def add(self, kind: str, value: str) -> str:
        identifier = secrets.token_hex(8)
        with self.write_lock, self.connection() as db:
            if db.execute("SELECT COUNT(*) FROM identifiers").fetchone()[0] >= MAX_IDENTIFIERS:
                raise OsintError(f"At most {MAX_IDENTIFIERS} identifiers are supported.")
            try:
                db.execute("INSERT INTO identifiers VALUES(?,?,?,?,NULL)", (identifier, kind, value, time.time()))
            except sqlite3.IntegrityError:
                raise OsintError("This identifier is already in the list.") from None
        return identifier

    def remove(self, identifier: str) -> None:
        with self.write_lock, self.connection() as db:
            if db.execute("DELETE FROM identifiers WHERE id=?", (identifier,)).rowcount != 1:
                raise OsintError("Unknown identifier.")

    def save_result(self, identifier: str, result: dict) -> None:
        with self.write_lock, self.connection() as db:
            db.execute("UPDATE identifiers SET result=? WHERE id=?", (json.dumps(result), identifier))


class HibpClient:
    """Serialises HIBP requests so they respect the subscription's requests-per-minute limit."""

    def __init__(self, session=None, *, clock=time.monotonic, sleep=time.sleep):
        self.session = session or requests.Session()
        self.clock, self.sleep = clock, sleep
        self.lock = threading.Lock()
        self.next_slot = 0.0
        self.spacing = 6.0

    def set_rpm(self, rpm) -> None:
        if isinstance(rpm, int) and rpm > 0:
            self.spacing = 60 / rpm + 0.1

    def get(self, path: str, *, key: str = "", params=None):
        headers = {"user-agent": USER_AGENT}
        if key:
            headers["hibp-api-key"] = key
        with self.lock:
            for attempt in range(2):
                wait = self.next_slot - self.clock()
                if wait > 0:
                    self.sleep(wait)
                try:
                    response = self.session.get(HIBP_BASE + path, headers=headers, params=params, timeout=20)
                except requests.RequestException as error:
                    raise OsintError(f"Have I Been Pwned is unreachable: {type(error).__name__}.") from None
                finally:
                    self.next_slot = self.clock() + self.spacing
                if response.status_code != 429:
                    break
                try:
                    retry = int(response.headers.get("retry-after", "0"))
                except ValueError:
                    retry = 60
                if attempt or retry > 10:
                    raise OsintError(f"Have I Been Pwned rate limit reached; try again in {max(retry, 1)} seconds.")
                self.sleep(max(retry, 1))
        status = response.status_code
        if status == 404:
            return None
        if status == 401:
            raise OsintError("The HIBP API key is invalid.")
        if status == 403:
            raise PermissionError("forbidden")
        if status == 400:
            raise OsintError("HIBP rejected the identifier format.")
        if status >= 500:
            raise OsintError("Have I Been Pwned is temporarily unavailable.")
        if status != 200:
            raise OsintError(f"Unexpected HIBP response ({status}).")
        try:
            return response.json()
        except ValueError:
            raise OsintError("HIBP returned an unreadable response.") from None


def footprint(session, username: str) -> list[dict]:
    safe = quote(username, safe="")

    def probe(site):
        name, api, profile, mode = site
        result = {"site": name, "url": profile.format(u=safe), "status": "unknown"}
        try:
            response = session.get(api.format(u=safe), headers={"user-agent": USER_AGENT, "accept": "application/json"}, timeout=10)
        except requests.RequestException:
            return result
        code = response.status_code
        try:
            if mode == "status":
                result["status"] = {200: "exists", 404: "not_found", 410: "not_found"}.get(code, "unknown")
            elif code != 200:
                result["status"] = "not_found" if code == 404 else "unknown"
            elif mode == "json_list":
                data = response.json()
                result["status"] = "exists" if isinstance(data, list) and data else "not_found"
            elif mode == "json_null":
                result["status"] = "not_found" if response.json() is None else "exists"
            elif mode == "keybase":
                data = response.json()
                status_code = (data.get("status") or {}).get("code")
                them = data.get("them") or []
                if status_code == 0 and them and them[0]:
                    result["status"] = "exists"
                elif status_code == 205 or (status_code == 0 and them and them[0] is None):
                    result["status"] = "not_found"
        except (ValueError, AttributeError):
            result["status"] = "unknown"
        return result

    with ThreadPoolExecutor(max_workers=5) as pool:
        return list(pool.map(probe, SITES))


class Osint:
    ACTIONS = {
        "add": {"kind", "value", "owned"}, "remove": {"id"}, "check": {"ids"}, "set_key": {"key"},
        "clear_key": set(), "verify_key": set(), "monitor": {"enabled", "hours", "sound"}, "password_range": {"prefix"},
    }

    def __init__(self, store: Store, notify=None, *, session=None, client: HibpClient | None = None):
        self.store = store
        self.notify = notify
        self.session = session or requests.Session()
        self.client = client or HibpClient(self.session)
        self.lock = threading.RLock()
        self.job = {"running": False, "done": 0, "total": 0, "started": 0, "finished": 0, "error": "", "new": 0}
        self.job_thread = None
        self.monitor = {"enabled": False, "hours": 24, "sound": False, "last_run": 0, "latest": "", "error": ""}
        self.monitor_thread = None
        self.monitor_stop = threading.Event()
        self.stop_event = threading.Event()

    def key(self) -> tuple[str, str]:
        env_key = os.environ.get("HIBP_API_KEY", "").strip()
        if env_key:
            if not KEY_RE.fullmatch(env_key):
                raise OsintError("HIBP_API_KEY is not a 32-character key.")
            return env_key, "environment"
        token = self.store.setting("hibp_key")
        if not token:
            return "", ""
        try:
            return unprotect(token), "stored"
        except (OsintError, OSError, ValueError, UnicodeDecodeError):
            raise OsintError("The stored HIBP key can no longer be read; enter it again.") from None

    def key_source(self) -> str:
        try:
            return self.key()[1]
        except OsintError:
            return "unreadable"

    def snapshot(self) -> dict:
        with self.lock:
            job, monitor = dict(self.job), dict(self.monitor)
        return {
            "identifiers": self.store.identifiers(), "key_source": self.key_source(),
            "subscription": self.store.setting("subscription", ""), "rpm": self.store.setting("rpm"),
            "job": job, "monitor": monitor, "dashboard": DOMAIN_DASHBOARD, "key_page": API_KEY_PAGE,
            "max_identifiers": MAX_IDENTIFIERS,
        }

    def handle(self, action: str, data: object):
        if action not in self.ACTIONS or not isinstance(data, dict) or set(data) != self.ACTIONS[action]:
            raise OsintError("Invalid request.")
        if action == "add":
            if data["owned"] is not True:
                raise OsintError("Only add identifiers that belong to you.")
            return {"id": self.store.add(data["kind"], validate_identifier(data["kind"], data["value"]))}
        if action == "remove":
            if not isinstance(data["id"], str):
                raise OsintError("Unknown identifier.")
            self.store.remove(data["id"])
        elif action == "check":
            self.check(data["ids"])
        elif action == "set_key":
            self.set_key(data["key"])
        elif action == "clear_key":
            self.store.set_setting("hibp_key", None)
            self.store.set_setting("subscription", None)
        elif action == "verify_key":
            key, _source = self.key()
            if not key:
                raise OsintError("No HIBP API key configured.")
            self.verify(key)
        elif action == "monitor":
            self.set_monitor(data)
        elif action == "password_range":
            return {"lines": self.password_range(data["prefix"])}
        return {}

    def verify(self, key: str) -> dict:
        try:
            status = self.client.get("/subscription/status", key=key)
        except PermissionError:
            raise OsintError("HIBP refused the key (403).") from None
        if not isinstance(status, dict):
            raise OsintError("HIBP did not return a subscription status.")
        rpm = status.get("Rpm") if isinstance(status.get("Rpm"), int) else None
        self.store.set_setting("rpm", rpm)
        self.store.set_setting("subscription", str(status.get("SubscriptionName") or "")[:80])
        self.client.set_rpm(rpm)
        return status

    def set_key(self, key) -> None:
        if not isinstance(key, str) or not KEY_RE.fullmatch(key.strip()):
            raise OsintError("An HIBP API key has 32 hexadecimal characters.")
        key = key.strip()
        self.verify(key)
        self.store.set_setting("hibp_key", protect(key))

    def password_range(self, prefix) -> list[str]:
        if not isinstance(prefix, str) or not re.fullmatch(r"[0-9A-Fa-f]{5}", prefix):
            raise OsintError("Send only the first 5 hexadecimal characters of the SHA-1 hash.")
        try:
            response = self.session.get(
                PWNED_RANGE + prefix.upper(), headers={"user-agent": USER_AGENT, "Add-Padding": "true"}, timeout=20,
            )
        except requests.RequestException:
            raise OsintError("Pwned Passwords is unreachable.") from None
        if response.status_code != 200:
            raise OsintError(f"Pwned Passwords returned HTTP {response.status_code}.")
        lines = []
        for line in response.text.splitlines():
            suffix, _, count = line.strip().partition(":")
            if re.fullmatch(r"[0-9A-Fa-f]{35}", suffix) and count.isdigit() and int(count) > 0:
                lines.append(f"{suffix.upper()}:{int(count)}")
        return lines

    def check(self, ids) -> None:
        if not isinstance(ids, list) or len(ids) > MAX_IDENTIFIERS or not all(isinstance(item, str) for item in ids):
            raise OsintError("Invalid selection.")
        targets = [item for item in self.store.identifiers() if not ids or item["id"] in ids]
        if not targets:
            raise OsintError("Add an identifier first.")
        self._start_job(targets, from_monitor=False)

    def _start_job(self, targets: list[dict], *, from_monitor: bool) -> bool:
        with self.lock:
            if self.job_thread and self.job_thread.is_alive():
                if from_monitor:
                    return False
                raise OsintError("A check is already running.")
            self.job = {"running": True, "done": 0, "total": len(targets), "started": time.time(), "finished": 0, "error": "", "new": 0}
            self.job_thread = threading.Thread(target=self._run_job, args=(targets, from_monitor), name="echo-osint-job", daemon=True)
            self.job_thread.start()
            return True

    def _run_job(self, targets: list[dict], from_monitor: bool) -> None:
        new_total, error = 0, ""
        try:
            self.client.set_rpm(self.store.setting("rpm"))
            key, _source = self.key()
        except OsintError as key_error:
            key, error = "", str(key_error)
        except (OSError, sqlite3.Error) as store_error:
            key, error = "", f"Settings unavailable: {type(store_error).__name__}"
        for identifier in targets:
            if self.stop_event.is_set():
                break
            previous = identifier["result"] or {}
            try:
                result = self.check_identifier(identifier, key)
            except OsintError as check_error:
                result = {"status": "error", "error": str(check_error)}
            except Exception as check_error:  # one failing identifier must not abort the rest
                LOGGER.exception("OSINT check failed")
                result = {"status": "error", "error": type(check_error).__name__}
            result["checked"] = time.time()
            if result["status"] == "ok" and previous.get("status") == "ok":
                result["new"] = sorted(set(result.get("breaches_names", [])) - set(previous.get("breaches_names", [])))
                new_total += len(result["new"])
            else:
                result.setdefault("new", [])
            try:
                self.store.save_result(identifier["id"], result)
            except (OSError, sqlite3.Error) as store_error:
                error = f"Could not save results: {type(store_error).__name__}"
            with self.lock:
                self.job["done"] += 1
        with self.lock:
            self.job.update(running=False, finished=time.time(), error=error, new=new_total)
        if from_monitor and new_total and self.notify:
            try:
                self.notify("osint_alert", self.monitor["sound"])
            except Exception:
                LOGGER.exception("OSINT notification failed")

    def check_identifier(self, identifier: dict, key: str) -> dict:
        kind, value = identifier["kind"], identifier["value"]
        if kind == "username":
            sites = footprint(self.session, value)
            return {"status": "ok", "sites": sites, "breaches_names": []}
        if kind == "email":
            if not key:
                return {"status": "needs_key", "error": "E-mail checks need an HIBP API key."}
            try:
                breaches = self.client.get(f"/breachedaccount/{quote(value, safe='')}", key=key, params={"truncateResponse": "false"}) or []
            except PermissionError:
                raise OsintError("Your HIBP subscription does not allow this search.") from None
            notes = []
            try:
                pastes = self.client.get(f"/pasteaccount/{quote(value, safe='')}", key=key) or []
            except (PermissionError, OsintError) as paste_error:
                pastes, notes = [], [f"Paste search unavailable: {paste_error if isinstance(paste_error, OsintError) else 'no access'}."]
            summaries = [summarize_breach(item) for item in breaches if isinstance(item, dict)][:100]
            paste_list = [
                {"source": str(item.get("Source") or "")[:40], "title": str(item.get("Title") or "")[:120], "date": str(item.get("Date") or "")[:20]}
                for item in pastes if isinstance(item, dict)
            ][:20]
            return {
                "status": "ok", "breaches": summaries, "breaches_names": [item["name"] for item in summaries],
                "pastes": paste_list, "paste_count": len(pastes) if isinstance(pastes, list) else 0, "notes": notes,
            }
        site = self.client.get("/breaches", params={"Domain": value}) or []
        summaries = [summarize_breach(item) for item in site if isinstance(item, dict)][:50]
        result = {"status": "ok", "breaches": summaries, "breaches_names": [item["name"] for item in summaries], "notes": [], "aliases": {}}
        if not key:
            result["notes"].append("Without an API key Echo only checks whether this site itself was breached.")
            return result
        try:
            domain = self.client.get(f"/breacheddomain/{quote(value, safe='')}", key=key) or {}
        except PermissionError:
            result["notes"].append("Verify this domain in your HIBP dashboard to search all addresses on it.")
            result["verify_url"] = DOMAIN_DASHBOARD
            return result
        if isinstance(domain, dict):
            aliases = {str(alias)[:64]: [str(name)[:100] for name in names][:50] for alias, names in list(domain.items())[:200] if isinstance(names, list)}
            result["aliases"] = aliases
            result["alias_count"] = len(domain)
            result["breaches_names"] = sorted(set(result["breaches_names"]) | {name for names in aliases.values() for name in names})
        return result

    def set_monitor(self, data: dict) -> None:
        if type(data["enabled"]) is not bool or type(data["sound"]) is not bool or type(data["hours"]) is not int or not MIN_HOURS <= data["hours"] <= MAX_HOURS:
            raise OsintError(f"Choose an interval of {MIN_HOURS}-{MAX_HOURS} hours.")
        with self.lock:
            self.monitor.update(enabled=data["enabled"], hours=data["hours"], sound=data["sound"], error="")
            running = self.monitor_thread and self.monitor_thread.is_alive() and not self.monitor_stop.is_set()
            if not data["enabled"]:
                self.monitor_stop.set()
            elif not running:
                self.monitor_stop = threading.Event()
                self.monitor_thread = threading.Thread(
                    target=self._run_monitor, args=(self.monitor_stop,), name="echo-osint-monitor", daemon=True,
                )
                self.monitor_thread.start()

    def _monitor_once(self) -> None:
        try:
            latest = self.client.get("/latestBreach") or {}
        except (OsintError, PermissionError) as error:
            with self.lock:
                self.monitor["error"] = str(error)
            return
        name = str(latest.get("Name") or "") if isinstance(latest, dict) else ""
        known = self.store.setting("latest_breach", "")
        with self.lock:
            self.monitor.update(last_run=time.time(), latest=str(latest.get("Title") or name)[:120] if isinstance(latest, dict) else "", error="")
        if name and name != known:
            self.store.set_setting("latest_breach", name)
            identifiers = self.store.identifiers()
            if identifiers:
                self._start_job(identifiers, from_monitor=True)

    def _run_monitor(self, stop: threading.Event) -> None:
        while not stop.is_set() and not self.stop_event.is_set():
            try:
                self._monitor_once()
            except (OSError, sqlite3.Error) as error:
                with self.lock:
                    self.monitor["error"] = type(error).__name__
            with self.lock:
                hours = self.monitor["hours"]
            if stop.wait(hours * 3600):
                break
        with self.lock:
            if self.monitor_stop is stop:
                self.monitor["enabled"] = False

    def shutdown(self) -> None:
        self.stop_event.set()
        with self.lock:
            self.monitor_stop.set()
        for thread in (self.monitor_thread, self.job_thread):
            if thread and thread.is_alive():
                thread.join(2)
