import json
import os
import queue
import random
import re
import socket
import ssl
import threading
import time
from datetime import datetime, timezone
from html.parser import HTMLParser
from tkinter import (
    BOTH,
    Canvas,
    END,
    LEFT,
    RIGHT,
    WORD,
    Y,
    Button,
    Entry,
    Frame,
    Label,
    StringVar,
    Text,
    Tk,
    Toplevel,
    filedialog,
    messagebox,
)
from typing import Dict, List, Set, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

APP_TITLE = "Quick Checker"
USER_AGENT = "QuickCheckerAI/1.0 defensive website scanner"
TIMEOUT = 10
MAX_BODY_BYTES = 800000
QUICK_MAX_PAGES = 6
HARD_MAX_PAGES = 30
QUICK_LINK_PROBES = 12
HARD_LINK_PROBES = 50
QUICK_TARGET_SECONDS = (10, 15)
HARD_TARGET_SECONDS = (30, 60)

SEVERITY_ORDER = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
}

SEVERITY_PENALTY = {
    "critical": 1.5,
    "high": 1.0,
    "medium": 0.6,
    "low": 0.25,
}

SEVERITY_RISK_POINTS = {
    "critical": 35,
    "high": 20,
    "medium": 9,
    "low": 3,
}

SECURITY_HEADERS = [
    "strict-transport-security",
    "content-security-policy",
    "x-frame-options",
    "x-content-type-options",
    "referrer-policy",
    "permissions-policy",
]

QUICK_EXPOSED_PATHS = [
    "/.env",
    "/.git/config",
    "/backup.zip",
    "/admin",
    "/login",
]

HARD_EXPOSED_PATHS = QUICK_EXPOSED_PATHS + [
    "/backup.sql",
    "/database.sql",
    "/wp-config.php",
    "/phpinfo.php",
    "/.well-known/security.txt",
]

HARD_GIT_AUDIT_PATHS = [
    "/.git/HEAD",
    "/.git/config",
    "/.git/index",
    "/.git/packed-refs",
    "/.git/refs/heads/main",
    "/.git/refs/heads/master",
    "/.git/logs/HEAD",
    "/.git/FETCH_HEAD",
]

GIT_REMOTE_URL_PATTERN = re.compile(r"^\s*url\s*=\s*(\S+)\s*$", flags=re.MULTILINE)
GIT_HEAD_REF_PATTERN = re.compile(r"ref:\s*(refs/heads/[A-Za-z0-9._/-]+)")

EMAIL_PATTERN = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,63}\b", flags=re.IGNORECASE)

ADMIN_EMAIL_KEYWORDS = (
    "admin",
    "administrator",
    "beheer",
    "owner",
    "webmaster",
    "security",
    "it",
    "support",
)

CONTACT_EMAIL_KEYWORDS = (
    "info",
    "contact",
    "hello",
    "team",
)

TECH_BODY_MARKERS: List[Tuple[str, str]] = [
    ("wp-content", "WordPress"),
    ("woocommerce", "WooCommerce"),
    ("shopify", "Shopify"),
    ("wix.com", "Wix"),
    ("squarespace", "Squarespace"),
    ("react", "React"),
    ("__next", "Next.js"),
    ("vue", "Vue.js"),
    ("angular", "Angular"),
    ("jquery", "jQuery"),
    ("bootstrap", "Bootstrap"),
]


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: List[str] = []
        self.has_title_tag = False
        self.has_meta_description = False
        self.h1_count = 0
        self.images_missing_alt = 0
        self.form_actions: List[str] = []
        self.mixed_content_assets: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, str]]) -> None:
        attr_map: Dict[str, str] = {}
        for name, value in attrs:
            if not name:
                continue
            attr_map[name.lower()] = (value or "").strip()

        tag = tag.lower()

        if tag == "a":
            href = attr_map.get("href", "")
            if href:
                self.links.append(href)

        if tag == "title":
            self.has_title_tag = True

        if tag == "meta":
            meta_name = attr_map.get("name", "").lower()
            meta_content = attr_map.get("content", "")
            if meta_name == "description" and meta_content:
                self.has_meta_description = True

        if tag == "h1":
            self.h1_count += 1

        if tag == "img" and not attr_map.get("alt", "").strip():
            self.images_missing_alt += 1

        if tag == "form":
            self.form_actions.append(attr_map.get("action", ""))

        if tag in ("script", "img", "iframe", "source"):
            src = attr_map.get("src", "")
            if src.lower().startswith("http://"):
                self.mixed_content_assets.append(src)

        if tag == "link":
            href = attr_map.get("href", "")
            if href.lower().startswith("http://"):
                self.mixed_content_assets.append(href)


def make_finding(
    title: str,
    category: str,
    severity: str,
    page: str,
    evidence: str,
    fix: str,
) -> Dict[str, str]:
    return {
        "title": title,
        "category": category,
        "severity": severity,
        "page": page,
        "evidence": evidence,
        "fix": fix,
    }


def normalize_url(raw_url: str) -> str:
    value = raw_url.strip()
    if not value:
        return ""

    if not re.match(r"^https?://", value, flags=re.IGNORECASE):
        value = "https://" + value

    parsed = urlparse(value)
    if not parsed.netloc:
        return ""

    scheme = parsed.scheme.lower()
    host = parsed.netloc.lower()
    path = parsed.path or "/"
    if path != "/" and path.endswith("/"):
        path = path[:-1]

    normalized = f"{scheme}://{host}{path}"
    if parsed.query:
        normalized += f"?{parsed.query}"

    return normalized


def remove_fragment(url: str) -> str:
    parsed = urlparse(url)
    cleaned = parsed._replace(fragment="")
    value = cleaned.geturl()
    if value.endswith("/") and cleaned.path not in ("", "/"):
        value = value[:-1]
    return value


def normalized_host(url: str) -> str:
    host = (urlparse(url).hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]
    return host


def same_domain(base_url: str, candidate_url: str) -> bool:
    return normalized_host(base_url) == normalized_host(candidate_url)


def extract_emails_from_text(text: str) -> Set[str]:
    emails: Set[str] = set()
    if not text:
        return emails

    for found in EMAIL_PATTERN.findall(text):
        email = found.strip().strip(".,;:()[]<>{}\"'").lower()
        if "@" not in email:
            continue
        local_part, domain = email.split("@", 1)
        if not local_part or not domain:
            continue
        if ".." in email:
            continue
        emails.add(email)

    return emails


def classify_public_admin_contact(email: str, base_host: str) -> Tuple[bool, str, int]:
    local_part, domain = email.split("@", 1)
    reasons: List[str] = []
    score = 0

    same_org_domain = False
    if base_host and (domain == base_host or domain.endswith("." + base_host)):
        same_org_domain = True
        reasons.append("zelfde domein")
        score += 2

    has_admin_keyword = any(keyword in local_part for keyword in ADMIN_EMAIL_KEYWORDS)
    has_contact_keyword = any(keyword in local_part for keyword in CONTACT_EMAIL_KEYWORDS)

    if has_admin_keyword:
        reasons.append("admin keyword")
        score += 3
    elif has_contact_keyword and same_org_domain:
        reasons.append("contact keyword")
        score += 1

    return score >= 3, ", ".join(reasons), score


def find_public_admin_contacts(base_url: str, pages: List[Dict[str, object]]) -> List[Dict[str, str]]:
    base_host = normalized_host(base_url)
    best_per_email: Dict[str, Dict[str, object]] = {}

    for page in pages:
        page_url = str(page.get("url", ""))
        body = str(page.get("body", ""))

        for email in extract_emails_from_text(body):
            include, reason, score = classify_public_admin_contact(email, base_host)
            if not include:
                continue

            previous = best_per_email.get(email)
            if not previous or int(previous["score"]) < score:
                best_per_email[email] = {
                    "email": email,
                    "page": page_url,
                    "reason": reason,
                    "score": score,
                }

    ordered = sorted(
        best_per_email.values(),
        key=lambda item: (-int(item["score"]), str(item["email"])),
    )

    return [
        {
            "email": str(item["email"]),
            "page": str(item["page"]),
            "reason": str(item["reason"]),
        }
        for item in ordered[:5]
    ]


def decode_body(body_bytes: bytes, headers: Dict[str, str]) -> str:
    content_type = headers.get("content-type", "")
    charset_match = re.search(r"charset=([a-zA-Z0-9_-]+)", content_type, flags=re.IGNORECASE)
    charset = charset_match.group(1) if charset_match else "utf-8"

    try:
        return body_bytes.decode(charset, errors="replace")
    except (LookupError, UnicodeDecodeError):
        return body_bytes.decode("utf-8", errors="replace")


def merge_headers(raw_headers: List[Tuple[str, str]]) -> Dict[str, str]:
    merged: Dict[str, str] = {}
    for key, value in raw_headers:
        lower_key = key.lower()
        if lower_key in merged:
            merged[lower_key] = merged[lower_key] + "; " + value
        else:
            merged[lower_key] = value
    return merged


def fetch_url(url: str, timeout: int = TIMEOUT) -> Dict[str, object]:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    started = time.time()

    try:
        with urlopen(request, timeout=timeout) as response:
            body_bytes = response.read(MAX_BODY_BYTES)
            headers = merge_headers(response.getheaders())
            return {
                "network_error": False,
                "status": int(getattr(response, "status", 200)),
                "final_url": response.geturl(),
                "headers": headers,
                "body": decode_body(body_bytes, headers),
                "elapsed": round(time.time() - started, 3),
                "error": "",
            }
    except HTTPError as exc:
        headers = merge_headers(list(exc.headers.items())) if exc.headers else {}
        try:
            body_bytes = exc.read(MAX_BODY_BYTES)
        except Exception:
            body_bytes = b""

        return {
            "network_error": False,
            "status": int(exc.code),
            "final_url": url,
            "headers": headers,
            "body": decode_body(body_bytes, headers) if body_bytes else "",
            "elapsed": round(time.time() - started, 3),
            "error": str(exc),
        }
    except (URLError, socket.timeout, ssl.SSLError, OSError) as exc:
        return {
            "network_error": True,
            "status": 0,
            "final_url": url,
            "headers": {},
            "body": "",
            "elapsed": round(time.time() - started, 3),
            "error": str(exc),
        }


