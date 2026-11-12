import os

import pytest
import requests

import echo_osint as osint

KEY = "0123456789abcdef0123456789abcdef"
BASE = osint.HIBP_BASE


class Response:
    def __init__(self, status=200, data=None, text="", headers=None):
        self.status_code, self._data, self.text, self.headers = status, data, text, headers or {}

    def json(self):
        if self._data is ValueError:
            raise ValueError("not json")
        return self._data


class Session:
    def __init__(self, routes=None):
        self.routes, self.calls = routes or {}, []

    def get(self, url, headers=None, params=None, timeout=None):
        self.calls.append({"url": url, "headers": headers or {}, "params": params, "timeout": timeout})
        value = self.routes.get(url, Response(404))
        if isinstance(value, list):
            value = value.pop(0)
        if isinstance(value, Exception):
            raise value
        return value


class Clock:
    def __init__(self):
        self.now, self.sleeps = 1000.0, []

    def __call__(self):
        return self.now

    def sleep(self, seconds):
        self.sleeps.append(round(seconds, 2))
        self.now += seconds


@pytest.fixture(autouse=True)
def no_environment_key(monkeypatch):
    monkeypatch.delenv("HIBP_API_KEY", raising=False)


def service(tmp_path, routes, notify=None):
    session, clock = Session(routes), Clock()
    client = osint.HibpClient(session, clock=clock, sleep=clock.sleep)
    return osint.Osint(osint.Store(tmp_path / "osint.sqlite3"), notify, session=session, client=client), session, clock


def run(checker, ids=()):
    checker.check(list(ids))
    checker.job_thread.join(5)
    assert not checker.job["running"]


@pytest.mark.parametrize(("kind", "value", "expected"), [
    ("email", "  Me@Example.COM ", "me@example.com"),
    ("domain", "www.Example.com.", "example.com"),
    ("domain", "bücher.de", "xn--bcher-kva.de"),
    ("username", "nordin_dev", "nordin_dev"),
])
def test_identifiers_are_normalized(kind, value, expected):
    assert osint.validate_identifier(kind, value) == expected


@pytest.mark.parametrize(("kind", "value"), [
    ("email", "not-an-email"), ("email", "a@b"), ("domain", "https://example.com/path"), ("domain", "-bad-.com"),
    ("username", "two words"), ("username", "x" * 41), ("phone", "0612345678"), ("email", None),
])
def test_invalid_identifiers_are_rejected(kind, value):
    with pytest.raises(osint.OsintError):
        osint.validate_identifier(kind, value)


def test_client_sends_headers_spaces_requests_and_maps_statuses():
    session, clock = Session({
        BASE + "/a": Response(200, {"ok": 1}), BASE + "/b": Response(404), BASE + "/c": Response(401),
        BASE + "/d": Response(403), BASE + "/e": Response(503), BASE + "/f": Response(200, ValueError),
    }), Clock()
    client = osint.HibpClient(session, clock=clock, sleep=clock.sleep)
    client.set_rpm(10)
    assert client.get("/a", key=KEY) == {"ok": 1}
    assert session.calls[0]["headers"] == {"user-agent": osint.USER_AGENT, "hibp-api-key": KEY}
    assert client.get("/b") is None
    assert clock.sleeps == [6.1]
    assert "hibp-api-key" not in session.calls[1]["headers"]
    with pytest.raises(osint.OsintError, match="invalid"):
        client.get("/c")
    with pytest.raises(PermissionError):
        client.get("/d")
    with pytest.raises(osint.OsintError, match="temporarily"):
        client.get("/e")
    with pytest.raises(osint.OsintError, match="unreadable"):
        client.get("/f")


def test_client_retries_short_rate_limits_once_only():
    session, clock = Session({
        BASE + "/short": [Response(429, headers={"retry-after": "2"}), Response(200, [])],
        BASE + "/long": Response(429, headers={"retry-after": "60"}),
        BASE + "/twice": [Response(429, headers={"retry-after": "1"}), Response(429, headers={"retry-after": "1"})],
        BASE + "/down": requests.ConnectionError("offline"),
    }), Clock()
    client = osint.HibpClient(session, clock=clock, sleep=clock.sleep)
    client.spacing = 0
    assert client.get("/short") == []
    assert clock.sleeps == [2]
    with pytest.raises(osint.OsintError, match="60 seconds"):
        client.get("/long")
    with pytest.raises(osint.OsintError, match="rate limit"):
        client.get("/twice")
    with pytest.raises(osint.OsintError, match="unreachable"):
        client.get("/down")


@pytest.mark.skipif(os.name != "nt", reason="DPAPI is Windows-only")
def test_dpapi_round_trip_never_stores_plain_key():
    token = osint.protect(KEY)
    assert KEY not in token and osint.unprotect(token) == KEY
    with pytest.raises(osint.OsintError):
        osint.unprotect("AAAA")


