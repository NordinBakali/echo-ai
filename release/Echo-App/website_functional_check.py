import argparse
import json
from datetime import datetime, timezone
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from typing import Callable, Dict, List, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urljoin, urlparse, urlunparse
from urllib.request import Request, urlopen
import webbrowser

USER_AGENT = "EchoWebsiteFunctionalChecker/1.0"
DEFAULT_TIMEOUT = 10
MAX_BODY_BYTES = 400_000
SEARCH_HINTS = ("search", "zoek", "zoeken", "query", "q")
BUTTON_CLASS_HINTS = ("btn", "button")


ProgressCallback = Optional[Callable[[Dict[str, object]], None]]


def clamp_percent(value: object, fallback: int = 0) -> int:
    try:
        percent = int(round(float(value)))
    except Exception:
        percent = int(fallback)
    return max(0, min(100, percent))


def progress_in_span(index: int, total: int, start: int, end: int) -> int:
    if total <= 0:
        return clamp_percent(start, start)
    ratio = max(0.0, min(1.0, float(index) / float(total)))
    return clamp_percent(start + ((end - start) * ratio), start)


def emit_progress(
    progress_callback: ProgressCallback,
    stage: str,
    progress_percent: object,
    message: str = "",
    current_test: Optional[Dict[str, object]] = None,
) -> None:
    if not callable(progress_callback):
        return

    payload: Dict[str, object] = {
        "stage": str(stage or "").strip().lower(),
        "progress_percent": clamp_percent(progress_percent, 0),
        "message": str(message or "").strip(),
    }

    if isinstance(current_test, dict) and current_test:
        payload["current_test"] = current_test

    try:
        progress_callback(payload)
    except Exception:
        pass


class InteractionParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: List[Dict[str, str]] = []
        self.buttons: List[Dict[str, str]] = []
        self.stylesheets: List[Dict[str, str]] = []
        self.forms: Dict[str, Dict[str, object]] = {}
        self.search_inputs: List[Dict[str, str]] = []
        self.inline_style_blocks = 0
        self._form_stack: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[tuple]) -> None:
        tag = str(tag or "").lower()
        attr_map: Dict[str, str] = {}
        for key, value in attrs:
            if not key:
                continue
            attr_map[str(key).lower()] = (value or "").strip()

        if tag == "form":
            form_key = f"form-{len(self.forms) + 1}"
            self.forms[form_key] = {
                "id": attr_map.get("id", ""),
                "action": attr_map.get("action", ""),
                "method": (attr_map.get("method", "get") or "get").lower(),
                "inputs": [],
            }
            self._form_stack.append(form_key)
            return

        active_form = self._form_stack[-1] if self._form_stack else ""

        if tag == "a":
            href = attr_map.get("href", "")
            if href:
                self.links.append({
                    "href": href,
                    "id": attr_map.get("id", ""),
                    "class": attr_map.get("class", ""),
                    "role": attr_map.get("role", ""),
                })

            class_value = attr_map.get("class", "").lower()
            role_value = attr_map.get("role", "").lower()
            has_button_style = any(token in class_value for token in BUTTON_CLASS_HINTS)
            if role_value == "button" or has_button_style:
                self.buttons.append({
                    "kind": "link-button",
                    "form_ref": active_form,
                    "href": href,
                    "id": attr_map.get("id", ""),
                    "class": attr_map.get("class", ""),
                    "type": "button",
                    "onclick": attr_map.get("onclick", ""),
                    "formaction": "",
                    "formmethod": "",
                    "disabled": "disabled" in attr_map,
                    "value": attr_map.get("title", "") or attr_map.get("aria-label", ""),
                })
            return

        if tag == "link":
            rel_tokens = {token.strip().lower() for token in str(attr_map.get("rel", "")).split() if token.strip()}
            as_value = str(attr_map.get("as", "")).strip().lower()
            href = attr_map.get("href", "")
            is_stylesheet = "stylesheet" in rel_tokens or ("preload" in rel_tokens and as_value == "style")

            if href and is_stylesheet:
                self.stylesheets.append({
                    "href": href,
                    "id": attr_map.get("id", ""),
                    "media": attr_map.get("media", ""),
                    "rel": attr_map.get("rel", ""),
                    "as": as_value,
                })
            return

        if tag == "style":
            self.inline_style_blocks += 1
            return

        if tag == "input":
            input_type = (attr_map.get("type", "text") or "text").lower()
            field = {
                "name": attr_map.get("name", ""),
                "id": attr_map.get("id", ""),
                "type": input_type,
                "placeholder": attr_map.get("placeholder", ""),
                "class": attr_map.get("class", ""),
                "aria_label": attr_map.get("aria-label", ""),
                "value": attr_map.get("value", ""),
            }

            if active_form:
                self.forms[active_form]["inputs"].append(field)

            if is_search_field(field):
                self.search_inputs.append({
                    "form_ref": active_form,
                    "name": field["name"],
                    "id": field["id"],
                    "placeholder": field["placeholder"],
                    "type": input_type,
                })

            if input_type in {"submit", "button", "reset", "image"}:
                self.buttons.append({
                    "kind": "input-button",
                    "form_ref": active_form,
                    "href": "",
                    "id": attr_map.get("id", ""),
                    "class": attr_map.get("class", ""),
                    "type": input_type,
                    "onclick": attr_map.get("onclick", ""),
                    "formaction": attr_map.get("formaction", ""),
                    "formmethod": attr_map.get("formmethod", ""),
                    "disabled": "disabled" in attr_map,
                    "value": attr_map.get("value", ""),
                })
            return

        if tag == "button":
            self.buttons.append({
                "kind": "button",
                "form_ref": active_form,
                "href": "",
                "id": attr_map.get("id", ""),
                "class": attr_map.get("class", ""),
                "type": (attr_map.get("type", "submit") or "submit").lower(),
                "onclick": attr_map.get("onclick", ""),
                "formaction": attr_map.get("formaction", ""),
                "formmethod": attr_map.get("formmethod", ""),
                "disabled": "disabled" in attr_map,
                "value": attr_map.get("value", "") or attr_map.get("aria-label", "") or attr_map.get("title", ""),
            })
            return

        if tag in {"textarea", "select"} and active_form:
            self.forms[active_form]["inputs"].append({
                "name": attr_map.get("name", ""),
                "id": attr_map.get("id", ""),
                "type": tag,
                "placeholder": attr_map.get("placeholder", ""),
                "class": attr_map.get("class", ""),
                "aria_label": attr_map.get("aria-label", ""),
                "value": "",
            })

    def handle_endtag(self, tag: str) -> None:
        if str(tag or "").lower() == "form" and self._form_stack:
            self._form_stack.pop()