def build_external_api_insights(
    findings: List[Dict[str, str]],
    pages: List[Dict[str, object]],
    links_checked: int,
    mode: str,
    git_audit: Dict[str, object],
) -> Dict[str, object]:
    security_by_severity: Dict[str, int] = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
    }

    security_total = 0
    for item in findings:
        if item["category"] != "Security":
            continue
        security_total += 1
        severity = item["severity"]
        security_by_severity[severity] = security_by_severity.get(severity, 0) + 1

    pages_crawled = len(pages)
    network_error_pages = sum(1 for page in pages if bool(page.get("network_error")))

    if security_by_severity["critical"] > 0:
        security_status = "alert"
        security_message = "Lokale scan toont kritieke security-risico's."
    elif security_by_severity["high"] > 0:
        security_status = "warn"
        security_message = "Lokale scan toont hoge security-risico's."
    elif security_total > 0:
        security_status = "warn"
        security_message = "Lokale scan toont security-verbeterpunten."
    else:
        security_status = "ok"
        security_message = "Lokale scan toont geen directe security-risico's."

    if pages_crawled == 0:
        coverage_status = "alert"
        coverage_message = "Geen pagina's gecrawld; dekking is onvoldoende."
    elif network_error_pages > 0:
        coverage_status = "warn"
        coverage_message = "Crawl deels gelukt; sommige pagina's waren niet bereikbaar."
    elif mode == "hard" and (pages_crawled < 4 or links_checked < 8):
        coverage_status = "warn"
        coverage_message = "Hard scan dekking is nog beperkt; verhoog bereik of controleer crawlblokkades."
    elif pages_crawled < 2 and links_checked == 0:
        coverage_status = "warn"
        coverage_message = "Basisdekkking is beperkt; overweeg hard scan voor meer bereik."
    else:
        coverage_status = "ok"
        coverage_message = "Crawl dekking is voldoende voor deze scanmodus."

    providers = [
        {
            "name": "Lokale Security Engine",
            "source": "local",
            "status": security_status,
            "message": security_message,
            "signals": {
                "security_total": security_total,
                "critical": security_by_severity["critical"],
                "high": security_by_severity["high"],
                "medium": security_by_severity["medium"],
                "low": security_by_severity["low"],
            },
        },
        {
            "name": "Lokale Crawl Dekking",
            "source": "local",
            "status": coverage_status,
            "message": coverage_message,
            "signals": {
                "pages_crawled": pages_crawled,
                "internal_links_checked": links_checked,
                "network_error_pages": network_error_pages,
            },
        },
    ]

    if mode == "hard" and isinstance(git_audit, dict) and bool(git_audit.get("enabled")):
        provider_status = str(git_audit.get("status", "ok"))
        provider_message = str(git_audit.get("message", "Hard git audit uitgevoerd."))
        remote_urls = git_audit.get("remote_urls", [])
        remote_provider = str(git_audit.get("remote_provider", "Onbekend"))

        providers.append(
            {
                "name": "Lokale Git Audit",
                "source": "local",
                "status": provider_status,
                "message": provider_message,
                "signals": {
                    "paths_checked": int(git_audit.get("paths_checked", 0)),
                    "exposed_count": int(git_audit.get("exposed_count", 0)),
                    "remote_urls": len(remote_urls) if isinstance(remote_urls, list) else 0,
                    "remote_provider": remote_provider,
                },
            }
        )

    alerts = sum(1 for item in providers if str(item.get("status", "")) == "alert")
    warnings = sum(1 for item in providers if str(item.get("status", "")) == "warn")
    errors = sum(1 for item in providers if str(item.get("status", "")) == "error")

    return {
        "mode": "local_only",
        "providers": providers,
        "providers_total": len(providers),
        "configured": len(providers),
        "alerts": alerts,
        "warnings": warnings,
        "errors": errors,
    }


def normalize_discovered_link(current_url: str, raw_link: str) -> str:
    candidate = (raw_link or "").strip()
    if not candidate:
        return ""

    lower = candidate.lower()
    if lower.startswith("#") or lower.startswith("mailto:") or lower.startswith("tel:"):
        return ""
    if lower.startswith("javascript:") or lower.startswith("data:"):
        return ""

    absolute = urljoin(current_url, candidate)
    parsed = urlparse(absolute)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return ""

    cleaned = parsed._replace(fragment="")
    result = cleaned.geturl()
    if result.endswith("/") and cleaned.path not in ("", "/"):
        result = result[:-1]

    return result


def sorted_findings(findings: List[Dict[str, str]]) -> List[Dict[str, str]]:
    return sorted(
        findings,
        key=lambda item: (
            -SEVERITY_ORDER.get(item["severity"], 0),
            item["category"],
            item["title"],
        ),
    )


