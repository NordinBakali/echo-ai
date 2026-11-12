import copy
import hashlib
import json
import threading
import time
from unittest.mock import Mock

import pytest
from flask import Flask, request
from werkzeug.serving import make_server

import echo_osint as osint
import echo_web_automation as web
import server

PRODUCT = """<!doctype html><html lang="nl"><head><meta charset="utf-8"><title>Echo testconsole</title>
<script type="application/ld+json">{jsonld}</script></head><body>
<header><nav><a href="/cart" class="nav-cart">Winkelwagen (<span id="cart-count">0</span>)</a></nav></header>
<main><h1>Echo testconsole</h1>
<p id="stock-label" class="stock-label">{stock_text}</p>
<span id="price" class="price">&euro; 499,00</span>
<div class="actions">{button}
<button id="wishlist" type="button">Op verlanglijst</button>
<button id="buy-now" type="button">Koop nu</button></div>
<a id="checkout-link" href="/checkout" style="display:none">Afrekenen</a>
</main>
<script>
const buy = document.querySelector('[data-cart]');
if (buy) buy.addEventListener('click', async () => {{
  await fetch('/api/cart', {{method: 'POST'}});
  document.getElementById('cart-count').textContent = '1';
  document.getElementById('checkout-link').style.display = 'inline';
}});
document.getElementById('buy-now').addEventListener('click', () => fetch('/api/order', {{method: 'POST'}}));
</script></body></html>"""
BUTTONS = {
    1: '<button id="add-to-cart" class="btn btn-buy" type="button" data-cart>In winkelwagen</button>',
    2: '<button id="product-cta-v2" class="button primary" type="button" data-cart>Toevoegen aan winkelwagen</button>',
}
CHECKOUT = """<!doctype html><html lang="nl"><head><meta charset="utf-8"><title>Kassa</title></head><body>
<h1>Afrekenen</h1><form id="pay" onsubmit="event.preventDefault(); fetch('/api/order', {method: 'POST'})">
<label>Kaartnummer <input name="cardnumber" autocomplete="cc-number"></label>
<button id="place-order">Bestelling plaatsen</button></form></body></html>"""


def serve(app):
    http = make_server("127.0.0.1", 0, app, threaded=True)
    worker = threading.Thread(target=http.serve_forever, daemon=True)
    worker.start()
    return http, worker, f"http://127.0.0.1:{http.server_port}"


@pytest.fixture()
def shop():
    state = {"stock": False, "variant": 1, "cart_posts": 0, "order_posts": 0, "reservation_posts": 0,
             "total": "EUR 499.00", "quantity": "1", "item": "Echo testconsole", "extra_item": False,
             "reject": False, "show_confirmation": True, "preconfirmed": False, "renamed_final": False}
    app = Flask("echo_fixture_shop")

    @app.get("/product")
    def product():
        availability = "InStock" if state["stock"] else "OutOfStock"
        jsonld = json.dumps({"@context": "https://schema.org", "@type": "Product", "name": "Echo testconsole", "offers": {
            "@type": "Offer", "price": "499.00", "priceCurrency": "EUR", "availability": f"https://schema.org/{availability}"}})
        button = BUTTONS[state["variant"]] if state["stock"] else '<button id="notify-me" type="button">Mail me bij voorraad</button>'
        return PRODUCT.format(jsonld=jsonld, stock_text="Op voorraad" if state["stock"] else "Uitverkocht", button=button)

    @app.get("/cart")
    def cart():
        return '<!doctype html><title>Winkelwagen</title><a href="/checkout">Afrekenen</a>'

    @app.get("/checkout")
    def checkout():
        return CHECKOUT

    @app.get("/transaction")
    def transaction():
        mode = request.args.get("mode", "order")
        endpoint = "/api/reservation" if mode == "reserve" else "/api/order"
        button_text = "Reservering bevestigen" if mode == "reserve" else "Bestelling plaatsen"
        success_text = "Reservering bevestigd" if mode == "reserve" else "Bestelling bevestigd"
        more = '<p class="summary-item">Other product</p>' if state["extra_item"] else ""
        button_id = "renamed-final" if state["renamed_final"] else "final-button"
        return f"""<!doctype html><meta charset="utf-8"><title>Final summary</title>
        <p class="summary-item">{state['item']}</p>{more}
        <input class="summary-quantity" value="{state['quantity']}">
        <p id="final-total">{state['total']}</p>
        <button id="{button_id}" onclick="submitTransaction()">{button_text}</button>
        <p id="confirmation" {'hidden' if not state['preconfirmed'] else ''}>{success_text}</p>
        <script>async function submitTransaction() {{
            const response = await fetch('{endpoint}', {{method:'POST'}});
            if (response.ok && {str(state['show_confirmation']).lower()})
                document.getElementById('confirmation').hidden=false;
        }}</script>"""

    @app.post("/api/cart")
    def add():
        state["cart_posts"] += 1
        return {"ok": True}

    @app.post("/api/order")
    def order():
        if state["reject"]:
            return {"ok": False}, 409
        state["order_posts"] += 1
        return {"ok": True, "order_id": state["order_posts"]}

    @app.post("/api/reservation")
    def reservation():
        if state["reject"]:
            return {"ok": False}, 409
        state["reservation_posts"] += 1
        return {"ok": True, "reservation_id": state["reservation_posts"]}

    http, worker, url = serve(app)
    try:
        yield url, state
    finally:
        http.shutdown()
        worker.join(5)