def normalize_url(raw_url: str) -> str:
    candidate = str(raw_url or "").strip()
    if not candidate:
        return ""

    if not candidate.lower().startswith(("http://", "https://")):
        candidate = "https://" + candidate

    parsed = urlparse(candidate)
    if not parsed.netloc:
        return ""

    path = parsed.path or "/"
    if path != "/" and path.endswith("/"):
        path = path[:-1]

    normalized = f"{parsed.scheme.lower()}://{parsed.netloc.lower()}{path}"
    if parsed.query:
        normalized = f"{normalized}?{parsed.query}"
    return normalized


def looks_like_search(value: str) -> bool:
    lowered = str(value or "").strip().lower()
    if not lowered:
        return False
    return any(hint in lowered for hint in SEARCH_HINTS)


def is_search_field(field: Dict[str, str]) -> bool:
    field_type = (field.get("type") or "").lower()
    if field_type == "search":
        return True

    candidates = [
        field.get("name", ""),
        field.get("id", ""),
        field.get("placeholder", ""),
        field.get("class", ""),
        field.get("aria_label", ""),
    ]
    return any(looks_like_search(item) for item in candidates)


def strip_fragment(url: str) -> str:
    parsed = urlparse(url)
    return urlunparse(parsed._replace(fragment=""))


def append_query(url: str, values: Dict[str, str]) -> str:
    parsed = urlparse(url)
    merged = dict(parse_qsl(parsed.query, keep_blank_values=True))
    merged.update(values)
    query = urlencode(merged, doseq=True)
    return urlunparse(parsed._replace(query=query))


def should_skip_href(href: str) -> bool:
    return bool(href_skip_reason(href))


def href_skip_reason(href: str) -> str:
    value = str(href or "").strip().lower()
    if not value:
        return "empty"
    if value.startswith("#"):
        return "fragment"
    if value.startswith("javascript:"):
        return "javascript"
    if value.startswith("mailto:"):
        return "mailto"
    if value.startswith("tel:"):
        return "tel"
    if value.startswith("sms:"):
        return "sms"
    return ""


def normalize_http_method(value: str, fallback: str = "get") -> str:
    method = str(value or fallback).strip().lower() or fallback
    if method in {"get", "post", "put", "patch", "delete", "head", "options"}:
        return method
    return str(fallback or "get").strip().lower() or "get"


def probe_url(
    url: str,
    timeout: int,
    method: str = "GET",
    payload: Optional[Dict[str, str]] = None,
) -> Dict[str, object]:
    method = str(method or "GET").upper()
    data = None
    target = url

    if method == "GET" and payload:
        target = append_query(url, payload)
    elif method == "POST" and payload is not None:
        data = urlencode(payload, doseq=True).encode("utf-8")

    request = Request(
        target,
        data=data,
        headers={"User-Agent": USER_AGENT},
        method=method,
    )
    if data is not None:
        request.add_header("Content-Type", "application/x-www-form-urlencoded")

    try:
        with urlopen(request, timeout=timeout) as response:
            status = int(getattr(response, "status", response.getcode()))
            body = response.read(MAX_BODY_BYTES).decode("utf-8", errors="replace")
            content_type = str(response.headers.get("Content-Type", "") or "").strip().lower()
            return {
                "ok": status < 400,
                "status": status,
                "url": str(response.geturl() or target),
                "error": "",
                "body": body,
                "content_type": content_type,
            }
    except HTTPError as error:
        body = ""
        error_headers = getattr(error, "headers", None)
        try:
            body = error.read(MAX_BODY_BYTES).decode("utf-8", errors="replace")
        except Exception:
            body = ""
        return {
            "ok": False,
            "status": int(error.code),
            "url": target,
            "error": str(error),
            "body": body,
            "content_type": str(error_headers.get("Content-Type", "") if error_headers else "").strip().lower(),
        }
    except URLError as error:
        return {
            "ok": False,
            "status": None,
            "url": target,
            "error": str(getattr(error, "reason", error)),
            "body": "",
            "content_type": "",
        }
    except Exception as error:
        return {
            "ok": False,
            "status": None,
            "url": target,
            "error": str(error),
            "body": "",
            "content_type": "",
        }


def build_button_label(button: Dict[str, str], index: int) -> str:
    chunks = [
        str(button.get("id") or "").strip(),
        str(button.get("value") or "").strip(),
        str(button.get("class") or "").strip(),
    ]
    for chunk in chunks:
        if chunk:
            return chunk[:80]
    return f"button-{index}"