def dedupe_findings(findings: List[Dict[str, str]]) -> List[Dict[str, str]]:
    unique: List[Dict[str, str]] = []
    seen: Set[Tuple[str, str, str, str]] = set()

    for item in findings:
        key = (item["title"], item["category"], item["severity"], item["page"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)

    return unique


def check_ssl_tls(base_url: str) -> List[Dict[str, str]]:
    findings: List[Dict[str, str]] = []
    parsed = urlparse(base_url)

    if parsed.scheme != "https":
        findings.append(
            make_finding(
                "Website gebruikt geen HTTPS",
                "Security",
                "critical",
                base_url,
                "URL start niet met https://",
                "Forceer HTTPS en stuur HTTP door naar HTTPS.",
            )
        )
        return findings

    host = parsed.hostname
    if not host:
        return findings

    try:
        context = ssl.create_default_context()
        with socket.create_connection((host, 443), timeout=TIMEOUT) as sock:
            with context.wrap_socket(sock, server_hostname=host) as tls_sock:
                cert = tls_sock.getpeercert()

                if not cert:
                    findings.append(
                        make_finding(
                            "SSL certificaat ontbreekt",
                            "Security",
                            "high",
                            base_url,
                            "Geen certificaatdata ontvangen.",
                            "Controleer TLS en certificaat chain.",
                        )
                    )
                else:
                    expires = cert.get("notAfter")
                    if expires:
                        try:
                            expires_date = datetime.strptime(expires, "%b %d %H:%M:%S %Y %Z").replace(
                                tzinfo=timezone.utc
                            )
                            days_left = (expires_date - datetime.now(timezone.utc)).days
                            if days_left < 0:
                                findings.append(
                                    make_finding(
                                        "SSL certificaat is verlopen",
                                        "Security",
                                        "critical",
                                        base_url,
                                        f"Certificaat vervallen op {expires_date.isoformat()}",
                                        "Vernieuw certificaat direct.",
                                    )
                                )
                            elif days_left < 21:
                                findings.append(
                                    make_finding(
                                        "SSL certificaat verloopt bijna",
                                        "Security",
                                        "high",
                                        base_url,
                                        f"Nog {days_left} dagen geldig.",
                                        "Plan certificaatvernieuwing.",
                                    )
                                )
                        except ValueError:
                            pass
    except Exception as exc:
        findings.append(
            make_finding(
                "SSL/TLS handshake fout",
                "Security",
                "high",
                base_url,
                str(exc),
                "Herstel TLS configuratie, certificaat en firewall regels.",
            )
        )

    return findings


def check_headers_and_cookies(page: Dict[str, object]) -> List[Dict[str, str]]:
    findings: List[Dict[str, str]] = []
    url = str(page["url"])
    headers = page["headers"] if isinstance(page["headers"], dict) else {}

    for header in SECURITY_HEADERS:
        if header not in headers:
            findings.append(
                make_finding(
                    f"Security header ontbreekt: {header}",
                    "Security",
                    "medium",
                    url,
                    "Header niet gevonden.",
                    f"Voeg {header} toe met een veilige waarde.",
                )
            )

    server_header = str(headers.get("server", "")).strip()
    if server_header:
        findings.append(
            make_finding(
                "Server fingerprint zichtbaar",
                "Security",
                "low",
                url,
                f"Server header: {server_header}",
                "Verberg serverversie en fingerprints in response headers.",
            )
        )

    powered_header = str(headers.get("x-powered-by", "")).strip()
    if powered_header:
        findings.append(
            make_finding(
                "X-Powered-By zichtbaar",
                "Security",
                "low",
                url,
                f"X-Powered-By: {powered_header}",
                "Verwijder framework versies uit response headers.",
            )
        )

    cookie = str(headers.get("set-cookie", "")).lower()
    if cookie:
        if "secure" not in cookie:
            findings.append(
                make_finding(
                    "Cookie mist Secure flag",
                    "Security",
                    "medium",
                    url,
                    "Set-Cookie zonder Secure.",
                    "Zet Secure op alle sessie cookies.",
                )
            )

        if "httponly" not in cookie:
            findings.append(
                make_finding(
                    "Cookie mist HttpOnly flag",
                    "Security",
                    "medium",
                    url,
                    "Set-Cookie zonder HttpOnly.",
                    "Zet HttpOnly op sessie cookies.",
                )
            )

        if "samesite" not in cookie:
            findings.append(
                make_finding(
                    "Cookie mist SameSite flag",
                    "Security",
                    "medium",
                    url,
                    "Set-Cookie zonder SameSite.",
                    "Gebruik SameSite=Lax of SameSite=Strict.",
                )
            )

    return findings


def check_page_quality(page: Dict[str, object]) -> Tuple[List[Dict[str, str]], Set[str]]:
    findings: List[Dict[str, str]] = []
    internal_links: Set[str] = set()

    url = str(page["url"])
    status = int(page["status"])
    elapsed = float(page["elapsed"])
    headers = page["headers"] if isinstance(page["headers"], dict) else {}
    body = str(page["body"])
    content_type = str(headers.get("content-type", "")).lower()

    if status >= 500:
        findings.append(
            make_finding(
                "Server fout op pagina",
                "Intern",
                "high",
                url,
                f"HTTP {status}",
                "Controleer server logs en herstel backend fouten.",
            )
        )
    elif status >= 400:
        findings.append(
            make_finding(
                "Client fout op pagina",
                "Intern",
                "medium",
                url,
                f"HTTP {status}",
                "Herstel routes, links en status handling.",
            )
        )

    if elapsed > 3:
        findings.append(
            make_finding(
                "Langzame paginalaad",
                "Performance",
                "medium",
                url,
                f"Reactietijd: {elapsed} seconden",
                "Optimaliseer caching, database queries en assets.",
            )
        )

    if "content-encoding" not in headers and "text/html" in content_type:
        findings.append(
            make_finding(
                "Compressie ontbreekt",
                "Performance",
                "low",
                url,
                "Geen content-encoding header op HTML response.",
                "Activeer gzip of brotli op de server.",
            )
        )

    if len(body) > 500000:
        findings.append(
            make_finding(
                "Pagina payload is zwaar",
                "Performance",
                "medium",
                url,
                f"HTML grootte: {len(body)} bytes",
                "Beperk inline scripts/styles en laad resources asynchroon.",
            )
        )

    if not body:
        return findings, internal_links

    parser = PageParser()
    try:
        parser.feed(body)
    except Exception:
        pass

    for raw_link in parser.links:
        normalized = normalize_discovered_link(url, raw_link)
        if not normalized:
            continue
        if same_domain(url, normalized):
            internal_links.add(normalized)

    if not parser.has_title_tag:
        findings.append(
            make_finding(
                "Title tag ontbreekt",
                "Ontwerp",
                "low",
                url,
                "Geen <title> element gevonden.",
                "Voeg een duidelijke title toe per pagina.",
            )
        )

    if not parser.has_meta_description:
        findings.append(
            make_finding(
                "Meta description ontbreekt",
                "Ontwerp",
                "low",
                url,
                "Geen meta description gevonden.",
                "Voeg een korte description toe voor SEO en snippets.",
            )
        )

    if parser.h1_count == 0:
        findings.append(
            make_finding(
                "H1 heading ontbreekt",
                "Ontwerp",
                "medium",
                url,
                "Geen <h1> op pagina.",
                "Voeg precies een duidelijke H1 toe.",
            )
        )
    elif parser.h1_count > 1:
        findings.append(
            make_finding(
                "Meerdere H1 headings",
                "Ontwerp",
                "low",
                url,
                f"Aantal H1 tags: {parser.h1_count}",
                "Gebruik bij voorkeur een H1 per pagina.",
            )
        )

    if parser.images_missing_alt > 0:
        findings.append(
            make_finding(
                "Afbeeldingen zonder alt tekst",
                "Ontwerp",
                "medium",
                url,
                f"Aantal zonder alt: {parser.images_missing_alt}",
                "Voeg alt teksten toe voor toegankelijkheid en SEO.",
            )
        )

    if parser.mixed_content_assets:
        findings.append(
            make_finding(
                "Mixed content assets gevonden",
                "Security",
                "medium",
                url,
                ", ".join(parser.mixed_content_assets[:5]),
                "Laad alle scripts, styles en images via HTTPS.",
            )
        )

    insecure_form_found = False
    for action in parser.form_actions:
        target = urljoin(url, action) if action else url
        if target.lower().startswith("http://"):
            insecure_form_found = True
            break

    if insecure_form_found:
        findings.append(
            make_finding(
                "Form submit over HTTP",
                "Security",
                "critical",
                url,
                "Form action wijst naar een niet HTTPS endpoint.",
                "Gebruik altijd HTTPS op formulieren en API endpoints.",
            )
        )

    if re.search(r"(api[_-]?key|access[_-]?token|secret)\s*[:=]", body, flags=re.IGNORECASE):
        findings.append(
            make_finding(
                "Mogelijke gevoelige sleutel in pagina bron",
                "Security",
                "high",
                url,
                "Pattern zoals api_key/secret gevonden in HTML of inline scripts.",
                "Verplaats secrets naar backend en environment variables.",
            )
        )

    return findings, internal_links


def crawl_and_analyze(base_url: str, mode: str) -> Tuple[List[Dict[str, object]], List[Dict[str, str]], Set[str]]:
    max_pages = HARD_MAX_PAGES if mode == "hard" else QUICK_MAX_PAGES

    queue_urls: List[str] = [base_url]
    visited: Set[str] = set()
    pages: List[Dict[str, object]] = []
    findings: List[Dict[str, str]] = []
    internal_links: Set[str] = set()

    while queue_urls and len(visited) < max_pages:
        current = remove_fragment(queue_urls.pop(0))
        if current in visited:
            continue

        response = fetch_url(current)
        visited.add(current)

        page_record: Dict[str, object] = {
            "url": remove_fragment(str(response["final_url"])),
            "status": int(response["status"]),
            "headers": response["headers"],
            "body": response["body"],
            "elapsed": float(response["elapsed"]),
            "error": str(response["error"]),
            "network_error": bool(response["network_error"]),
        }
        pages.append(page_record)

        if bool(response["network_error"]):
            findings.append(
                make_finding(
                    "Pagina niet bereikbaar",
                    "Intern",
                    "high",
                    current,
                    str(response["error"]),
                    "Controleer DNS, firewall, hosting en SSL instellingen.",
                )
            )
            continue

        header_findings = check_headers_and_cookies(page_record)
        page_findings, discovered_links = check_page_quality(page_record)

        findings.extend(header_findings)
        findings.extend(page_findings)

        for link in discovered_links:
            internal_links.add(link)
            if link not in visited and link not in queue_urls and same_domain(base_url, link):
                queue_urls.append(link)

    return pages, findings, internal_links


def check_special_files(base_url: str, mode: str) -> List[Dict[str, str]]:
    findings: List[Dict[str, str]] = []
    paths: List[Tuple[str, str]] = [
        ("/robots.txt", "Intern"),
        ("/sitemap.xml", "Intern"),
    ]

    if mode == "hard":
        paths.extend(
            [
                ("/security.txt", "Security"),
                ("/.well-known/security.txt", "Security"),
            ]
        )

    for path, category in paths:
        target = urljoin(base_url + "/", path.lstrip("/"))
        response = fetch_url(target, timeout=6)

        if int(response["status"]) != 200:
            findings.append(
                make_finding(
                    f"Bestand ontbreekt of niet bereikbaar: {path}",
                    category,
                    "low",
                    target,
                    f"HTTP status: {response['status']}",
                    f"Voeg {path} toe als dit van toepassing is.",
                )
            )

    return findings


def check_exposed_paths(base_url: str, mode: str) -> List[Dict[str, str]]:
    findings: List[Dict[str, str]] = []
    paths = HARD_EXPOSED_PATHS if mode == "hard" else QUICK_EXPOSED_PATHS

    for path in paths:
        if mode == "hard" and path == "/.git/config":
            # Hard mode uses a dedicated git audit for deeper and cleaner reporting.
            continue

        target = urljoin(base_url + "/", path.lstrip("/"))
        response = fetch_url(target, timeout=6)
        status = int(response["status"])

        if status == 200 and len(str(response["body"])) > 20:
            if path in ("/admin", "/login"):
                severity = "low"
            elif path in ("/.env", "/.git/config", "/backup.sql", "/database.sql", "/wp-config.php"):
                severity = "high"
            else:
                severity = "medium"

            findings.append(
                make_finding(
                    f"Mogelijk gevoelig pad bereikbaar: {path}",
                    "Security",
                    severity,
                    target,
                    f"HTTP 200 met response lengte {len(str(response['body']))}",
                    "Blokkeer publiek toegang en scherm admin of debug data af.",
                )
            )

    return findings


def extract_git_remote_urls(config_text: str) -> List[str]:
    urls: List[str] = []
    if not config_text:
        return urls

    for found in GIT_REMOTE_URL_PATTERN.findall(config_text):
        value = found.strip()
        if not value:
            continue
        if value not in urls:
            urls.append(value)

    return urls[:5]


def extract_git_head_ref(head_text: str) -> str:
    if not head_text:
        return ""

    match = GIT_HEAD_REF_PATTERN.search(head_text)
    if not match:
        return ""

    return match.group(1)


def detect_git_provider(remote_urls: List[str]) -> str:
    for remote_url in remote_urls:
        lower_url = remote_url.lower()
        if "github.com" in lower_url:
            return "GitHub"
        if "gitlab.com" in lower_url:
            return "GitLab"
        if "bitbucket.org" in lower_url:
            return "Bitbucket"

    return "Onbekend"


def run_git_audit(base_url: str, mode: str) -> Tuple[Dict[str, object], List[Dict[str, str]]]:
    if mode != "hard":
        return {
            "enabled": False,
            "status": "quick_only",
            "message": "Quick scan draait zonder uitgebreide git deep-audit.",
            "paths_checked": 0,
            "exposed_count": 0,
            "exposed_paths": [],
            "remote_urls": [],
            "remote_provider": "Onbekend",
            "head_ref": "",
        }, []

    findings: List[Dict[str, str]] = []
    exposed_paths: List[Dict[str, object]] = []
    remote_urls: List[str] = []
    head_ref = ""

    for path in HARD_GIT_AUDIT_PATHS:
        target = urljoin(base_url + "/", path.lstrip("/"))
        response = fetch_url(target, timeout=6)
        status = int(response["status"])
        body = str(response["body"])
        body_len = len(body)

        if status != 200 or body_len <= 0:
            continue

        exposed_paths.append(
            {
                "path": path,
                "status": status,
                "size": body_len,
            }
        )

        if path == "/.git/config":
            remote_urls = extract_git_remote_urls(body)
        if path == "/.git/HEAD":
            head_ref = extract_git_head_ref(body)

        if path in (
            "/.git/config",
            "/.git/index",
            "/.git/logs/HEAD",
            "/.git/FETCH_HEAD",
            "/.git/packed-refs",
        ):
            severity = "critical"
        else:
            severity = "high"

        findings.append(
            make_finding(
                f"Git metadata publiek bereikbaar: {path}",
                "Security",
                severity,
                target,
                f"HTTP 200 en inhoudslengte {body_len}",
                "Blokkeer publiek toegang tot /.git en redeploy zonder git bestanden in webroot.",
            )
        )

    remote_provider = detect_git_provider(remote_urls)
    if remote_urls:
        findings.append(
            make_finding(
                "Git remote koppeling zichtbaar in productie",
                "Security",
                "critical",
                base_url,
                ", ".join(remote_urls[:2]),
                "Verwijder gelekte git metadata en deploy een schone build zonder .git map.",
            )
        )

    if exposed_paths:
        status = "alert"
        message = "Publiek toegankelijke .git metadata gevonden; directe actie nodig."
    else:
        status = "ok"
        message = "Geen publiek toegankelijke .git metadata gevonden in hard audit."

    return {
        "enabled": True,
        "status": status,
        "message": message,
        "paths_checked": len(HARD_GIT_AUDIT_PATHS),
        "exposed_count": len(exposed_paths),
        "exposed_paths": exposed_paths,
        "remote_urls": remote_urls,
        "remote_provider": remote_provider,
        "head_ref": head_ref,
    }, findings


def probe_internal_links(links: Set[str], mode: str) -> Tuple[List[Dict[str, str]], int]:
    findings: List[Dict[str, str]] = []
    limit = HARD_LINK_PROBES if mode == "hard" else QUICK_LINK_PROBES
    checked = 0

    for link in sorted(links):
        if checked >= limit:
            break

        response = fetch_url(link, timeout=6)
        checked += 1

        if bool(response["network_error"]):
            findings.append(
                make_finding(
                    "Interne link niet bereikbaar",
                    "Intern",
                    "high",
                    link,
                    str(response["error"]),
                    "Herstel interne verwijzing en controleer hosting bereikbaarheid.",
                )
            )
            continue

        status = int(response["status"])
        if status >= 500:
            findings.append(
                make_finding(
                    "Interne link geeft serverfout",
                    "Intern",
                    "high",
                    link,
                    f"HTTP {status}",
                    "Onderzoek backend fout op dit endpoint.",
                )
            )
        elif status >= 400:
            findings.append(
                make_finding(
                    "Interne link geeft clientfout",
                    "Intern",
                    "medium",
                    link,
                    f"HTTP {status}",
                    "Werk de link bij of herstel de pagina.",
                )
            )

    return findings, checked


def calculate_ratings(findings: List[Dict[str, str]]) -> Tuple[Dict[str, float], float]:
    ratings: Dict[str, float] = {
        "Intern": 5.0,
        "Security": 5.0,
        "Ontwerp": 5.0,
        "Performance": 5.0,
    }

    for finding in findings:
        category = finding["category"]
        if category in ratings:
            ratings[category] -= SEVERITY_PENALTY.get(finding["severity"], 0.25)

    for key in ratings:
        ratings[key] = max(1.0, min(5.0, round(ratings[key], 1)))

    overall = round(sum(ratings.values()) / len(ratings), 1)
    return ratings, overall


def build_analytics(findings: List[Dict[str, str]]) -> Dict[str, object]:
    by_severity: Dict[str, int] = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
    }

    by_category: Dict[str, int] = {
        "Intern": 0,
        "Security": 0,
        "Ontwerp": 0,
        "Performance": 0,
    }

    for finding in findings:
        severity = finding["severity"]
        category = finding["category"]
        by_severity[severity] = by_severity.get(severity, 0) + 1
        by_category[category] = by_category.get(category, 0) + 1

    return {
        "by_severity": by_severity,
        "by_category": by_category,
        "total_findings": len(findings),
    }


def grade_from_score(score: float) -> str:
    if score >= 4.8:
        return "A+"
    if score >= 4.4:
        return "A"
    if score >= 3.8:
        return "B"
    if score >= 3.0:
        return "C"
    if score >= 2.2:
        return "D"
    return "E"


def collect_security_titles(findings: List[Dict[str, str]]) -> Set[str]:
    return {
        str(item.get("title", ""))
        for item in findings
        if str(item.get("category", "")) == "Security"
    }


def has_security_title_prefix(findings: List[Dict[str, str]], title_prefix: str) -> bool:
    for item in findings:
        if str(item.get("category", "")) != "Security":
            continue
        if str(item.get("title", "")).startswith(title_prefix):
            return True
    return False


