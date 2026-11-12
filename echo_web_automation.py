"""Opt-in stock watches, guarded shop actions and self-healing element selectors."""

import difflib
import json
import logging
import os
import queue
import random
import re
import secrets
import sqlite3
import threading
import time
from decimal import Decimal
from contextlib import closing, contextmanager
from pathlib import Path
from urllib.parse import urlparse

try:
    from playwright.sync_api import Error as PlaywrightError
    from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover - Playwright is listed in requirements.txt
    sync_playwright = None
    PlaywrightError = PlaywrightTimeoutError = RuntimeError


LOGGER = logging.getLogger(__name__)
DATA_DIR = Path(os.environ.get("LOCALAPPDATA", str(Path.home() / ".local" / "share"))) / "Echo" / "web-automation"
MODES = ("notify", "cart", "checkout", "order", "reserve")
TRANSACTION_MODES = frozenset({"order", "reserve"})
ROLES = ("add_to_cart", "checkout", "stock_indicator", "price")
ACTION_ROLES = frozenset({"add_to_cart", "checkout"})
WATCH_KEYS = frozenset({
    "name", "url", "mode", "interval", "in_stock_text", "out_of_stock_text",
    "max_price", "elements", "checkout_url", "authorized",
})
MIN_INTERVAL, MAX_INTERVAL, MAX_WATCHES, MAX_BACKOFF, MAX_FAILURES = 60, 86400, 25, 3600, 5
KEEP_THRESHOLD, HEAL_THRESHOLD, HEAL_MARGIN = 0.35, 0.55, 0.08
DEFAULT_OUT = ("uitverkocht", "niet op voorraad", "niet leverbaar", "tijdelijk niet beschikbaar", "out of stock", "sold out", "currently unavailable")
DEFAULT_IN = ("op voorraad", "in stock", "direct leverbaar", "morgen in huis", "available now")
DEFAULT_STATE = {
    "availability": "", "monitor_availability": "", "price": None, "last_check": 0, "next_check": 0,
    "paused": False, "status": "", "failures": 0, "backoff": 0, "notes": [], "last_error": "", "signals": {}, "elements": {},
}
ROLE_KEYWORDS = {
    "add_to_cart": ("winkelwagen", "winkelmand", "mandje", "add to cart", "add to basket", "add to bag", "toevoegen", "in cart"),
    "checkout": ("afrekenen", "checkout", "check out", "kassa", "naar bestellen", "view cart", "winkelwagen bekijken", "naar winkelwagen", "go to cart", "bekijk winkelwagen"),
    "stock_indicator": ("voorraad", "stock", "leverbaar", "beschikbaar", "available", "uitverkocht", "sold out"),
    "price": ("€", "$", "£", "prijs", "price"),
}
NEGATIVE_KEYWORDS = {
    "add_to_cart": ("wishlist", "verlanglijst", "favoriet", "favorite", "vergelijk", "compare", "notify", "houd me op de hoogte", "mail me", "e-mail mij", "alert", "remove", "verwijder"),
    "checkout": ("verder winkelen", "continue shopping", "remove", "verwijder", "leeg"),
}
FINAL_PURCHASE = re.compile(
    r"(?<![\w-])(place (?:your )?order|plaats(?:en)? (?:de )?bestelling|bestelling (?:plaatsen|afronden|bevestigen)|"
    r"bevestig (?:de )?bestelling|complete (?:order|purchase)|confirm (?:order|purchase)|submit order|order now|"
    r"nu bestellen|bestellen en betalen|pay(?:ment)?(?: now)?|betaal|betalen|1[- ]?click|one[- ]click|"
    r"met (?:1|één|een) klik|buy (?:it )?now|koop nu|nu kopen|direct kopen|kopen|purchase|paypal|apple pay|"
    r"google pay|gpay|klarna|ideal|afterpay|shop pay)(?![\w-])",
    re.IGNORECASE,
)
CHALLENGE = re.compile(
    r"verify you are (?:a )?human|are you a robot|ben je een robot|bent u een robot|checking your browser|"
    r"just a moment\.\.\.|attention required|unusual traffic|ongebruikelijk verkeer",
    re.IGNORECASE,
)
FINAL_RESERVATION = re.compile(r"\breserve(?:er|ren)?\b|\breservering\b|\breservation\b|\bbook now\b", re.IGNORECASE)
TRANSACTION_FIELDS = ("button", "confirmation", "item", "quantity", "total")
TRANSACTION_CURRENCIES = {"EUR": ("EUR", "€"), "GBP": ("GBP", "£"), "USD": ("USD", "US$")}
NEGATION = re.compile(r"(?:niet|not|no|geen|nicht)\s+(?:meer\s+)?$")
WEIGHTS = {
    "text": .30, "aria": .10, "title": .04, "id": .12, "testid": .12, "name": .08,
    "classes": .08, "tag": .04, "type": .03, "role": .03, "near": .06, "href": .04,
}
FINGERPRINT_KEYS = tuple(WEIGHTS) + ("value", "chrome")
AVAILABILITY_IN = {"instock", "limitedavailability", "onlineonly", "preorder", "presale"}
AVAILABILITY_OUT = {"outofstock", "soldout", "discontinued", "instoreonly"}

DESCRIBE_JS = r"""({selector, mode, limit, paths}) => {
  const clean = (value, size = 160) => String(value || '').replace(/\s+/g, ' ').trim().slice(0, size);
  const stableClass = name => /^[A-Za-z][\w-]{1,40}$/.test(name) && !/\d{3,}|^(css|sc|jsx|emotion|styled|svelte)-|__[A-Za-z0-9]{5,}$/.test(name);
  const stableId = id => /^[A-Za-z][\w-]{0,60}$/.test(id) && !/\d{3,}/.test(id);
  const quote = value => '"' + String(value).replace(/["\\]/g, '\\$&') + '"';
  const unique = (css, element) => {
    try { const found = document.querySelectorAll(css); return found.length === 1 && found[0] === element; } catch (error) { return false; }
  };
  const path = element => {
    const tag = element.tagName.toLowerCase();
    if (element.id && stableId(element.id) && unique('#' + CSS.escape(element.id), element)) return '#' + CSS.escape(element.id);
    for (const attribute of ['data-testid', 'data-test', 'data-qa', 'name', 'aria-label']) {
      const value = element.getAttribute(attribute);
      if (value) { const css = `${tag}[${attribute}=${quote(value)}]`; if (unique(css, element)) return css; }
    }
    const classes = [...element.classList].filter(stableClass).slice(0, 3);
    if (classes.length) { const css = tag + classes.map(name => '.' + CSS.escape(name)).join(''); if (unique(css, element)) return css; }
    const parts = [];
    for (let node = element; node && node.nodeType === 1 && node !== document.documentElement; node = node.parentElement) {
      if (node !== element && node.id && stableId(node.id) && unique('#' + CSS.escape(node.id), node)) { parts.unshift('#' + CSS.escape(node.id)); break; }
      let index = 1;
      for (let sibling = node.previousElementSibling; sibling; sibling = sibling.previousElementSibling) {
        if (sibling.tagName === node.tagName) index += 1;
      }
      parts.unshift(`${node.tagName.toLowerCase()}:nth-of-type(${index})`);
    }
    const css = parts.join(' > ');
    return unique(css, element) ? css : '';
  };
  const describe = (element, index) => {
    const rect = element.getBoundingClientRect();
    const style = getComputedStyle(element);
    const isInput = element.tagName === 'INPUT';
    const text = clean(isInput ? element.value : element.innerText);
    const parentText = element.parentElement ? clean(element.parentElement.innerText, 400) : '';
    const near = element.labels && element.labels.length ? clean(element.labels[0].innerText, 120) : clean(parentText.replace(text, ''), 120);
    return {
      tag: element.tagName.toLowerCase(), id: element.id || '', classes: [...element.classList].filter(stableClass).slice(0, 8),
      name: element.getAttribute('name') || '', type: (element.getAttribute('type') || '').toLowerCase(),
      role: element.getAttribute('role') || '', aria: clean(element.getAttribute('aria-label'), 120),
      title: clean(element.getAttribute('title'), 120), value: isInput ? clean(element.value, 120) : '',
      testid: element.getAttribute('data-testid') || element.getAttribute('data-test') || element.getAttribute('data-qa') || '',
      href: element.tagName === 'A' ? (element.getAttribute('href') || '').slice(0, 200) : '', text, near,
      visible: rect.width > 0 && rect.height > 0 && style.visibility !== 'hidden' && style.display !== 'none' && Number(style.opacity) > 0,
      enabled: !(element.disabled || element.getAttribute('aria-disabled') === 'true'),
      chrome: !!element.closest('header, nav, footer, [role=navigation], [role=banner]'),
      index, path: paths ? path(element) : '',
    };
  };
  let elements;
  if (mode === 'selector') {
    try { elements = [...document.querySelectorAll(selector)]; } catch (error) { return { error: 'invalid_selector', items: [] }; }
  } else if (mode === 'action') {
    elements = [...document.querySelectorAll('button, a[href], input[type=submit], input[type=button], [role=button], [onclick]')];
  } else {
    const skip = new Set(['SCRIPT', 'STYLE', 'NOSCRIPT', 'TEMPLATE', 'SVG', 'HEAD']);
    elements = document.body ? [...document.body.querySelectorAll('*')].filter(element => !skip.has(element.tagName)
      && [...element.childNodes].some(node => node.nodeType === 3 && node.textContent.trim())) : [];
  }
  window.__echoCandidates = elements.slice(0, limit);
  window.__echoPath = path;
  return { items: window.__echoCandidates.map(describe) };
}"""