def wait_for(predicate, timeout=60.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.2)
    raise AssertionError("Timed out waiting for condition")


def watch_data(url, **changes):
    data = {
        "name": "Testconsole", "url": url + "/product", "mode": "notify", "interval": 60,
        "in_stock_text": [], "out_of_stock_text": [], "max_price": None,
        "elements": {
            "stock_indicator": {"selector": "#stock-label", "text": ""}, "price": {"selector": "#price", "text": ""},
            "add_to_cart": {"selector": "#add-to-cart", "text": "In winkelwagen"},
        },
        "checkout_url": "", "authorized": False,
    }
    data.update(changes)
    return data


def transaction_watch(url, mode="order"):
    data = watch_data(url, mode=mode, authorized=True, max_price=500, checkout_url=url + "/transaction?mode=" + mode)
    data["transaction"] = {
        "authorized": True, "currency": "EUR",
        "button": {"selector": "#final-button", "text": "Reservering bevestigen" if mode == "reserve" else "Bestelling plaatsen"},
        "confirmation": {"selector": "#confirmation", "text": "Reservering bevestigd" if mode == "reserve" else "Bestelling bevestigd"},
        "item": {"selector": ".summary-item", "text": "Echo testconsole"},
        "quantity": {"selector": ".summary-quantity", "text": "1"},
        "total": {"selector": "#final-total", "text": ""},
    }
    return data


def test_check_now_detects_restock_heals_renamed_button_and_rolls_back(tmp_path, shop):
    url, state = shop
    service = web.WebAutomation(web.Store(tmp_path / "web.sqlite3"), Mock(), shop=Mock())
    watch_id = service.save_watch("", watch_data(url))
    sold_out = service.check_now(watch_id)
    assert sold_out["availability"] == "out_of_stock" and sold_out["signals"]["jsonld"] == "out"
    assert sold_out["elements"]["add_to_cart"]["status"] == "missing"
    assert service.store.active_selector(watch_id, "add_to_cart")["version"] == 1

    state["stock"] = True
    available = service.check_now(watch_id)
    assert available["availability"] == "in_stock" and available["price"] == 499.0
    assert available["elements"]["add_to_cart"]["status"] == "ok"
    assert service.store.active_selector(watch_id, "add_to_cart")["fingerprint"]["id"] == "add-to-cart"

    state["variant"] = 2
    healed = service.check_now(watch_id)
    info = healed["elements"]["add_to_cart"]
    assert info["status"] == "healed" and info["selector"] == "#product-cta-v2" and info["score"] >= web.HEAL_THRESHOLD
    assert healed["availability"] == "in_stock"
    assert service.check_now(watch_id)["elements"]["add_to_cart"]["status"] == "ok"
    assert any(event["kind"] == "healed" for event in service.store.events())

    service.handle("rollback", {"id": watch_id, "role": "add_to_cart", "version": 1})
    state["variant"] = 1
    restored = service.check_now(watch_id)["elements"]["add_to_cart"]
    assert (restored["status"], restored["selector"], restored["version"]) == ("ok", "#add-to-cart", 3)
    assert state["cart_posts"] == 0 and state["order_posts"] == 0
    assert service.store.watch(watch_id)["state"]["monitor_availability"] == ""