def build_benchmark_overview(base_url: str, findings: List[Dict[str, str]]) -> Dict[str, object]:
    checks: List[Dict[str, str]] = []
    security_titles = collect_security_titles(findings)

    def add_check(name: str, status: str, detail: str) -> None:
        checks.append({"name": name, "status": status, "detail": detail})

    uses_https = urlparse(base_url).scheme == "https"
    if uses_https and "Website gebruikt geen HTTPS" not in security_titles:
        add_check("HTTPS actief", "pass", "Website gebruikt HTTPS als basis.")
    else:
        add_check("HTTPS actief", "fail", "Website forceert nog geen veilige HTTPS-verbinding.")

    if (
        "SSL certificaat ontbreekt" in security_titles
        or "SSL certificaat is verlopen" in security_titles
        or "SSL/TLS handshake fout" in security_titles
    ):
        add_check("TLS certificaat status", "fail", "Certificaat of handshake bevat kritieke problemen.")
    elif "SSL certificaat verloopt bijna" in security_titles:
        add_check("TLS certificaat status", "warn", "Certificaat moet op korte termijn vernieuwd worden.")
    else:
        add_check("TLS certificaat status", "pass", "Geen directe certificaatproblemen gevonden.")

    if "Security header ontbreekt: strict-transport-security" in security_titles:
        add_check("HSTS header", "fail", "Strict-Transport-Security ontbreekt.")
    else:
        add_check("HSTS header", "pass", "HSTS lijkt aanwezig.")

    if "Security header ontbreekt: content-security-policy" in security_titles:
        add_check("CSP header", "warn", "Content-Security-Policy ontbreekt.")
    else:
        add_check("CSP header", "pass", "CSP lijkt aanwezig.")

    if "Security header ontbreekt: x-frame-options" in security_titles:
        add_check("Clickjacking bescherming", "warn", "X-Frame-Options ontbreekt.")
    else:
        add_check("Clickjacking bescherming", "pass", "X-Frame-Options lijkt aanwezig.")

    if "Security header ontbreekt: x-content-type-options" in security_titles:
        add_check("MIME sniff bescherming", "warn", "X-Content-Type-Options ontbreekt.")
    else:
        add_check("MIME sniff bescherming", "pass", "X-Content-Type-Options lijkt aanwezig.")

    if (
        "Cookie mist Secure flag" in security_titles
        or "Cookie mist HttpOnly flag" in security_titles
        or "Cookie mist SameSite flag" in security_titles
    ):
        add_check("Cookie hardening", "fail", "Een of meer cookie beveiligingsflags ontbreken.")
    else:
        add_check("Cookie hardening", "pass", "Geen directe cookie hardening issues gevonden.")

    if "Mixed content assets gevonden" in security_titles:
        add_check("Mixed content", "fail", "Assets worden nog via HTTP geladen.")
    else:
        add_check("Mixed content", "pass", "Geen mixed content aangetroffen.")

    if "Form submit over HTTP" in security_titles:
        add_check("Form submit via HTTPS", "fail", "Minimaal een formulier post nog naar HTTP.")
    else:
        add_check("Form submit via HTTPS", "pass", "Form submit lijkt via HTTPS te verlopen.")

    if has_security_title_prefix(findings, "Mogelijk gevoelig pad bereikbaar:"):
        add_check("Gevoelige paden afgeschermd", "fail", "Publiek bereikbare gevoelige paden zijn gedetecteerd.")
    else:
        add_check("Gevoelige paden afgeschermd", "pass", "Geen direct bereikbare gevoelige paden gevonden.")

    if "Mogelijke gevoelige sleutel in pagina bron" in security_titles:
        add_check("Secrets in broncode", "fail", "Mogelijke API key of secret in frontend bron gedetecteerd.")
    else:
        add_check("Secrets in broncode", "pass", "Geen duidelijke secrets in broncode gedetecteerd.")

    totals = {"pass": 0, "warn": 0, "fail": 0}
    for item in checks:
        status = str(item.get("status", "warn"))
        totals[status] = totals.get(status, 0) + 1

    benchmark_score = int(round((totals["pass"] / max(len(checks), 1)) * 100))

    return {
        "score": benchmark_score,
        "totals": totals,
        "checks": checks,
    }


def map_security_finding_to_owasp(title: str) -> str:
    lower_title = title.lower()

    if "gevoelig pad" in lower_title:
        return "A01 Broken Access Control"

    if (
        "https" in lower_title
        or "ssl" in lower_title
        or "tls" in lower_title
        or "cookie" in lower_title
        or "mixed content" in lower_title
        or "form submit" in lower_title
        or "sleutel" in lower_title
    ):
        return "A02 Cryptographic Failures"

    return "A05 Security Misconfiguration"


def build_owasp_overview(findings: List[Dict[str, str]]) -> List[Dict[str, object]]:
    counters: Dict[str, int] = {}

    for item in findings:
        if str(item.get("category", "")) != "Security":
            continue

        title = str(item.get("title", ""))
        owasp_key = map_security_finding_to_owasp(title)
        counters[owasp_key] = counters.get(owasp_key, 0) + 1

    ordered = sorted(counters.items(), key=lambda pair: (-pair[1], pair[0]))
    return [{"category": key, "count": value} for key, value in ordered[:5]]


def detect_technology_fingerprint(pages: List[Dict[str, object]]) -> List[str]:
    found: Set[str] = set()

    for page in pages:
        headers = page.get("headers", {})
        header_map = headers if isinstance(headers, dict) else {}

        server_header = str(header_map.get("server", "")).lower()
        powered_header = str(header_map.get("x-powered-by", "")).lower()
        via_header = str(header_map.get("via", "")).lower()

        if "cloudflare" in server_header or "cloudflare" in via_header or "cf-ray" in header_map:
            found.add("Cloudflare")
        if "nginx" in server_header:
            found.add("Nginx")
        if "apache" in server_header:
            found.add("Apache")
        if "iis" in server_header:
            found.add("IIS")
        if "php" in powered_header:
            found.add("PHP")
        if "asp.net" in powered_header:
            found.add("ASP.NET")
        if "express" in powered_header or "node" in powered_header:
            found.add("Node.js")

        body = str(page.get("body", "")).lower()
        if not body:
            continue

        for marker, label in TECH_BODY_MARKERS:
            if marker in body:
                found.add(label)

    if not found:
        return ["Onbekend"]

    return sorted(found)[:8]


def build_industry_snapshot(
    base_url: str,
    findings: List[Dict[str, str]],
    ratings: Dict[str, float],
    overall: float,
    pages: List[Dict[str, object]],
) -> Dict[str, object]:
    security_findings = [item for item in findings if item["category"] == "Security"]

    by_severity: Dict[str, int] = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
    }
    for item in security_findings:
        severity = item["severity"]
        by_severity[severity] = by_severity.get(severity, 0) + 1

    risk_points = 0
    for severity, count in by_severity.items():
        risk_points += SEVERITY_RISK_POINTS.get(severity, 0) * count

    risk_score = min(100, risk_points)
    if risk_score >= 80:
        risk_level = "Kritiek"
    elif risk_score >= 55:
        risk_level = "Hoog"
    elif risk_score >= 30:
        risk_level = "Gemiddeld"
    elif risk_score >= 10:
        risk_level = "Laag"
    else:
        risk_level = "Minimaal"

    highest_severity = "none"
    for level in ("critical", "high", "medium", "low"):
        if by_severity[level] > 0:
            highest_severity = level
            break

    if highest_severity == "critical":
        sla_priority = "Direct (0-24 uur)"
    elif highest_severity == "high":
        sla_priority = "Binnen 7 dagen"
    elif highest_severity == "medium":
        sla_priority = "Binnen 30 dagen"
    else:
        sla_priority = "Planmatig verbeteren"

    if overall >= 4.2:
        market_position = "Bovengemiddeld"
    elif overall >= 3.2:
        market_position = "Gemiddeld"
    else:
        market_position = "Onder gemiddeld"

    benchmark = build_benchmark_overview(base_url, findings)
    owasp_top = build_owasp_overview(findings)
    technologies = detect_technology_fingerprint(pages)

    return {
        "overall_grade": grade_from_score(overall),
        "security_grade": grade_from_score(float(ratings["Security"])),
        "risk_score": risk_score,
        "risk_level": risk_level,
        "highest_severity": highest_severity,
        "sla_priority": sla_priority,
        "market_position": market_position,
        "benchmark": benchmark,
        "owasp_top": owasp_top,
        "technologies": technologies,
    }


def build_security_overview(
    findings: List[Dict[str, str]],
    security_rating: float,
    pages_crawled: int,
) -> Dict[str, object]:
    security_findings = [item for item in sorted_findings(findings) if item["category"] == "Security"]

    by_severity: Dict[str, int] = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
    }

    for item in security_findings:
        severity = item["severity"]
        by_severity[severity] = by_severity.get(severity, 0) + 1

    if pages_crawled == 0:
        status = "Niet volledig gemeten"
        customer_note = "Website was niet goed bereikbaar, security check is gedeeltelijk uitgevoerd."
    elif by_severity["critical"] > 0:
        status = "Direct actie nodig"
        customer_note = "Er zijn kritieke security-risico's gevonden die direct aandacht nodig hebben."
    elif by_severity["high"] > 0 or security_rating <= 3.0:
        status = "Aandacht nodig"
        customer_note = "Er zijn duidelijke security-risico's die snel opgepakt moeten worden."
    elif security_findings:
        status = "Verbeterpunten"
        customer_note = "Basis is aanwezig, maar er zijn nog security-verbeterpunten open."
    else:
        status = "Geen directe risico's"
        customer_note = "Geen directe security-risico's gedetecteerd in deze scan."

    top_items = [
        {
            "title": item["title"],
            "severity": item["severity"],
            "page": item["page"],
            "fix": item["fix"],
        }
        for item in security_findings[:3]
    ]

    return {
        "status": status,
        "score": security_rating,
        "total_security_findings": len(security_findings),
        "by_severity": by_severity,
        "top_items": top_items,
        "customer_note": customer_note,
    }


def build_ai_summary(
    findings: List[Dict[str, str]],
    ratings: Dict[str, float],
    overall: float,
) -> Dict[str, object]:
    sorted_items = sorted_findings(findings)
    top_items = sorted_items[:6]

    top_priority_items = [
        {
            "title": item["title"],
            "severity": item["severity"],
            "page": item["page"],
            "fix": item["fix"],
        }
        for item in top_items
    ]

    action_plan: List[str] = []

    if ratings["Security"] <= 3.0:
        action_plan.append("Pak eerst Security aan: HTTPS, headers, cookies en exposed files.")
    if ratings["Intern"] <= 3.0:
        action_plan.append("Fix interne fouten: 4xx/5xx endpoints en kapotte links.")
    if ratings["Performance"] <= 3.0:
        action_plan.append("Verbeter snelheid met caching, compressie en lichtere pagina payloads.")
    if ratings["Ontwerp"] <= 3.0:
        action_plan.append("Werk on-page kwaliteit bij: title, meta description, H1 en alt teksten.")

    if not action_plan:
        action_plan.append("Basis staat goed. Los de open medium en low findings op voor extra kwaliteit.")

    return {
        "summary": f"AI quickcheck geeft een totaalscore van {overall}/5.",
        "top_priorities": top_priority_items,
        "action_plan": action_plan,
    }