def build_safe_form_payload(form: Optional[Dict[str, object]], force_search: bool = False) -> Dict[str, str]:
    if not form:
        return {"q": "echo test"} if force_search else {}

    payload: Dict[str, str] = {}
    inputs = form.get("inputs", [])
    if not isinstance(inputs, list):
        return {"q": "echo test"} if force_search else {}

    search_field_name = ""

    for entry in inputs:
        if not isinstance(entry, dict):
            continue

        field_type = str(entry.get("type") or "text").lower()
        name = str(entry.get("name") or entry.get("id") or "").strip()
        if not name:
            continue

        if field_type in {"hidden", "submit", "button", "reset", "image", "file", "password", "checkbox", "radio"}:
            continue

        if is_search_field({
            "name": str(entry.get("name") or ""),
            "id": str(entry.get("id") or ""),
            "placeholder": str(entry.get("placeholder") or ""),
            "class": str(entry.get("class") or ""),
            "aria_label": str(entry.get("aria_label") or ""),
            "type": field_type,
        }):
            search_field_name = name

        if name not in payload:
            payload[name] = "echo-test"

    if search_field_name:
        payload[search_field_name] = "echo test"
    elif force_search:
        payload["q"] = "echo test"

    return payload


def check_links(
    base_url: str,
    links: List[Dict[str, str]],
    timeout: int,
    progress_callback: ProgressCallback = None,
) -> List[Dict[str, object]]:
    results: List[Dict[str, object]] = []
    totaal = len(links)
    if totaal <= 0:
        emit_progress(progress_callback, "links", 52, "No links detected.")
        return results

    probe_cache: Dict[str, Dict[str, object]] = {}

    for positie, link in enumerate(links, start=1):
        href = str(link.get("href") or "").strip()
        raw_id = str(link.get("id") or "").strip()
        link_id = raw_id or f"link-{positie}"
        progress = progress_in_span(positie - 1, totaal, 20, 52)
        emit_progress(
            progress_callback,
            "links",
            progress,
            f"Testing link {positie}/{totaal}: {href or '(empty href)'}",
            current_test={
                "type": "link",
                "id": link_id,
                "target": href,
            },
        )

        skip_reason = href_skip_reason(href)
        if skip_reason == "empty":
            results.append({
                "id": link_id,
                "status": "failed",
                "method": "n/a",
                "target": "",
                "http_status": None,
                "message": "Empty href attribute.",
            })
            continue

        if skip_reason == "fragment":
            results.append({
                "id": link_id,
                "status": "ok",
                "method": "n/a",
                "target": href,
                "http_status": None,
                "message": "In-page anchor link (no HTTP probe needed).",
            })
            continue

        if skip_reason in {"mailto", "tel", "sms"}:
            results.append({
                "id": link_id,
                "status": "ok",
                "method": "n/a",
                "target": href,
                "http_status": None,
                "message": f"{skip_reason.upper()} link detected.",
            })
            continue

        if skip_reason == "javascript":
            results.append({
                "id": link_id,
                "status": "warning",
                "method": "js",
                "target": href,
                "http_status": None,
                "message": "JavaScript link cannot be validated with HTTP probe.",
            })
            continue

        absolute = strip_fragment(urljoin(base_url, href))
        parsed = urlparse(absolute)
        if parsed.scheme not in {"http", "https"}:
            results.append({
                "id": link_id,
                "status": "warning",
                "method": "n/a",
                "target": absolute,
                "http_status": None,
                "message": "Non-HTTP scheme skipped.",
            })
            continue

        if absolute in probe_cache:
            probe = probe_cache[absolute]
            reused_probe = True
        else:
            probe = probe_url(absolute, timeout=timeout)
            probe_cache[absolute] = probe
            reused_probe = False

        results.append({
            "id": link_id,
            "target": absolute,
            "method": "get",
            "status": "ok" if probe["ok"] else "failed",
            "http_status": probe["status"],
            "message": (
                "Reachable"
                if probe["ok"] and not reused_probe
                else ("Reachable (shared target)" if probe["ok"] else (probe["error"] or "HTTP failure"))
            ),
        })

    emit_progress(progress_callback, "links", 52, "Link checks completed.")
    return results


