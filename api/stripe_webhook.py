"""
Stripe Webhook Handler — TryOnYou V10.

Verifies the Stripe-Signature header and dispatches supported event types.
Requires env var: STRIPE_WEBHOOK_SECRET (whsec_…).
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

import requests
import stripe

WIX_PENDING_AMOUNT_EUR = 489.0
_SERVICE_WEBHOOK_ENV_KEYS = (
    "MAKE_SERVICE_SANITATION_WEBHOOK_URL",
    "MAKE_BUNKER_SERVICES_WEBHOOK_URL",
    "MAKE_WEBHOOK_URL",
)
_PROCESSED_SERVICE_EVENT_IDS: set[str] = set()


def handle_webhook(payload: bytes, sig_header: str) -> tuple[dict[str, Any], int]:
    """
    Verify the Stripe webhook signature and process the event.

    Args:
        payload: Raw request body bytes.
        sig_header: Value of the 'Stripe-Signature' HTTP header.

    Returns:
        A (response_dict, http_status_code) tuple.
    """
    secret = (os.getenv("STRIPE_WEBHOOK_SECRET") or "").strip()
    if not secret:
        return {"status": "error", "message": "webhook_secret_not_configured"}, 500

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, secret)
    except ValueError:
        return {"status": "error", "message": "invalid_payload"}, 400
    except stripe.error.SignatureVerificationError:
        return {"status": "error", "message": "invalid_signature"}, 400

    return _dispatch(event)


def _dispatch(event: stripe.Event) -> tuple[dict[str, Any], int]:
    """Route a verified Stripe event to the appropriate handler."""
    event_type: str = event.get("type", "")

    if event_type == "checkout.session.completed":
        return _on_checkout_session_completed(event["data"]["object"])
    if event_type == "payout.created":
        event_id = str(event.get("id", "")).strip()
        return _on_payout_created(event["data"]["object"], event_id)

    # Acknowledge unhandled event types without error
    return {"status": "ok", "event": event_type, "handled": False}, 200


def _on_checkout_session_completed(session: Any) -> tuple[dict[str, Any], int]:
    """Handle checkout.session.completed events."""
    session_id = session.get("id", "")
    customer_email = session.get("customer_details", {}).get("email", "")
    amount_total = session.get("amount_total")
    currency = session.get("currency", "")

    return {
        "status": "ok",
        "event": "checkout.session.completed",
        "handled": True,
        "session_id": session_id,
        "customer_email": customer_email,
        "amount_total": amount_total,
        "currency": currency,
    }, 200


def _resolve_service_webhook_url() -> str:
    for key in _SERVICE_WEBHOOK_ENV_KEYS:
        value = (os.getenv(key) or "").strip()
        if value:
            return value
    return ""


def _parse_optional_amount(raw: str) -> float | None:
    v = raw.strip().replace(",", ".")
    if not v:
        return None
    try:
        return float(v)
    except ValueError:
        return None


def _build_pending_services_payload() -> list[dict[str, Any]]:
    apple_amount = _parse_optional_amount(os.getenv("SERVICE_SANITATION_APPLE_AMOUNT_EUR", ""))
    apple_payment: dict[str, Any] = {
        "service": "Apple",
        "currency": "EUR",
        "status": "pending_payment",
        "amount_eur": apple_amount,
    }
    if apple_amount is None:
        apple_payment["amount_status"] = "manual_confirmation_required"

    return [
        {
            "service": "Wix",
            "currency": "EUR",
            "status": "pending_payment",
            "amount_eur": WIX_PENDING_AMOUNT_EUR,
        },
        apple_payment,
    ]


def _event_identifier(event_id: str, payout: Any) -> str:
    if event_id:
        return event_id
    if isinstance(payout, dict):
        return str(payout.get("id") or "").strip()
    return ""


def _on_payout_created(payout: Any, event_id: str) -> tuple[dict[str, Any], int]:
    payout_id = str((payout or {}).get("id") or "").strip() if isinstance(payout, dict) else ""
    payout_amount = (payout or {}).get("amount") if isinstance(payout, dict) else None
    payout_currency = str((payout or {}).get("currency") or "").strip() if isinstance(payout, dict) else ""
    dedupe_id = _event_identifier(event_id, payout)

    if dedupe_id and dedupe_id in _PROCESSED_SERVICE_EVENT_IDS:
        return {
            "status": "ok",
            "event": "payout.created",
            "handled": True,
            "triggered": False,
            "duplicate": True,
            "event_id": dedupe_id,
        }, 200

    webhook_url = _resolve_service_webhook_url()
    if not webhook_url:
        return {
            "status": "error",
            "event": "payout.created",
            "handled": True,
            "message": "service_sanitation_webhook_not_configured",
            "required_env": "MAKE_SERVICE_SANITATION_WEBHOOK_URL or MAKE_WEBHOOK_URL",
        }, 502

    services = _build_pending_services_payload()
    payload = {
        "event": "service_sanitation.payout.created",
        "phase": "Fase de Saneamiento de Servicios",
        "stripe_event": "payout.created",
        "stripe_event_id": dedupe_id,
        "triggered_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "payout": {
            "id": payout_id,
            "amount": payout_amount,
            "currency": payout_currency,
        },
        "pending_service_payments": services,
    }

    try:
        response = requests.post(webhook_url, json=payload, timeout=25)
        if not response.ok:
            return {
                "status": "error",
                "event": "payout.created",
                "handled": True,
                "message": f"service_sanitation_http_{response.status_code}",
            }, 502
    except (requests.RequestException, OSError) as e:
        return {
            "status": "error",
            "event": "payout.created",
            "handled": True,
            "message": str(e),
        }, 502

    if dedupe_id:
        _PROCESSED_SERVICE_EVENT_IDS.add(dedupe_id)

    return {
        "status": "ok",
        "event": "payout.created",
        "handled": True,
        "triggered": True,
        "event_id": dedupe_id,
        "payments": services,
    }, 200


def _reset_runtime_state_for_tests() -> None:
    _PROCESSED_SERVICE_EVENT_IDS.clear()