def run_scan(url: str, mode: str) -> Dict[str, object]:
    selected_mode = "hard" if mode == "hard" else "quick"
    base_url = normalize_url(url)

    if not base_url:
        raise ValueError("Voer een geldige URL in, bijvoorbeeld example.com")

    findings: List[Dict[str, str]] = []

    findings.extend(check_ssl_tls(base_url))

    pages, crawl_findings, discovered_links = crawl_and_analyze(base_url, selected_mode)
    findings.extend(crawl_findings)

    if not pages:
        findings.append(
            make_finding(
                "Geen pagina opgehaald",
                "Intern",
                "critical",
                base_url,
                "Crawler heeft geen enkele pagina kunnen ophalen.",
                "Controleer URL, DNS, hosting en firewall instellingen.",
            )
        )

    findings.extend(check_special_files(base_url, selected_mode))
    findings.extend(check_exposed_paths(base_url, selected_mode))

    git_audit, git_findings = run_git_audit(base_url, selected_mode)
    findings.extend(git_findings)

    link_findings, links_checked = probe_internal_links(discovered_links, selected_mode)
    findings.extend(link_findings)

    public_admin_contacts = find_public_admin_contacts(base_url, pages)

    findings = dedupe_findings(findings)
    ratings, overall = calculate_ratings(findings)
    analytics = build_analytics(findings)
    security_overview = build_security_overview(findings, float(ratings["Security"]), len(pages))
    industry_snapshot = build_industry_snapshot(base_url, findings, ratings, overall, pages)
    external_api_insights = build_external_api_insights(
        findings,
        pages,
        links_checked,
        selected_mode,
        git_audit,
    )
    ai_summary = build_ai_summary(findings, ratings, overall)

    scan_profile = {
        "mode": selected_mode,
        "depth": "full" if selected_mode == "hard" else "compact",
        "page_target": HARD_MAX_PAGES if selected_mode == "hard" else QUICK_MAX_PAGES,
        "link_probe_target": HARD_LINK_PROBES if selected_mode == "hard" else QUICK_LINK_PROBES,
        "git_deep_audit": bool(git_audit.get("enabled")),
    }

    report = {
        "target": base_url,
        "scan_type": selected_mode,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "pages_crawled": len(pages),
        "internal_links_checked": links_checked,
        "public_admin_contacts": public_admin_contacts,
        "scan_profile": scan_profile,
        "ratings": ratings,
        "security_overview": security_overview,
        "industry_snapshot": industry_snapshot,
        "benchmark": industry_snapshot["benchmark"],
        "owasp_top": industry_snapshot["owasp_top"],
        "technology_fingerprint": industry_snapshot["technologies"],
        "git_audit": git_audit,
        "external_api_insights": external_api_insights,
        "overall_rating": overall,
        "analytics": analytics,
        "findings": sorted_findings(findings),
        "ai_summary": ai_summary,
    }

    return report


def stars_for_score(score: float) -> str:
    stars = max(1, min(5, int(round(score))))
    return "*" * stars + "-" * (5 - stars)


def report_to_text(report: Dict[str, object]) -> str:
    ratings = report["ratings"]
    findings = report["findings"]
    ai_summary = report["ai_summary"]
    scan_profile = report.get("scan_profile", {})
    public_admin_contacts = report.get("public_admin_contacts", [])
    security_overview = report.get("security_overview", {})
    industry_snapshot = report.get("industry_snapshot", {})
    benchmark = report.get("benchmark", {})
    owasp_top = report.get("owasp_top", [])
    technology_fingerprint = report.get("technology_fingerprint", [])
    git_audit = report.get("git_audit", {})
    external_api_insights = report.get("external_api_insights", {})

    lines: List[str] = []
    lines.append("=== QUICK CHECKER RAPPORT ===")
    lines.append(f"Target: {report['target']}")
    lines.append(f"Scan type: {report['scan_type']}")
    lines.append(f"Tijdstip: {report['timestamp']}")
    lines.append(f"Paginas gecrawld: {report['pages_crawled']}")
    lines.append(f"Interne links gecheckt: {report['internal_links_checked']}")
    lines.append("")

    lines.append("--- Scan Profiel ---")
    if isinstance(scan_profile, dict):
        mode_label = str(scan_profile.get("mode", report.get("scan_type", "quick"))).lower()
        depth_label = str(scan_profile.get("depth", "compact"))
        page_target = int(scan_profile.get("page_target", 0))
        link_target = int(scan_profile.get("link_probe_target", 0))
        git_enabled = bool(scan_profile.get("git_deep_audit", False))

        if mode_label == "hard":
            lines.append("- HARDSCAN: volledige deep audit op website + git metadata checks.")
        else:
            lines.append("- QUICKSCAN: compacte baseline op belangrijkste fouten en risico's.")

        lines.append(f"- Diepte: {depth_label}")
        lines.append(f"- Target pagina's: {page_target}")
        lines.append(f"- Target interne link probes: {link_target}")
        lines.append(f"- Git deep audit: {'Ja' if git_enabled else 'Nee'}")
    else:
        lines.append("- Profielinformatie niet beschikbaar.")

    lines.append("")

    lines.append("--- Publiek admin account check ---")
    if isinstance(public_admin_contacts, list) and public_admin_contacts:
        for item in public_admin_contacts:
            if not isinstance(item, dict):
                continue
            email = str(item.get("email", ""))
            page = str(item.get("page", ""))
            reason = str(item.get("reason", ""))
            lines.append(f"- {email} | Pagina: {page} | Reden: {reason}")
    else:
        lines.append("- Geen publiek admin account gevonden in gescande paginas.")

    lines.append("")

    lines.append("--- Security check (klantgericht) ---")
    if isinstance(security_overview, dict):
        status = str(security_overview.get("status", "Onbekend"))
        total_security = int(security_overview.get("total_security_findings", 0))
        customer_note = str(security_overview.get("customer_note", ""))
        by_severity = security_overview.get("by_severity", {})

        lines.append(f"Status: {status}")
        lines.append(f"Security score: {ratings['Security']}/5")
        lines.append(f"Security findings: {total_security}")
        lines.append(
            "Verdeling: "
            f"Critical={int(by_severity.get('critical', 0))}, "
            f"High={int(by_severity.get('high', 0))}, "
            f"Medium={int(by_severity.get('medium', 0))}, "
            f"Low={int(by_severity.get('low', 0))}"
        )
        if customer_note:
            lines.append(f"Uitleg: {customer_note}")

        top_security = security_overview.get("top_items", [])
        if isinstance(top_security, list) and top_security:
            lines.append("Top security prioriteiten:")
            for item in top_security:
                if not isinstance(item, dict):
                    continue
                lines.append(
                    f"- [{str(item.get('severity', '')).upper()}] {str(item.get('title', ''))}"
                    f" | Pagina: {str(item.get('page', ''))}"
                )
    else:
        lines.append("Status: Onbekend")

    lines.append("")

    lines.append("--- Industry scan snapshot ---")
    if isinstance(industry_snapshot, dict):
        lines.append(f"Overall grade: {industry_snapshot.get('overall_grade', '-')}")
        lines.append(f"Security grade: {industry_snapshot.get('security_grade', '-')}")
        lines.append(
            f"Risk score: {industry_snapshot.get('risk_score', 0)}/100 ({industry_snapshot.get('risk_level', 'Onbekend')})"
        )
        lines.append(f"Patch prioriteit: {industry_snapshot.get('sla_priority', 'Onbekend')}")
        lines.append(f"Positie t.o.v. benchmark: {industry_snapshot.get('market_position', 'Onbekend')}")
    else:
        lines.append("Industry snapshot: niet beschikbaar")

    if isinstance(benchmark, dict):
        totals = benchmark.get("totals", {})
        lines.append(
            "Benchmark checks: "
            f"Pass={int(totals.get('pass', 0))}, "
            f"Warn={int(totals.get('warn', 0))}, "
            f"Fail={int(totals.get('fail', 0))}, "
            f"Score={int(benchmark.get('score', 0))}/100"
        )

        check_items = benchmark.get("checks", [])
        if isinstance(check_items, list) and check_items:
            lines.append("Belangrijkste benchmark checks:")
            for item in check_items[:6]:
                if not isinstance(item, dict):
                    continue
                lines.append(
                    f"- [{str(item.get('status', 'WARN')).upper()}] {str(item.get('name', ''))}: {str(item.get('detail', ''))}"
                )

    if isinstance(technology_fingerprint, list) and technology_fingerprint:
        lines.append("Tech stack indicatie: " + ", ".join(str(item) for item in technology_fingerprint[:8]))

    if isinstance(owasp_top, list) and owasp_top:
        lines.append("OWASP indicatie:")
        for item in owasp_top:
            if not isinstance(item, dict):
                continue
            lines.append(f"- {str(item.get('category', ''))}: {int(item.get('count', 0))} finding(s)")

    lines.append("")

    lines.append("--- Lokale intelligence checks (zonder API keys) ---")
    if isinstance(external_api_insights, dict):
        mode_label = str(external_api_insights.get("mode", "local_only"))
        lines.append(
            "Status: "
            f"Mode={mode_label}, "
            f"Modules={int(external_api_insights.get('configured', 0))}/"
            f"{int(external_api_insights.get('providers_total', 0))}, "
            f"Alerts={int(external_api_insights.get('alerts', 0))}, "
            f"Warnings={int(external_api_insights.get('warnings', 0))}, "
            f"Errors={int(external_api_insights.get('errors', 0))}"
        )

        providers = external_api_insights.get("providers", [])
        if isinstance(providers, list) and providers:
            for provider in providers:
                if not isinstance(provider, dict):
                    continue

                provider_name = str(provider.get("name", "Module"))
                provider_status = str(provider.get("status", "onbekend")).upper()
                provider_message = str(provider.get("message", ""))
                lines.append(f"- {provider_name}: {provider_status} | {provider_message}")

                signals = provider.get("signals", {})
                if not isinstance(signals, dict) or not signals:
                    continue

                signal_parts = [f"{str(key)}={str(value)}" for key, value in list(signals.items())[:6]]
                if signal_parts:
                    lines.append("  " + ", ".join(signal_parts))
    else:
        lines.append("Status: Geen lokale intelligence beschikbaar.")

    lines.append("")

    lines.append("--- Git Deep Audit ---")
    if isinstance(git_audit, dict) and bool(git_audit.get("enabled")):
        lines.append(f"Status: {str(git_audit.get('status', 'onbekend')).upper()}")
        lines.append(f"Uitleg: {str(git_audit.get('message', ''))}")
        lines.append(
            f"Controlepunten: {int(git_audit.get('paths_checked', 0))} | "
            f"Exposed: {int(git_audit.get('exposed_count', 0))}"
        )
        lines.append(f"Remote provider indicatie: {str(git_audit.get('remote_provider', 'Onbekend'))}")

        head_ref = str(git_audit.get("head_ref", "")).strip()
        if head_ref:
            lines.append(f"HEAD ref: {head_ref}")

        remote_urls = git_audit.get("remote_urls", [])
        if isinstance(remote_urls, list) and remote_urls:
            lines.append("Mogelijke remote koppelingen:")
            for remote_url in remote_urls[:3]:
                lines.append(f"- {str(remote_url)}")

        exposed_paths = git_audit.get("exposed_paths", [])
        if isinstance(exposed_paths, list) and exposed_paths:
            lines.append("Exposed git paden:")
            for item in exposed_paths[:5]:
                if not isinstance(item, dict):
                    continue
                lines.append(
                    f"- {str(item.get('path', ''))} | status={int(item.get('status', 0))} | size={int(item.get('size', 0))}"
                )
    else:
        lines.append("Status: Niet uitgevoerd (alleen actief in hardscan).")

    lines.append("")

    lines.append("--- Ratings ---")
    lines.append(f"Intern:      {ratings['Intern']}/5  {stars_for_score(ratings['Intern'])}")
    lines.append(f"Security:    {ratings['Security']}/5  {stars_for_score(ratings['Security'])}")
    lines.append(f"Ontwerp:     {ratings['Ontwerp']}/5  {stars_for_score(ratings['Ontwerp'])}")
    lines.append(f"Performance: {ratings['Performance']}/5  {stars_for_score(ratings['Performance'])}")
    lines.append(f"Overall:     {report['overall_rating']}/5")
    lines.append("")

    lines.append("--- AI Samenvatting ---")
    lines.append(str(ai_summary["summary"]))
    lines.append("Actieplan:")
    for action in ai_summary["action_plan"]:
        lines.append(f"- {action}")

    lines.append("")
    lines.append("Top prioriteiten:")
    for idx, item in enumerate(ai_summary["top_priorities"], start=1):
        lines.append(
            f"{idx}. [{item['severity'].upper()}] {item['title']} | Pagina: {item['page']} | Fix: {item['fix']}"
        )

    lines.append("")
    lines.append("--- Fouten Klad ---")
    for idx, finding in enumerate(findings, start=1):
        lines.append(f"{idx}. [{finding['severity'].upper()}] {finding['category']} - {finding['title']}")
        lines.append(f"   Pagina: {finding['page']}")
        lines.append(f"   Evidence: {finding['evidence']}")
        lines.append(f"   Fix: {finding['fix']}")

    return "\n".join(lines)


