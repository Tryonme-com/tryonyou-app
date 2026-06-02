"""
Business-logic handlers — one function per Stripe event type.

Called exclusively by the execution engine (Jules worker).
NEVER called from the webhook route.

Each handler receives:
  event   — the full Stripe event dict
  context — Redis metadata for this event (retries, timestamps, etc.)

Returns a dict with at least {"ok": bool, "action": str}.
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def handle_payment_intent_succeeded(
    event: dict[str, Any], context: dict[str, Any]
) -> dict[str, Any]:
    obj = event["data"]["object"]
    logger.info(
        "[handler] payment_intent.succeeded id=%s amount=%s currency=%s",
        obj.get("id"), obj.get("amount"), obj.get("currency"),
    )
    # TODO: mark order paid in DB, send confirmation email, trigger fulfillment
    return {"ok": True, "action": "mark_order_paid"}


def handle_payment_intent_failed(
    event: dict[str, Any], context: dict[str, Any]
) -> dict[str, Any]:
    obj = event["data"]["object"]
    error = obj.get("last_payment_error", {}).get("message", "unknown")
    logger.warning(
        "[handler] payment_intent.payment_failed id=%s error=%.200s",
        obj.get("id"), error,
    )
    # TODO: update order status, notify customer, log decline reason
    return {"ok": True, "action": "mark_payment_failed"}


def handle_checkout_session_completed(
    event: dict[str, Any], context: dict[str, Any]
) -> dict[str, Any]:
    obj = event["data"]["object"]
    logger.info(
        "[handler] checkout.session.completed id=%s customer=%s payment_status=%s",
        obj.get("id"), obj.get("customer"), obj.get("payment_status"),
    )
    # TODO: provision access, send receipt, trigger onboarding
    return {"ok": True, "action": "activate_subscription"}


def handle_charge_refunded(
    event: dict[str, Any], context: dict[str, Any]
) -> dict[str, Any]:
    obj = event["data"]["object"]
    logger.info(
        "[handler] charge.refunded id=%s amount_refunded=%s",
        obj.get("id"), obj.get("amount_refunded"),
    )
    # TODO: update order status, notify customer, alert support if needed
    return {"ok": True, "action": "handle_refund"}


def handle_unhandled_event(
    event: dict[str, Any], context: dict[str, Any]
) -> dict[str, Any]:
    logger.info("[handler] unhandled event_type=%s", event.get("type"))
    return {"ok": True, "action": "ignore_event"}
