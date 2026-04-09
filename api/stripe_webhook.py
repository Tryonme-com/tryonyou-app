"""
Stripe Webhook Handler — TryOnYou V10.

Verifies the Stripe-Signature header and dispatches supported event types.
Requires env var: STRIPE_WEBHOOK_SECRET (whsec_…).
"""

from __future__ import annotations

import os
from typing import Any

import stripe


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