def build_client_message(report: Dict[str, object]) -> str:
    ratings = report["ratings"]
    top_findings = report["findings"][:5]
    scan_profile = report.get("scan_profile", {})
    security_overview = report.get("security_overview", {})
    industry_snapshot = report.get("industry_snapshot", {})
    benchmark = report.get("benchmark", {})
    technology_fingerprint = report.get("technology_fingerprint", [])
    git_audit = report.get("git_audit", {})
    external_api_insights = report.get("external_api_insights", {})

    lines: List[str] = []
    lines.append("Beste klant,")
    lines.append("")
    lines.append(
        f"Wij hebben een {report['scan_type']} scan uitgevoerd op {report['target']} en een AI quickcheck opgesteld."
    )

    if isinstance(scan_profile, dict):
        mode_label = str(scan_profile.get("mode", report.get("scan_type", "quick"))).lower()
        if mode_label == "hard":
            lines.append("Scopetype: volledige hardscan met deep audit op website en git metadata.")
        else:
            lines.append("Scopetype: quickscan baseline met compacte controle op hoofd-risico's.")

    lines.append("Resultaat:")
    lines.append(f"- Intern: {ratings['Intern']}/5")
    lines.append(f"- Security: {ratings['Security']}/5")
    lines.append(f"- Ontwerp: {ratings['Ontwerp']}/5")
    lines.append(f"- Performance: {ratings['Performance']}/5")
    lines.append(f"- Algemeen: {report['overall_rating']}/5")
    lines.append("")

    if isinstance(industry_snapshot, dict):
        lines.append("Vergelijkbare scanner metrics:")
        lines.append(f"- Overall grade: {industry_snapshot.get('overall_grade', '-')}")
        lines.append(f"- Security grade: {industry_snapshot.get('security_grade', '-')}")
        lines.append(
            f"- Risk score: {industry_snapshot.get('risk_score', 0)}/100 ({industry_snapshot.get('risk_level', 'Onbekend')})"
        )
        lines.append(f"- Prioriteit: {industry_snapshot.get('sla_priority', 'Onbekend')}")

        if isinstance(benchmark, dict):
            totals = benchmark.get("totals", {})
            lines.append(
                f"- Benchmark checks: Pass={int(totals.get('pass', 0))}, Warn={int(totals.get('warn', 0))}, Fail={int(totals.get('fail', 0))}"
            )

        if isinstance(technology_fingerprint, list) and technology_fingerprint:
            lines.append("- Herkende technologieen: " + ", ".join(str(item) for item in technology_fingerprint[:5]))

        lines.append("")

    if isinstance(external_api_insights, dict):
        lines.append("Lokale checks (zonder externe API):")
        lines.append(
            f"- Modules actief: {int(external_api_insights.get('configured', 0))}/"
            f"{int(external_api_insights.get('providers_total', 0))}"
        )
        lines.append(f"- Alerts: {int(external_api_insights.get('alerts', 0))}")
        lines.append(f"- Warnings: {int(external_api_insights.get('warnings', 0))}")

        providers = external_api_insights.get("providers", [])
        if isinstance(providers, list):
            for provider in providers:
                if not isinstance(provider, dict):
                    continue
                lines.append(
                    f"- {str(provider.get('name', 'Module'))}: {str(provider.get('status', 'onbekend')).upper()}"
                )
        lines.append("")

    if isinstance(git_audit, dict) and bool(git_audit.get("enabled")):
        lines.append("Git deep audit (hardscan):")
        lines.append(f"- Status: {str(git_audit.get('status', 'onbekend')).upper()}")
        lines.append(f"- Exposed git paden: {int(git_audit.get('exposed_count', 0))}")
        lines.append(f"- Remote provider indicatie: {str(git_audit.get('remote_provider', 'Onbekend'))}")
        lines.append("")

    if isinstance(security_overview, dict):
        lines.append("Security check voor uw bedrijf:")
        lines.append(f"- Status: {security_overview.get('status', 'Onbekend')}")
        lines.append(f"- Security findings: {security_overview.get('total_security_findings', 0)}")
        note = str(security_overview.get("customer_note", "")).strip()
        if note:
            lines.append(f"- Toelichting: {note}")
        lines.append("")

    lines.append("Belangrijkste punten:")

    if top_findings:
        for finding in top_findings:
            lines.append(
                f"- [{finding['severity'].upper()}] {finding['title']} ({finding['category']})"
            )
    else:
        lines.append("- Geen kritieke issues gevonden.")

    lines.append("")
    lines.append(
        "Wij kunnen direct helpen met een complete ICT nazorg: herstel, beveiliging, monitoring en periodieke checks."
    )
    lines.append("Als u wilt, plannen we direct een technisch opvolgadvies in.")

    return "\n".join(lines)


def safe_filename(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]", "_", text)


