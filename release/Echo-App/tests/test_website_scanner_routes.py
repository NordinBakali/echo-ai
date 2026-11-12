import json
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from urllib.parse import parse_qs, urlparse

import pytest
import server
import website_scanner as scanner


@pytest.fixture
def client():
    server.app.config.update(TESTING=True)
    with server.app.test_client() as test_client:
        yield test_client


def test_website_scanner_page_loads(client):
    response = client.get("/website-scanner/")

    assert response.status_code == 200
    assert b"Website Scanner" in response.data
    assert b"/website-scanner/scan?" in response.data


def test_website_scanner_stylesheet_loads(client):
    response = client.get("/website-scanner/style.css")

    assert response.status_code == 200
    assert b".scanner-card" in response.data


def test_functional_checker_route_redirects_to_website_scanner(client):
    response = client.get("/functional-checker")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/website-scanner/")


def test_functional_checker_redirect_keeps_the_target_url(client):
    response = client.get(
        "/functional-checker?url=http%3A%2F%2Flocalhost%3A3000"
    )

    assert response.status_code == 302
    location = urlparse(response.headers["Location"])
    assert location.path == "/website-scanner/"
    assert parse_qs(location.query)["url"] == ["http://localhost:3000"]


def test_website_scanner_rejects_invalid_scan_id(client):
    response = client.get("/website-scanner/scan?url=https%3A%2F%2Fexample.com&scan_id=invalid")

    assert response.status_code == 200
    assert response.mimetype == "text/event-stream"
    assert b"Ongeldig scan-ID" in response.data


def test_website_scanner_streams_completed_scan(client, monkeypatch):
    monkeypatch.setattr(
        scanner,
        "crawl",
        lambda url, update, cancel_event: ([{"url": url}], object(), False),
    )
    monkeypatch.setattr(
        scanner,
        "check_resources",
        lambda pages, session, update, cancel_event: ({}, {}),
    )
    monkeypatch.setattr(
        scanner,
        "browser_test",
        lambda pages, update, **kwargs: {"evidence": []},
    )
    monkeypatch.setattr(
        scanner,
        "make_result",
        lambda url, pages, resources, errors, browser, **kwargs: (
            "scan complete",
            {"page_limit_reached": kwargs["page_limit_reached"]},
        ),
    )

    response = client.get(
        "/website-scanner/scan",
        query_string={
            "url": "https://example.com",
            "scan_id": "123e4567-e89b-42d3-a456-426614174000",
        },
    )

    assert response.status_code == 200
    assert b'"type": "result"' in response.data
    assert b"scan complete" in response.data
    assert b'"page_limit_reached": false' in response.data


def test_crawl_stops_at_page_limit(monkeypatch):
    class Response:
        status_code = 200
        headers = {"content-type": "text/html"}

        def __init__(self, url):
            self.url = url
            self.text = (
                "<html><title>Page</title><meta name='description' content='test'>"
                "<body><h1>Page</h1>"
                "<a href='/two'>Two</a><a href='/three'>Three</a>"
                "</body></html>"
            )

    class Session:
        def mount(self, *_args):
            pass

    monkeypatch.setattr(scanner.requests, "Session", Session)
    monkeypatch.setattr(scanner, "get_page", lambda _session, url: (Response(url), None))
    monkeypatch.setattr(scanner, "MAX_CRAWL_PAGES", 1)
    updates = []

    pages, _session, limit_reached = scanner.crawl(
        "http://localhost/", lambda message, _progress: updates.append(message),
        scanner.threading.Event()
    )

    assert len(pages) == 1
    assert limit_reached is True
    assert any("maximaal 1 interne pagina" in message for message in updates)


def test_resource_check_streams_response_body(monkeypatch):
    class Response:
        status_code = 200
        closed = False

        def close(self):
            self.closed = True

    response = Response()
    calls = []

    class Session:
        def get(self, url, **kwargs):
            calls.append((url, kwargs))
            return response

    status, error = scanner.get_resource_status(Session(), "http://localhost/image.png")

    assert status == 200
    assert error is None
    assert calls[0][1]["stream"] is True
    assert response.closed is True


def test_local_development_site_scans_pages_and_button():
    if scanner.sync_playwright is None:
        pytest.skip("Playwright is not installed in this environment.")
    with scanner.sync_playwright() as playwright:
        if not Path(playwright.chromium.executable_path).is_file():
            pytest.skip("Playwright Chromium is not installed in this environment.")

    class SiteHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            pages = {
                "/": (
                    "text/html; charset=utf-8",
                    b"""<!doctype html><html><head><title>Local site</title>
                    <meta name="description" content="A local test site">
                    <link rel="stylesheet" href="/style.css"></head><body>
                    <h1>Local site</h1><a href="/about">About</a>
                    <button onclick="document.getElementById('result').textContent='Done'">
                    Run test</button><p id="result">Ready</p></body></html>""",
                ),
                "/about": (
                    "text/html; charset=utf-8",
                    b"""<!doctype html><html><head><title>About</title>
                    <meta name="description" content="About page"></head>
                    <body><h1>About</h1></body></html>""",
                ),
                "/style.css": ("text/css", b"body { color: black; }"),
            }
            content_type, body = pages.get(
                self.path,
                ("text/plain", b"Not found"),
            )
            self.send_response(200 if self.path in pages else 404)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, _format, *_args):
            pass

    site = ThreadingHTTPServer(("127.0.0.1", 0), SiteHandler)
    Thread(target=site.serve_forever, daemon=True).start()
    try:
        with server.app.test_client() as test_client:
            response = test_client.get(
                "/website-scanner/scan",
                query_string={
                    "url": f"http://127.0.0.1:{site.server_port}/",
                    "visible": "0",
                    "scan_id": "123e4567-e89b-42d3-a456-426614174003",
                },
            )
        events = [
            json.loads(line[6:])
            for line in response.get_data(as_text=True).splitlines()
            if line.startswith("data: ")
        ]
        result = next((event for event in events if event["type"] == "result"), None)
        assert result is not None, response.get_data(as_text=True)

        assert response.status_code == 200
        assert result["summary"]["pages"] == "2/2"
        assert result["summary"]["css"] == "1/1"
        assert result["summary"]["interactions_passed"] == 1
        assert "Run test" in result["text"]
    finally:
        site.shutdown()
        site.server_close()