@pytest.mark.parametrize("mode", ["cart", "checkout"])
def test_monitor_adds_to_cart_once_and_never_orders(tmp_path, shop, mode):
    url, state = shop
    notify = Mock()
    service = web.WebAutomation(web.Store(tmp_path / "web.sqlite3"), notify, shop=web.ShopSession(tmp_path / "profile", headless=True))
    elements = watch_data(url)["elements"]
    if mode == "checkout":
        elements["checkout"] = {"selector": "", "text": "Afrekenen"}
    watch_id = service.save_watch("", watch_data(url, mode=mode, authorized=True, max_price=500, elements=elements))
    try:
        service.handle("start", {"authorized": True, "sound": False})
        wait_for(lambda: service.store.watch(watch_id)["state"]["monitor_availability"] == "out_of_stock")
        assert state["cart_posts"] == 0
        state["stock"] = True
        service.store.update_state(watch_id, {"next_check": 0})
        service.wake_event.set()
        wait_for(lambda: service.store.watch(watch_id)["state"]["status"] in ("action_done", "action_failed"), timeout=120)
        watch = service.store.watch(watch_id)
        events = [event["summary"] for event in service.store.events()]
        assert watch["state"]["status"] == "action_done", events
        assert watch["state"]["paused"]
        assert state["cart_posts"] == 1 and state["order_posts"] == 0
        notify.assert_called_once_with("action_done", False)
        if mode == "checkout":
            assert "opened checkout" in events[0]
            assert any(row["role"] == "checkout" and row["reason"] == "discovered" for row in service.store.selectors())
        service.wake_event.set()
        time.sleep(2)
        assert state["cart_posts"] == 1 and state["order_posts"] == 0
    finally:
        service.stop()
        service.shop.close()
    assert not service.snapshot()["running"] and not service.shop.snapshot()["running"]


def test_monitor_skips_action_above_max_price(tmp_path, shop):
    url, state = shop
    state["stock"] = True
    shop_session = Mock()
    service = web.WebAutomation(web.Store(tmp_path / "web.sqlite3"), Mock(), shop=shop_session)
    watch_id = service.save_watch("", watch_data(url, mode="cart", authorized=True, max_price=450))
    try:
        service.handle("start", {"authorized": True, "sound": False})
        wait_for(lambda: service.store.watch(watch_id)["state"]["monitor_availability"] == "in_stock_over_price")
    finally:
        service.stop()
    shop_session.submit.assert_not_called()
    assert service.store.events(1)[0]["kind"] == "over_price"


@pytest.mark.parametrize("mode", ["order", "reserve"])
def test_restock_places_real_order_or_reservation_once(tmp_path, shop, mode):
    url, state = shop
    service = web.WebAutomation(web.Store(tmp_path / "transactions.sqlite3"), Mock(),
                                shop=web.ShopSession(tmp_path / "profile", headless=True))
    watch_id = service.save_watch("", transaction_watch(url, mode))
    try:
        service.handle("start", {"authorized": True, "sound": False})
        wait_for(lambda: service.store.watch(watch_id)["state"]["monitor_availability"] == "out_of_stock")
        assert state["order_posts"] == state["reservation_posts"] == 0
        state["stock"], state["variant"] = True, 2
        service.store.update_state(watch_id, {"next_check": 0})
        service.wake_event.set()
        wait_for(lambda: service.store.watch(watch_id)["state"]["status"] in (
            "order_confirmed", "reservation_confirmed", "action_failed", "transaction_uncertain"), timeout=90)
        watch = service.store.watch(watch_id)
        expected = "order_confirmed" if mode == "order" else "reservation_confirmed"
        assert watch["state"]["status"] == expected, service.store.events()
        assert state["order_posts"] == (1 if mode == "order" else 0)
        assert state["reservation_posts"] == (1 if mode == "reserve" else 0)
        assert state["cart_posts"] == (1 if mode == "order" else 0)
        assert web.Store(service.store.path).transaction(watch_id)["status"] == "confirmed"
        assert watch["state"]["paused"]
        service.stop()
        replacement = web.WebAutomation(web.Store(service.store.path), Mock(), shop=Mock())
        with pytest.raises(web.AutomationError):
            replacement.handle("resume", {"id": watch_id, "rearm": False})
        replacement._handle(replacement.store.watch(watch_id), "restock", {"price": 499.0})
        replacement.shop.submit.assert_not_called()
    finally:
        service.shutdown()


@pytest.mark.parametrize("change", [
    {"total": "EUR 510.00"}, {"total": "USD 499.00"}, {"quantity": "2"},
    {"item": "Different console"}, {"extra_item": True}, {"preconfirmed": True}, {"renamed_final": True},
])
def test_final_checks_prevent_unapproved_submission(tmp_path, shop, browser, change):
    url, state = shop
    state.update(change)
    store = web.Store(tmp_path / "web.sqlite3")
    store.save_watch("watch", web.validate_watch(transaction_watch(url)))
    page = browser.new_page()
    try:
        page.goto(url + "/transaction")
        with pytest.raises((web.AutomationError, web.PlaywrightError)):
            web.submit_transaction(page, store, store.watch("watch"), lambda: False)
        assert state["order_posts"] == state["reservation_posts"] == 0
        assert store.transaction("watch") is None
    finally:
        page.close()