def check_buttons(
    base_url: str,
    buttons: List[Dict[str, str]],
    forms: Dict[str, Dict[str, object]],
    timeout: int,
    progress_callback: ProgressCallback = None,
) -> List[Dict[str, object]]:
    results: List[Dict[str, object]] = []
    totaal = len(buttons)

    if totaal <= 0:
        emit_progress(progress_callback, "buttons", 78, "No buttons detected.")
        return results

    for index, button in enumerate(buttons, start=1):
        label = build_button_label(button, index)
        progress = progress_in_span(index - 1, totaal, 53, 78)
        emit_progress(
            progress_callback,
            "buttons",
            progress,
            f"Testing button {index}/{totaal}: {label}",
            current_test={
                "type": "button",
                "id": label,
                "target": str(button.get("href") or button.get("formaction") or "").strip(),
            },
        )

        if button.get("disabled"):
            results.append({
                "id": label,
                "status": "warning",
                "method": "n/a",
                "target": "",
                "http_status": None,
                "message": "Button is disabled and was not executed.",
            })
            continue

        form_ref = str(button.get("form_ref") or "")
        form = forms.get(form_ref)

        onclick = str(button.get("onclick") or "").strip()
        kind = str(button.get("kind") or "").strip().lower()

        method = "get"
        target = ""
        payload: Dict[str, str] = {}

        if kind == "link-button":
            target = str(button.get("href") or "")
            skip_reason = href_skip_reason(target)

            if skip_reason == "empty":
                results.append({
                    "id": label,
                    "status": "failed",
                    "method": "n/a",
                    "target": "",
                    "http_status": None,
                    "message": "Button link has empty href.",
                })
                continue

            if skip_reason == "fragment":
                results.append({
                    "id": label,
                    "status": "ok",
                    "method": "n/a",
                    "target": target,
                    "http_status": None,
                    "message": "In-page anchor button (no HTTP probe needed).",
                })
                continue

            if skip_reason in {"mailto", "tel", "sms"}:
                results.append({
                    "id": label,
                    "status": "ok",
                    "method": "n/a",
                    "target": target,
                    "http_status": None,
                    "message": f"{skip_reason.upper()} button link detected.",
                })
                continue

            if skip_reason == "javascript":
                results.append({
                    "id": label,
                    "status": "warning",
                    "method": "js",
                    "target": target,
                    "http_status": None,
                    "message": "JavaScript button cannot be validated with HTTP probe.",
                })
                continue
        else:
            form_method = str(button.get("formmethod") or "").strip().lower()
            if form_method:
                method = normalize_http_method(form_method, fallback="get")
            elif form and isinstance(form.get("method"), str):
                method = normalize_http_method(str(form.get("method") or "get"), fallback="get")
            else:
                method = normalize_http_method(method, fallback="get")

            target = str(button.get("formaction") or "").strip()
            if not target and form and isinstance(form.get("action"), str):
                target = str(form.get("action") or "").strip()
            if not target:
                target = base_url

            payload = build_safe_form_payload(form)

        if onclick and not target and not form:
            results.append({
                "id": label,
                "status": "warning",
                "method": "js",
                "target": "",
                "http_status": None,
                "message": "JS-only button cannot be verified with HTTP probe.",
            })
            continue

        if target and should_skip_href(target):
            results.append({
                "id": label,
                "status": "warning",
                "method": method,
                "target": target,
                "http_status": None,
                "message": "Button target uses non-HTTP scheme and was skipped.",
            })
            continue

        absolute_target = strip_fragment(urljoin(base_url, target or base_url))
        parsed = urlparse(absolute_target)
        if parsed.scheme not in {"http", "https"}:
            results.append({
                "id": label,
                "status": "warning",
                "method": method,
                "target": absolute_target,
                "http_status": None,
                "message": "Button target uses non-HTTP scheme and was skipped.",
            })
            continue

        if method != "get":
            safe_probe = probe_url(absolute_target, timeout=timeout, method="GET")
            safe_ok = bool(safe_probe.get("ok"))
            results.append({
                "id": label,
                "status": "warning" if safe_ok else "failed",
                "method": method,
                "target": absolute_target,
                "http_status": safe_probe.get("status"),
                "message": (
                    "Non-GET button was not auto-executed; target is reachable via safe GET probe."
                    if safe_ok
                    else "Non-GET button target is not reachable with safe GET probe."
                ),
            })
            continue

        probe = probe_url(absolute_target, timeout=timeout, method="GET", payload=payload)
        results.append({
            "id": label,
            "status": "ok" if probe["ok"] else "failed",
            "method": "get",
            "target": probe["url"],
            "http_status": probe["status"],
            "message": "Button target reachable" if probe["ok"] else (probe["error"] or "HTTP failure"),
        })

    emit_progress(progress_callback, "buttons", 78, "Button checks completed.")
    return results


def check_search_bars(
    base_url: str,
    search_inputs: List[Dict[str, str]],
    forms: Dict[str, Dict[str, object]],
    timeout: int,
    progress_callback: ProgressCallback = None,
) -> List[Dict[str, object]]:
    if not search_inputs:
        emit_progress(progress_callback, "search_bars", 90, "No search bar detected on the page.")
        return [{
            "id": "search-1",
            "status": "failed",
            "method": "n/a",
            "target": "",
            "http_status": None,
            "message": "No search bar detected on the page.",
        }]

    results: List[Dict[str, object]] = []
    totaal = len(search_inputs)

    for index, field in enumerate(search_inputs, start=1):
        progress = progress_in_span(index - 1, totaal, 79, 90)
        form_ref = str(field.get("form_ref") or "")
        form = forms.get(form_ref)

        method = "get"
        action = ""
        if form and isinstance(form.get("method"), str):
            method = str(form.get("method") or "get").strip().lower() or "get"
        if form and isinstance(form.get("action"), str):
            action = str(form.get("action") or "").strip()

        target = strip_fragment(urljoin(base_url, action or base_url))
        search_id = f"search-{index}"

        emit_progress(
            progress_callback,
            "search_bars",
            progress,
            f"Testing search bar {index}/{totaal}: {target}",
            current_test={
                "type": "search",
                "id": search_id,
                "target": target,
            },
        )

        if method != "get":
            results.append({
                "id": search_id,
                "status": "warning",
                "method": method,
                "target": target,
                "http_status": None,
                "message": "Non-GET search form was not auto-submitted.",
            })
            continue

        payload = build_safe_form_payload(form, force_search=True)
        field_name = str(field.get("name") or field.get("id") or "q").strip() or "q"
        payload[field_name] = "echo test"

        probe = probe_url(target, timeout=timeout, method="GET", payload=payload)
        message = "Search request responded" if probe["ok"] else (probe["error"] or "HTTP failure")

        results.append({
            "id": search_id,
            "status": "ok" if probe["ok"] else "failed",
            "method": "get",
            "target": probe["url"],
            "http_status": probe["status"],
            "message": message,
        })

    emit_progress(progress_callback, "search_bars", 90, "Search checks completed.")
    return results