PATH_JS = r"""index => {
  const element = (window.__echoCandidates || [])[index];
  return element && element.isConnected && window.__echoPath ? window.__echoPath(element) : '';
}"""

SIGNALS_JS = r"""() => ({
  title: document.title || '',
  text: document.body ? document.body.innerText.slice(0, 200000) : '',
  jsonld: [...document.querySelectorAll('script[type="application/ld+json"]')].slice(0, 20).map(node => node.textContent.slice(0, 200000)),
  captcha: !!document.querySelector('iframe[src*="captcha" i], iframe[src*="challenges.cloudflare.com"], #challenge-form, .g-recaptcha, .h-captcha, .cf-turnstile'),
  payment: !!document.querySelector('input[autocomplete^="cc-"], input[name*="cardnumber" i], input[id*="cardnumber" i], input[name*="card_number" i], input[name*="cvc" i], input[name*="cvv" i], iframe[src*="js.stripe.com"], iframe[name*="adyen" i], iframe[title*="card" i]'),
})"""

OBSERVE_JS = r"""() => {
  window.__echoMutations = 0;
  if (window.__echoObserver) window.__echoObserver.disconnect();
  window.__echoObserver = new MutationObserver(records => { window.__echoMutations += records.length; });
  window.__echoObserver.observe(document.documentElement, { subtree: true, childList: true, characterData: true });
}"""


class AutomationError(Exception):
    pass


def normalize(value) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip().lower()


def text_similarity(first, second) -> float:
    first, second = normalize(first), normalize(second)
    if not first or not second:
        return 0.0
    if first == second:
        return 1.0
    first_words, second_words = set(re.findall(r"\w+", first)), set(re.findall(r"\w+", second))
    overlap = len(first_words & second_words) / len(first_words | second_words) if first_words and second_words else 0.0
    return max(overlap, difflib.SequenceMatcher(None, first, second).ratio())


def label(item: dict) -> str:
    return normalize(" ".join(str(item.get(key) or "") for key in ("text", "aria", "title", "value")))


def safety_label(item: dict) -> str:
    raw = " ".join(str(item.get(key) or "") for key in ("text", "aria", "title", "value", "id", "name", "testid"))
    split = re.sub(r"[-_]+", " ", re.sub(r"([a-z])([A-Z])", r"\1 \2", raw))
    return normalize(f"{re.sub(r'[-_]+', ' ', raw)} | {split}")


def is_final_purchase(item: dict) -> bool:
    return bool(FINAL_PURCHASE.search(safety_label(item)))


def is_safe(role: str, item: dict) -> bool:
    if role not in ACTION_ROLES:
        return True
    text = safety_label(item)
    return not is_final_purchase(item) and not FINAL_RESERVATION.search(text) and not any(word in text for word in NEGATIVE_KEYWORDS.get(role, ()))


def fingerprint_of(item: dict) -> dict:
    return {key: item[key] for key in FINGERPRINT_KEYS if item.get(key)}


def is_partial(fingerprint: dict) -> bool:
    return set(fingerprint) <= {"text"}


def score_candidate(fingerprints: list[dict], item: dict, role: str) -> float:
    if not fingerprints:
        return 1.0
    best = 0.0
    for fingerprint in fingerprints:
        total = weight = 0.0
        for key, key_weight in WEIGHTS.items():
            expected = fingerprint.get(key)
            if not expected:
                continue
            actual = item.get(key)
            if key == "classes":
                expected_set, actual_set = set(expected), set(actual or ())
                similarity = len(expected_set & actual_set) / len(expected_set | actual_set)
            elif key in ("tag", "type", "role"):
                similarity = float(normalize(expected) == normalize(actual))
            elif key in ("id", "testid", "name"):
                similarity = 1.0 if expected == actual else text_similarity(expected, actual) * 0.5
            else:
                similarity = text_similarity(expected, actual)
            total += key_weight * similarity
            weight += key_weight
        best = max(best, total / weight if weight else 0.0)
    if any(word in label(item) for word in ROLE_KEYWORDS.get(role, ())):
        best = min(1.0, best + 0.12)
    if role == "add_to_cart" and item.get("chrome") and not any(fingerprint.get("chrome") for fingerprint in fingerprints):
        best *= 0.7
    if not item.get("visible"):
        best *= 0.6
    return round(best, 3)


def eligible(role: str, item: dict, fingerprints: list[dict]) -> bool:
    if not is_safe(role, item):
        return False
    text = label(item)
    if role in ACTION_ROLES:
        same_identity = any(
            fingerprint.get(key) and fingerprint.get(key) == item.get(key)
            for fingerprint in fingerprints for key in ("id", "testid", "name")
        )
        return same_identity or any(word in text for word in ROLE_KEYWORDS[role])
    if role == "price":
        return bool(re.search(r"\d", text)) and len(text) <= 60
    return 0 < len(text) <= 120


def rank(fingerprints: list[dict], items: list[dict], role: str, *, healing: bool) -> list[tuple[float, dict]]:
    allowed = (item for item in items if (eligible(role, item, fingerprints) if healing else is_safe(role, item)))
    return sorted(((score_candidate(fingerprints, item, role), item) for item in allowed), key=lambda pair: pair[0], reverse=True)


def classify_text(text: str, in_terms, out_terms) -> str | None:
    value = normalize(text)
    if not value:
        return None
    if any(term in value for term in out_terms):
        return "out"
    negated = False
    for term in in_terms:
        start = value.find(term)
        while start >= 0:
            if not NEGATION.search(value[max(0, start - 16):start]):
                return "in"
            negated = True
            start = value.find(term, start + 1)
    return "out" if negated else None


def parse_price(value) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value) if 0 < value < 10_000_000 else None
    text = str(value or "")
    match = re.search(r"\d[\d.,\s\u00a0]*", text)
    if not match:
        return None
    raw = re.sub(r"[\s\u00a0]", "", match.group()).rstrip(".,")
    if "," in raw and "." in raw:
        decimal = "," if raw.rfind(",") > raw.rfind(".") else "."
        raw = raw.replace("." if decimal == "," else ",", "").replace(decimal, ".")
    elif "," in raw:
        head, _, tail = raw.rpartition(",")
        raw = raw.replace(",", "") if len(tail) == 3 else head.replace(",", "") + "." + tail
    elif "." in raw:
        head, _, tail = raw.rpartition(".")
        if len(tail) == 3:
            raw = raw.replace(".", "")
        else:
            raw = head.replace(".", "") + "." + tail
    try:
        number = float(raw)
    except ValueError:
        return None
    return number if 0 < number < 10_000_000 else None


def structured_price(value) -> float | None:
    """schema.org prices always use '.' as decimal separator."""
    if isinstance(value, str) and re.fullmatch(r"\s*\d+(?:\.\d+)?\s*", value):
        number = float(value)
        return number if 0 < number < 10_000_000 else None
    return parse_price(value)