@pytest.mark.parametrize("rejected", [False, True])
def test_unconfirmed_submission_is_persistently_unknown_not_retried(tmp_path, shop, browser, rejected):
    url, state = shop
    state["show_confirmation"] = False
    state["reject"] = rejected
    store = web.Store(tmp_path / "web.sqlite3")
    store.save_watch("watch", web.validate_watch(transaction_watch(url)))
    page = browser.new_page()
    try:
        page.goto(url + "/transaction")
        result = web.submit_transaction(page, store, store.watch("watch"), lambda: False)
        assert not result["ok"] and result["steps"] == ["submitted"]
        assert state["order_posts"] == (0 if rejected else 1)
        assert web.Store(store.path).transaction("watch")["status"] == "uncertain"
        with pytest.raises(web.AutomationError, match="already attempted"):
            web.submit_transaction(page, store, store.watch("watch"), lambda: False)
        assert state["order_posts"] == (0 if rejected else 1)
    finally:
        page.close()


def test_late_price_change_and_cancellation_block_dispatch(tmp_path, shop, browser, monkeypatch):
    url, state = shop
    store = web.Store(tmp_path / "web.sqlite3")
    store.save_watch("watch", web.validate_watch(transaction_watch(url)))
    page = browser.new_page()
    try:
        page.goto(url + "/transaction")
        with pytest.raises(web.AutomationError, match="cancelled"):
            web.submit_transaction(page, store, store.watch("watch"), lambda: True)
        evaluate = page.evaluate

        def mutate(script, arg=None):
            result = evaluate(script, arg)
            if script == web.TRANSACTION_JS and not arg["commit"]:
                evaluate("document.getElementById('final-total').textContent = 'EUR 900.00'")
            return result

        monkeypatch.setattr(page, "evaluate", mutate)
        with pytest.raises(web.PlaywrightError, match="details changed"):
            web.submit_transaction(page, store, store.watch("watch"), lambda: False)
        assert state["order_posts"] == 0 and store.transaction("watch")["status"] == "uncertain"
    finally:
        page.close()


class FakeSession:
    def __init__(self):
        sha = hashlib.sha1(b"password").hexdigest().upper()
        self.routes = {
            osint.HIBP_BASE + "/breaches": (200, [{"Name": "Example", "Title": "Example", "Domain": "example.com",
                                                   "BreachDate": "2023-05-01", "DataClasses": ["Email addresses"]}]),
            osint.PWNED_RANGE + sha[:5]: (200, f"{sha[5:]}:3861493\r\n{'0' * 35}:0"),
        }
        self.calls = []

    def get(self, url, headers=None, params=None, timeout=None):
        self.calls.append(url)
        status, data = self.routes.get(url, (404, None))
        return Mock(status_code=status, headers={}, json=Mock(return_value=data), text=data if isinstance(data, str) else "")


@pytest.fixture()
def browser():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as runtime:
        instance = runtime.chromium.launch(headless=True)
        try:
            yield instance
        finally:
            instance.close()