def check_stylesheets(
    base_url: str,
    stylesheets: List[Dict[str, str]],
    inline_style_blocks: int,
    timeout: int,
    progress_callback: ProgressCallback = None,
) -> List[Dict[str, object]]:
    results: List[Dict[str, object]] = []
    probe_cache: Dict[str, Dict[str, object]] = {}

    total_items = len(stylesheets) + (1 if inline_style_blocks > 0 else 0)
    if total_items <= 0:
        emit_progress(progress_callback, "summary", 93, "No stylesheet links or inline style blocks detected.")
        return [{
            "id": "css-1",
            "status": "failed",
            "method": "n/a",
            "target": "",
            "http_status": None,
            "message": "No stylesheet links or inline <style> blocks detected.",
        }]

    for index, stylesheet in enumerate(stylesheets, start=1):
        href = str(stylesheet.get("href") or "").strip()
        style_id = str(stylesheet.get("id") or "").strip() or f"css-{index}"
        media = str(stylesheet.get("media") or "").strip()
        rel_value = str(stylesheet.get("rel") or "").strip() or "stylesheet"

        progress = progress_in_span(index - 1, total_items, 90, 93)
        emit_progress(
            progress_callback,
            "summary",
            progress,
            f"Checking stylesheet {index}/{len(stylesheets)}: {href or '(empty href)'}",
            current_test={
                "type": "stylesheet",
                "id": style_id,
                "target": href,
            },
        )

        skip_reason = href_skip_reason(href)
        if skip_reason == "empty":
            results.append({
                "id": style_id,
                "status": "failed",
                "method": "get",
                "target": "",
                "http_status": None,
                "message": "Stylesheet link has empty href.",
            })
            continue

        if skip_reason in {"fragment", "javascript", "mailto", "tel", "sms"}:
            results.append({
                "id": style_id,
                "status": "warning",
                "method": "get",
                "target": href,
                "http_status": None,
                "message": "Stylesheet href uses unsupported scheme for HTTP probe.",
            })
            continue

        absolute = strip_fragment(urljoin(base_url, href))
        parsed = urlparse(absolute)
        if parsed.scheme not in {"http", "https"}:
            results.append({
                "id": style_id,
                "status": "warning",
                "method": "get",
                "target": absolute,
                "http_status": None,
                "message": "Stylesheet uses non-HTTP scheme.",
            })
            continue

        if absolute in probe_cache:
            probe = probe_cache[absolute]
            reused_probe = True
        else:
            probe = probe_url(absolute, timeout=timeout, method="GET")
            probe_cache[absolute] = probe
            reused_probe = False

        status = "ok" if probe.get("ok") else "failed"
        message = "Stylesheet loaded successfully."

        if not probe.get("ok"):
            message = probe.get("error") or "Stylesheet request failed."
        else:
            content_type = str(probe.get("content_type") or "").strip().lower()
            body = str(probe.get("body") or "")
            body_preview = body.lstrip().lower()[:240]
            looks_like_html = body_preview.startswith("<!doctype html") or body_preview.startswith("<html") or "<html" in body_preview

            if not body.strip():
                status = "failed"
                message = "Stylesheet response body is empty."
            elif looks_like_html:
                status = "failed"
                message = "Stylesheet URL returned HTML instead of CSS."
            elif content_type and "css" not in content_type:
                status = "warning"
                message = f"Unexpected stylesheet Content-Type: {content_type}."
            elif reused_probe:
                message = "Stylesheet loaded successfully (shared target)."

        details = [message]
        if media:
            details.append(f"media={media}")
        details.append(f"rel={rel_value}")

        results.append({
            "id": style_id,
            "status": status,
            "method": "get",
            "target": absolute,
            "http_status": probe.get("status"),
            "message": " | ".join(details),
        })

    if inline_style_blocks > 0:
        inline_progress = progress_in_span(len(stylesheets), total_items, 90, 93)
        emit_progress(
            progress_callback,
            "summary",
            inline_progress,
            f"Detected {inline_style_blocks} inline style block(s).",
            current_test={
                "type": "stylesheet",
                "id": "inline-style",
                "target": "inline <style>",
            },
        )
        results.append({
            "id": "inline-style",
            "status": "ok",
            "method": "inline",
            "target": "inline <style>",
            "http_status": None,
            "message": f"Detected {inline_style_blocks} inline <style> block(s).",
        })

    emit_progress(progress_callback, "summary", 93, "Stylesheet checks completed.")
    return results


def count_status(items: List[Dict[str, object]], value: str) -> int:
    return sum(1 for item in items if str(item.get("status") or "").lower() == value)


def sanitize_slug(value: str) -> str:
    slug = "".join(char.lower() if char.isalnum() else "-" for char in str(value or ""))
    while "--" in slug:
        slug = slug.replace("--", "-")
    slug = slug.strip("-")
    return slug or "site"


def build_default_visual_output_path(target_url: str) -> str:
    host = urlparse(str(target_url or "")).netloc or "site"
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return str(Path("reports") / "website-audits" / f"functional-check-{sanitize_slug(host)}-{timestamp}.html")


def status_css_class(status: str) -> str:
    normalized = str(status or "").strip().lower()
    if normalized == "ok":
        return "status-ok"
    if normalized == "warning":
        return "status-warning"
    if normalized in {"failed", "issues"}:
        return "status-failed"
    return "status-unknown"


def format_http_status(value: object) -> str:
    if value in (None, ""):
        return "-"
    return str(value)


def build_metric_card(title: str, value: str, subtitle: str) -> str:
    return (
        '<article class="metric-card">'
        f"<h3>{escape(title)}</h3>"
        f'<p class="metric-value">{escape(value)}</p>'
        f'<p class="metric-subtitle">{escape(subtitle)}</p>'
        "</article>"
    )


