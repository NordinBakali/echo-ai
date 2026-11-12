from flask import Blueprint, Response, render_template, request, send_from_directory
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urldefrag
from collections import Counter, deque
from requests.adapters import HTTPAdapter
from queue import Empty, Queue
import json
import logging
import re
import threading
import uuid
from pathlib import Path
from urllib3.util.retry import Retry

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None

website_scanner = Blueprint("website_scanner", __name__)
logger = logging.getLogger(__name__)

TIMEOUT = (5, 15)
MAX_CRAWL_PAGES = 250
EVIDENCE_DIR = Path(__file__).resolve().parent / "scan_evidence"
active_scans = {}
active_scans_lock = threading.Lock()


class ScanCancelled(Exception):
    pass


def raise_if_cancelled(cancel_event):
    if cancel_event.is_set():
        raise ScanCancelled("Scan gestopt door de gebruiker.")


def normalize_url(url):
    url, _ = urldefrag(url)
    parsed = urlparse(url)
    if parsed.scheme in ("http", "https") and parsed.netloc and not parsed.path:
        return parsed._replace(path="/").geturl()
    return url


def same_domain(a, b):
    first = urlparse(a)
    second = urlparse(b)
    first_host = (first.hostname or "").lower().removeprefix("www.")
    second_host = (second.hostname or "").lower().removeprefix("www.")
    try:
        same_port = first.port == second.port
    except ValueError:
        return False
    return first_host == second_host and same_port


def get_page(session, url):
    try:
        response = session.get(
            url,
            timeout=TIMEOUT,
            allow_redirects=True,
            headers={"User-Agent": "WebsiteScanner/1.0"}
        )
        return response, None
    except requests.RequestException as error:
        return None, str(error)


def get_resource_status(session, url):
    try:
        response = session.get(
            url,
            timeout=TIMEOUT,
            allow_redirects=True,
            headers={"User-Agent": "WebsiteScanner/1.0"},
            stream=True
        )
        status = response.status_code
        response.close()
        return status, None
    except requests.RequestException as error:
        return None, str(error)