def test_page_creates_checks_and_runs_breach_tools(tmp_path, monkeypatch, shop, browser):
    from playwright.sync_api import expect
    shop_url, state = shop
    shop_session = Mock()
    shop_session.snapshot.return_value = {"open": False, "busy": False, "host": "", "error": "", "running": False}
    automation = web.WebAutomation(web.Store(tmp_path / "web.sqlite3"), Mock(), shop=shop_session)
    session = FakeSession()
    checker = osint.Osint(osint.Store(tmp_path / "osint.sqlite3"), Mock(), session=session)
    monkeypatch.delenv("HIBP_API_KEY", raising=False)
    monkeypatch.setattr(server, "WEBAUTOMATISERING", automation)
    monkeypatch.setattr(server, "OSINT", checker)
    monkeypatch.setattr(server, "ECHO_DEMO_MODE", False)
    monkeypatch.setattr(server, "ECHO_ENTERPRISE_MODE", False)
    monkeypatch.setattr(server, "instellingen", copy.deepcopy(server.instellingen))
    monkeypatch.setitem(server.instellingen, "taal", "Nederlands")
    http, worker, url = serve(server.app)
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.on("dialog", lambda dialog: dialog.accept())
    try:
        page.goto(url + "/webautomatisering")
        expect(page.locator("#web-status")).to_contain_text("Bewaking uit")
        expect(page.locator("#web-start")).to_be_disabled()
        assert page.request.post(url + "/api/webautomatisering/start", data={"authorized": True, "sound": False}).status == 403
        page.fill("#web-name", "Testconsole")
        page.fill("#web-url", shop_url + "/product")
        page.fill("#web-interval", "60")
        page.fill("#web-stock-selector", "#stock-label")
        page.fill("#web-price-selector", "#price")
        page.fill("#web-add-selector", "#add-to-cart")
        page.fill("#web-add-text", "In winkelwagen")
        page.locator("#web-save").click()
        expect(page.locator("#web-watches")).to_contain_text("Testconsole - Melden")
        expect(page.locator("#web-name")).to_have_value("")
        page.get_by_role("button", name="Nu controleren (geen actie)").click()
        expect(page.locator("#web-watches")).to_contain_text("Voorraad: Uitverkocht", timeout=60000)
        state["stock"] = True
        page.get_by_role("button", name="Nu controleren (geen actie)").click()
        expect(page.locator("#web-watches")).to_contain_text("Voorraad: Op voorraad | Prijs: 499.00", timeout=60000)
        page.locator("#web-watches summary").click()
        expect(page.locator("#web-watches details")).to_contain_text("configured")
        page.get_by_role("button", name="Bewerken").click()
        expect(page.locator("#web-name")).to_have_value("Testconsole")
        expect(page.locator("#web-add-selector")).to_have_value("#add-to-cart")
        page.locator("#web-new").click()

        page.fill("#web-name", "Approved reservation")
        page.fill("#web-url", shop_url + "/product")
        page.select_option("#web-mode", "reserve")
        expect(page.locator("#web-transaction-fields")).to_be_visible()
        page.fill("#web-max-price", "500")
        page.fill("#web-checkout-url", shop_url + "/transaction?mode=reserve")
        for role, prefix in {"button": "final", "item": "item", "quantity": "quantity", "total": "total", "confirmation": "confirmation"}.items():
            spec = transaction_watch(shop_url, "reserve")["transaction"][role]
            page.fill(f"#web-{prefix}-selector", spec["selector"])
            if role in ("button", "item", "confirmation"):
                page.fill(f"#web-{prefix}-text", spec["text"])
        page.locator("#web-authorized").check()
        expect(page.locator("#web-transaction-authorized")).not_to_be_checked()
        page.locator("#web-transaction-authorized").check()
        page.locator("#web-save").click()
        expect(page.locator("#web-watches")).to_contain_text("Approved reservation - Automatisch reserveren")
        reserved = next(w for w in automation.store.watches() if w["config"]["mode"] == "reserve")
        assert reserved["config"]["transaction"] == transaction_watch(shop_url, "reserve")["transaction"]
        automation.set_paused(reserved["id"], True)
        reservation_row = page.locator("#web-watches > li").filter(has_text="Approved reservation -")
        reservation_row.get_by_role("button", name="Bewerken", exact=True).click()
        expect(page.locator("#web-transaction-authorized")).not_to_be_checked()
        expect(page.locator("#web-item-text")).to_have_value("Echo testconsole")
        page.set_viewport_size({"width": 390, "height": 844})
        assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
        page.locator("#web-new").click()

        page.locator("#web-consent").check()
        page.locator("#web-start").click()
        expect(page.locator("#web-status")).to_contain_text("Bewaking aan")
        page.locator("#web-stop").click()
        expect(page.locator("#web-status")).to_contain_text("Bewaking uit", timeout=30000)

        page.select_option("#web-osint-kind", "domain")
        page.fill("#web-osint-value", "Example.com")
        page.locator("#web-osint-owned").check()
        page.locator("#web-osint-add").click()
        expect(page.locator("#web-identifiers")).to_contain_text("domain: example.com")
        page.get_by_role("button", name="Controleren", exact=True).click()
        expect(page.locator("#web-identifiers")).to_contain_text("1 lek(ken) van deze site", timeout=20000)
        expect(page.locator("#web-identifiers")).to_contain_text("Email addresses")
        page.fill("#web-password", "password")
        page.locator("#web-password-check").click()
        expect(page.locator("#web-password-result")).to_contain_text("keer voor in bekende lekken")
        expect(page.locator("#web-password")).to_have_value("")
        assert not any("password" in call.lower() and "range" not in call for call in session.calls)
        assert all(not call.endswith(hashlib.sha1(b"password").hexdigest().upper()) for call in session.calls)
        page.set_viewport_size({"width": 390, "height": 844})
        assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
        assert errors == []
        assert state["cart_posts"] == 0 and state["order_posts"] == 0
    finally:
        page.close()
        automation.stop()
        checker.shutdown()
        http.shutdown()
        worker.join(5)