def jsonld_offers(blocks: list[str]) -> list[dict]:
    offers = []

    def walk(node, depth=0):
        if depth > 12:
            return
        if isinstance(node, list):
            for child in node[:200]:
                walk(child, depth + 1)
        elif isinstance(node, dict):
            if "availability" in node:
                offers.append(node)
            for child in node.values():
                if isinstance(child, (dict, list)):
                    walk(child, depth + 1)

    for block in blocks:
        try:
            walk(json.loads(block))
        except (ValueError, RecursionError):
            continue
    return offers[:200]


def jsonld_signal(blocks: list[str]) -> tuple[str | None, float | None, str]:
    votes, prices = set(), set()
    for offer in jsonld_offers(blocks):
        token = str(offer.get("availability") or "").rstrip("/").rsplit("/", 1)[-1].lower()
        if token in AVAILABILITY_IN:
            votes.add("in")
        elif token in AVAILABILITY_OUT:
            votes.add("out")
        price = structured_price(offer.get("price", offer.get("lowPrice")))
        if price is not None:
            prices.add(price)
    note = "Structured data lists variants with different availability." if len(votes) > 1 else ""
    return (votes.pop() if len(votes) == 1 else None), (prices.pop() if len(prices) == 1 else None), note


def decide_availability(signals: dict) -> str:
    strong = {signals[key] for key in ("jsonld", "indicator") if signals.get(key)}
    if len(strong) > 1:
        return "conflict"
    vote = strong.pop() if strong else signals.get("button") or signals.get("body")
    if vote == "in" and signals.get("button") == "out":
        return "conflict"
    return {"in": "in_stock", "out": "out_of_stock"}.get(vote, "unknown")


def action_allowed(config: dict, price: float | None) -> tuple[bool, str]:
    if config["max_price"] is None:
        return True, ""
    if price is None:
        return False, "Price unknown; maximum price cannot be verified."
    if price > config["max_price"]:
        return False, f"Price {price:.2f} is above the maximum {config['max_price']:.2f}."
    return True, ""


def validate_url(value, *, optional=False) -> str:
    if optional and value == "":
        return ""
    if not isinstance(value, str) or not value.strip() or len(value) > 2048 or any(ord(char) < 32 for char in value):
        raise AutomationError("Enter a valid http(s) URL.")
    value = value.strip()
    parsed = urlparse(value)
    if parsed.scheme not in ("http", "https") or not parsed.hostname or parsed.username or parsed.password:
        raise AutomationError("Only http(s) URLs without embedded credentials are allowed.")
    return value


def validate_terms(value) -> list[str]:
    if not isinstance(value, list) or len(value) > 10 or not all(isinstance(term, str) and len(term) <= 80 for term in value):
        raise AutomationError("Stock phrases must be a list of at most 10 short texts.")
    return [normalize(term) for term in value if normalize(term)]


def validate_watch(data: object) -> dict:
    if not isinstance(data, dict) or set(data) - {"transaction"} != WATCH_KEYS:
        raise AutomationError("Invalid watch settings.")
    name = data["name"].strip() if isinstance(data["name"], str) else ""
    if not 1 <= len(name) <= 80:
        raise AutomationError("Give the watch a name of 1-80 characters.")
    if data["mode"] not in MODES:
        raise AutomationError("Unknown action mode.")
    if type(data["interval"]) is not int or not MIN_INTERVAL <= data["interval"] <= MAX_INTERVAL:
        raise AutomationError(f"The interval must be {MIN_INTERVAL}-{MAX_INTERVAL} seconds.")
    max_price = data["max_price"]
    if max_price is not None and (type(max_price) not in (int, float) or not 0 < max_price < 10_000_000):
        raise AutomationError("The maximum price must be empty or a positive number.")
    if type(data["authorized"]) is not bool or not isinstance(data["elements"], dict) or not set(data["elements"]) <= set(ROLES):
        raise AutomationError("Invalid elements or authorization.")
    elements = {}
    for role, spec in data["elements"].items():
        if (
            not isinstance(spec, dict) or set(spec) != {"selector", "text"}
            or not all(isinstance(spec[key], str) for key in spec)
            or len(spec["selector"]) > 300 or len(spec["text"]) > 120
            or any(ord(char) < 32 for char in spec["selector"] + spec["text"])
        ):
            raise AutomationError("Each element needs a short CSS selector and/or visible text.")
        selector, text = spec["selector"].strip(), spec["text"].strip()
        if selector or text:
            elements[role] = {"selector": selector, "text": text}
    config = {
        "name": name, "url": validate_url(data["url"]), "mode": data["mode"], "interval": data["interval"],
        "in_stock_text": validate_terms(data["in_stock_text"]), "out_of_stock_text": validate_terms(data["out_of_stock_text"]),
        "max_price": None if max_price is None else float(max_price), "elements": elements,
        "checkout_url": validate_url(data["checkout_url"], optional=True), "authorized": data["authorized"],
    }
    if config["mode"] != "notify":
        if not config["authorized"]:
            raise AutomationError("Cart and checkout modes require your explicit authorization.")
        if config["mode"] != "reserve" and "add_to_cart" not in elements:
            raise AutomationError("Cart and checkout modes require an add-to-cart button.")
    if config["mode"] in ("checkout", "order") and not (config["checkout_url"] or "checkout" in elements):
        raise AutomationError("Checkout mode requires a checkout URL or checkout button.")
    for role in ACTION_ROLES & set(elements):
        if is_final_purchase({"text": elements[role]["text"]}) or FINAL_RESERVATION.search(elements[role]["text"]):
            raise AutomationError("Echo never clicks final buttons as cart/navigation actions. Configure a separate authorized transaction.")
    if config["mode"] in TRANSACTION_MODES:
        config["transaction"] = validate_transaction(data.get("transaction"), config)
    elif data.get("transaction") is not None:
        raise AutomationError("Transaction settings require order or reserve mode.")
    return config


def origin(url: str) -> tuple:
    parsed = urlparse(url)
    try:
        return parsed.scheme, parsed.hostname, parsed.port or (443 if parsed.scheme == "https" else 80)
    except ValueError as error:
        raise AutomationError("Invalid shop origin or port.") from error