def build_section_html(title: str, entries: List[Dict[str, object]], default_method: str = "-") -> str:
    rows: List[str] = []

    if not entries:
        rows.append('<tr><td colspan="6" class="empty-row">No items detected.</td></tr>')

    for item in entries:
        raw_status = str(item.get("status") or "unknown").strip().lower()
        status_label = raw_status.upper() if raw_status else "UNKNOWN"
        method = str(item.get("method") or default_method).strip().upper() or "-"
        target = str(item.get("target") or "").strip()
        message = str(item.get("message") or "").strip() or "-"
        item_id = str(item.get("id") or "").strip() or "-"

        if target:
            safe_target = escape(target)
            target_html = (
                f'<a href="{safe_target}" target="_blank" rel="noopener noreferrer">'
                f"{safe_target}"
                "</a>"
            )
        else:
            target_html = "-"

        rows.append(
            "<tr>"
            f"<td>{escape(item_id)}</td>"
            f'<td><span class="status-badge {status_css_class(raw_status)}">{escape(status_label)}</span></td>'
            f"<td>{escape(method)}</td>"
            f"<td>{escape(format_http_status(item.get('http_status')))}</td>"
            f"<td>{target_html}</td>"
            f"<td>{escape(message)}</td>"
            "</tr>"
        )

    table = [
        '<section class="section-card">',
        f"<h2>{escape(title)}</h2>",
        '<div class="table-wrap">',
        '<table class="result-table">',
        "<thead>",
        "<tr>",
        "<th>ID</th>",
        "<th>Status</th>",
        "<th>Method</th>",
        "<th>HTTP</th>",
        "<th>Target</th>",
        "<th>Message</th>",
        "</tr>",
        "</thead>",
        "<tbody>",
        *rows,
        "</tbody>",
        "</table>",
        "</div>",
        "</section>",
    ]
    return "\n".join(table)


def build_visual_report_html(report: Dict[str, object]) -> str:
    summary = report.get("summary", {}) if isinstance(report.get("summary"), dict) else {}
    target_url = str(report.get("target_url") or "")
    scanned_at = str(report.get("scanned_at") or "")
    overall_status = str(summary.get("overall_status") or "unknown")
    homepage_ok = bool(summary.get("homepage_ok"))
    homepage_status = format_http_status(summary.get("homepage_http_status"))

    cards = [
        build_metric_card("Homepage", "OK" if homepage_ok else "FAILED", f"HTTP {homepage_status}"),
        build_metric_card(
            "Links",
            f"{summary.get('links_ok', 0)}/{summary.get('links_total', 0)}",
            f"Failed: {summary.get('links_failed', 0)} | Warning: {summary.get('links_warning', 0)}",
        ),
        build_metric_card(
            "Buttons",
            f"{summary.get('buttons_ok', 0)}/{summary.get('buttons_total', 0)}",
            f"Failed: {summary.get('buttons_failed', 0)} | Warning: {summary.get('buttons_warning', 0)}",
        ),
        build_metric_card(
            "Search Bars",
            f"{summary.get('search_ok', 0)}/{summary.get('search_total', 0)}",
            f"Failed: {summary.get('search_failed', 0)} | Warning: {summary.get('search_warning', 0)}",
        ),
        build_metric_card(
            "Stylesheets",
            f"{summary.get('css_ok', 0)}/{summary.get('css_total', 0)}",
            f"Failed: {summary.get('css_failed', 0)} | Warning: {summary.get('css_warning', 0)}",
        ),
    ]

    note_rows: List[str] = []
    notes = report.get("notes", [])
    if isinstance(notes, list):
        for note in notes:
            note_text = str(note).strip()
            if note_text:
                note_rows.append(f"<li>{escape(note_text)}</li>")

    html_parts = [
        "<!doctype html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>Echo Website Functional Report</title>",
        "<style>",
        "body { margin: 0; font-family: 'Segoe UI', Tahoma, Arial, sans-serif; background: linear-gradient(160deg, #071a2b 0%, #102a43 52%, #0b1f36 100%); color: #e9f2ff; }",
        ".wrap { width: min(1280px, 94vw); margin: 20px auto 36px; display: grid; gap: 14px; }",
        ".header { background: rgba(7, 26, 43, 0.72); border: 1px solid rgba(97, 218, 251, 0.24); border-radius: 14px; padding: 16px 18px; }",
        ".kicker { letter-spacing: 0.12em; text-transform: uppercase; color: #8ed0ff; font-size: 12px; margin: 0 0 8px; }",
        "h1 { margin: 0 0 8px; font-size: clamp(1.4rem, 2.2vw, 2rem); }",
        ".meta { margin: 0; opacity: 0.92; word-break: break-all; }",
        ".overall-pill { display: inline-block; margin-top: 10px; padding: 6px 12px; border-radius: 999px; font-weight: 700; letter-spacing: 0.06em; }",
        ".summary-grid { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 10px; }",
        ".metric-card { background: rgba(6, 21, 36, 0.72); border: 1px solid rgba(97, 218, 251, 0.22); border-radius: 12px; padding: 12px; }",
        ".metric-card h3 { margin: 0; font-size: 13px; letter-spacing: 0.08em; text-transform: uppercase; color: #8ed0ff; }",
        ".metric-value { margin: 8px 0 4px; font-size: 1.34rem; font-weight: 700; }",
        ".metric-subtitle { margin: 0; font-size: 0.92rem; color: #cde6ff; opacity: 0.92; }",
        ".section-card { background: rgba(6, 21, 36, 0.72); border: 1px solid rgba(97, 218, 251, 0.22); border-radius: 12px; padding: 12px; }",
        ".section-card h2 { margin: 0 0 8px; font-size: 1.02rem; letter-spacing: 0.04em; text-transform: uppercase; color: #9dd9ff; }",
        ".table-wrap { overflow: auto; border-radius: 8px; }",
        ".result-table { width: 100%; border-collapse: collapse; min-width: 860px; font-size: 0.93rem; }",
        ".result-table th, .result-table td { text-align: left; padding: 9px 10px; border-bottom: 1px solid rgba(128, 178, 215, 0.2); vertical-align: top; }",
        ".result-table th { position: sticky; top: 0; background: rgba(3, 12, 20, 0.98); color: #8ed0ff; font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; }",
        ".result-table a { color: #7fe6ff; text-decoration: none; word-break: break-all; }",
        ".result-table a:hover { text-decoration: underline; }",
        ".status-badge { display: inline-block; min-width: 72px; text-align: center; padding: 4px 8px; border-radius: 999px; font-size: 12px; font-weight: 700; letter-spacing: 0.05em; }",
        ".status-ok { background: rgba(20, 187, 96, 0.2); border: 1px solid rgba(44, 223, 129, 0.6); color: #b8ffd8; }",
        ".status-warning { background: rgba(219, 147, 27, 0.18); border: 1px solid rgba(255, 190, 92, 0.58); color: #ffddb2; }",
        ".status-failed { background: rgba(205, 68, 68, 0.2); border: 1px solid rgba(255, 111, 111, 0.58); color: #ffd2d2; }",
        ".status-unknown { background: rgba(102, 139, 171, 0.2); border: 1px solid rgba(150, 190, 226, 0.55); color: #d8edff; }",
        ".empty-row { text-align: center; opacity: 0.86; font-style: italic; }",
        ".notes { background: rgba(5, 18, 32, 0.75); border: 1px solid rgba(97, 218, 251, 0.22); border-radius: 12px; padding: 12px 14px; }",
        ".notes h2 { margin: 0 0 8px; font-size: 1rem; text-transform: uppercase; letter-spacing: 0.06em; color: #9dd9ff; }",
        ".notes ul { margin: 0; padding-left: 18px; }",
        ".notes li { margin: 6px 0; }",
        "@media (max-width: 1100px) { .summary-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); } }",
        "@media (max-width: 780px) { .summary-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }",
        "@media (max-width: 640px) { .wrap { width: 96vw; } .summary-grid { grid-template-columns: 1fr; } .result-table { min-width: 640px; } }",
        "</style>",
        "</head>",
        "<body>",
        '<main class="wrap">',
        '<section class="header">',
        '<p class="kicker">Echo Functional Scanner</p>',
        "<h1>Website Functional Report</h1>",
        f'<p class="meta">Target: {escape(target_url)}</p>',
        f'<p class="meta">Scanned at: {escape(scanned_at)}</p>',
        f'<span class="overall-pill {status_css_class(overall_status)}">Overall: {escape(overall_status.upper())}</span>',
        "</section>",
        '<section class="summary-grid">',
        *cards,
        "</section>",
        build_section_html("Links", report.get("links", []) if isinstance(report.get("links"), list) else [], default_method="GET"),
        build_section_html("Buttons", report.get("buttons", []) if isinstance(report.get("buttons"), list) else [], default_method="-"),
        build_section_html("Search Bars", report.get("search_bars", []) if isinstance(report.get("search_bars"), list) else [], default_method="GET"),
        build_section_html("Stylesheets", report.get("stylesheets", []) if isinstance(report.get("stylesheets"), list) else [], default_method="GET"),
    ]

    if note_rows:
        html_parts.extend([
            '<section class="notes">',
            "<h2>Notes</h2>",
            "<ul>",
            *note_rows,
            "</ul>",
            "</section>",
        ])

    html_parts.extend([
        "</main>",
        "</body>",
        "</html>",
    ])

    return "\n".join(html_parts)