def center_window(window: Toplevel, width: int, height: int) -> None:
    window.update_idletasks()
    screen_w = window.winfo_screenwidth()
    screen_h = window.winfo_screenheight()
    x = max((screen_w - width) // 2, 0)
    y = max((screen_h - height) // 2, 0)
    window.geometry(f"{width}x{height}+{x}+{y}")


class QuickCheckerUI:
    BLACK = "#050505"
    RED = "#d1001f"
    WHITE = "#f2f2f2"
    PANEL_DARK = "#0f0f0f"

    def __init__(self, root: Tk) -> None:
        self.root = root
        self.root.title(APP_TITLE)
        self.root.configure(bg=self.BLACK)

        try:
            self.root.state("zoomed")
        except Exception:
            self.root.geometry("1200x760")

        self.root.minsize(900, 620)
        self.root.bind("<Escape>", lambda _event: self.root.destroy())

        self.url_var = StringVar(value="")
        self.mode_var = StringVar(value="quick")

        self.scan_dialog: Toplevel = None
        self.progress_dialog: Toplevel = None
        self.result_dialog: Toplevel = None

        self.quick_mode_button: Button = None
        self.hard_mode_button: Button = None
        self.progress_label: Label = None
        self.progress_percent_label: Label = None
        self.progress_eta_label: Label = None
        self.progress_canvas: Canvas = None
        self.progress_fill = None

        self.worker_queue: "queue.Queue[Tuple[str, object]]" = queue.Queue()
        self.progress_step = 0
        self.scan_started_at = 0.0
        self.scan_expected_seconds = 0.0
        self.scan_mode_active = "quick"
        self.worker_completed = False
        self.worker_state = ""
        self.worker_payload = None

        self.build_home_screen()

    def build_home_screen(self) -> None:
        for child in self.root.winfo_children():
            child.destroy()

        container = Frame(self.root, bg=self.BLACK)
        container.pack(fill=BOTH, expand=True)

        center = Frame(container, bg=self.BLACK)
        center.place(relx=0.5, rely=0.5, anchor="center")

        border = Frame(center, bg=self.RED, padx=6, pady=6)
        border.pack()

        quick_button = Button(
            border,
            text="QUICK SCAN",
            command=self.open_scan_dialog,
            font=("Bahnschrift SemiBold", 46),
            bg=self.BLACK,
            fg=self.RED,
            activebackground=self.BLACK,
            activeforeground=self.WHITE,
            relief="flat",
            bd=0,
            padx=120,
            pady=70,
            cursor="hand2",
        )
        quick_button.pack()

        subtitle = Label(
            container,
            text="Klik om website AI quickcheck of hard scan te starten",
            bg=self.BLACK,
            fg="#b8b8b8",
            font=("Consolas", 13),
        )
        subtitle.place(relx=0.5, rely=0.72, anchor="center")

        disclaimer = Label(
            container,
            text="Disclaimer: Wij zijn niet verantwoordelijk voor leaks en andere omstandigheden.",
            bg=self.BLACK,
            fg="#8f8f8f",
            font=("Consolas", 10),
        )
        disclaimer.place(relx=0.5, rely=0.76, anchor="center")

    def open_scan_dialog(self) -> None:
        if self.scan_dialog and self.scan_dialog.winfo_exists():
            self.scan_dialog.focus_force()
            return

        self.scan_dialog = Toplevel(self.root)
        self.scan_dialog.title("Scan Keuze")
        self.scan_dialog.configure(bg=self.BLACK)
        self.scan_dialog.resizable(False, False)
        self.scan_dialog.transient(self.root)
        center_window(self.scan_dialog, 900, 500)

        outer_border = Frame(self.scan_dialog, bg=self.RED, padx=4, pady=4)
        outer_border.pack(fill=BOTH, expand=True, padx=22, pady=22)

        panel = Frame(outer_border, bg=self.BLACK)
        panel.pack(fill=BOTH, expand=True)

        grid = Frame(panel, bg=self.RED)
        grid.pack(fill=BOTH, expand=True, padx=22, pady=22)

        for row in range(2):
            grid.grid_rowconfigure(row, weight=1)
        for col in range(2):
            grid.grid_columnconfigure(col, weight=1)

        quick_tile = Frame(grid, bg=self.BLACK)
        quick_tile.grid(row=0, column=0, sticky="nsew", padx=(0, 2), pady=(0, 2))

        self.quick_mode_button = Button(
            quick_tile,
            text="QUICKSCAN",
            command=lambda: self.set_scan_mode("quick"),
            font=("Bahnschrift SemiBold", 28),
            bg=self.BLACK,
            fg=self.RED,
            activebackground="#2b0000",
            activeforeground=self.WHITE,
            relief="flat",
            bd=0,
            cursor="hand2",
        )
        self.quick_mode_button.pack(fill=BOTH, expand=True)

        hard_tile = Frame(grid, bg=self.BLACK)
        hard_tile.grid(row=1, column=0, sticky="nsew", padx=(0, 2), pady=(2, 0))

        self.hard_mode_button = Button(
            hard_tile,
            text="HARDSCAN",
            command=lambda: self.set_scan_mode("hard"),
            font=("Bahnschrift SemiBold", 28),
            bg=self.BLACK,
            fg=self.RED,
            activebackground="#2b0000",
            activeforeground=self.WHITE,
            relief="flat",
            bd=0,
            cursor="hand2",
        )
        self.hard_mode_button.pack(fill=BOTH, expand=True)

        input_tile = Frame(grid, bg=self.PANEL_DARK)
        input_tile.grid(row=0, column=1, sticky="nsew", padx=(2, 0), pady=(0, 2))

        input_label = Label(
            input_tile,
            text="INPUT URL",
            bg=self.PANEL_DARK,
            fg=self.WHITE,
            font=("Consolas", 20),
        )
        input_label.pack(pady=(30, 12))

        input_hint = Label(
            input_tile,
            text="bijv: bedrijf.nl of https://bedrijf.nl",
            bg=self.PANEL_DARK,
            fg="#a8a8a8",
            font=("Consolas", 11),
        )
        input_hint.pack(pady=(0, 10))

        entry_border = Frame(input_tile, bg="#a0a0a0", padx=3, pady=3)
        entry_border.pack(fill="x", padx=26, pady=(0, 20))

        entry = Entry(
            entry_border,
            textvariable=self.url_var,
            font=("Consolas", 15),
            bg=self.BLACK,
            fg=self.WHITE,
            insertbackground=self.WHITE,
            relief="flat",
            bd=0,
            justify="center",
        )
        entry.pack(fill="x", ipady=8)
        entry.focus_set()

        action_tile = Frame(grid, bg=self.PANEL_DARK)
        action_tile.grid(row=1, column=1, sticky="nsew", padx=(2, 0), pady=(2, 0))

        start_button_border = Frame(action_tile, bg="#8a8a8a", padx=4, pady=4)
        start_button_border.place(relx=0.5, rely=0.5, anchor="center")

        start_button = Button(
            start_button_border,
            text="START ANALYSE",
            command=self.start_scan_from_dialog,
            font=("Bahnschrift SemiBold", 19),
            bg=self.BLACK,
            fg=self.WHITE,
            activebackground="#242424",
            activeforeground=self.WHITE,
            relief="flat",
            bd=0,
            padx=30,
            pady=14,
            cursor="hand2",
        )
        start_button.pack()

        self.set_scan_mode(self.mode_var.get())

    def set_scan_mode(self, mode: str) -> None:
        chosen = "hard" if mode == "hard" else "quick"
        self.mode_var.set(chosen)

        if not self.quick_mode_button or not self.hard_mode_button:
            return

        if chosen == "quick":
            self.quick_mode_button.config(bg="#2a0000", fg=self.WHITE, text="QUICKSCAN [ACTIVE]")
            self.hard_mode_button.config(bg=self.BLACK, fg=self.RED, text="HARDSCAN")
        else:
            self.quick_mode_button.config(bg=self.BLACK, fg=self.RED, text="QUICKSCAN")
            self.hard_mode_button.config(bg="#2a0000", fg=self.WHITE, text="HARDSCAN [ACTIVE]")

    def start_scan_from_dialog(self) -> None:
        raw_url = self.url_var.get().strip()
        normalized = normalize_url(raw_url)

        if not normalized:
            messagebox.showerror("URL fout", "Vul een geldige URL in, bijvoorbeeld bedrijf.nl")
            return

        mode = self.mode_var.get()

        if self.scan_dialog and self.scan_dialog.winfo_exists():
            self.scan_dialog.destroy()

        self.start_scan(normalized, mode)

    def start_scan(self, url: str, mode: str) -> None:
        self.clear_worker_queue()
        self.scan_mode_active = "hard" if mode == "hard" else "quick"
        self.scan_started_at = time.time()
        self.scan_expected_seconds = self.pick_target_duration(self.scan_mode_active)
        self.worker_completed = False
        self.worker_state = ""
        self.worker_payload = None
        self.progress_step = 0

        self.show_progress_dialog(mode)

        worker = threading.Thread(target=self.worker_scan, args=(url, mode), daemon=True)
        worker.start()

        self.animate_progress()
        self.poll_worker_queue()

    def clear_worker_queue(self) -> None:
        while True:
            try:
                self.worker_queue.get_nowait()
            except queue.Empty:
                break

    def pick_target_duration(self, mode: str) -> float:
        if mode == "hard":
            return float(random.randint(HARD_TARGET_SECONDS[0], HARD_TARGET_SECONDS[1]))
        return float(random.randint(QUICK_TARGET_SECONDS[0], QUICK_TARGET_SECONDS[1]))

    def format_seconds_human(self, total_seconds: float) -> str:
        rounded = max(0, int(round(total_seconds)))
        minutes = rounded // 60
        seconds = rounded % 60
        if minutes > 0:
            return f"{minutes}m {seconds:02d}s"
        return f"{seconds}s"

    def update_progress_bar(self, progress_ratio: float) -> None:
        if not self.progress_canvas or self.progress_fill is None:
            return

        normalized = max(0.0, min(1.0, float(progress_ratio)))
        self.progress_canvas.update_idletasks()
        width = max(self.progress_canvas.winfo_width(), 1)
        self.progress_canvas.coords(self.progress_fill, 0, 0, int(width * normalized), 18)

    def show_progress_dialog(self, mode: str) -> None:
        self.progress_dialog = Toplevel(self.root)
        self.progress_dialog.title("Scan bezig")
        self.progress_dialog.configure(bg=self.BLACK)
        self.progress_dialog.resizable(False, False)
        self.progress_dialog.transient(self.root)
        center_window(self.progress_dialog, 560, 290)

        border = Frame(self.progress_dialog, bg=self.RED, padx=4, pady=4)
        border.pack(fill=BOTH, expand=True, padx=18, pady=18)

        panel = Frame(border, bg=self.BLACK)
        panel.pack(fill=BOTH, expand=True)

        label_title = Label(
            panel,
            text=f"{'HARD' if mode == 'hard' else 'QUICK'} SCAN",
            bg=self.BLACK,
            fg=self.RED,
            font=("Bahnschrift SemiBold", 32),
        )
        label_title.pack(pady=(20, 8))

        duration_hint = Label(
            panel,
            text=f"Verwachte duur: {self.format_seconds_human(self.scan_expected_seconds)}",
            bg=self.BLACK,
            fg="#a8a8a8",
            font=("Consolas", 11),
        )
        duration_hint.pack(pady=(0, 8))

        self.progress_label = Label(
            panel,
            text="AI analyse bezig",
            bg=self.BLACK,
            fg=self.WHITE,
            font=("Consolas", 14),
        )
        self.progress_label.pack()

        bar_shell = Frame(panel, bg="#3a3a3a", padx=2, pady=2)
        bar_shell.pack(fill="x", padx=28, pady=(14, 8))

        self.progress_canvas = Canvas(
            bar_shell,
            height=18,
            bg="#101010",
            highlightthickness=0,
            bd=0,
            relief="flat",
        )
        self.progress_canvas.pack(fill="x")
        self.progress_fill = self.progress_canvas.create_rectangle(0, 0, 0, 18, fill=self.RED, width=0)

        self.progress_percent_label = Label(
            panel,
            text="0% voltooid",
            bg=self.BLACK,
            fg=self.WHITE,
            font=("Consolas", 11),
        )
        self.progress_percent_label.pack()

        self.progress_eta_label = Label(
            panel,
            text=f"Nog ongeveer {self.format_seconds_human(self.scan_expected_seconds)}",
            bg=self.BLACK,
            fg="#bdbdbd",
            font=("Consolas", 11),
        )
        self.progress_eta_label.pack(pady=(4, 0))

    def animate_progress(self) -> None:
        if not self.progress_dialog or not self.progress_dialog.winfo_exists():
            return

        elapsed = max(0.0, time.time() - self.scan_started_at)
        target = max(self.scan_expected_seconds, 1.0)

        if self.worker_completed:
            progress_ratio = min(1.0, elapsed / target)
            progress_text = "Resultaten afronden"
            remaining_text = f"Nog ongeveer {self.format_seconds_human(max(0.0, target - elapsed))}"
        else:
            if elapsed <= target:
                stage_ratio = elapsed / target
                progress_ratio = min(0.96, 0.03 + (stage_ratio * 0.90))
                progress_text = f"AI analyse bezig ({int(stage_ratio * 100)}%)"
                remaining_text = f"Nog ongeveer {self.format_seconds_human(target - elapsed)}"
            else:
                progress_ratio = 0.95 + ((self.progress_step % 4) * 0.01)
                progress_text = "Analyse duurt iets langer dan verwacht"
                remaining_text = "Nog ongeveer 5-15s (schatting)"

        self.progress_step += 1
        self.update_progress_bar(progress_ratio)

        if self.progress_label:
            self.progress_label.config(text=progress_text)

        if self.progress_percent_label:
            self.progress_percent_label.config(text=f"{int(min(100, round(progress_ratio * 100)))}% voltooid")

        if self.progress_eta_label:
            self.progress_eta_label.config(text=remaining_text)

        self.root.after(250, self.animate_progress)

    def worker_scan(self, url: str, mode: str) -> None:
        try:
            report = run_scan(url, mode)
            self.worker_queue.put(("ok", report))
        except Exception as exc:
            self.worker_queue.put(("error", str(exc)))

    def poll_worker_queue(self) -> None:
        if not self.worker_completed:
            try:
                state, payload = self.worker_queue.get_nowait()
                self.worker_completed = True
                self.worker_state = state
                self.worker_payload = payload
            except queue.Empty:
                pass

        elapsed = max(0.0, time.time() - self.scan_started_at)
        if not self.worker_completed:
            self.root.after(120, self.poll_worker_queue)
            return

        if elapsed < self.scan_expected_seconds:
            self.root.after(120, self.poll_worker_queue)
            return

        self.close_progress_dialog()

        if self.worker_state == "error":
            messagebox.showerror("Scan fout", str(self.worker_payload))
            return

        self.show_results(self.worker_payload)

    def close_progress_dialog(self) -> None:
        if self.progress_dialog and self.progress_dialog.winfo_exists():
            self.progress_dialog.destroy()
        self.progress_dialog = None
        self.progress_canvas = None
        self.progress_fill = None
        self.progress_label = None
        self.progress_percent_label = None
        self.progress_eta_label = None

    def show_results(self, report: Dict[str, object]) -> None:
        if self.result_dialog and self.result_dialog.winfo_exists():
            self.result_dialog.destroy()

        self.result_dialog = Toplevel(self.root)
        self.result_dialog.title("Quick Checker Resultaat")
        self.result_dialog.configure(bg=self.BLACK)
        self.result_dialog.transient(self.root)
        center_window(self.result_dialog, 1320, 790)

        outer = Frame(self.result_dialog, bg=self.RED, padx=4, pady=4)
        outer.pack(fill=BOTH, expand=True, padx=16, pady=16)

        shell = Frame(outer, bg=self.BLACK)
        shell.pack(fill=BOTH, expand=True)

        header = Frame(shell, bg=self.BLACK)
        header.pack(fill="x", padx=18, pady=(14, 8))

        title = Label(
            header,
            text="QUICK CHECKER AI REPORT",
            bg=self.BLACK,
            fg=self.RED,
            font=("Bahnschrift SemiBold", 28),
        )
        title.pack(anchor="w")

        industry_snapshot = report.get("industry_snapshot", {})
        overall_grade = "-"
        risk_score = 0
        risk_level = "Onbekend"
        if isinstance(industry_snapshot, dict):
            overall_grade = str(industry_snapshot.get("overall_grade", "-"))
            try:
                risk_score = int(industry_snapshot.get("risk_score", 0))
            except (TypeError, ValueError):
                risk_score = 0
            risk_level = str(industry_snapshot.get("risk_level", "Onbekend"))

        subtitle = Label(
            header,
            text=(
                f"Target: {report['target']} | Type: {report['scan_type']} | Overall: {report['overall_rating']}/5"
                f" | Grade: {overall_grade} | Risk: {risk_score}/100 ({risk_level})"
            ),
            bg=self.BLACK,
            fg="#c9c9c9",
            font=("Consolas", 11),
        )
        subtitle.pack(anchor="w")

        body = Frame(shell, bg=self.BLACK)
        body.pack(fill=BOTH, expand=True, padx=18, pady=10)

        left_side = Frame(body, bg=self.RED, padx=2, pady=2)
        left_side.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))

        text_shell = Frame(left_side, bg=self.BLACK)
        text_shell.pack(fill=BOTH, expand=True)

        text_area = Text(
            text_shell,
            wrap=WORD,
            bg=self.BLACK,
            fg=self.WHITE,
            insertbackground=self.WHITE,
            relief="flat",
            bd=0,
            padx=12,
            pady=12,
            font=("Consolas", 10),
        )
        text_area.pack(fill=BOTH, expand=True)

        text_area.insert("1.0", report_to_text(report))
        text_area.config(state="disabled")

        right_side = Frame(body, bg=self.PANEL_DARK, width=355)
        right_side.pack(side=RIGHT, fill=Y)
        right_side.pack_propagate(False)

        rating_title = Label(
            right_side,
            text="RATING SCREEN",
            bg=self.PANEL_DARK,
            fg=self.WHITE,
            font=("Bahnschrift SemiBold", 20),
        )
        rating_title.pack(pady=(18, 14))

        ratings = report["ratings"]
        self.add_rating_line(right_side, "Intern", float(ratings["Intern"]))
        self.add_rating_line(right_side, "Security", float(ratings["Security"]))
        self.add_rating_line(right_side, "Ontwerp", float(ratings["Ontwerp"]))
        self.add_rating_line(right_side, "Performance", float(ratings["Performance"]))

        overall_border = Frame(right_side, bg=self.RED, padx=3, pady=3)
        overall_border.pack(fill="x", padx=16, pady=(14, 12))

        overall_panel = Frame(overall_border, bg=self.BLACK)
        overall_panel.pack(fill="x")

        Label(
            overall_panel,
            text="OVERALL",
            bg=self.BLACK,
            fg=self.RED,
            font=("Consolas", 14, "bold"),
        ).pack(pady=(8, 0))

        Label(
            overall_panel,
            text=f"{report['overall_rating']}/5",
            bg=self.BLACK,
            fg=self.WHITE,
            font=("Bahnschrift SemiBold", 30),
        ).pack(pady=(0, 8))

        analytics = report["analytics"]
        security_overview = report.get("security_overview", {})
        benchmark = report.get("benchmark", {})
        owasp_top = report.get("owasp_top", [])
        technology_fingerprint = report.get("technology_fingerprint", [])
        external_api_insights = report.get("external_api_insights", {})

        security_status = "Onbekend"
        security_count = 0
        if isinstance(security_overview, dict):
            security_status = str(security_overview.get("status", "Onbekend"))
            try:
                security_count = int(security_overview.get("total_security_findings", 0))
            except (TypeError, ValueError):
                security_count = 0

        benchmark_score = 0
        benchmark_pass = 0
        benchmark_warn = 0
        benchmark_fail = 0
        if isinstance(benchmark, dict):
            try:
                benchmark_score = int(benchmark.get("score", 0))
            except (TypeError, ValueError):
                benchmark_score = 0

            totals = benchmark.get("totals", {})
            if isinstance(totals, dict):
                benchmark_pass = int(totals.get("pass", 0))
                benchmark_warn = int(totals.get("warn", 0))
                benchmark_fail = int(totals.get("fail", 0))

        top_owasp = "-"
        if isinstance(owasp_top, list) and owasp_top:
            first_item = owasp_top[0]
            if isinstance(first_item, dict):
                top_owasp = str(first_item.get("category", "-"))

        tech_short = "Onbekend"
        if isinstance(technology_fingerprint, list) and technology_fingerprint:
            tech_short = ", ".join(str(item) for item in technology_fingerprint[:3])

        local_modules = 0
        local_total = 0
        local_alerts = 0
        local_warnings = 0
        local_short = "geen"
        if isinstance(external_api_insights, dict):
            local_modules = int(external_api_insights.get("configured", 0))
            local_total = int(external_api_insights.get("providers_total", 0))
            local_alerts = int(external_api_insights.get("alerts", 0))
            local_warnings = int(external_api_insights.get("warnings", 0))

            provider_tags: List[str] = []
            providers = external_api_insights.get("providers", [])
            if isinstance(providers, list):
                for provider in providers:
                    if not isinstance(provider, dict):
                        continue
                    status = str(provider.get("status", ""))
                    provider_tags.append(f"{str(provider.get('name', 'Module'))}:{status.upper()}")
                    if len(provider_tags) >= 2:
                        break

            if provider_tags:
                local_short = " | ".join(provider_tags)

        analytics_label = Label(
            right_side,
            text=(
                "DATA ANALYTICS\n"
                f"Findings: {analytics['total_findings']}\n"
                f"Security status: {security_status}\n"
                f"Security findings: {security_count}\n"
                f"Grade: {overall_grade}\n"
                f"Risk: {risk_score}/100 ({risk_level})\n"
                f"Benchmark: {benchmark_score}/100\n"
                f"Pass/Warn/Fail: {benchmark_pass}/{benchmark_warn}/{benchmark_fail}\n"
                f"Top OWASP: {top_owasp}\n"
                f"Tech: {tech_short}\n"
                f"LOCAL: {local_modules}/{local_total} | Alerts={local_alerts} | Warnings={local_warnings}\n"
                f"Local details: {local_short}\n"
                "\n"
                f"Critical: {analytics['by_severity']['critical']}\n"
                f"High: {analytics['by_severity']['high']}\n"
                f"Medium: {analytics['by_severity']['medium']}\n"
                f"Low: {analytics['by_severity']['low']}\n"
                "\n"
                "Per categorie\n"
                f"Intern: {analytics['by_category']['Intern']}\n"
                f"Security: {analytics['by_category']['Security']}\n"
                f"Ontwerp: {analytics['by_category']['Ontwerp']}\n"
                f"Performance: {analytics['by_category']['Performance']}"
            ),
            justify="left",
            bg=self.PANEL_DARK,
            fg="#c7c7c7",
            font=("Consolas", 11),
        )
        analytics_label.pack(anchor="w", padx=18)

        action_bar = Frame(shell, bg=self.BLACK)
        action_bar.pack(fill="x", padx=18, pady=(0, 14))

        self.make_action_button(
            action_bar,
            "Bewaar JSON rapport",
            lambda: self.save_report_json(report),
        ).pack(side=LEFT, padx=(0, 10))

        self.make_action_button(
            action_bar,
            "Bewaar kladblok rapport",
            lambda: self.save_report_text(report),
        ).pack(side=LEFT, padx=(0, 10))

        self.make_action_button(
            action_bar,
            "Kopieer klant bericht",
            lambda: self.copy_client_message(report),
        ).pack(side=LEFT, padx=(0, 10))

        self.make_action_button(
            action_bar,
            "Nieuwe scan",
            self.new_scan,
        ).pack(side=LEFT)

    def add_rating_line(self, parent: Frame, label: str, score: float) -> None:
        line = Frame(parent, bg=self.PANEL_DARK)
        line.pack(fill="x", padx=16, pady=4)

        left_label = Label(
            line,
            text=f"{label:<11}",
            bg=self.PANEL_DARK,
            fg="#d6d6d6",
            font=("Consolas", 12),
            width=11,
            anchor="w",
        )
        left_label.pack(side=LEFT)

        stars = Label(
            line,
            text=stars_for_score(score),
            bg=self.PANEL_DARK,
            fg=self.RED,
            font=("Consolas", 14, "bold"),
            width=6,
            anchor="w",
        )
        stars.pack(side=LEFT)

        score_label = Label(
            line,
            text=f"{score}/5",
            bg=self.PANEL_DARK,
            fg=self.WHITE,
            font=("Consolas", 12),
            anchor="e",
        )
        score_label.pack(side=RIGHT)

    def make_action_button(self, parent: Frame, text: str, command) -> Button:
        return Button(
            parent,
            text=text,
            command=command,
            font=("Consolas", 10, "bold"),
            bg=self.BLACK,
            fg=self.WHITE,
            activebackground="#1a1a1a",
            activeforeground=self.WHITE,
            relief="solid",
            bd=1,
            highlightthickness=1,
            highlightbackground=self.RED,
            highlightcolor=self.RED,
            cursor="hand2",
            padx=10,
            pady=6,
        )

    def save_report_json(self, report: Dict[str, object]) -> None:
        host = urlparse(str(report["target"])).netloc or "website"
        default_name = safe_filename(f"{host}_{report['scan_type']}_report.json")

        path = filedialog.asksaveasfilename(
            title="Bewaar JSON rapport",
            defaultextension=".json",
            initialfile=default_name,
            filetypes=[("JSON", "*.json"), ("Alle bestanden", "*.*")],
        )

        if not path:
            return

        with open(path, "w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2, ensure_ascii=False)

        messagebox.showinfo("Opgeslagen", f"JSON rapport opgeslagen in:\n{path}")

    def save_report_text(self, report: Dict[str, object]) -> None:
        host = urlparse(str(report["target"])).netloc or "website"
        default_name = safe_filename(f"{host}_{report['scan_type']}_kladblok.txt")

        path = filedialog.asksaveasfilename(
            title="Bewaar kladblok rapport",
            defaultextension=".txt",
            initialfile=default_name,
            filetypes=[("Tekst", "*.txt"), ("Alle bestanden", "*.*")],
        )

        if not path:
            return

        with open(path, "w", encoding="utf-8") as handle:
            handle.write(report_to_text(report))

        messagebox.showinfo("Opgeslagen", f"Kladblok rapport opgeslagen in:\n{path}")

    def copy_client_message(self, report: Dict[str, object]) -> None:
        message = build_client_message(report)
        self.root.clipboard_clear()
        self.root.clipboard_append(message)
        self.root.update()
        messagebox.showinfo("Gekopieerd", "Klant bericht staat nu op je klembord.")

    def new_scan(self) -> None:
        if self.result_dialog and self.result_dialog.winfo_exists():
            self.result_dialog.destroy()
        self.open_scan_dialog()


def main() -> None:
    root = Tk()
    _app = QuickCheckerUI(root)
    icon_path = os.path.join(os.path.dirname(__file__), "quick-check.ico")
    if os.path.exists(icon_path):
        try:
            root.iconbitmap(icon_path)
        except Exception:
            pass
    root.mainloop()


if __name__ == "__main__":
    main()
