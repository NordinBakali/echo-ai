import copy
from unittest.mock import Mock

import pytest

import echo_web_automation as web


def watch_data(**changes):
    data = {
        "name": "Console", "url": "https://shop.example/p/1", "mode": "notify", "interval": 300,
        "in_stock_text": [], "out_of_stock_text": [], "max_price": None,
        "elements": {"add_to_cart": {"selector": "#buy", "text": "In winkelwagen"}},
        "checkout_url": "", "authorized": False,
    }
    data.update(changes)
    return data


@pytest.fixture()
def service(tmp_path):
    automation = web.WebAutomation(web.Store(tmp_path / "web.sqlite3"), Mock(), shop=Mock())
    yield automation
    automation.stop()


def ok(availability, price=None):
    return {"result": "ok", "status": 200, "availability": availability, "price": price, "signals": {}, "elements": {}, "notes": []}


@pytest.mark.parametrize(("text", "expected"), [
    ("€ 1.299,00", 1299.0), ("19,99", 19.99), ("49,-", 49.0), ("$1,299.99", 1299.99),
    ("1,5", 1.5), ("1.299", 1299.0), ("Prijs: 12 345,50", 12345.5), ("gratis", None), (True, None),
])
def test_parse_price_handles_dutch_and_english_formats(text, expected):
    assert web.parse_price(text) == expected


def test_structured_price_uses_schema_dot_decimal():
    assert web.structured_price("1.299") == 1.299
    assert web.structured_price("1299.00") == 1299.0
    assert web.jsonld_signal(['{"offers": {"availability": "https://schema.org/InStock", "price": "24.95"}}']) == ("in", 24.95, "")
    vote, price, note = web.jsonld_signal(['{"offers": [{"availability": "InStock"}, {"availability": "OutOfStock"}]}'])
    assert vote is None and price is None and "variants" in note


@pytest.mark.parametrize("item", [
    {"text": "Bestelling plaatsen"}, {"text": "Betalen"}, {"id": "placeOrderButton"}, {"text": "Koop nu"},
    {"id": "place-order"}, {"aria": "Pay with iDEAL"}, {"testid": "buy_now"}, {"value": "Bevestig bestelling"},
])
def test_final_purchase_elements_are_never_safe(item):
    assert web.is_final_purchase(item)
    assert not web.is_safe("add_to_cart", item)
    assert not web.is_safe("checkout", item)


@pytest.mark.parametrize("text", ["In winkelwagen", "Afrekenen", "Toevoegen aan winkelwagen", "Add to cart"])
def test_cart_navigation_is_allowed(text):
    assert not web.is_final_purchase({"text": text})


def test_negative_keywords_block_wishlist_buttons():
    assert not web.is_safe("add_to_cart", {"text": "Zet op verlanglijst"})
    assert web.is_safe("stock_indicator", {"text": "Betalen"})


@pytest.mark.parametrize(("text", "expected"), [
    ("Niet op voorraad", "out"), ("Op voorraad, morgen in huis", "in"), ("Not in stock", "out"),
    ("Dit product is niet meer op voorraad leverbaar", "out"), ("Geen voorraadinformatie", None), ("", None),
])
def test_classify_text_respects_negation(text, expected):
    assert web.classify_text(text, web.DEFAULT_IN, web.DEFAULT_OUT) == expected


@pytest.mark.parametrize(("signals", "expected"), [
    ({"jsonld": "in", "indicator": "out"}, "conflict"),
    ({"jsonld": "in", "button": "out"}, "conflict"),
    ({"indicator": "out", "button": "in"}, "out_of_stock"),
    ({"button": "in", "body": "out"}, "in_stock"),
    ({"body": "out"}, "out_of_stock"),
    ({}, "unknown"),
])
def test_decide_availability_prefers_strong_signals(signals, expected):
    assert web.decide_availability(signals) == expected