def validate_transaction(data: object, config: dict) -> dict:
    if (
        not isinstance(data, dict) or set(data) != {"authorized", "currency", *TRANSACTION_FIELDS}
        or data["authorized"] is not True
    ):
        raise AutomationError("A purchase/reservation requires separate explicit transaction authorization.")
    if config["max_price"] is None or not isinstance(data["currency"], str) or data["currency"] not in TRANSACTION_CURRENCIES:
        raise AutomationError("Set a maximum final total and a supported currency before authorizing a transaction.")
    if config["checkout_url"] and origin(config["checkout_url"]) != origin(config["url"]):
        raise AutomationError("The final order/reservation page must use the product page's origin.")
    result = {"authorized": True, "currency": data["currency"]}
    for role in TRANSACTION_FIELDS:
        spec = data[role]
        if (
            not isinstance(spec, dict) or set(spec) != {"selector", "text"}
            or not all(isinstance(value, str) for value in spec.values())
            or not 1 <= len(spec["selector"].strip()) <= 300 or len(spec["text"]) > 120
            or any(ord(char) < 32 for char in spec["selector"] + spec["text"])
            or (role in ("button", "confirmation", "item") and not spec["text"].strip())
        ):
            raise AutomationError("Transaction elements need exact CSS selectors; button, product and confirmation also need exact text.")
        result[role] = {"selector": spec["selector"].strip(), "text": spec["text"].strip()}
    if result["quantity"]["text"] != "1":
        raise AutomationError("Only one unit of one product may be authorized.")
    pattern = FINAL_PURCHASE if config["mode"] == "order" else FINAL_RESERVATION
    if not pattern.search(result["button"]["text"]):
        raise AutomationError("The final button text must explicitly describe an order/payment or reservation.")
    return result


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
                CREATE TABLE IF NOT EXISTS watches (id TEXT PRIMARY KEY, config TEXT NOT NULL, state TEXT NOT NULL, created REAL);
                CREATE TABLE IF NOT EXISTS selectors (
                    watch_id TEXT, role TEXT, version INTEGER, selector TEXT, fingerprint TEXT, last_seen TEXT,
                    reason TEXT, score REAL, created REAL, PRIMARY KEY(watch_id, role, version));
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, watch_id TEXT, kind TEXT, summary TEXT, created REAL);
                CREATE TABLE IF NOT EXISTS transactions (
                    watch_id TEXT PRIMARY KEY, attempt TEXT, mode TEXT, status TEXT, proof TEXT, created REAL);
            """)
            yield db

    @staticmethod
    def _watch(row) -> dict:
        return {"id": row["id"], "config": json.loads(row["config"]), "state": json.loads(row["state"]), "created": row["created"]}

    @staticmethod
    def _selector(row) -> dict:
        return {
            "watch_id": row["watch_id"], "role": row["role"], "version": row["version"], "selector": row["selector"],
            "fingerprint": json.loads(row["fingerprint"]), "last_seen": json.loads(row["last_seen"]),
            "reason": row["reason"], "score": row["score"], "created": row["created"],
        }

    def watches(self) -> list[dict]:
        with self.connection() as db:
            return [self._watch(row) for row in db.execute("SELECT * FROM watches ORDER BY created")]

    def watch(self, watch_id: str) -> dict:
        with self.connection() as db:
            row = db.execute("SELECT * FROM watches WHERE id=?", (watch_id,)).fetchone()
        if not row:
            raise AutomationError("Unknown watch.")
        return self._watch(row)

    def _add_version(self, db, watch_id, role, selector, fingerprint, reason, score) -> int:
        version = db.execute(
            "SELECT COALESCE(MAX(version), 0) + 1 FROM selectors WHERE watch_id=? AND role=?", (watch_id, role),
        ).fetchone()[0]
        db.execute(
            "INSERT INTO selectors VALUES(?,?,?,?,?,?,?,?,?)",
            (watch_id, role, version, selector, json.dumps(fingerprint), "{}", reason, score, time.time()),
        )
        db.execute("DELETE FROM selectors WHERE watch_id=? AND role=? AND version<=?", (watch_id, role, version - 25))
        return version

    def save_watch(self, watch_id: str, config: dict) -> None:
        with self.write_lock, self.connection() as db:
            row = db.execute("SELECT config FROM watches WHERE id=?", (watch_id,)).fetchone()
            if row is None:
                if db.execute("SELECT COUNT(*) FROM watches").fetchone()[0] >= MAX_WATCHES:
                    raise AutomationError(f"At most {MAX_WATCHES} watches are supported.")
                db.execute(
                    "INSERT INTO watches VALUES(?,?,?,?)",
                    (watch_id, json.dumps(config), json.dumps(DEFAULT_STATE), time.time()),
                )
                previous = {}
            else:
                previous = json.loads(row["config"])["elements"]
                db.execute(
                    "UPDATE watches SET config=?, state=? WHERE id=?",
                    (json.dumps(config), json.dumps(DEFAULT_STATE), watch_id),
                )
            for role, spec in config["elements"].items():
                if previous.get(role) != spec:
                    fingerprint = {"text": spec["text"]} if spec["text"] else {}
                    self._add_version(db, watch_id, role, spec["selector"], fingerprint, "configured", None)

    def delete_watch(self, watch_id: str) -> None:
        with self.write_lock, self.connection() as db:
            if db.execute("DELETE FROM watches WHERE id=?", (watch_id,)).rowcount != 1:
                raise AutomationError("Unknown watch.")
            db.execute("DELETE FROM selectors WHERE watch_id=?", (watch_id,))
            db.execute("DELETE FROM events WHERE watch_id=?", (watch_id,))

    def update_state(self, watch_id: str, changes: dict) -> dict:
        with self.write_lock, self.connection() as db:
            row = db.execute("SELECT state FROM watches WHERE id=?", (watch_id,)).fetchone()
            if not row:
                raise AutomationError("Unknown watch.")
            state = {**DEFAULT_STATE, **json.loads(row["state"]), **changes}
            db.execute("UPDATE watches SET state=? WHERE id=?", (json.dumps(state), watch_id))
            return state

    def active_selector(self, watch_id: str, role: str) -> dict | None:
        with self.connection() as db:
            row = db.execute(
                "SELECT * FROM selectors WHERE watch_id=? AND role=? ORDER BY version DESC LIMIT 1", (watch_id, role),
            ).fetchone()
        return self._selector(row) if row else None

    def add_version(self, watch_id, role, selector, fingerprint, reason, score) -> int:
        with self.write_lock, self.connection() as db:
            return self._add_version(db, watch_id, role, selector, fingerprint, reason, score)

    def observe(self, watch_id: str, role: str, version: int, descriptor: dict, *, capture: bool) -> None:
        column = "fingerprint" if capture else "last_seen"
        with self.write_lock, self.connection() as db:
            db.execute(
                f"UPDATE selectors SET {column}=? WHERE watch_id=? AND role=? AND version=?",
                (json.dumps(descriptor), watch_id, role, version),
            )

    def rollback(self, watch_id: str, role: str, version: int) -> int:
        with self.write_lock, self.connection() as db:
            row = db.execute(
                "SELECT * FROM selectors WHERE watch_id=? AND role=? AND version=?", (watch_id, role, version),
            ).fetchone()
            if not row:
                raise AutomationError("Unknown selector version.")
            return self._add_version(
                db, watch_id, role, row["selector"], json.loads(row["fingerprint"]), f"rollback:{version}", None,
            )

    def selectors(self) -> list[dict]:
        with self.connection() as db:
            return [self._selector(row) for row in db.execute(
                "SELECT * FROM selectors ORDER BY watch_id, role, version DESC",
            )]

    def event(self, watch_id: str, kind: str, summary: str) -> int:
        with self.write_lock, self.connection() as db:
            cursor = db.execute(
                "INSERT INTO events(watch_id, kind, summary, created) VALUES(?,?,?,?)",
                (watch_id, kind, summary[:600], time.time()),
            )
            db.execute("DELETE FROM events WHERE id NOT IN (SELECT id FROM events ORDER BY id DESC LIMIT 300)")
            return cursor.lastrowid

    def events(self, limit: int = 100) -> list[dict]:
        with self.connection() as db:
            return [dict(row) for row in db.execute("SELECT * FROM events ORDER BY id DESC LIMIT ?", (limit,))]

    def transaction(self, watch_id: str) -> dict | None:
        with self.connection() as db:
            row = db.execute("SELECT * FROM transactions WHERE watch_id=?", (watch_id,)).fetchone()
            return dict(row) if row else None

    def claim_transaction(self, watch: dict) -> str:
        with self.write_lock, self.connection() as db:
            row = db.execute("SELECT config,state FROM watches WHERE id=?", (watch["id"],)).fetchone()
            if (
                not row or json.loads(row["config"]) != watch["config"]
                or json.loads(row["state"]).get("execution_id") != watch["state"].get("execution_id")
            ):
                raise AutomationError("The watch changed or was cancelled before submission.")
            if db.execute("SELECT 1 FROM transactions WHERE watch_id=?", (watch["id"],)).fetchone():
                raise AutomationError("A transaction was already attempted. Check the shop before explicitly authorizing another.")
            attempt = secrets.token_hex(16)
            db.execute("INSERT INTO transactions VALUES(?,?,?,?,?,?)",
                       (watch["id"], attempt, watch["config"]["mode"], "uncertain", "", time.time()))
            return attempt

    def confirm_transaction(self, watch_id: str, attempt: str, proof: str) -> None:
        with self.write_lock, self.connection() as db:
            db.execute("UPDATE transactions SET status='confirmed',proof=? WHERE watch_id=? AND attempt=?",
                       (proof[:500], watch_id, attempt))

    def rearm_transaction(self, watch_id: str) -> None:
        with self.write_lock, self.connection() as db:
            db.execute("DELETE FROM transactions WHERE watch_id=?", (watch_id,))


def describe_elements(page, *, selector: str = "", mode: str = "selector", limit: int = 20) -> list[dict]:
    result = page.evaluate(DESCRIBE_JS, {"selector": selector, "mode": mode, "limit": limit, "paths": mode == "selector"})
    return list((result or {}).get("items") or [])


def resolve_element(page, store: Store, watch_id: str, role: str, *, heal: bool = True) -> tuple[dict | None, dict]:
    active = store.active_selector(watch_id, role)
    if active is None:
        return None, {"status": "unconfigured"}
    fingerprints = [fingerprint for fingerprint in (active["fingerprint"], active["last_seen"]) if fingerprint]
    info = {"status": "missing", "version": active["version"], "selector": active["selector"], "score": None, "label": ""}
    if active["selector"]:
        ranked = rank(fingerprints, describe_elements(page, selector=active["selector"]), role, healing=False)
        if ranked:
            score, item = ranked[0]
            clear = len(ranked) == 1 or not fingerprints or score - ranked[1][0] >= HEAL_MARGIN
            if score >= KEEP_THRESHOLD and clear and item.get("path"):
                store.observe(watch_id, role, active["version"], fingerprint_of(item), capture=is_partial(active["fingerprint"]))
                return item, {**info, "status": "ok", "score": score, "label": label(item)[:120]}
    if not heal or not fingerprints:
        return None, info
    ranked = rank(
        fingerprints, describe_elements(page, mode="action" if role in ACTION_ROLES else "text", limit=1500), role, healing=True,
    )
    if not ranked:
        return None, info
    score, item = ranked[0]
    runner_up = ranked[1][0] if len(ranked) > 1 else 0.0
    info["candidates"] = [{"score": value, "label": label(candidate)[:80]} for value, candidate in ranked[:3]]
    if score < HEAL_THRESHOLD or score - runner_up < HEAL_MARGIN:
        return None, {**info, "status": "ambiguous" if score >= HEAL_THRESHOLD else "missing"}
    path = page.evaluate(PATH_JS, item["index"])
    if not path:
        return None, {**info, "status": "unaddressable"}
    item["path"] = path
    fingerprint = fingerprint_of(item) if is_partial(active["fingerprint"]) else active["fingerprint"]
    reason = "healed" if active["selector"] else "discovered"
    version = store.add_version(watch_id, role, path, fingerprint, reason, score)
    store.observe(watch_id, role, version, fingerprint_of(item), capture=False)
    store.event(watch_id, reason, f"{role}: {active['selector'] or '(text)'} -> {path} (score {score:.2f})")
    return item, {**info, "status": reason, "version": version, "selector": path, "score": score, "label": label(item)[:120]}


def load(page, url: str) -> int:
    response = page.goto(url, wait_until="domcontentloaded", timeout=30_000)
    try:
        page.wait_for_load_state("networkidle", timeout=6_000)
    except PlaywrightTimeoutError:
        pass
    return response.status if response else 0


def inspect_page(page, store: Store, watch: dict, status: int) -> dict:
    config = watch["config"]
    raw = page.evaluate(SIGNALS_JS)
    text = raw.get("text") or ""
    challenge = CHALLENGE.search(raw.get("title") or "") or (len(text) < 5000 and CHALLENGE.search(text))
    if challenge or (raw.get("captcha") and (status >= 400 or len(text) < 1500)):
        return {"result": "blocked", "status": status, "error": "The site shows a bot check or CAPTCHA. Echo does not bypass it."}
    if status in (429, 503):
        return {"result": "rate_limited", "status": status, "error": f"The site returned HTTP {status}."}
    if status >= 400:
        return {"result": "error", "status": status, "error": f"The site returned HTTP {status}."}
    in_terms = config["in_stock_text"] or list(DEFAULT_IN)
    out_terms = config["out_of_stock_text"] or list(DEFAULT_OUT)
    jsonld, jsonld_price, note = jsonld_signal(raw.get("jsonld") or [])
    signals, found, elements = {"jsonld": jsonld}, {}, {}
    notes = [note] if note else []

    def resolve(role, heal=True):
        if role in config["elements"]:
            descriptor, elements[role] = resolve_element(page, store, watch["id"], role, heal=heal)
            if descriptor:
                found[role] = descriptor

    resolve("stock_indicator")
    resolve("price")
    indicator = found.get("stock_indicator")
    signals["indicator"] = classify_text(indicator["text"], in_terms, out_terms) if indicator else None
    strong = {vote for vote in (signals["jsonld"], signals["indicator"]) if vote}
    # Shops often remove the buy button when sold out; healing then would latch onto an unrelated button.
    resolve("add_to_cart", heal=strong != {"out"})
    button = found.get("add_to_cart")
    if button:
        button_vote = classify_text(label(button), in_terms, out_terms)
        signals["button"] = "out" if button_vote == "out" or not (button["visible"] and button["enabled"]) else "in"
    else:
        signals["button"] = None
    signals["body"] = classify_text(text, in_terms, out_terms)
    availability = decide_availability(signals)
    if availability == "conflict":
        notes.append("Stock signals disagree; Echo takes no action.")
    price_element = found.get("price")
    price = parse_price(price_element["text"]) if price_element else None
    if price is None:
        price = jsonld_price
    return {
        "result": "ok", "status": status, "availability": availability, "price": price, "signals": signals,
        "elements": elements, "found": found, "payment": bool(raw.get("payment")), "notes": notes,
    }


def click_verified(page, role: str, descriptor: dict) -> bool:
    if not descriptor.get("path") or not is_safe(role, descriptor):
        raise AutomationError("Echo refused to click this element.")
    requests, before = [], page.url

    def record(request):
        if request.resource_type in ("xhr", "fetch", "document"):
            requests.append(request.url)

    page.evaluate(OBSERVE_JS)
    page.on("request", record)
    try:
        page.locator(descriptor["path"]).first.click(timeout=10_000)
        page.wait_for_timeout(800)
        try:
            page.wait_for_load_state("networkidle", timeout=5_000)
        except PlaywrightTimeoutError:
            pass
    finally:
        page.remove_listener("request", record)
    try:
        mutations = page.evaluate("() => window.__echoMutations || 0")
    except PlaywrightError:
        mutations = 0
    return page.url != before or bool(requests) or mutations > 0


TRANSACTION_JS = r"""({spec, expected, commit, approvedOrigin}) => {
    const normalize = value => String(value || '').replace(/\s+/g, ' ').trim().toLowerCase();
    const visible = el => {
        const rect = el.getBoundingClientRect(), style = getComputedStyle(el);
        return rect.width > 0 && rect.height > 0 && style.visibility !== 'hidden' && style.display !== 'none' && Number(style.opacity) > 0;
    };
    const text = el => normalize(['INPUT', 'SELECT'].includes(el.tagName) ? el.value : el.innerText);
    const found = {}, snapshot = {};
    for (const role of ['button', 'item', 'quantity', 'total']) {
        const nodes = [...document.querySelectorAll(spec[role].selector)].filter(visible);
        if (nodes.length !== 1) throw new Error('Exactly one visible ' + role + ' is required.');
        found[role] = nodes[0];
        snapshot[role] = text(nodes[0]);
    }
    const success = [...document.querySelectorAll(spec.confirmation.selector)].filter(visible);
    if (success.some(el => text(el) === normalize(spec.confirmation.text))) throw new Error('Confirmation was already visible before submission.');
    const button = found.button;
    if (!['BUTTON', 'INPUT'].includes(button.tagName) || button.disabled || button.getAttribute('aria-disabled') === 'true'
        || (button.tagName === 'INPUT' && !['submit', 'button'].includes(button.type))) throw new Error('Final button is not actionable.');
    for (const role of ['button', 'item', 'quantity']) {
        if (snapshot[role] !== normalize(spec[role].text)) throw new Error('Exact transaction text changed: ' + role);
    }
    if (location.origin !== new URL(approvedOrigin).origin) throw new Error('Final origin changed.');
    if (button.form && !button.form.checkValidity()) throw new Error('The checkout/reservation form still requires manual input.');
    if (commit) {
        if (JSON.stringify(snapshot) !== JSON.stringify(expected)) throw new Error('Transaction details changed before submission.');
        button.click();
    }
    return snapshot;
}"""

CONFIRMATION_JS = r"""spec => {
    const normalize = value => String(value || '').replace(/\s+/g, ' ').trim().toLowerCase();
    const found = [...document.querySelectorAll(spec.selector)].filter(el => {
        const rect = el.getBoundingClientRect(), style = getComputedStyle(el);
        return rect.width > 0 && rect.height > 0 && style.visibility !== 'hidden' && style.display !== 'none' && Number(style.opacity) > 0;
    });
    return found.length === 1 && normalize(found[0].innerText) === normalize(spec.text);
}"""


def transaction_total(text: str, currency: str) -> Decimal:
    upper = text.upper()
    tokens = re.findall(r"\b[A-Z]{3}\b|US\$|€|£|\$", upper)
    if not tokens or any(token not in TRANSACTION_CURRENCIES[currency] for token in tokens):
        raise AutomationError("The final total has an unknown, ambiguous or different currency.")
    numbers = re.findall(r"\d[\d.,\s\u00a0]*", text)
    if len(numbers) != 1 or re.search(r"[-+]\s*\d", text):
        raise AutomationError("The final total must contain one unambiguous nonnegative amount.")
    number = numbers[0].strip()
    if " " in number or "\u00a0" in number:
        if not re.fullmatch(r"\d{1,3}(?:[ \u00a0]\d{3})+(?:[.,]\d{2})?", number):
            raise AutomationError("Ambiguous grouping in the final total.")
        number = re.sub(r"[ \u00a0]", "", number)
    if re.fullmatch(r"\d+(?:[.,]\d{2})?", number):
        number = number.replace(",", ".")
    elif re.fullmatch(r"\d{1,3}(?:,\d{3})+(?:\.\d{2})?", number):
        number = number.replace(",", "")
    elif re.fullmatch(r"\d{1,3}(?:\.\d{3})+(?:,\d{2})?", number):
        number = number.replace(".", "").replace(",", ".")
    else:
        raise AutomationError("The final total could not be verified to cents.")
    return Decimal(number)


def action_current(store: Store, watch: dict, cancelled) -> None:
    if cancelled():
        raise AutomationError("Action cancelled before submission.")
    current = store.watch(watch["id"])
    if current["config"] != watch["config"] or current["state"].get("execution_id") != watch["state"].get("execution_id"):
        raise AutomationError("The watch was edited, paused or rearmed during this action.")
    if watch["config"]["mode"] in TRANSACTION_MODES and store.transaction(watch["id"]):
        raise AutomationError("A transaction was already attempted. Check the shop and explicitly rearm before another attempt.")


def submit_transaction(page, store: Store, watch: dict, cancelled) -> dict:
    config = watch["config"]
    spec = validate_transaction(config.get("transaction"), config)
    action_current(store, watch, cancelled)
    if origin(page.url) != origin(config["url"]):
        raise AutomationError("The final page is outside the authorized shop origin.")
    signals = page.evaluate(SIGNALS_JS)
    if signals.get("captcha") or CHALLENGE.search((signals.get("title") or "") + (signals.get("text") or "")):
        raise AutomationError("A bot check requires manual intervention; no transaction was submitted.")
    parsed = urlparse(config["url"])
    approved_origin = f"{parsed.scheme}://{parsed.netloc}"
    args = {"spec": spec, "expected": None, "commit": False, "approvedOrigin": approved_origin}
    snapshot = page.evaluate(TRANSACTION_JS, args)
    total = transaction_total(snapshot["total"], spec["currency"])
    if total > Decimal(str(config["max_price"])):
        raise AutomationError("The final total including fees exceeds your authorized budget.")
    with store.write_lock:
        action_current(store, watch, cancelled)
        # Commit the attempt before the external side effect. A crash or timeout must never cause an automatic retry.
        attempt = store.claim_transaction(watch)
        if cancelled():
            raise AutomationError("Cancelled at submission. Check the shop before rearming.")
        page.evaluate(TRANSACTION_JS, {**args, "expected": snapshot, "commit": True})
    try:
        page.wait_for_function(CONFIRMATION_JS, arg=spec["confirmation"], timeout=12_000)
    except PlaywrightTimeoutError:
        return {"ok": False, "steps": ["submitted"], "reason": "Submission outcome unknown: no verified confirmation. Check the shop; Echo will not retry."}
    if origin(page.url) != origin(config["url"]):
        return {"ok": False, "steps": ["submitted"], "reason": "Confirmation left the authorized shop. Check the shop; Echo will not retry."}
    proof = f"{config['mode']}: {spec['confirmation']['text']} | {spec['currency']} {total:.2f}"
    store.confirm_transaction(watch["id"], attempt, proof)
    return {"ok": True, "steps": ["reservation_confirmed" if config["mode"] == "reserve" else "order_confirmed"], "reason": proof}


def purchase_flow(page, store: Store, watch: dict, cancelled=lambda: False) -> dict:
    """Run only the configured action, with separately authorized final submissions."""
    config = watch["config"]
    action_current(store, watch, cancelled)
    observation = inspect_page(page, store, watch, load(page, config["url"]))
    if observation["result"] != "ok":
        return {"ok": False, "steps": [], "reason": observation["error"]}
    if observation["availability"] != "in_stock":
        return {"ok": False, "steps": [], "reason": "The product is no longer clearly in stock."}
    allowed, reason = action_allowed(config, observation["price"])
    if not allowed:
        return {"ok": False, "steps": [], "reason": reason}
    if config["mode"] == "reserve":
        if config["checkout_url"]:
            load(page, config["checkout_url"])
        return submit_transaction(page, store, watch, cancelled)
    if observation["payment"]:
        return {"ok": False, "steps": [], "reason": "Payment fields are visible; Echo stops before payment."}
    button = observation["found"].get("add_to_cart")
    if not button or not button["visible"] or not button["enabled"]:
        return {"ok": False, "steps": [], "reason": "The add-to-cart button was not found or is disabled."}
    action_current(store, watch, cancelled)
    if not click_verified(page, "add_to_cart", button):
        return {"ok": False, "steps": [], "reason": "Clicking add-to-cart had no visible effect."}
    steps = ["added_to_cart"]
    if config["mode"] in ("checkout", "order"):
        action_current(store, watch, cancelled)
        if config["checkout_url"]:
            load(page, config["checkout_url"])
        else:
            if config["mode"] == "checkout" and page.evaluate(SIGNALS_JS).get("payment"):
                return {"ok": True, "steps": steps, "reason": "Payment fields are visible; Echo stops before payment."}
            descriptor, _info = resolve_element(page, store, watch["id"], "checkout")
            if not descriptor:
                return {"ok": False, "steps": steps, "reason": "Added to cart, but the checkout button was not found."}
            if not click_verified(page, "checkout", descriptor):
                return {"ok": False, "steps": steps, "reason": "Added to cart, but opening checkout had no visible effect."}
        steps.append("checkout_opened")
    if config["mode"] == "order":
        result = submit_transaction(page, store, watch, cancelled)
        return {**result, "steps": steps + result["steps"]}
    return {"ok": True, "steps": steps, "reason": ""}


def short_error(error: BaseException) -> str:
    text = str(error).strip().splitlines()
    return (text[0] if text else type(error).__name__)[:300]


def _block_heavy(route) -> None:
    try:
        if route.request.resource_type in ("image", "media", "font"):
            route.abort()
        else:
            route.continue_()
    except PlaywrightError:
        pass


def open_task(url: str):
    def task(context):
        page = context.pages[0] if context.pages else context.new_page()
        page.bring_to_front()
        page.goto(url, wait_until="domcontentloaded", timeout=30_000)
        return {"ok": True}
    return task


def purchase_task(store: Store, watch: dict, cancelled=lambda: False):
    def task(context):
        page = context.new_page()
        result = purchase_flow(page, store, watch, cancelled)
        page.bring_to_front()
        return result
    return task


class ShopSession:
    """A visible persistent browser profile for user-prepared shopping sessions."""

    def __init__(self, profile_dir: Path, *, headless: bool = False):
        self.profile_dir = profile_dir
        self.headless = headless
        self.commands = queue.Queue(maxsize=5)
        self.lock = threading.RLock()
        self.stop_event = threading.Event()
        self.thread = None
        self.state = {"open": False, "busy": False, "host": "", "error": ""}

    def snapshot(self) -> dict:
        with self.lock:
            return {**self.state, "running": bool(self.thread and self.thread.is_alive())}

    def _set(self, **changes) -> None:
        with self.lock:
            self.state.update(changes)

    def submit(self, task, *, wait: float | None):
        if sync_playwright is None:
            raise AutomationError("Playwright is not installed.")
        reply = queue.Queue(maxsize=1)
        try:
            self.commands.put_nowait((task, reply))
        except queue.Full:
            raise AutomationError("The shop window is busy.") from None
        self._ensure_thread()
        if wait is None:
            return None
        try:
            outcome = reply.get(timeout=wait)
        except queue.Empty:
            raise AutomationError("The shop window did not respond in time.") from None
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    def _ensure_thread(self) -> None:
        with self.lock:
            if self.thread and self.thread.is_alive():
                return
            self.stop_event.clear()
            self.thread = threading.Thread(target=self._run, name="echo-shop-session", daemon=True)
            self.thread.start()

    def close(self, timeout: float = 15) -> None:
        with self.lock:
            thread = self.thread
            self.stop_event.set()
        if thread and thread is not threading.current_thread():
            thread.join(timeout)

    def _run(self) -> None:
        current, failed = threading.current_thread(), None
        try:
            self.profile_dir.mkdir(parents=True, exist_ok=True)
            with sync_playwright() as playwright:
                context = playwright.chromium.launch_persistent_context(
                    str(self.profile_dir), headless=self.headless, no_viewport=True,
                )
                closed = []
                context.on("close", lambda *_args: closed.append(True))
                self._set(open=True, error="")
                try:
                    while not self.stop_event.is_set() and not closed and context.pages:
                        try:
                            task, reply = self.commands.get_nowait()
                        except queue.Empty:
                            try:
                                context.wait_for_event("close", timeout=500)
                            except PlaywrightError:
                                pass
                            continue
                        self._set(busy=True)
                        try:
                            reply.put(task(context))
                        except Exception as error:  # report every task failure to the waiting caller
                            LOGGER.warning("Shop task failed: %s", error)
                            reply.put(AutomationError(short_error(error)))
                        finally:
                            host = urlparse(context.pages[-1].url).hostname if context.pages and not closed else ""
                            self._set(busy=False, host=host or "")
                finally:
                    if not closed:
                        try:
                            context.close()
                        except PlaywrightError:
                            pass
        except Exception as error:  # surface launch errors such as a locked profile
            LOGGER.warning("Shop browser failed: %s", error)
            failed = short_error(error)
            self._set(error=failed)
        finally:
            self._set(open=False, busy=False, host="")
            drained = []
            with self.lock:
                if self.thread is current:
                    self.thread = None
                if self.stop_event.is_set() or failed:
                    while True:
                        try:
                            drained.append(self.commands.get_nowait()[1])
                        except queue.Empty:
                            break
                restart = not self.commands.empty()
            for reply in drained:
                reply.put(AutomationError(failed or "The shop window was closed."))
            if restart:
                self._ensure_thread()


def jitter(interval: float) -> float:
    return interval * random.uniform(0.9, 1.1)


class WebAutomation:
    ACTIONS = {
        "save": {"id", "watch"}, "delete": {"id"}, "pause": {"id"}, "resume": {"id", "rearm"},
        "rollback": {"id", "role", "version"}, "check": {"id"}, "start": {"authorized", "sound"},
        "stop": set(), "shop_open": {"url"}, "shop_close": set(),
    }

    def __init__(self, store: Store, notify=None, *, shop: ShopSession | None = None):
        self.store = store
        self.notify = notify
        self.shop = shop or ShopSession(DATA_DIR / "shop-profile")
        self.lock = threading.RLock()
        self.check_lock = threading.Lock()
        self.stop_event = threading.Event()
        self.wake_event = threading.Event()
        self.thread = None
        self.sound = False
        self.active = ""
        self.errors = {}

    def snapshot(self) -> dict:
        selectors = {}
        for row in self.store.selectors():
            selectors.setdefault(row["watch_id"], {}).setdefault(row["role"], []).append({
                "version": row["version"], "selector": row["selector"], "reason": row["reason"], "score": row["score"],
                "created": row["created"], "text": str(row["fingerprint"].get("text") or "")[:120],
                "seen": str(row["last_seen"].get("text") or "")[:120],
            })
        watches = [{**watch, "selectors": selectors.get(watch["id"], {}),
                    "transaction": self.store.transaction(watch["id"])} for watch in self.store.watches()]
        with self.lock:
            running = bool(self.thread and self.thread.is_alive()) and not self.stop_event.is_set()
            errors, active = dict(self.errors), self.active
        return {
            "available": sync_playwright is not None, "running": running, "sound": self.sound, "active": active,
            "errors": errors, "watches": watches, "events": self.store.events(100), "shop": self.shop.snapshot(),
            "limits": {"min_interval": MIN_INTERVAL, "max_interval": MAX_INTERVAL, "max_watches": MAX_WATCHES},
        }

    def handle(self, action: str, data: object):
        if action not in self.ACTIONS or not isinstance(data, dict) or set(data) != self.ACTIONS[action]:
            raise AutomationError("Invalid request.")
        if "id" in data and action != "save" and not isinstance(data["id"], str):
            raise AutomationError("Unknown watch.")
        if action == "save":
            return {"id": self.save_watch(data["id"], data["watch"])}
        if action == "delete":
            self.store.delete_watch(data["id"])
        elif action == "pause":
            self.set_paused(data["id"], True)
        elif action == "resume":
            if type(data["rearm"]) is not bool:
                raise AutomationError("Invalid request.")
            self.set_paused(data["id"], False, rearm=data["rearm"])
        elif action == "rollback":
            self.rollback(data["id"], data["role"], data["version"])
        elif action == "check":
            return {"check": self.check_now(data["id"])}
        elif action == "start":
            self.start(data)
        elif action == "stop":
            self.stop()
        elif action == "shop_open":
            self.shop.submit(open_task(validate_url(data["url"])), wait=None)
        elif action == "shop_close":
            self.shop.close()
        return {}

    def save_watch(self, watch_id, data) -> str:
        if not isinstance(watch_id, str):
            raise AutomationError("Unknown watch.")
        config = validate_watch(data)
        if watch_id:
            self.store.watch(watch_id)
        else:
            watch_id = secrets.token_hex(8)
        self.store.save_watch(watch_id, config)
        self.store.event(watch_id, "saved", f"Saved '{config['name']}' ({config['mode']}).")
        self.wake_event.set()
        return watch_id

    def set_paused(self, watch_id: str, paused: bool, *, rearm: bool = False) -> None:
        with self.store.write_lock:
            watch = self.store.watch(watch_id)
            if not paused and self.active == watch_id:
                raise AutomationError("Wait for the current action to finish before resuming.")
            if not paused and self.store.transaction(watch_id):
                if not rearm:
                    raise AutomationError("A transaction was attempted. Check the shop and explicitly authorize another attempt.")
                self.store.rearm_transaction(watch_id)
                self.store.event(watch_id, "rearmed", "User explicitly authorized another transaction after checking the previous outcome.")
            changes = {"paused": paused, "execution_id": ""}
            if not paused:
                state = watch["state"]
                current = state["availability"] if state["availability"] in ("in_stock", "out_of_stock") else state["monitor_availability"]
                changes.update(failures=0, backoff=0, next_check=0, monitor_availability="" if rearm else current)
            self.store.update_state(watch_id, changes)
        self.wake_event.set()

    def rollback(self, watch_id, role, version) -> int:
        if role not in ROLES or type(version) is not int:
            raise AutomationError("Unknown selector version.")
        self.store.watch(watch_id)
        new_version = self.store.rollback(watch_id, role, version)
        self.store.event(watch_id, "rollback", f"{role}: restored version {version} as version {new_version}.")
        return new_version

    def start(self, data: dict) -> None:
        if data.get("authorized") is not True or type(data.get("sound")) is not bool:
            raise AutomationError("Confirm that you may monitor these pages.")
        if sync_playwright is None:
            raise AutomationError("Playwright is not installed.")
        with self.lock:
            self.sound = data["sound"]
            if self.thread and self.thread.is_alive():
                if self.stop_event.is_set():
                    raise AutomationError("The monitor is still stopping; try again in a moment.")
                return
            self.stop_event.clear()
            self.errors.pop("monitor", None)
            self.thread = threading.Thread(target=self._run, name="echo-web-monitor", daemon=True)
            self.thread.start()

    def stop(self, timeout: float = 20) -> None:
        with self.lock:
            thread = self.thread
            self.stop_event.set()
            self.wake_event.set()
        if thread and thread is not threading.current_thread():
            thread.join(timeout)

    def shutdown(self) -> None:
        self.stop(timeout=5)
        self.shop.close(timeout=5)

    def check_now(self, watch_id: str) -> dict:
        watch = self.store.watch(watch_id)
        if sync_playwright is None:
            raise AutomationError("Playwright is not installed.")
        if not self.check_lock.acquire(blocking=False):
            raise AutomationError("A manual check is already running.")
        try:
            with sync_playwright() as playwright:
                try:
                    browser = playwright.chromium.launch(headless=True)
                except PlaywrightError as error:
                    raise AutomationError(f"Chromium could not start: {short_error(error)}") from None
                try:
                    observation = self._observe(browser, watch)
                finally:
                    browser.close()
        except PlaywrightError as error:
            raise AutomationError(f"The browser check failed: {short_error(error)}") from None
        finally:
            self.check_lock.release()
        self._record(watch, observation, monitor=False)
        return {key: value for key, value in observation.items() if key != "found"}

    def _observe(self, browser, watch: dict) -> dict:
        try:
            context = browser.new_context(locale="nl-NL")
        except PlaywrightError as error:
            return {"result": "error", "status": 0, "error": short_error(error)}
        try:
            context.route("**/*", _block_heavy)
            page = context.new_page()
            return inspect_page(page, self.store, watch, load(page, watch["config"]["url"]))
        except PlaywrightTimeoutError:
            return {"result": "error", "status": 0, "error": "The page did not load within 30 seconds."}
        except PlaywrightError as error:
            return {"result": "error", "status": 0, "error": short_error(error)}
        finally:
            try:
                context.close()
            except PlaywrightError:
                pass

    def _record(self, watch: dict, observation: dict, *, monitor: bool) -> str | None:
        config, state, now = watch["config"], watch["state"], time.time()
        result = observation["result"]
        changes = {
            "last_check": now, "status": result, "last_error": observation.get("error", ""),
            "notes": list(observation.get("notes", []))[:5],
        }
        trigger = None
        if result == "ok":
            changes.update(
                availability=observation["availability"], price=observation["price"],
                signals=observation["signals"], elements=observation["elements"],
            )
            if monitor:
                changes.update(failures=0, backoff=0, next_check=now + jitter(config["interval"]))
        if result == "ok" and monitor and observation["availability"] in ("in_stock", "out_of_stock"):
            current = observation["availability"]
            if current == "in_stock":
                allowed, reason = action_allowed(config, observation["price"])
                if not allowed:
                    current = "in_stock_over_price"
                    changes["notes"].append(reason)
            previous = state["monitor_availability"]
            if current == "in_stock" and previous != "in_stock":
                trigger = "restock"
            elif current == "in_stock_over_price" and previous not in ("in_stock", "in_stock_over_price"):
                trigger = "over_price"
            changes["monitor_availability"] = current
        elif monitor and result == "rate_limited":
            backoff = min(MAX_BACKOFF, max(config["interval"], (state["backoff"] or 30) * 2))
            changes.update(backoff=backoff, next_check=now + backoff)
        elif monitor and result == "blocked":
            changes.update(paused=True, next_check=now + config["interval"])
            trigger = "blocked"
        elif monitor and result == "error":
            failures = state["failures"] + 1
            changes.update(failures=failures, next_check=now + jitter(config["interval"]))
            if failures >= MAX_FAILURES:
                changes["paused"] = True
                trigger = "failing"
        self.store.update_state(watch["id"], changes)
        return trigger

    def _notify(self, kind: str) -> None:
        if self.notify:
            try:
                self.notify(kind, self.sound)
            except Exception:  # notifications must never stop monitoring
                LOGGER.exception("Web automation notification failed")

    def _handle(self, watch: dict, trigger: str, observation: dict) -> None:
        watch_id, config = watch["id"], watch["config"]
        if self.stop_event.is_set():
            return
        price = observation.get("price")
        price_text = f" for {price:.2f}" if isinstance(price, float) else ""
        if trigger == "over_price":
            self.store.event(watch_id, "over_price", f"In stock{price_text}, but above your maximum price. No action.")
            return
        if trigger in ("blocked", "failing"):
            summary = observation.get("error") or "Check failed."
            self.store.event(watch_id, trigger, f"Paused: {summary}")
            self._notify(trigger)
            return
        self.store.event(watch_id, "restock", f"In stock{price_text}.")
        if config["mode"] == "notify":
            self._notify("restock")
            return
        with self.store.write_lock:
            current = self.store.watch(watch_id)
            if current["config"] != config or current["state"]["paused"]:
                return
            if config["mode"] in TRANSACTION_MODES and self.store.transaction(watch_id):
                self.store.update_state(watch_id, {"paused": True, "status": "transaction_uncertain",
                                                  "last_error": "Previous transaction attempt retained. Check the shop before rearming."})
                return
            execution_id = secrets.token_hex(16)
            self.store.update_state(watch_id, {"paused": True, "status": "acting", "execution_id": execution_id})
            executing = self.store.watch(watch_id)
        cancelled = threading.Event()
        deadline = time.monotonic() + 230
        try:
            result = self.shop.submit(purchase_task(
                self.store, executing,
                lambda: cancelled.is_set() or self.stop_event.is_set() or time.monotonic() > deadline,
            ), wait=240)
        except AutomationError as error:
            result = {"ok": False, "steps": [], "reason": str(error)}
        finally:
            cancelled.set()
        transaction = self.store.transaction(watch_id)
        if result["ok"]:
            if "order_confirmed" in result["steps"] or "reservation_confirmed" in result["steps"]:
                kind = "order_confirmed" if config["mode"] == "order" else "reservation_confirmed"
                summary = "Order confirmed by the shop." if kind == "order_confirmed" else "Reservation confirmed by the shop."
            else:
                kind = "action_done"
                summary = "Added to cart" + (" and opened checkout" if "checkout_opened" in result["steps"] else "")
                summary += ". Finish the payment yourself in the shop window."
            if result["reason"]:
                summary += " " + result["reason"]
        else:
            kind = "transaction_uncertain" if transaction and transaction["status"] != "confirmed" else "action_failed"
            summary = ("Partly done: " if result["steps"] else "Action failed: ") + result["reason"]
            if kind == "transaction_uncertain":
                summary += " Outcome uncertain: check the shop. No automatic retry."
        with self.store.write_lock:
            if self.store.watch(watch_id)["state"].get("execution_id") == execution_id:
                self.store.update_state(watch_id, {"status": kind, "last_error": "" if result["ok"] else
                                                  summary if kind == "transaction_uncertain" else result["reason"]})
        self.store.event(watch_id, kind, summary)
        self._notify(kind)

    def _due(self) -> list[dict]:
        now = time.time()
        return [watch for watch in self.store.watches() if not watch["state"]["paused"] and watch["state"]["next_check"] <= now]

    def _sleep_seconds(self) -> float:
        upcoming = [watch["state"]["next_check"] for watch in self.store.watches() if not watch["state"]["paused"]]
        return 30.0 if not upcoming else max(1.0, min(30.0, min(upcoming) - time.time()))

    def _check(self, browser, watch: dict) -> None:
        with self.lock:
            self.active = watch["id"]
        try:
            observation = self._observe(browser, watch)
            trigger = self._record(watch, observation, monitor=True)
            if trigger and not self.stop_event.is_set():
                self._handle(watch, trigger, observation)
            with self.lock:
                self.errors.pop("store", None)
        except AutomationError:
            pass  # the watch was deleted during the check
        except (OSError, sqlite3.Error) as error:
            with self.lock:
                self.errors["store"] = short_error(error)
        finally:
            with self.lock:
                self.active = ""

    def _run(self) -> None:
        current = threading.current_thread()
        try:
            with sync_playwright() as playwright:
                browser = None
                try:
                    while not self.stop_event.is_set():
                        try:
                            due, sleep = self._due(), None
                        except (OSError, sqlite3.Error) as error:
                            with self.lock:
                                self.errors["store"] = short_error(error)
                            due, sleep = [], 30.0
                        if due and (browser is None or not browser.is_connected()):
                            browser = playwright.chromium.launch(headless=True)
                        for watch in due:
                            if self.stop_event.is_set():
                                break
                            self._check(browser, watch)
                        if sleep is None:
                            try:
                                sleep = self._sleep_seconds()
                            except (OSError, sqlite3.Error):
                                sleep = 30.0
                        self.wake_event.wait(sleep)
                        self.wake_event.clear()
                finally:
                    if browser is not None and browser.is_connected():
                        browser.close()
        except Exception as error:  # keep the failure visible in the UI instead of dying silently
            LOGGER.exception("Web monitor stopped")
            with self.lock:
                self.errors["monitor"] = short_error(error)
        finally:
            with self.lock:
                if self.thread is current:
                    self.thread = None
                self.active = ""
