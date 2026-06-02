from __future__ import annotations

from typing import Any


def _extract_object(event: dict[str, Any]) -> dict[str, Any]:
    return event.get("data", {}).get("object", {})


def handle_payment_intent_succeeded(event: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    obj = _extract_object(event)
    return {
        "result": "order_paid",
        "payment_intent_id": obj.get("id"),
        "amount_received": obj.get("amount_received"),
        "currency": obj.get("currency"),
        "trace_id": context.get("trace_id"),
    }


def handle_payment_intent_failed(event: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    obj = _extract_object(event)
    return {
        "result": "payment_failed",
        "payment_intent_id": obj.get("id"),
        "last_payment_error": obj.get("last_payment_error", {}).get("message"),
        "trace_id": context.get("trace_id"),
    }


def handle_checkout_session_completed(event: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    obj = _extract_object(event)
    return {
        "result": "subscription_activated",
        "checkout_session_id": obj.get("id"),
        "customer": obj.get("customer"),
        "subscription": obj.get("subscription"),
        "trace_id": context.get("trace_id"),
    }


def handle_charge_refunded(event: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    obj = _extract_object(event)
    return {
        "result": "refund_handled",
        "charge_id": obj.get("id"),
        "amount_refunded": obj.get("amount_refunded"),
        "trace_id": context.get("trace_id"),
    }