def test_renamed_button_heals_but_header_cart_link_does_not():
    fingerprint = {"text": "In winkelwagen", "id": "add-to-cart", "classes": ["btn", "btn-buy"], "tag": "button", "near": "€ 499,00"}
    renamed = {"text": "Toevoegen aan winkelwagen", "id": "product-buy", "classes": ["button", "primary"], "tag": "button",
               "near": "€ 499,00", "visible": True, "enabled": True}
    header = {"text": "Winkelwagen", "href": "/cart", "tag": "a", "chrome": True, "visible": True, "enabled": True}
    wishlist = {"text": "Op verlanglijst", "tag": "button", "visible": True, "enabled": True}
    ranked = web.rank([fingerprint], [header, renamed, wishlist], "add_to_cart", healing=True)
    assert ranked[0][1] is renamed and ranked[0][0] >= web.HEAL_THRESHOLD
    assert ranked[0][0] - ranked[1][0] >= web.HEAL_MARGIN
    assert all(item is not wishlist for _score, item in ranked)
    assert web.score_candidate([fingerprint], header, "add_to_cart") < web.HEAL_THRESHOLD


@pytest.mark.parametrize(("changes", "message"), [
    ({"mode": "cart"}, "authorization"),
    ({"mode": "cart", "authorized": True, "elements": {}}, "add-to-cart"),
    ({"mode": "checkout", "authorized": True}, "checkout URL"),
    ({"elements": {"add_to_cart": {"selector": "", "text": "Bestelling plaatsen"}}}, "never clicks"),
    ({"interval": 10}, "interval"),
    ({"interval": True}, "interval"),
    ({"max_price": -1}, "maximum price"),
    ({"url": "javascript:alert(1)"}, "http"),
    ({"url": "https://user:pass@shop.example/"}, "credentials"),
    ({"elements": {"buy": {"selector": "#x", "text": ""}}}, "elements"),
    ({"in_stock_text": "op voorraad"}, "phrases"),
])
def test_validate_watch_rejects_unsafe_configs(changes, message):
    with pytest.raises(web.AutomationError, match=message):
        web.validate_watch(watch_data(**changes))


def test_validate_watch_normalizes_and_requires_exact_keys():
    config = web.validate_watch(watch_data(
        mode="checkout", authorized=True, checkout_url="https://shop.example/cart", max_price=500,
        in_stock_text=["  Direct  LEVERBAAR "], elements={
            "add_to_cart": {"selector": " #buy ", "text": ""}, "price": {"selector": "", "text": ""},
        },
    ))
    assert config["elements"] == {"add_to_cart": {"selector": "#buy", "text": ""}}
    assert config["in_stock_text"] == ["direct leverbaar"] and config["max_price"] == 500.0
    with pytest.raises(web.AutomationError):
        web.validate_watch({**watch_data(), "extra": 1})


def test_store_versions_rollback_and_reconfigure(service):
    watch_id = service.save_watch("", watch_data())
    store = service.store
    assert store.active_selector(watch_id, "add_to_cart")["fingerprint"] == {"text": "In winkelwagen"}
    store.add_version(watch_id, "add_to_cart", "#new-buy", {"text": "In winkelwagen"}, "healed", 0.71)
    assert service.rollback(watch_id, "add_to_cart", 1) == 3
    active = store.active_selector(watch_id, "add_to_cart")
    assert (active["selector"], active["reason"]) == ("#buy", "rollback:1")
    service.save_watch(watch_id, watch_data(name="Renamed"))
    assert store.active_selector(watch_id, "add_to_cart")["version"] == 3
    with pytest.raises(web.AutomationError):
        service.rollback(watch_id, "add_to_cart", 99)
    snapshot = service.snapshot()
    assert [item["version"] for item in snapshot["watches"][0]["selectors"]["add_to_cart"]] == [3, 2, 1]
    assert [event["kind"] for event in snapshot["events"]][:2] == ["saved", "rollback"]


def test_record_fires_restock_only_on_transition(service):
    watch_id = service.save_watch("", watch_data(max_price=100))
    record = lambda observation: service._record(service.store.watch(watch_id), observation, monitor=True)
    assert record(ok("in_stock", 90.0)) == "restock"
    assert record(ok("in_stock", 90.0)) is None
    assert record(ok("unknown")) is None
    assert record(ok("out_of_stock")) is None
    assert record(ok("in_stock", 150.0)) == "over_price"
    assert record(ok("in_stock", 150.0)) is None
    assert record(ok("in_stock", 99.0)) == "restock"
    state = service.store.watch(watch_id)["state"]
    assert state["monitor_availability"] == "in_stock" and state["price"] == 99.0


