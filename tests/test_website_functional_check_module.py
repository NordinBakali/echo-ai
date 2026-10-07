import website_functional_check as wfc


def test_check_links_reports_every_link_entry_and_caches_http_probe(monkeypatch):
    calls = []

    def fake_probe(url, timeout, method="GET", payload=None):
        calls.append((url, method))
        return {
            "ok": True,
            "status": 200,
            "url": url,
            "error": "",
            "body": "ok",
            "content_type": "text/html",
        }

    monkeypatch.setattr(wfc, "probe_url", fake_probe)

    links = [
        {"href": "#top"},
        {"href": "mailto:admin@example.com"},
        {"href": "javascript:void(0)"},
        {"href": "/contact"},
        {"href": "/contact"},
    ]

    results = wfc.check_links("https://example.com", links, timeout=8)

    assert len(results) == 5
    assert results[0]["status"] == "ok"
    assert results[1]["status"] == "ok"
    assert results[2]["status"] == "warning"
    assert results[3]["status"] == "ok"
    assert results[4]["status"] == "ok"
    assert "shared target" in str(results[4]["message"]).lower()

    # The duplicated HTTP target should be probed once because the checker caches per URL.
    assert calls == [("https://example.com/contact", "GET")]


def test_check_stylesheets_flags_broken_and_html_css_responses(monkeypatch):
    def fake_probe(url, timeout, method="GET", payload=None):
        if url.endswith("main.css"):
            return {
                "ok": True,
                "status": 200,
                "url": url,
                "error": "",
                "body": "body { color: red; }",
                "content_type": "text/css; charset=utf-8",
            }
        if url.endswith("broken.css"):
            return {
                "ok": False,
                "status": 404,
                "url": url,
                "error": "HTTP Error 404: Not Found",
                "body": "",
                "content_type": "text/plain",
            }
        return {
            "ok": True,
            "status": 200,
            "url": url,
            "error": "",
            "body": "<!doctype html><html><body>wrong file</body></html>",
            "content_type": "text/html; charset=utf-8",
        }

    monkeypatch.setattr(wfc, "probe_url", fake_probe)

    stylesheets = [
        {"href": "/main.css", "id": "main-css", "media": "all", "rel": "stylesheet", "as": ""},
        {"href": "/broken.css", "id": "broken-css", "media": "all", "rel": "stylesheet", "as": ""},
        {"href": "/layout.css", "id": "layout-css", "media": "all", "rel": "stylesheet", "as": ""},
    ]

    results = wfc.check_stylesheets(
        "https://example.com",
        stylesheets,
        inline_style_blocks=1,
        timeout=8,
    )

    assert len(results) == 4
    assert results[0]["status"] == "ok"
    assert results[1]["status"] == "failed"
    assert results[2]["status"] == "failed"
    assert results[3]["id"] == "inline-style"
    assert results[3]["status"] == "ok"

    summary = wfc.build_summary({"ok": True, "status": 200}, [], [], [], results)
    assert summary["css_total"] == 4
    assert summary["css_ok"] == 2
    assert summary["css_failed"] == 2