def test_key_storage_environment_precedence_and_clear(tmp_path, monkeypatch):
    monkeypatch.setattr(osint, "protect", lambda text: "enc:" + text[::-1])
    monkeypatch.setattr(osint, "unprotect", lambda token: token.removeprefix("enc:")[::-1])
    checker, session, _ = service(tmp_path, {BASE + "/subscription/status": Response(200, {"SubscriptionName": "Pwned 1", "Rpm": 10})})
    with pytest.raises(osint.OsintError, match="32 hexadecimal"):
        checker.handle("set_key", {"key": "short"})
    checker.handle("set_key", {"key": f" {KEY} "})
    assert checker.store.setting("hibp_key") == "enc:" + KEY[::-1]
    snapshot = checker.snapshot()
    assert (snapshot["key_source"], snapshot["subscription"], snapshot["rpm"]) == ("stored", "Pwned 1", 10)
    assert KEY not in str(snapshot)
    monkeypatch.setenv("HIBP_API_KEY", "f" * 32)
    assert checker.key() == ("f" * 32, "environment")
    monkeypatch.setenv("HIBP_API_KEY", "bad")
    assert checker.key_source() == "unreadable"
    monkeypatch.delenv("HIBP_API_KEY")
    checker.handle("clear_key", {})
    assert checker.key() == ("", "")
    with pytest.raises(osint.OsintError, match="No HIBP API key"):
        checker.handle("verify_key", {})


def test_rejected_key_is_not_stored(tmp_path, monkeypatch):
    monkeypatch.setattr(osint, "protect", lambda text: pytest.fail("must not store"))
    checker, _, _ = service(tmp_path, {BASE + "/subscription/status": Response(401)})
    with pytest.raises(osint.OsintError, match="invalid"):
        checker.handle("set_key", {"key": KEY})
    assert checker.store.setting("hibp_key") is None


def test_password_range_filters_padding_and_validates_prefix(tmp_path):
    suffix = "1E4C9B93F3F0682250B6CF8331B7EE68FD8"
    text = f"{suffix}:3\r\n{'0' * 35}:0\r\nnot-a-line\r\n{'a' * 35}:12\r\n"
    checker, session, _ = service(tmp_path, {osint.PWNED_RANGE + "5BAA6": Response(200, text=text)})
    assert checker.handle("password_range", {"prefix": "5baa6"}) == {"lines": [f"{suffix}:3", f"{'A' * 35}:12"]}
    assert session.calls[0]["headers"]["Add-Padding"] == "true"
    for prefix in ("5BAA61", "zzzzz", 12345):
        with pytest.raises(osint.OsintError):
            checker.handle("password_range", {"prefix": prefix})


def breach(name, classes=("Email addresses", "Passwords")):
    return {"Name": name, "Title": name.title(), "Domain": f"{name}.com", "BreachDate": "2024-01-02",
            "DataClasses": list(classes), "Description": "<p>Leaked &amp; sold</p>", "PwnCount": 5}


def test_email_check_reports_breaches_pastes_and_new_results(tmp_path):
    email = "me@example.com"
    account = BASE + "/breachedaccount/me%40example.com"
    checker, session, _ = service(tmp_path, {
        account: [Response(200, [breach("adobe")]), Response(200, [breach("adobe"), breach("canva")])],
        BASE + "/pasteaccount/me%40example.com": [Response(404), Response(200, [{"Source": "Pastebin", "Title": "dump", "Date": "2024-02-02T00:00:00Z"}])],
    })
    with pytest.raises(osint.OsintError, match="belong to you"):
        checker.handle("add", {"kind": "email", "value": email, "owned": False})
    identifier = checker.handle("add", {"kind": "email", "value": email, "owned": True})["id"]
    run(checker)
    result = checker.store.identifiers()[0]["result"]
    assert result["status"] == "needs_key"
    checker.store.set_setting("hibp_key", "unused")
    checker.key = lambda: (KEY, "stored")
    run(checker, [identifier])
    result = checker.store.identifiers()[0]["result"]
    assert result["breaches"][0]["description"] == "Leaked & sold" and result["new"] == []
    run(checker, [identifier])
    result = checker.store.identifiers()[0]["result"]
    assert result["new"] == ["canva"] and result["paste_count"] == 1 and checker.job["new"] == 1
    assert session.calls[0]["params"] == {"truncateResponse": "false"}