def test_record_pauses_on_bot_checks_and_repeated_errors(service):
    watch_id = service.save_watch("", watch_data())
    record = lambda observation: service._record(service.store.watch(watch_id), observation, monitor=True)
    assert record({"result": "rate_limited", "status": 429, "error": "HTTP 429"}) is None
    assert service.store.watch(watch_id)["state"]["backoff"] == 300
    assert record({"result": "rate_limited", "status": 429, "error": "HTTP 429"}) is None
    assert service.store.watch(watch_id)["state"]["backoff"] == 600
    assert record({"result": "blocked", "status": 403, "error": "CAPTCHA"}) == "blocked"
    assert service.store.watch(watch_id)["state"]["paused"]
    service.set_paused(watch_id, False)
    triggers = [record({"result": "error", "status": 0, "error": "timeout"}) for _ in range(web.MAX_FAILURES)]
    assert triggers == [None] * (web.MAX_FAILURES - 1) + ["failing"]
    assert service.store.watch(watch_id)["state"]["paused"]


def test_manual_check_does_not_arm_triggers(service):
    watch_id = service.save_watch("", watch_data())
    assert service._record(service.store.watch(watch_id), ok("in_stock"), monitor=False) is None
    state = service.store.watch(watch_id)["state"]
    assert state["availability"] == "in_stock" and state["monitor_availability"] == ""
    assert service._record(service.store.watch(watch_id), ok("in_stock"), monitor=True) == "restock"


def test_resume_without_rearm_needs_a_new_restock(service):
    watch_id = service.save_watch("", watch_data())
    service.store.update_state(watch_id, {"availability": "in_stock", "monitor_availability": "in_stock", "paused": True})
    service.handle("resume", {"id": watch_id, "rearm": False})
    assert service._record(service.store.watch(watch_id), ok("in_stock"), monitor=True) is None
    service.handle("pause", {"id": watch_id})
    service.handle("resume", {"id": watch_id, "rearm": True})
    assert service._record(service.store.watch(watch_id), ok("in_stock"), monitor=True) == "restock"


def test_handle_runs_cart_action_once_and_keeps_watch_paused(service):
    watch_id = service.save_watch("", watch_data(mode="cart", authorized=True))
    service.shop.submit.return_value = {"ok": True, "steps": ["added_to_cart"], "reason": ""}
    service._handle(service.store.watch(watch_id), "restock", ok("in_stock", 10.0))
    service.shop.submit.assert_called_once()
    assert service.shop.submit.call_args.kwargs == {"wait": 240}
    state = service.store.watch(watch_id)["state"]
    assert state["paused"] and state["status"] == "action_done"
    service.notify.assert_called_with("action_done", False)
    service.shop.submit.side_effect = web.AutomationError("The shop window is busy.")
    service.handle("resume", {"id": watch_id, "rearm": True})
    service._handle(service.store.watch(watch_id), "restock", ok("in_stock"))
    assert service.store.watch(watch_id)["state"]["last_error"] == "The shop window is busy."
    assert service.store.events(1)[0]["kind"] == "action_failed"


def test_notify_mode_only_notifies(service):
    watch_id = service.save_watch("", watch_data())
    service._handle(service.store.watch(watch_id), "restock", ok("in_stock"))
    service.shop.submit.assert_not_called()
    service.notify.assert_called_once_with("restock", False)
    assert not service.store.watch(watch_id)["state"]["paused"]


def transaction_data(**changes):
    data = watch_data(
        mode="order", authorized=True, max_price=500, checkout_url="https://shop.example/checkout",
        transaction={
            "authorized": True, "currency": "EUR",
            "button": {"selector": "#order", "text": "Bestelling plaatsen"},
            "confirmation": {"selector": "#confirmed", "text": "Bestelling bevestigd"},
            "item": {"selector": ".item", "text": "Console variant A"},
            "quantity": {"selector": ".quantity", "text": "1"},
            "total": {"selector": "#total", "text": ""},
        },
    )
    data.update(changes)
    return data


