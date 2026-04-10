"""
Stripe Webhook Handler — TryOnYou V10.

Verifies the Stripe-Signature header and dispatches supported event types.
Requires env var: STRIPE_WEBHOOK_SECRET (whsec_…).
"""

from __future__ import annotations

import logging
import os
from typing import Any

import stripe

LOGGER = logging.getLogger(__name__)


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
    if event_type == "invoice.paid":
        return _on_invoice_paid(event["data"]["object"])
    if event_type == "payment_intent.succeeded":
        return _on_payment_intent_succeeded(event["data"]["object"])

    # Acknowledge unhandled event types without error
    return {"status": "ok", "event": event_type, "handled": False}, 200


def _log_invoice_succeeded(
    *,
    source_event: str,
    invoice_id: str,
    customer_email: str,
    amount_total: Any,
    currency: str,
) -> None:
    """
    Emit an explicit transition log every time billing reaches SUCCEEDED.

    This keeps log consumers informed of successful billing transitions.
    """
    LOGGER.info(
        "invoice_status_transition status=SUCCEEDED source_event=%s invoice_id=%s customer_email=%s amount_total=%s currency=%s",
        source_event,
        invoice_id,
        customer_email,
        amount_total,
        currency,
    )


def _on_checkout_session_completed(session: Any) -> tuple[dict[str, Any], int]:
    """Handle checkout.session.completed events."""
    session_id = session.get("id", "")
    invoice_id = session.get("invoice") or session_id
    customer_email = session.get("customer_details", {}).get("email", "")
    amount_total = session.get("amount_total")
    currency = session.get("currency", "")
    invoice_status = "SUCCEEDED"
    _log_invoice_succeeded(
        source_event="checkout.session.completed",
        invoice_id=invoice_id,
        customer_email=customer_email,
        amount_total=amount_total,
        currency=currency,
    )

    return {
        "status": "ok",
        "event": "checkout.session.completed",
        "handled": True,
        "session_id": session_id,
        "invoice_id": invoice_id,
        "customer_email": customer_email,
        "amount_total": amount_total,
        "currency": currency,
        "invoice_status": invoice_status,
    }, 200


def _on_invoice_paid(invoice: Any) -> tuple[dict[str, Any], int]:
    """Handle invoice.paid events."""
    invoice_id = invoice.get("id", "")
    customer_email = invoice.get("customer_email", "")
    amount_total = invoice.get("amount_paid")
    currency = invoice.get("currency", "")
    invoice_status = "SUCCEEDED"
    _log_invoice_succeeded(
        source_event="invoice.paid",
        invoice_id=invoice_id,
        customer_email=customer_email,
        amount_total=amount_total,
        currency=currency,
    )

    return {
        "status": "ok",
        "event": "invoice.paid",
        "handled": True,
        "invoice_id": invoice_id,
        "customer_email": customer_email,
        "amount_total": amount_total,
        "currency": currency,
        "invoice_status": invoice_status,
    }, 200


def _on_payment_intent_succeeded(payment_intent: Any) -> tuple[dict[str, Any], int]:
    """Handle payment_intent.succeeded events."""
    invoice_id = payment_intent.get("invoice") or payment_intent.get("id", "")
    customer_email = payment_intent.get("receipt_email", "")
    amount_total = payment_intent.get("amount_received")
    currency = payment_intent.get("currency", "")
    invoice_status = "SUCCEEDED"
    _log_invoice_succeeded(
        source_event="payment_intent.succeeded",
        invoice_id=invoice_id,
        customer_email=customer_email,
        amount_total=amount_total,
        currency=currency,
    )

    return {
        "status": "ok",
        "event": "payment_intent.succeeded",
        "handled": True,
        "invoice_id": invoice_id,
        "customer_email": customer_email,
        "amount_total": amount_total,
        "currency": currency,
        "invoice_status": invoice_status,
    }, 200