def test_domain_check_without_key_forbidden_and_verified(tmp_path):
    routes = {
        BASE + "/breaches": Response(200, [breach("example")]),
        BASE + "/breacheddomain/example.com": [Response(403), Response(200, {"alice": ["adobe"], "bob": ["adobe", "canva"]})],
    }
    checker, session, _ = service(tmp_path, routes)
    checker.handle("add", {"kind": "domain", "value": "Example.com", "owned": True})
    run(checker)
    result = checker.store.identifiers()[0]["result"]
    assert "Without an API key" in result["notes"][0] and len(session.calls) == 1
    checker.key = lambda: (KEY, "stored")
    run(checker)
    result = checker.store.identifiers()[0]["result"]
    assert result["verify_url"] == osint.DOMAIN_DASHBOARD and "Verify this domain" in result["notes"][0]
    routes[BASE + "/breaches"] = Response(200, [])
    run(checker)
    result = checker.store.identifiers()[0]["result"]
    assert result["alias_count"] == 2 and result["breaches_names"] == ["adobe", "canva"]
    assert set(result["new"]) == {"adobe", "canva"} - {"example"}


def test_username_footprint_classifies_each_site(tmp_path):
    routes = {
        "https://api.github.com/users/nordin": Response(200, {}),
        "https://gitlab.com/api/v4/users?username=nordin": Response(200, []),
        "https://keybase.io/_/api/1.0/user/lookup.json?usernames=nordin": Response(200, {"status": {"code": 0}, "them": [None]}),
        "https://hacker-news.firebaseio.com/v0/user/nordin.json": Response(200, None),
        "https://www.reddit.com/user/nordin/about.json": Response(429),
        "https://pypi.org/user/nordin/": requests.Timeout("slow"),
    }
    checker, _, _ = service(tmp_path, routes)
    checker.handle("add", {"kind": "username", "value": "nordin", "owned": True})
    run(checker)
    sites = {site["site"]: site for site in checker.store.identifiers()[0]["result"]["sites"]}
    assert sites["GitHub"]["status"] == "exists" and sites["GitHub"]["url"] == "https://github.com/nordin"
    assert sites["GitLab"]["status"] == sites["Keybase"]["status"] == sites["Hacker News"]["status"] == "not_found"
    assert sites["Docker Hub"]["status"] == "not_found"
    assert sites["Reddit"]["status"] == sites["PyPI"]["status"] == "unknown"
    assert len(sites) == len(osint.SITES)


def test_monitor_rechecks_on_new_hibp_breach_and_alerts_once(tmp_path):
    alerts = []
    routes = {
        BASE + "/latestBreach": [Response(200, {"Name": "adobe", "Title": "Adobe"}), Response(200, {"Name": "adobe"}), Response(200, {"Name": "canva", "Title": "Canva"})],
        BASE + "/breachedaccount/me%40example.com": [Response(200, [breach("adobe")]), Response(200, [breach("adobe"), breach("canva")])],
    }
    checker, _, _ = service(tmp_path, routes, notify=lambda kind, sound: alerts.append((kind, sound)))
    checker.key = lambda: (KEY, "stored")
    checker.handle("add", {"kind": "email", "value": "me@example.com", "owned": True})
    checker.monitor["sound"] = True
    for _ in range(3):
        checker._monitor_once()
        if checker.job_thread:
            checker.job_thread.join(5)
    assert checker.monitor["latest"] == "Canva"
    assert alerts == [("osint_alert", True)]
    assert checker.store.identifiers()[0]["result"]["new"] == ["canva"]


def test_monitor_settings_and_shutdown(tmp_path):
    checker, _, _ = service(tmp_path, {BASE + "/latestBreach": Response(200, {"Name": "x"})})
    with pytest.raises(osint.OsintError, match="6-168"):
        checker.handle("monitor", {"enabled": True, "hours": 1, "sound": False})
    checker.handle("monitor", {"enabled": True, "hours": 24, "sound": False})
    thread = checker.monitor_thread
    assert thread.is_alive()
    checker.handle("monitor", {"enabled": False, "hours": 24, "sound": False})
    thread.join(5)
    assert not thread.is_alive() and not checker.snapshot()["monitor"]["enabled"]
    checker.shutdown()


@pytest.mark.parametrize(("action", "data"), [
    ("add", {"kind": "email", "value": "me@example.com"}), ("remove", {"id": 5}), ("check", {"ids": "all"}),
    ("check", {"ids": [1]}), ("unknown", {}), ("clear_key", []), ("monitor", {"enabled": "yes", "hours": 24, "sound": False}),
])
def test_handle_rejects_malformed_requests(tmp_path, action, data):
    checker, session, _ = service(tmp_path, {})
    with pytest.raises(osint.OsintError):
        checker.handle(action, data)
    assert session.calls == []


def test_check_requires_identifiers_and_single_job(tmp_path):
    checker, _, _ = service(tmp_path, {})
    with pytest.raises(osint.OsintError, match="Add an identifier"):
        checker.handle("check", {"ids": []})