def write_visual_report(report: Dict[str, object], output_path: str) -> str:
    destination = Path(str(output_path or "").strip())
    if not destination.is_absolute():
        destination = Path.cwd() / destination

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(build_visual_report_html(report), encoding="utf-8")
    return str(destination)


def build_summary(
    homepage_probe: Dict[str, object],
    links: List[Dict[str, object]],
    buttons: List[Dict[str, object]],
    searches: List[Dict[str, object]],
    stylesheets: List[Dict[str, object]],
) -> Dict[str, object]:
    links_failed = count_status(links, "failed")
    links_warning = count_status(links, "warning")
    buttons_failed = count_status(buttons, "failed")
    buttons_warning = count_status(buttons, "warning")
    search_failed = count_status(searches, "failed")
    search_warning = count_status(searches, "warning")
    css_failed = count_status(stylesheets, "failed")
    css_warning = count_status(stylesheets, "warning")

    failed_total = links_failed + buttons_failed + search_failed + css_failed
    warning_total = links_warning + buttons_warning + search_warning + css_warning

    if failed_total > 0:
        overall = "issues"
    elif warning_total > 0:
        overall = "warning"
    else:
        overall = "ok"

    return {
        "overall_status": overall,
        "homepage_ok": bool(homepage_probe.get("ok")),
        "homepage_http_status": homepage_probe.get("status"),
        "links_total": len(links),
        "links_ok": count_status(links, "ok"),
        "links_failed": links_failed,
        "links_warning": links_warning,
        "buttons_total": len(buttons),
        "buttons_ok": count_status(buttons, "ok"),
        "buttons_failed": buttons_failed,
        "buttons_warning": buttons_warning,
        "search_total": len(searches),
        "search_ok": count_status(searches, "ok"),
        "search_failed": search_failed,
        "search_warning": search_warning,
        "css_total": len(stylesheets),
        "css_ok": count_status(stylesheets, "ok"),
        "css_failed": css_failed,
        "css_warning": css_warning,
        "failed_total": failed_total,
        "warning_total": warning_total,
    }