def crawl(start_url, update, cancel_event):
    session = requests.Session()
    retry = Retry(
        total=2,
        connect=2,
        read=2,
        status=2,
        backoff_factor=0.3,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET", "HEAD"])
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    queue_urls = deque([start_url])
    visited = set()
    pages = []
    crawl_origin = start_url
    page_limit_reached = False

    while queue_urls:
        raise_if_cancelled(cancel_event)
        if len(pages) >= MAX_CRAWL_PAGES:
            page_limit_reached = any(
                pending_url not in visited for pending_url in queue_urls
            )
            if page_limit_reached:
                update(
                    f"Limiet bereikt: maximaal {MAX_CRAWL_PAGES} interne pagina's gecontroleerd.",
                    35
                )
            break
        url = queue_urls.popleft()

        if url in visited:
            continue

        visited.add(url)
        update(
            f"Pagina controleren ({len(visited)} gevonden): {url}",
            min(35, 5 + len(visited))
        )

        response, request_error = get_page(session, url)
        if (
            response is None
            and url == start_url
            and urlparse(url).scheme == "https"
        ):
            http_url = urlparse(url)._replace(scheme="http").geturl()
            update("HTTPS niet bereikbaar; HTTP proberen...", 5)
            response, request_error = get_page(session, http_url)
            if response is not None:
                url = http_url

        page = {
            "url": url,
            "status": None,
            "error": request_error,
            "links": [],
            "images": [],
            "css": [],
            "buttons": [],
            "html_issues": [],
            "title": "",
            "description": "",
            "h1": 0,
        }

        if response is None:
            pages.append(page)
            continue

        page["status"] = response.status_code
        page["error"] = ""
        page["url"] = normalize_url(response.url)
        if len(pages) == 0:
            crawl_origin = response.url
        visited.add(normalize_url(response.url))

        if "html" not in response.headers.get("content-type", "").lower():
            pages.append(page)
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        base_tag = soup.find("base", href=True)
        page_base_url = (
            normalize_url(urljoin(page["url"], base_tag["href"]))
            if base_tag else page["url"]
        )

        if soup.title:
            page["title"] = soup.title.get_text(" ", strip=True)

        meta = soup.find("meta", attrs={"name": "description"})
        if meta:
            page["description"] = meta.get("content", "").strip()

        page["h1"] = len(soup.find_all("h1"))
        if not page["title"]:
            page["html_issues"].append("Geen paginatitel gevonden")
        if page["h1"] == 0:
            page["html_issues"].append("Geen H1-kop gevonden")
        elif page["h1"] > 1:
            page["html_issues"].append(f"Meerdere H1-koppen gevonden ({page['h1']})")
        if not page["description"]:
            page["html_issues"].append("Geen meta description gevonden")

        ids = Counter(element["id"] for element in soup.find_all(id=True))
        duplicate_ids = sorted(element_id for element_id, count in ids.items() if count > 1)
        page["html_issues"].extend(
            f"Dubbele HTML-id: {element_id}" for element_id in duplicate_ids
        )

        for element in soup.find_all(["button", "a", "input"]):
            element_type = (element.get("type") or "").lower()
            if element.name == "input" and element_type not in [
                "button", "submit", "reset", "image"
            ]:
                continue

            accessible_name = (
                element.get_text(" ", strip=True)
                or element.get("aria-label", "").strip()
                or element.get("title", "").strip()
                or element.get("value", "").strip()
                or element.get("alt", "").strip()
            )
            has_labeled_image = any(
                image.get("alt", "").strip() for image in element.find_all("img")
            )
            if not accessible_name and not has_labeled_image:
                page["html_issues"].append(
                    f"{element.name.upper()} zonder toegankelijke naam"
                )

        for a in soup.find_all(["a", "area"], href=True):
            href = a["href"].strip()

            if href.startswith(("mailto:", "tel:", "javascript:", "#")):
                continue

            target = normalize_url(urljoin(page_base_url, href))
            if urlparse(target).scheme not in ("http", "https"):
                continue
            page["links"].append(target)

            if same_domain(crawl_origin, target) and target not in visited:
                queue_urls.append(target)

        for img in soup.find_all("img"):
            src = img.get("src") or img.get("data-src")

            if src:
                image_url = normalize_url(urljoin(page_base_url, src))
                if urlparse(image_url).scheme not in ("http", "https"):
                    continue
                page["images"].append({
                    "url": image_url,
                    "alt": img.get("alt", "")
                })

        for link in soup.find_all("link", href=True):
            rel = [x.lower() for x in link.get("rel", [])]

            if "stylesheet" in rel:
                stylesheet_url = normalize_url(urljoin(page_base_url, link["href"]))
                if urlparse(stylesheet_url).scheme in ("http", "https"):
                    page["css"].append(stylesheet_url)

        for element in soup.find_all(["button", "input"]):
            element_type = (element.get("type") or "").lower()

            if element.name == "button" or element_type in ["button", "submit", "reset"]:
                text = (
                    element.get_text(" ", strip=True)
                    or element.get("value", "")
                    or element.get("aria-label", "")
                    or "button"
                )
                page["buttons"].append(text[:100])

        pages.append(page)

    return pages, session, page_limit_reached


def check_resources(pages, session, update, cancel_event):
    resources = {}
    resource_errors = {}
    urls = set()

    for page in pages:
        urls.update(page["links"])
        urls.update(image["url"] for image in page["images"])
        urls.update(page["css"])

    total = max(len(urls), 1)

    for number, url in enumerate(urls, 1):
        raise_if_cancelled(cancel_event)
        update(f"Resources controleren: {number}/{len(urls)}", 40 + int(number / total * 20))
        status, error = get_resource_status(session, url)
        resources[url] = status
        if error:
            resource_errors[url] = error

    return resources, resource_errors


def browser_test(
    pages, update, visible_macro=False, cancel_event=None, scan_id=None
):
    cancel_event = cancel_event or threading.Event()
    scan_id = scan_id or str(uuid.uuid4())
    results = {
        "console_errors": [],
        "page_errors": [],
        "failed_requests": [],
        "blocked_requests": [],
        "link_clicks": [],
        "buttons": [],
        "forms": [],
        "evidence": [],
        "scan_id": scan_id,
        "layout_issues": [],
        "macro_enabled": visible_macro,
        "macro_available": sync_playwright is not None,
        "available": sync_playwright is not None,
        "availability_error": ""
    }

    if sync_playwright is None:
        return results

    def save_failure_evidence(page, item, item_type):
        evidence_number = len(results["evidence"]) + 1
        filename = f"failure-{evidence_number:04d}.png"
        screenshot_url = f"/website-scanner/evidence/{scan_id}/{filename}"
        item["evidence_url"] = screenshot_url
        evidence = {
            "type": item_type,
            "page_url": item.get("url", ""),
            "element": item.get("text", "Onbekend element"),
            "target": item.get("target", ""),
            "error": item.get("reason") or item.get("error") or "Geen bevestigd effect",
            "screenshot_url": screenshot_url,
        }
        results["evidence"].append(evidence)
        try:
            scan_directory = EVIDENCE_DIR / scan_id
            scan_directory.mkdir(parents=True, exist_ok=True)
            page.screenshot(
                path=str(scan_directory / filename),
                full_page=True,
                animations="disabled",
                timeout=10000
            )
        except Exception as error:
            evidence["screenshot_url"] = ""
            evidence["screenshot_error"] = str(error)[:300]
            item["evidence_url"] = ""
            item["evidence_error"] = evidence["screenshot_error"]
            logger.warning(
                "Screenshot bewijs opslaan mislukt voor scan %s: %s",
                scan_id,
                error
            )

    def is_risky_action(*values):
        action = " ".join(value or "" for value in values).lower()
        action = re.sub(r"[-_/]+", " ", action)
        risky_terms = (
            "delete", "delet", "verwijder", "remove", "wissen",
            "logout", "log out", "uitloggen", "sign out", "signout",
            "checkout", "purchase", "buy now", "buy", "add to cart",
            "kopen", "aankoop", "winkelmand",
            "bestel", "betalen",
            "koop", "afrekenen", "payment", "winkelwagen", "shopping cart",
            "account sluiten", "account verwijderen", "cancel subscription",
            "unsubscribe", "abonnement opzeggen"
        )
        return any(term in action for term in risky_terms)

    def protect_mutations(route):
        method = route.request.method
        if method in ["POST", "PUT", "PATCH", "DELETE"]:
            results["blocked_requests"].append(
                f"{route.request.method} {route.request.url}"
            )
            route.abort()
        else:
            route.continue_()

    macro_style = """
        .scanner-macro-highlight {
            outline: 4px solid #ff3b30 !important;
            outline-offset: 3px !important;
            box-shadow: 0 0 0 8px rgba(255, 59, 48, .25) !important;
        }
        #scanner-macro-pointer {
            position: fixed;
            z-index: 2147483647;
            left: 0;
            top: 0;
            width: 20px;
            height: 20px;
            border: 3px solid #fff;
            border-radius: 50%;
            background: #ff3b30;
            box-shadow: 0 1px 8px #000;
            pointer-events: none;
            transform: translate(-50%, -50%);
        }
        #scanner-macro-pointer::after {
            content: "TEST";
            position: absolute;
            left: 18px;
            top: -5px;
            padding: 3px 6px;
            border-radius: 4px;
            background: #ff3b30;
            color: #fff;
            font: bold 11px Arial, sans-serif;
        }
    """

    def add_macro_overlay(page):
        page.add_style_tag(content=macro_style)
        page.evaluate("""() => {
            if (document.getElementById('scanner-macro-pointer')) return;
            const marker = document.createElement('div');
            marker.id = 'scanner-macro-pointer';
            document.body.appendChild(marker);
            document.addEventListener('mousemove', event => {
                marker.style.left = `${event.clientX}px`;
                marker.style.top = `${event.clientY}px`;
            });
        }""")

    def install_form_guard(page):
        page.evaluate("""() => {
            if (window.__scannerFormGuardInstalled) return;
            window.__scannerFormGuardInstalled = true;
            window.__scannerBlockedFormSubmissions = 0;
            document.addEventListener('submit', event => {
                window.__scannerBlockedFormSubmissions += 1;
                event.preventDefault();
                event.stopImmediatePropagation();
            }, true);
        }""")

    def inspect_forms(page, url):
        for form in page.locator("form").evaluate_all("""forms =>
            forms.map((form, index) => {
                const excludedTypes = new Set([
                    'hidden', 'submit', 'button', 'reset', 'image'
                ]);
                const controls = Array.from(form.elements).filter(element => {
                    const type = (element.type || '').toLowerCase();
                    return !element.disabled && element.tagName !== 'BUTTON' &&
                        !(element.tagName === 'INPUT' && excludedTypes.has(type));
                });
                const unlabeledControls = controls.filter(element => {
                    if (!['INPUT', 'SELECT', 'TEXTAREA'].includes(element.tagName)) {
                        return false;
                    }
                    const radioGroupLabel = element.type === 'radio' &&
                        element.closest('fieldset')?.querySelector('legend')
                            ?.innerText.trim();
                    return !element.labels?.length &&
                        !element.getAttribute('aria-label') &&
                        !element.getAttribute('aria-labelledby') &&
                        !radioGroupLabel;
                }).map(element =>
                    element.name || element.id || element.type || element.tagName.toLowerCase()
                );
                return {
                    number: index + 1,
                    action: form.action || location.href,
                    method: (form.method || 'get').toUpperCase(),
                    controls: controls.length,
                    required: controls.filter(element => element.required).length,
                    unlabeledControls
                };
            })
        """):
            results["forms"].append({
                "url": url,
                **form
            })

    def capture_page_state(page):
        return page.evaluate("""() => {
            const clone = document.body.cloneNode(true);
            clone.querySelectorAll('#scanner-macro-pointer').forEach(node => node.remove());
            const interactiveState = Array.from(document.querySelectorAll(
                'button, input, select, textarea, [role="button"], ' +
                '[aria-expanded], [aria-pressed], [role="alert"], [role="status"]'
            )).filter(element => {
                const rect = element.getBoundingClientRect();
                const style = getComputedStyle(element);
                return rect.width > 0 && rect.height > 0 &&
                    style.visibility !== 'hidden' && style.display !== 'none';
            }).map(element => ({
                tag: element.tagName,
                id: element.id,
                text: (element.innerText || element.getAttribute('aria-label') || '')
                    .trim().slice(0, 300),
                expanded: element.getAttribute('aria-expanded'),
                pressed: element.getAttribute('aria-pressed'),
                checked: 'checked' in element ? element.checked : null,
                value: 'value' in element ? element.value : null,
                disabled: 'disabled' in element ? element.disabled : null
            }));
            const messages = Array.from(document.querySelectorAll(
                '[role="alert"], [role="status"], [aria-live]'
            )).map(element => (element.innerText || '').trim()).filter(Boolean);
            return JSON.stringify({
                url: location.href,
                scrollY: window.scrollY,
                text: (clone.innerText || '').replace(/\\s+/g, ' ').trim().slice(0, 30000),
                interactiveState,
                messages
            });
        }""")

    def page_state_changed(before_state, after_state):
        before = json.loads(before_state)
        after = json.loads(after_state)
        return any(
            before[key] != after[key]
            for key in ("url", "text", "interactiveState", "messages")
        )

    def page_content_changed(before_state, after_state):
        before = json.loads(before_state)
        after = json.loads(after_state)
        return any(
            before[key] != after[key]
            for key in ("text", "interactiveState", "messages")
        )

    def wait_for_interaction_result(page, before_state, dialog_messages, cancel_event):
        after_state = before_state
        for _ in range(8):
            if cancel_event.is_set():
                break
            page.wait_for_timeout(250)
            after_state = capture_page_state(page)
            if page_state_changed(before_state, after_state) or dialog_messages:
                break
        return after_state

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(
                headless=not visible_macro,
                slow_mo=180 if visible_macro else 0
            )
        except Exception as error:
            results["available"] = False
            results["macro_available"] = False
            results["availability_error"] = str(error)
            return results

        context = browser.new_context(ignore_https_errors=True)

        for number, item in enumerate(pages, 1):
            if cancel_event.is_set():
                break
            url = item["url"]
            update(
                f"{'Zichtbare macro' if visible_macro else 'Browser testen'} "
                f"({number}/{len(pages)}): {url}",
                60 + int(number / max(len(pages), 1) * 35)
            )

            page = context.new_page()
            page.set_viewport_size({"width": 1280, "height": 800})
            console_errors = []
            page_errors = []
            failed_requests = []
            navigation_responses = []
            interaction_http_errors = []
            dialog_messages = []

            page.on(
                "console",
                lambda msg: console_errors.append(msg.text) if msg.type == "error" else None
            )
            page.on("pageerror", lambda error: page_errors.append(str(error)))
            page.on(
                "response",
                lambda response: (
                    navigation_responses.append(response)
                    if response.request.is_navigation_request else None,
                    interaction_http_errors.append({
                        "url": response.url,
                        "status": response.status
                    }) if response.status >= 400 else None
                )
            )
            page.on(
                "requestfailed",
                lambda req: failed_requests.append(f"{req.method} {req.url}")
            )
            page.on(
                "dialog",
                lambda dialog: (
                    dialog_messages.append(f"{dialog.type}: {dialog.message}"),
                    dialog.dismiss()
                )
            )

            try:
                page.goto(url, wait_until="domcontentloaded", timeout=20000)
                page.wait_for_timeout(500)
                install_form_guard(page)
                inspect_forms(page, url)
                if cancel_event.is_set():
                    page.close()
                    break
                if visible_macro:
                    add_macro_overlay(page)

                if visible_macro:
                    page.bring_to_front()
                    page.evaluate("window.scrollTo(0, 0)")
                    page.wait_for_timeout(250)
                    page_height = page.evaluate(
                        "() => document.documentElement.scrollHeight"
                    )
                    viewport_height = page.evaluate("() => window.innerHeight")
                    scroll_step = max(viewport_height - 100, 300)
                    for scroll_position in range(
                        scroll_step, page_height, scroll_step
                    ):
                        if cancel_event.is_set():
                            break
                        page.mouse.wheel(0, scroll_step)
                        page.wait_for_timeout(180)
                    if cancel_event.is_set():
                        page.close()
                        break
                    page.mouse.wheel(0, -page_height)
                    page.wait_for_timeout(180)

                for viewport in [
                    {"width": 1280, "height": 800},
                    {"width": 390, "height": 844}
                ]:
                    page.set_viewport_size(viewport)
                    layout = page.evaluate("""() => ({
                        viewportWidth: document.documentElement.clientWidth,
                        documentWidth: document.documentElement.scrollWidth
                    })""")
                    if layout["documentWidth"] > layout["viewportWidth"] + 2:
                        results["layout_issues"].append(
                            f"{url}: horizontale overflow bij "
                            f"{viewport['width']}px "
                            f"({layout['documentWidth']}px inhoud bij "
                            f"{layout['viewportWidth']}px viewport)"
                        )
                page.set_viewport_size({"width": 1280, "height": 800})

                if visible_macro:
                    anchors = page.locator("a[href]")
                    link_count = anchors.count()
                    for link_number in range(link_count):
                        if cancel_event.is_set():
                            break
                        link = anchors.nth(link_number)
                        label = "Onbekende link"
                        target_url = ""
                        try:
                            href = link.get_attribute("href") or ""
                            label = (
                                link.inner_text(timeout=800)
                                or link.get_attribute("aria-label")
                                or href
                            ).strip()[:100]
                            target_url = normalize_url(urljoin(url, href))
                            target_domain = urlparse(target_url)
                            if target_domain.scheme not in ("http", "https"):
                                results["link_clicks"].append({
                                    "url": url,
                                    "text": label,
                                    "target": target_url or href,
                                    "ok": None,
                                    "clicked": False,
                                    "skipped": True,
                                    "reason": "Geen web-link: niet automatisch geopend"
                                })
                                continue

                            risky_link = is_risky_action(
                                href,
                                label,
                                link.get_attribute("aria-label"),
                                link.get_attribute("title"),
                                link.get_attribute("id"),
                                link.get_attribute("onclick")
                            )
                            same_site = same_domain(url, target_url)
                            new_tab = (
                                (link.get_attribute("target") or "").lower() == "_blank"
                            )
                            download_link = link.get_attribute("download") is not None
                            if risky_link or not same_site or new_tab or download_link:
                                reason = (
                                    "mogelijk risicovolle link overgeslagen"
                                    if risky_link else
                                    "downloadlink overgeslagen; URL wordt wel gecontroleerd"
                                    if download_link else
                                    "nieuw tabblad overgeslagen; URL wordt wel gecontroleerd"
                                    if new_tab else
                                    "externe link: URL wordt gecontroleerd, niet automatisch geopend"
                                )
                                results["link_clicks"].append({
                                    "url": url,
                                    "text": label,
                                    "target": target_url,
                                    "ok": None,
                                    "clicked": False,
                                    "skipped": True,
                                    "reason": reason
                                })
                                continue

                            update(
                                f"Macro: link {link_number + 1}/{link_count} testen: {label}",
                                min(94, 60 + int((number - 1) / max(len(pages), 1) * 35))
                            )
                            link.scroll_into_view_if_needed(timeout=3000)
                            link.evaluate(
                                "(element) => element.classList.add('scanner-macro-highlight')"
                            )
                            box = link.bounding_box()
                            if not box:
                                raise RuntimeError("Link heeft geen zichtbare positie")

                            page.mouse.move(
                                box["x"] + box["width"] / 2,
                                box["y"] + box["height"] / 2
                            )
                            page.wait_for_timeout(220)
                            navigation_responses.clear()
                            interaction_http_errors.clear()
                            dialog_messages.clear()
                            before_state = capture_page_state(page)
                            source_url = normalize_url(page.url)
                            page.route("**/*", protect_mutations)
                            link.click(timeout=4000, no_wait_after=True)
                            after_state = wait_for_interaction_result(
                                page, before_state, dialog_messages, cancel_event
                            )
                            page.unroute("**/*")

                            nav_response = next(
                                reversed(navigation_responses), None
                            )
                            navigated = normalize_url(page.url) != source_url
                            arrived_at_target = (
                                navigated and normalize_url(page.url) == target_url
                            )
                            state_changed = page_content_changed(
                                before_state, after_state
                            )
                            http_error = next(
                                (
                                    error for error in interaction_http_errors
                                    if error["status"] >= 400
                                ),
                                None
                            )
                            if http_error:
                                click_ok = False
                            elif nav_response is not None and nav_response.status < 400:
                                click_ok = True
                            elif state_changed or navigated or arrived_at_target:
                                click_ok = True
                            else:
                                click_ok = None
                            click_error = (
                                f"HTTP {http_error['status']} - {http_error['url']}"
                                if http_error
                                else ""
                            )
                            fragment = urlparse(urljoin(url, href)).fragment
                            if fragment and not page.evaluate(
                                "(id) => Boolean(document.getElementById(id) || "
                                "document.getElementsByName(id).length)",
                                fragment
                            ):
                                click_ok = False
                                click_error = f"Fragmentdoel bestaat niet: #{fragment}"
                            elif not click_ok and not click_error and not state_changed:
                                click_error = (
                                    "Klik uitgevoerd, maar geen paginawijziging, "
                                    "zichtbare verandering of succesvolle navigatie waargenomen"
                                )
                            link_result = {
                                "url": url,
                                "text": label,
                                "target": target_url,
                                "ok": click_ok,
                                "clicked": True,
                                "status": nav_response.status if nav_response else None,
                                "error": click_error,
                                "reason": click_error,
                                "effect": "Pagina of inhoud veranderde"
                                if state_changed else
                                "Navigatie bevestigd"
                                if nav_response is not None or navigated else
                                "Geen zichtbare verandering waargenomen"
                            }
                            results["link_clicks"].append(link_result)
                            if click_ok is not True:
                                save_failure_evidence(page, link_result, "link")

                            if page.url != url:
                                page.goto(url, wait_until="domcontentloaded", timeout=15000)
                                install_form_guard(page)
                                add_macro_overlay(page)
                                page.evaluate("window.scrollTo(0, 0)")
                        except Exception as error:
                            try:
                                page.unroute("**/*")
                            except Exception as cleanup_error:
                                page_errors.append(
                                    "Veiligheidsfilter opruimen mislukt: "
                                    f"{str(cleanup_error)[:200]}"
                                )
                            link_result = {
                                "url": url,
                                "text": label,
                                "target": target_url,
                                "ok": False,
                                "clicked": True,
                                "error": str(error)[:200],
                                "reason": str(error)[:200]
                            }
                            results["link_clicks"].append(link_result)
                            save_failure_evidence(page, link_result, "link")
                            if page.url != url:
                                page.goto(url, wait_until="domcontentloaded", timeout=15000)

                buttons = page.locator(
                    "button, input[type='button'], input[type='submit'], "
                    "input[type='reset'], [role='button'], [role='tab'], "
                    "[role='menuitem'], [aria-haspopup], summary"
                )
                install_form_guard(page)

                count = buttons.count()

                for i in range(count):
                    if cancel_event.is_set():
                        break
                    text = "Onbekende knop"
                    kind = "button"
                    try:
                        button = buttons.nth(i)

                        if not button.is_visible():
                            continue

                        text = (
                            button.inner_text(timeout=1000)
                            or button.get_attribute("aria-label")
                            or button.get_attribute("value")
                            or "button"
                        )
                        kind = button.evaluate("""element => {
                            const role = element.getAttribute('role');
                            const controlled = element.getAttribute('aria-controls')
                                ?.split(/\\s+/)
                                .map(id => document.getElementById(id))
                                .find(Boolean);
                            const controlledRole = controlled?.getAttribute('role');
                            const popup = element.getAttribute('aria-haspopup');
                            const toggle = element.getAttribute('data-bs-toggle') ||
                                element.getAttribute('data-toggle');
                            if (role === 'tab') return 'tab';
                            if (role === 'menuitem') return 'menu-item';
                            if (element.tagName === 'SUMMARY') return 'disclosure';
                            if (popup === 'dialog' || controlledRole === 'dialog' ||
                                toggle === 'modal') {
                                return 'modal trigger';
                            }
                            if (popup === 'menu' || controlledRole === 'menu' ||
                                toggle === 'dropdown') {
                                return 'menu trigger';
                            }
                            if (popup || controlledRole === 'listbox') {
                                return 'dropdown trigger';
                            }
                            return 'button';
                        }""")

                        dangerous = is_risky_action(
                            text,
                            button.get_attribute("aria-label"),
                            button.get_attribute("title"),
                            button.get_attribute("id"),
                            button.get_attribute("name"),
                            button.get_attribute("onclick"),
                            button.get_attribute("href"),
                            button.get_attribute("formaction"),
                            button.evaluate("(element) => element.form?.action || ''")
                        )

                        if dangerous:
                            results["buttons"].append({
                                "url": url,
                                "text": text.strip()[:100],
                                "kind": kind,
                                "ok": None,
                                "skipped": True,
                                "reason": "Mogelijk koop-, verwijder- of uitlogactie"
                            })
                            continue

                        if visible_macro:
                            button.scroll_into_view_if_needed(timeout=3000)
                            button.evaluate(
                                "(element) => element.classList.add('scanner-macro-highlight')"
                            )
                            button_box = button.bounding_box()
                            if button_box:
                                page.mouse.move(
                                    button_box["x"] + button_box["width"] / 2,
                                    button_box["y"] + button_box["height"] / 2
                                )
                                page.wait_for_timeout(220)

                        interaction_http_errors.clear()
                        dialog_messages.clear()
                        console_count_before = len(console_errors)
                        page_error_count_before = len(page_errors)
                        failed_request_count_before = len(failed_requests)
                        blocked_form_count_before = page.evaluate(
                            "() => window.__scannerBlockedFormSubmissions || 0"
                        )
                        before_state = capture_page_state(page)
                        page.route("**/*", protect_mutations)
                        old_url = page.url
                        blocked_before = len(results["blocked_requests"])
                        button.click(timeout=3000, no_wait_after=True)
                        after_state = wait_for_interaction_result(
                            page, before_state, dialog_messages, cancel_event
                        )
                        page.unroute("**/*")

                        state_changed = page_content_changed(
                            before_state, after_state
                        )
                        navigated = page.url != old_url
                        was_blocked = len(results["blocked_requests"]) > blocked_before
                        form_submit_blocked = (
                            page.evaluate(
                                "() => window.__scannerBlockedFormSubmissions || 0"
                            ) > blocked_form_count_before
                        )
                        http_error = next(
                            (
                                error for error in interaction_http_errors
                                if error["status"] >= 400
                            ),
                            None
                        )
                        request_error = (
                            failed_requests[failed_request_count_before:]
                        )
                        script_error = (
                            console_errors[console_count_before:]
                            + page_errors[page_error_count_before:]
                        )
                        if was_blocked or form_submit_blocked:
                            outcome = None
                            outcome_reason = (
                                "Formulierverzending is uit veiligheid geblokkeerd; "
                                "het eindresultaat is niet gecontroleerd"
                            )
                            if form_submit_blocked:
                                results["blocked_requests"].append(
                                    f"Form submission {url} (browser-event geblokkeerd)"
                                )
                        elif http_error:
                            outcome = False
                            outcome_reason = (
                                f"HTTP {http_error['status']} - {http_error['url']}"
                            )
                        elif request_error:
                            outcome = False
                            outcome_reason = request_error[0]
                        elif script_error:
                            outcome = False
                            outcome_reason = script_error[0]
                        elif state_changed or navigated or dialog_messages:
                            outcome = True
                            outcome_reason = ""
                        else:
                            outcome = None
                            outcome_reason = (
                                "Klik uitgevoerd, maar geen zichtbare verandering, "
                                "navigatie of melding waargenomen"
                            )

                        button_result = {
                            "url": url,
                            "text": text.strip()[:100],
                            "kind": kind,
                            "ok": outcome,
                            "reason": outcome_reason,
                            "effect": "Pagina of inhoud veranderde"
                            if state_changed else
                            "Pagina navigeerde"
                            if navigated else
                            f"Melding getoond: {dialog_messages[0]}"
                            if dialog_messages else
                            "Geen waarneembaar effect",
                            "blocked": was_blocked or form_submit_blocked,
                            "http_error": http_error,
                            "script_errors": script_error,
                            "from": old_url,
                            "to": page.url
                        }
                        results["buttons"].append(button_result)
                        if outcome is False or (
                            outcome is None and not button_result["blocked"]
                        ):
                            save_failure_evidence(page, button_result, "knop")

                        if page.url != old_url:
                            try:
                                page.go_back(wait_until="domcontentloaded", timeout=5000)
                                install_form_guard(page)
                                if visible_macro:
                                    add_macro_overlay(page)
                            except Exception as error:
                                page_errors.append(
                                    f"Terug navigeren na knoptest mislukt: {str(error)[:200]}"
                                )
                                try:
                                    page.goto(
                                        old_url, wait_until="domcontentloaded", timeout=10000
                                    )
                                    install_form_guard(page)
                                    if visible_macro:
                                        add_macro_overlay(page)
                                except Exception as restore_error:
                                    page_errors.append(
                                        "Pagina herstellen na knoptest mislukt: "
                                        f"{str(restore_error)[:200]}"
                                    )

                    except Exception as error:
                        try:
                            page.unroute("**/*")
                        except Exception as cleanup_error:
                            page_errors.append(
                                "Veiligheidsfilter opruimen mislukt: "
                                f"{str(cleanup_error)[:200]}"
                            )
                        button_result = {
                            "url": url,
                            "text": "Onbekende knop",
                            "kind": "button",
                            "ok": False,
                            "error": str(error)[:200],
                            "reason": str(error)[:200]
                        }
                        results["buttons"].append(button_result)
                        save_failure_evidence(page, button_result, "knop")

            except Exception as error:
                page_errors.append(str(error)[:300])

            results["console_errors"].extend(f"{url}: {x}" for x in console_errors)
            results["page_errors"].extend(f"{url}: {x}" for x in page_errors)
            results["failed_requests"].extend(f"{url}: {x}" for x in failed_requests)
            page.close()

        browser.close()

    return results


def make_result(
    url, pages, resources, resource_errors, browser, page_limit_reached=False
):
    page_errors = [p for p in pages if p["status"] is None or p["status"] >= 400]

    all_links, broken_links = [], []
    all_images, broken_images = [], []
    all_css, broken_css = [], []

    for page in pages:
        for link in page["links"]:
            all_links.append(link)
            status = resources.get(link)
            if status is None or status >= 400:
                broken_links.append((page["url"], link, status, resource_errors.get(link)))

        for image in page["images"]:
            all_images.append(image)
            status = resources.get(image["url"])
            if status is None or status >= 400:
                broken_images.append(
                    (page["url"], image["url"], status, resource_errors.get(image["url"]))
                )

        for css in page["css"]:
            all_css.append(css)
            status = resources.get(css)
            if status is None or status >= 400:
                broken_css.append((page["url"], css, status, resource_errors.get(css)))

    buttons = browser["buttons"]
    forms = browser.get("forms", [])
    interactions = [
        (button, False) for button in buttons
    ] + [
        (link, True) for link in browser["link_clicks"]
    ]
    interaction_counts = {
        status: sum(
            interaction_status(item, is_link) == status
            for item, is_link in interactions
        )
        for status in ("passed", "failed", "skipped", "unconfirmed")
    }
    verified_buttons = [
        button for button in buttons
        if button["ok"] and not button.get("skipped") and not button.get("blocked")
    ]
    js_errors = len(browser["console_errors"]) + len(browser["page_errors"])
    html_issues = [issue for page in pages for issue in page["html_issues"]]
    layout_issues = browser["layout_issues"]
    successful_link_clicks = sum(
        link["ok"] is True for link in browser["link_clicks"]
    )
    failed_link_clicks = sum(
        link["ok"] is False for link in browser["link_clicks"]
    )
    unverified_link_clicks = sum(
        link["clicked"] and link["ok"] is None
        for link in browser["link_clicks"]
    )
    tested_link_clicks = (
        successful_link_clicks + failed_link_clicks + unverified_link_clicks
    )
    unverified_buttons = sum(
        button["ok"] is None
        and not button.get("skipped")
        and not button.get("blocked")
        for button in buttons
    )
    specialized_controls = sum(
        button.get("kind") in {
            "tab", "menu-item", "modal trigger", "menu trigger",
            "dropdown trigger", "disclosure"
        }
        for button in buttons
    )
    form_warnings = sum(
        len(form.get("unlabeledControls", []))
        for form in forms
    )

    total = (
        len(pages) + len(all_links) + len(all_images) + len(all_css) + len(buttons)
        + len(html_issues) + len(layout_issues) + tested_link_clicks
    )
    passed = (
        len(pages) - len(page_errors)
        + len(all_links) - len(broken_links)
        + len(all_images) - len(broken_images)
        + len(all_css) - len(broken_css)
        + len(verified_buttons)
        + successful_link_clicks
    )

    score = round((passed / total) * 100) if total else 0
    score = max(0, score - min(js_errors * 2, 20))

    lines = [
        "=" * 65,
        "WEBSITE SCANNER RESULTAAT",
        "=" * 65,
        "",
        f"Website: {url}",
        "",
    ]
    if page_limit_reached:
        lines += [
            f"LET OP: De limiet van {MAX_CRAWL_PAGES} pagina's is bereikt. "
            "Niet alle interne pagina's zijn gecontroleerd.",
            "",
        ]

    lines += [
        "SAMENVATTING",
        "-" * 65,
        f"Pagina's:       {len(pages) - len(page_errors)}/{len(pages)}",
        f"Links:          {len(all_links) - len(broken_links)}/{len(all_links)}",
        f"Afbeeldingen:   {len(all_images) - len(broken_images)}/{len(all_images)}",
        f"CSS:            {len(all_css) - len(broken_css)}/{len(all_css)}",
        f"Interacties gevonden: {len(interactions)}",
        f"  Getest:          {len(interactions) - interaction_counts['skipped']}",
        f"  Geslaagd:        {interaction_counts['passed']}",
        f"  Mislukt:         {interaction_counts['failed']}",
        f"  Overgeslagen:    {interaction_counts['skipped']}",
        f"  Niet bevestigd:  {interaction_counts['unconfirmed']}",
        (
            (
                f"Links aangeklikt: {successful_link_clicks}/{tested_link_clicks}"
            )
            if browser["macro_available"] else
            "Links aangeklikt: zichtbare browser niet beschikbaar"
            if browser["macro_enabled"] else
            "Links aangeklikt: macro niet ingeschakeld"
        ),
        f"JavaScript errors: {js_errors}",
        "",
        f"SCORE: {score}/100",
        ""
    ]

    lines += ["=" * 65, "PAGINA'S", "=" * 65]

    for page in pages:
        status = page["status"] if page["status"] is not None else "ERROR"
        symbol = "OK" if page["status"] is not None and page["status"] < 400 else "PROBLEEM"
        lines.append(f"[{symbol}] {status} - {page['url']}")
        if page.get("error"):
            lines.append(f"    FOUT: {page['error']}")

        if not page["title"]:
            lines.append("    WARNING: Geen title gevonden")
        if not page["description"]:
            lines.append("    WARNING: Geen meta description gevonden")
        if page["h1"] == 0:
            lines.append("    WARNING: Geen H1 gevonden")

    lines += ["", "=" * 65, "HTML-CONTROLE", "=" * 65]
    if html_issues:
        for page in pages:
            for issue in page["html_issues"]:
                lines.append(f"[WARNING] {page['url']} - {issue}")
    else:
        lines.append("Geen HTML-waarschuwingen gevonden.")

    lines += ["", "=" * 65, "BROKEN LINKS", "=" * 65]
    if broken_links:
        lines += [
            f"[ERROR] {source} -> {target} ({status or 'geen response'}"
            f"{': ' + error if error else ''})"
            for source, target, status, error in broken_links
        ]
    else:
        lines.append("Geen broken links gevonden.")

    lines += ["", "=" * 65, "ZICHTBARE LINK-MACRO", "=" * 65]
    if not browser["macro_enabled"]:
        lines.append("Niet uitgevoerd. Schakel de zichtbare macro in voor de volgende scan.")
    elif not browser["macro_available"]:
        lines.append(
            "Niet uitgevoerd: zichtbare browser niet beschikbaar. "
            + (browser["availability_error"] or "")
        )
    elif browser["link_clicks"]:
        for link in browser["link_clicks"]:
            status = interaction_status(link, is_link=True)
            if status == "passed":
                lines.append(
                    f"[GESLAAGD] {link['url']} -> {link['target']} "
                    f"({link['text']})"
                )
            elif status == "failed":
                lines.append(
                    f"[MISLUKT] {link['url']} -> {link['target']} "
                    f"({link['text']}): "
                    f"{link.get('reason') or link.get('error') or 'klik mislukt'}"
                )
                if link.get("evidence_url"):
                    lines.append(f"    Screenshot: {link['evidence_url']}")
            else:
                status_label = (
                    "OVERGESLAGEN" if status == "skipped" else "NIET BEVESTIGD"
                )
                lines.append(
                    f"[{status_label}] {link['url']} -> {link['target']} "
                    f"({link['text']}): {link.get('reason') or 'Geen resultaat'}"
                )
                if link.get("evidence_url"):
                    lines.append(f"    Screenshot: {link['evidence_url']}")
    else:
        lines.append("Geen zichtbare web-links gevonden om aan te klikken.")

    lines += ["", "=" * 65, "BROKEN AFBEELDINGEN", "=" * 65]
    if broken_images:
        lines += [
            f"[ERROR] {source} -> {target} ({status or 'geen response'}"
            f"{': ' + error if error else ''})"
            for source, target, status, error in broken_images
        ]
    else:
        lines.append("Geen broken afbeeldingen gevonden.")

    lines += ["", "=" * 65, "CSS", "=" * 65]
    if broken_css:
        lines += [
            f"[ERROR] {source} -> {target} ({status or 'geen response'}"
            f"{': ' + error if error else ''})"
            for source, target, status, error in broken_css
        ]
    else:
        lines.append("Alle gevonden CSS-bestanden zijn bereikbaar.")

    lines += ["", "=" * 65, "KNOPPEN EN INTERACTIEVE ELEMENTEN", "=" * 65]
    if buttons:
        for b in buttons:
            kind_label = f"[{b['kind'].upper()}] " if b.get("kind") else ""
            status = interaction_status(b)
            if status == "skipped" and b.get("blocked"):
                lines.append(
                    f"{kind_label}[OVERGESLAGEN - VEILIGHEID] {b['url']} - "
                    f"{b['text']}: verzendactie geblokkeerd"
                )
            elif status == "skipped":
                lines.append(
                    f"{kind_label}[OVERGESLAGEN] {b['url']} - {b['text']}: "
                    f"{b.get('reason') or 'Mogelijk risicovolle actie'}"
                )
            elif status == "unconfirmed":
                lines.append(
                    f"{kind_label}[NIET BEVESTIGD] {b['url']} - {b['text']}: "
                    f"{b.get('reason', 'Geen waarneembaar effect')}"
                )
                if b.get("evidence_url"):
                    lines.append(f"    Screenshot: {b['evidence_url']}")
            elif status == "passed":
                lines.append(
                    f"{kind_label}[GESLAAGD] {b['url']} - {b['text']}: "
                    f"{b.get('effect', 'Klik bevestigd')}"
                )
            else:
                lines.append(
                    f"{kind_label}[MISLUKT] {b['url']} - {b['text']}: "
                    f"{b.get('reason') or b.get('error', 'klik mislukt')}"
                )
                if b.get("evidence_url"):
                    lines.append(f"    Screenshot: {b['evidence_url']}")
    elif not browser["available"]:
        lines.append(
            "Knoptest niet uitgevoerd: browser niet beschikbaar. "
            + (browser["availability_error"] or "Installeer Playwright en Chromium.")
        )
    else:
        lines.append("Geen knoppen gevonden.")

    lines += ["", "=" * 65, "FORMULIERCONTROLE", "=" * 65]
    if forms:
        for form in forms:
            lines.append(
                f"[GECONTROLEERD] {form['url']} - formulier {form['number']}: "
                f"{form['method']} {form['action']}; {form['controls']} velden, "
                f"{form['required']} verplicht"
            )
            for field in form.get("unlabeledControls", []):
                lines.append(
                    f"[WAARSCHUWING] Veld zonder toegankelijk label: {field}"
                )
        lines.append(
            "Formulieren zijn niet verzonden; verzendacties zijn geblokkeerd."
        )
    else:
        lines.append("Geen formulieren gevonden.")

    lines += ["", "=" * 65, "BEWIJS VAN MISLUKTE KLIKKEN", "=" * 65]
    evidence = browser.get("evidence", [])
    if evidence:
        lines.append(
            f"Bewijsbestanden: scan_evidence/{browser.get('scan_id', '')}/"
        )
        for item in evidence:
            target = f" -> {item['target']}" if item.get("target") else ""
            lines.append(
                f"[{item['type'].upper()}] {item['page_url']}{target} "
                f"({item['element']}): {item['error']}"
            )
            if item.get("screenshot_url"):
                lines.append(f"    Screenshot: {item['screenshot_url']}")
            elif item.get("screenshot_error"):
                lines.append(
                    f"    Screenshot opslaan mislukt: {item['screenshot_error']}"
                )
    else:
        lines.append("Geen mislukte of onbevestigde klikken met screenshotbewijs.")

    lines += ["", "=" * 65, "JAVASCRIPT ERRORS", "=" * 65]
    for error in browser["console_errors"]:
        lines.append("[CONSOLE] " + error)
    for error in browser["page_errors"]:
        lines.append("[PAGE] " + error)
    if not browser["console_errors"] and not browser["page_errors"]:
        lines.append("Geen JavaScript/page errors gevonden.")

    lines += ["", "=" * 65, "MISLUKTE BROWSER-REQUESTS", "=" * 65]
    if browser["failed_requests"]:
        lines += [f"[ERROR] {failure}" for failure in browser["failed_requests"]]
    else:
        lines.append("Geen mislukte browser-requests gevonden.")

    if browser["blocked_requests"]:
        lines += [
            "[VEILIGHEID] Verzendactie geblokkeerd tijdens knoptest: " + request
            for request in browser["blocked_requests"]
        ]

    lines += ["", "=" * 65, "LAYOUT-CONTROLE", "=" * 65]
    if layout_issues:
        lines += [f"[WARNING] {issue}" for issue in layout_issues]
    elif not browser["available"]:
        lines.append(
            "Niet gecontroleerd: browser niet beschikbaar. "
            + (browser["availability_error"] or "Installeer Playwright en Chromium.")
        )
    else:
        lines.append("Geen horizontale overflow gevonden.")

    lines += ["", "=" * 65, "AFBEELDINGEN ZONDER ALT", "=" * 65]

    no_alt = False
    for page in pages:
        for image in page["images"]:
            if not image["alt"].strip():
                no_alt = True
                lines.append(f"[WARNING] {page['url']} -> {image['url']}")

    if not no_alt:
        lines.append("Geen afbeeldingen zonder ALT gevonden.")

    lines += ["", "=" * 65, "EINDE SCAN", "=" * 65]

    summary = {
        "pages": f"{len(pages) - len(page_errors)}/{len(pages)}",
        "page_limit_reached": page_limit_reached,
        "links": f"{len(all_links) - len(broken_links)}/{len(all_links)}",
        "images": f"{len(all_images) - len(broken_images)}/{len(all_images)}",
        "css": f"{len(all_css) - len(broken_css)}/{len(all_css)}",
        "buttons": f"{len(verified_buttons)}/{len(buttons)}",
        "buttons_unverified": unverified_buttons,
        "interactions_total": len(interactions),
        "interactions_tested": len(interactions) - interaction_counts["skipped"],
        "interactions_passed": interaction_counts["passed"],
        "interactions_failed": interaction_counts["failed"],
        "interactions_skipped": interaction_counts["skipped"],
        "interactions_unconfirmed": interaction_counts["unconfirmed"],
        "interactive_controls": specialized_controls,
        "forms_checked": len(forms),
        "form_warnings": form_warnings,
        "link_clicks": (
            f"{successful_link_clicks}/{tested_link_clicks}"
            if browser["macro_available"] and browser["macro_enabled"] else
            "niet beschikbaar"
            if browser["macro_enabled"] else "uit"
        ),
        "link_clicks_unverified": unverified_link_clicks,
        "html": len(html_issues),
        "layout": len(layout_issues),
        "score": score
    }

    return "\n".join(lines), summary


def sse(data):
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


@website_scanner.route("/")
def index():
    return render_template("website-scanner.html")


@website_scanner.route("/style.css")
def stylesheet():
    return send_from_directory(
        Path(__file__).resolve().parent / "static",
        "website-scanner.css"
    )


@website_scanner.route("/evidence/<scan_id>/<filename>")
def scan_evidence(scan_id, filename):
    if (
        not re.fullmatch(r"[0-9a-fA-F-]{36}", scan_id)
        or not re.fullmatch(r"failure-\d{4}\.png", filename)
    ):
        return {"error": "Ongeldig bewijsbestand."}, 404
    return send_from_directory(
        EVIDENCE_DIR / scan_id,
        filename,
        mimetype="image/png",
        max_age=0
    )


def interaction_status(item, is_link=False):
    if item.get("skipped") or item.get("blocked"):
        return "skipped"
    if is_link and not item.get("clicked"):
        return "skipped"
    if item.get("ok") is True:
        return "passed"
    if item.get("ok") is False:
        return "failed"
    return "unconfirmed"


@website_scanner.route("/scan")
def scan():
    start_url = request.args.get("url", "").strip()
    visible_macro = request.args.get("visible", "1") == "1"
    scan_id = request.args.get("scan_id", "")
    if not re.fullmatch(r"[0-9a-fA-F-]{36}", scan_id):
        return Response(
            sse({"type": "error", "message": "Ongeldig scan-ID. Start de scan opnieuw."}),
            mimetype="text/event-stream",
            headers={"Cache-Control": "no-cache"}
        )

    cancel_event = threading.Event()

    url = start_url
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    parsed_url = urlparse(url)
    if parsed_url.scheme not in ("http", "https") or not parsed_url.hostname:
        return Response(
            sse({"type": "error", "message": "Vul een geldige website-URL in."}),
            mimetype="text/event-stream",
            headers={"Cache-Control": "no-cache"}
        )

    url = normalize_url(url)
    with active_scans_lock:
        if scan_id in active_scans:
            return Response(
                sse({"type": "error", "message": "Deze scan is al actief."}),
                status=409,
                mimetype="text/event-stream",
                headers={"Cache-Control": "no-cache"}
            )
        active_scans[scan_id] = cancel_event

    def generate():
        events = Queue()

        def update(message, progress):
            events.put({
                "type": "status",
                "message": message,
                "progress": progress
            })

        def run_scan():
            try:
                events.put({
                    "type": "status",
                    "message": "Website wordt voorbereid...",
                    "progress": 2
                })

                pages, session, page_limit_reached = crawl(
                    url, update, cancel_event
                )
                raise_if_cancelled(cancel_event)
                resources, resource_errors = check_resources(
                    pages, session, update, cancel_event
                )
                raise_if_cancelled(cancel_event)
                browser = browser_test(
                    pages,
                    update,
                    visible_macro=visible_macro,
                    cancel_event=cancel_event,
                    scan_id=scan_id
                )
                raise_if_cancelled(cancel_event)
                result, summary = make_result(
                    url,
                    pages,
                    resources,
                    resource_errors,
                    browser,
                    page_limit_reached=page_limit_reached
                )

                events.put({
                    "type": "result",
                    "text": result,
                    "summary": summary,
                    "evidence": browser["evidence"],
                    "website_url": pages[0]["url"] if pages else url
                })
            except ScanCancelled:
                events.put({"type": "cancelled"})
            except Exception as error:
                logger.exception("Website scan mislukt")
                events.put({
                    "type": "error",
                    "message": f"Scan mislukt: {error}"
                })
            finally:
                with active_scans_lock:
                    if active_scans.get(scan_id) is cancel_event:
                        active_scans.pop(scan_id, None)

        threading.Thread(target=run_scan, daemon=True).start()

        try:
            while True:
                try:
                    event = events.get(timeout=15)
                except Empty:
                    yield ": keep-alive\n\n"
                    continue

                is_finished = event["type"] in ("result", "error", "cancelled")
                yield sse(event)
                if is_finished:
                    return
        finally:
            cancel_event.set()

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )


@website_scanner.route("/scan/<scan_id>/stop", methods=["POST"])
def stop_scan(scan_id):
    if not re.fullmatch(r"[0-9a-fA-F-]{36}", scan_id):
        return {"error": "Ongeldig scan-ID."}, 400

    with active_scans_lock:
        cancel_event = active_scans.get(scan_id)
        if cancel_event is None:
            return {"error": "Deze scan is niet meer actief."}, 404
        cancel_event.set()

    return {"status": "stopping"}