@pytest.mark.parametrize("change", ["consent", "budget", "currency", "missing", "quantity", "cross_origin", "final_text"])
def test_final_transactions_fail_closed_without_complete_authorization(change):
    data = transaction_data()
    if change == "consent":
        data["transaction"]["authorized"] = False
    elif change == "budget":
        data["max_price"] = None
    elif change == "currency":
        data["transaction"]["currency"] = []
    elif change == "missing":
        data["transaction"]["confirmation"]["selector"] = ""
    elif change == "quantity":
        data["transaction"]["quantity"]["text"] = "2"
    elif change == "cross_origin":
        data["checkout_url"] = "https://other.example/checkout"
    else:
        data["transaction"]["button"]["text"] = "In winkelwagen"
    with pytest.raises(web.AutomationError):
        web.validate_watch(data)


def test_order_and_reservation_are_distinct_from_cart():
    assert web.validate_watch(transaction_data())["transaction"]["authorized"] is True
    data = transaction_data(mode="reserve", elements={})
    data["transaction"]["button"]["text"] = "Reservering bevestigen"
    assert web.validate_watch(data)["mode"] == "reserve"
    assert not web.is_safe("add_to_cart", {"text": "Reserveer"})
    assert not web.is_safe("checkout", {"text": "Confirm reservation"})


@pytest.mark.parametrize(("text", "currency", "expected"), [("€ 499,00", "EUR", "499.00"), ("EUR 1.299,99", "EUR", "1299.99"), ("US$ 499.00", "USD", "499.00"), ("GBP 0.00", "GBP", "0.00")])
def test_final_total_includes_currency(text, currency, expected):
    assert str(web.transaction_total(text, currency)) == expected


@pytest.mark.parametrize("text", ["$ 499.00", "USD 499.00", "€ -5", "€ 499 plus € 10 shipping", "499.00", "€ NaN", "€ 1 2", "€ 1.2345"])
def test_unverifiable_final_totals_are_rejected(text):
    with pytest.raises(web.AutomationError):
        web.transaction_total(text, "EUR")


def test_transaction_claim_survives_reload_edit_and_requires_explicit_rearm(service):
    watch_id = service.save_watch("", transaction_data())
    watch = service.store.watch(watch_id)
    attempt = service.store.claim_transaction(watch)
    assert web.Store(service.store.path).transaction(watch_id)["status"] == "uncertain"
    changed = copy.deepcopy(watch["config"])
    changed["name"] = "Renamed"
    service.save_watch(watch_id, changed)
    with pytest.raises(web.AutomationError):
        service.store.claim_transaction(service.store.watch(watch_id))
    with pytest.raises(web.AutomationError):
        service.set_paused(watch_id, False)
    service.store.confirm_transaction(watch_id, attempt, "Confirmed")
    assert service.snapshot()["watches"][0]["transaction"]["status"] == "confirmed"
    service.set_paused(watch_id, False, rearm=True)
    assert service.store.transaction(watch_id) is None


def test_cancelled_and_stale_observations_do_not_schedule_actions(service):
    watch_id = service.save_watch("", transaction_data())
    watch = service.store.watch(watch_id)
    service.stop_event.set()
    service._handle(watch, "restock", ok("in_stock", 499.0))
    service.shop.submit.assert_not_called()
    service.stop_event.clear()
    service.save_watch(watch_id, transaction_data(name="Changed authorization"))
    service._handle(watch, "restock", ok("in_stock", 499.0))
    service.shop.submit.assert_not_called()
    service.notify.assert_not_called()


@pytest.mark.parametrize(("action", "data"), [
    ("save", {"watch": watch_data()}), ("delete", {"id": 1}), ("resume", {"id": "x", "rearm": "yes"}),
    ("start", {"authorized": False, "sound": False}), ("start", {"authorized": True}), ("unknown", {}),
    ("stop", []), ("rollback", {"id": "x", "role": "evil", "version": 1}),
])
def test_handle_rejects_malformed_requests(service, action, data):
    with pytest.raises(web.AutomationError):
        service.handle(action, data)
    assert not service.snapshot()["running"]


def test_shop_open_requires_valid_url(service):
    with pytest.raises(web.AutomationError):
        service.handle("shop_open", {"url": "file:///C:/Windows"})
    service.shop.submit.assert_not_called()