def print_human_report(report: Dict[str, object]) -> None:
    summary = report.get("summary", {})
    print("Website functional check")
    print(f"Target: {report.get('target_url', '')}")
    print(f"Scanned at: {report.get('scanned_at', '')}")
    print(f"Overall: {summary.get('overall_status', 'unknown')}")
    print("")

    print(f"Homepage: {'ok' if summary.get('homepage_ok') else 'failed'} (HTTP {summary.get('homepage_http_status')})")
    print(
        "Links: {ok}/{total} ok, {failed} failed, {warning} warning".format(
            ok=summary.get("links_ok", 0),
            total=summary.get("links_total", 0),
            failed=summary.get("links_failed", 0),
            warning=summary.get("links_warning", 0),
        )
    )
    print(
        "Buttons: {ok}/{total} ok, {failed} failed, {warning} warning".format(
            ok=summary.get("buttons_ok", 0),
            total=summary.get("buttons_total", 0),
            failed=summary.get("buttons_failed", 0),
            warning=summary.get("buttons_warning", 0),
        )
    )
    print(
        "Search bars: {ok}/{total} ok, {failed} failed, {warning} warning".format(
            ok=summary.get("search_ok", 0),
            total=summary.get("search_total", 0),
            failed=summary.get("search_failed", 0),
            warning=summary.get("search_warning", 0),
        )
    )
    print(
        "Stylesheets: {ok}/{total} ok, {failed} failed, {warning} warning".format(
            ok=summary.get("css_ok", 0),
            total=summary.get("css_total", 0),
            failed=summary.get("css_failed", 0),
            warning=summary.get("css_warning", 0),
        )
    )

    print("\nDetails (problems only):")
    has_problems = False

    for section_name, section_key in (
        ("Links", "links"),
        ("Buttons", "buttons"),
        ("Search", "search_bars"),
        ("Stylesheets", "stylesheets"),
    ):
        entries = report.get(section_key, [])
        if not isinstance(entries, list):
            continue

        problematic = [item for item in entries if str(item.get("status") or "").lower() in {"failed", "warning"}]
        if not problematic:
            continue

        has_problems = True
        print(f"- {section_name}:")
        for item in problematic:
            status = str(item.get("status") or "unknown").upper()
            target = str(item.get("target") or "")
            message = str(item.get("message") or "")
            print(f"  [{status}] {item.get('id', '')} -> {target} :: {message}")

    if not has_problems:
        print("- No failed or warning checks.")

    print("\nNote: JS-only interactions may need browser-based testing for full validation.")


def run_scan(target_url: str, timeout: int, progress_callback: ProgressCallback = None) -> Dict[str, object]:
    base_url = normalize_url(target_url)
    if not base_url:
        emit_progress(progress_callback, "failed", 100, "Please provide a valid website URL.")
        raise ValueError("Please provide a valid website URL.")

    emit_progress(progress_callback, "queued", 2, "Functional check queued.")

    try:
        emit_progress(progress_callback, "homepage", 8, f"Opening homepage: {base_url}")
        homepage_probe = probe_url(base_url, timeout=timeout)

        emit_progress(progress_callback, "parse_dom", 16, "Parsing page elements.")
        parser = InteractionParser()

        body = str(homepage_probe.get("body") or "")
        if body:
            try:
                parser.feed(body)
            except Exception:
                pass

        emit_progress(progress_callback, "links", 20, "Starting link checks.")
        links = check_links(base_url, parser.links, timeout=timeout, progress_callback=progress_callback)

        emit_progress(progress_callback, "buttons", 53, "Starting button checks.")
        buttons = check_buttons(base_url, parser.buttons, parser.forms, timeout=timeout, progress_callback=progress_callback)

        emit_progress(progress_callback, "search_bars", 79, "Starting search-bar checks.")
        searches = check_search_bars(
            base_url,
            parser.search_inputs,
            parser.forms,
            timeout=timeout,
            progress_callback=progress_callback,
        )

        emit_progress(progress_callback, "summary", 90, "Starting stylesheet checks.")
        stylesheets = check_stylesheets(
            base_url,
            parser.stylesheets,
            parser.inline_style_blocks,
            timeout=timeout,
            progress_callback=progress_callback,
        )

        emit_progress(progress_callback, "summary", 94, "Building scan summary.")
        summary = build_summary(homepage_probe, links, buttons, searches, stylesheets)

        result = {
            "target_url": base_url,
            "scanned_at": datetime.now(timezone.utc).isoformat(),
            "summary": summary,
            "homepage": {
                "ok": homepage_probe.get("ok"),
                "http_status": homepage_probe.get("status"),
                "message": "Homepage reachable" if homepage_probe.get("ok") else (homepage_probe.get("error") or "Homepage probe failed"),
            },
            "links": links,
            "buttons": buttons,
            "search_bars": searches,
            "stylesheets": stylesheets,
            "notes": [
                "Checks are HTTP-based and safe by default.",
                "Non-GET actions are reported as warnings to avoid side effects.",
                "Stylesheet checks validate CSS resource loading and basic content sanity.",
                "Dynamic JavaScript interactions are best validated with browser automation.",
            ],
        }

        emit_progress(
            progress_callback,
            "completed",
            100,
            f"Functional check completed with status: {summary.get('overall_status', 'unknown')}.",
        )
        return result
    except Exception as error:
        emit_progress(progress_callback, "failed", 100, f"Functional check failed: {error}")
        raise


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check website links, buttons, and search bars.")
    parser.add_argument("--url", required=True, help="Target website URL")
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    parser.add_argument("--output", default="", help="Optional path to write JSON report")
    parser.add_argument("--visual-output", default="", help="Optional path to write HTML visual report")
    parser.add_argument("--open-visual", action="store_true", help="Open visual report in default browser")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="HTTP timeout in seconds")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        report = run_scan(args.url, timeout=max(3, int(args.timeout)))
    except ValueError as error:
        print(str(error))
        return 2
    except Exception as error:
        print(f"Website check failed: {error}")
        return 1

    visual_output = str(args.visual_output or "").strip()
    visual_requested = bool(args.open_visual or visual_output)
    visual_report_path = ""

    if visual_requested:
        if not visual_output:
            visual_output = build_default_visual_output_path(str(report.get("target_url") or ""))
        visual_report_path = write_visual_report(report, visual_output)
        report["visual_report_path"] = visual_report_path

        if args.open_visual:
            try:
                webbrowser.open_new_tab(Path(visual_report_path).resolve().as_uri())
            except Exception:
                pass

    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2, ensure_ascii=False)

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print_human_report(report)
        if visual_report_path:
            print(f"\nVisual report: {visual_report_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
