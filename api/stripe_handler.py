"""
Stripe Handler — TryOnYou V10.

Centralises Stripe Billing Meters and PaymentIntent/Invoice creation with
mandatory legal traceability (SIREN 943 610 196).

Fixes applied:
  - /v1/billing/meters: always sends ``customer`` and ``event_name``.
    When the caller supplies a null customer, falls back to the active
    mirror-session context.
  - /v1/prices: amounts are always expressed in the smallest currency unit
    (cents for EUR).  See ``src/constants/prices.ts`` for the canonical
    price catalogue.
  - Every PaymentIntent and Invoice carries ``siren`` in metadata for
    legal traceability (requested by Isabella @ Stripe Support).

Requires env vars:
  STRIPE_SECRET_KEY  — sk_live_… or sk_test_…
"""

from __future__ import annotations

import os
from typing import Any

import stripe

SIREN = "943 610 196"
PATENT = "PCT/EP2025/067317"

_REQUIRED_METER_FIELDS = ("customer", "event_name")


def _init_stripe() -> None:
    """Set the module-level Stripe API key from the environment."""
    sk = (os.getenv("STRIPE_SECRET_KEY") or "").strip()
    if not sk.startswith(("sk_live_", "sk_test_")):
        raise EnvironmentError(
            "STRIPE_SECRET_KEY must be set and start with sk_live_ or sk_test_"
        )
    stripe.api_key = sk


def _resolve_customer_from_session(session_context: dict[str, Any] | None) -> str | None:
    """Extract the Stripe customer ID from an active mirror-session context.

    The session context is the dict stored on the front-end under
    ``window.UserCheck`` or passed through the API payload.  It may
    contain any of the following keys (checked in priority order):

      - ``stripe_customer_id``
      - ``customer_id``
      - ``customer``
    """
    if not session_context:
        return None
    for key in ("stripe_customer_id", "customer_id", "customer"):
        value = session_context.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _legal_metadata(extra: dict[str, str] | None = None) -> dict[str, str]:
    """Return metadata dict that always includes SIREN + patent."""
    base: dict[str, str] = {
        "siren": SIREN,
        "patent": PATENT,
        "platform": "TryOnYou_V10",
    }
    if extra:
        base.update(extra)
    return base


def record_billing_meter_event(
    *,
    customer: str | None = None,
    event_name: str | None = None,
    payload: dict[str, Any] | None = None,
    session_context: dict[str, Any] | None = None,
    timestamp: int | None = None,
) -> dict[str, Any]:
    """Record a billing meter event on Stripe (/v1/billing/meter_events).

    Fixes the ``parameter_missing`` error by guaranteeing that both
    ``customer`` and ``event_name`` are present before calling the API.
    When ``customer`` is *None*, the function attempts to recover it
    from the active mirror-session context.

    Args:
        customer:        Stripe customer ID (cus_…). Falls back to session
                         context when *None*.
        event_name:      The meter event name registered in Stripe Billing.
        payload:         Extra payload fields forwarded to the meter event.
        session_context: Active mirror-session dict (UserCheck) used as
                         fallback for ``customer``.
        timestamp:       Optional Unix timestamp override.

    Returns:
        ``{'ok': True, 'meter_event': <event>}`` on success, or
        ``{'ok': False, 'error': '…'}`` on failure.
    """
    _init_stripe()

    resolved_customer = customer or _resolve_customer_from_session(session_context)
    if not resolved_customer:
        return {
            "ok": False,
            "error": "parameter_missing: customer is required. "
                     "Provide it directly or ensure the mirror session "
                     "contains stripe_customer_id / customer_id.",
        }

    if not event_name:
        return {
            "ok": False,
            "error": "parameter_missing: event_name is required for "
                     "/v1/billing/meter_events.",
        }

    try:
        params: dict[str, Any] = {
            "event_name": event_name,
            "payload": {
                "stripe_customer_id": resolved_customer,
                **(payload or {}),
            },
        }
        if timestamp is not None:
            params["timestamp"] = timestamp

        meter_event = stripe.billing.MeterEvent.create(**params)
        return {"ok": True, "meter_event": meter_event}
    except stripe.error.StripeError as exc:
        return {"ok": False, "error": str(exc.user_message or exc)}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def create_payment_intent(
    *,
    amount_cents: int,
    currency: str = "eur",
    session_id: str = "",
    customer: str | None = None,
    session_context: dict[str, Any] | None = None,
    extra_metadata: dict[str, str] | None = None,
    description: str = "",
) -> dict[str, Any]:
    """Create a Stripe PaymentIntent with mandatory SIREN metadata.

    Args:
        amount_cents:    Amount in the smallest currency unit (e.g. cents).
        currency:        ISO 4217, lowercase (default ``'eur'``).
        session_id:      Mirror session ID for traceability.
        customer:        Stripe customer ID; falls back to session_context.
        session_context: Active mirror session (UserCheck).
        extra_metadata:  Additional metadata key/value pairs.
        description:     Human-readable description.

    Returns:
        ``{'ok': True, 'client_secret': '…', 'payment_intent_id': '…'}``
        on success, or ``{'ok': False, 'error': '…'}``.
    """
    _init_stripe()

    resolved_customer = customer or _resolve_customer_from_session(session_context)

    meta = _legal_metadata(extra_metadata)
    if session_id:
        meta["session_id"] = session_id

    try:
        params: dict[str, Any] = {
            "amount": amount_cents,
            "currency": currency.lower(),
            "payment_method_types": ["card"],
            "metadata": meta,
        }
        if resolved_customer:
            params["customer"] = resolved_customer
        if description:
            params["description"] = description

        pi = stripe.PaymentIntent.create(**params)
        return {
            "ok": True,
            "client_secret": pi.client_secret,
            "payment_intent_id": pi.id,
        }
    except stripe.error.StripeError as exc:
        return {"ok": False, "error": str(exc.user_message or exc)}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def create_invoice(
    *,
    customer: str | None = None,
    session_context: dict[str, Any] | None = None,
    description: str = "",
    extra_metadata: dict[str, str] | None = None,
    auto_advance: bool = True,
) -> dict[str, Any]:
    """Create a Stripe Invoice with mandatory SIREN metadata.

    Args:
        customer:        Stripe customer ID (cus_…).  Falls back to
                         session_context when *None*.
        session_context: Active mirror-session dict used as fallback.
        description:     Invoice description.
        extra_metadata:  Additional metadata key/value pairs.
        auto_advance:    Whether Stripe should auto-finalise the invoice.

    Returns:
        ``{'ok': True, 'invoice_id': '…', 'invoice': <obj>}`` on success,
        or ``{'ok': False, 'error': '…'}``.
    """
    _init_stripe()

    resolved_customer = customer or _resolve_customer_from_session(session_context)
    if not resolved_customer:
        return {
            "ok": False,
            "error": "parameter_missing: customer is required to create "
                     "an invoice.  Provide it directly or via session_context.",
        }

    meta = _legal_metadata(extra_metadata)

    try:
        params: dict[str, Any] = {
            "customer": resolved_customer,
            "metadata": meta,
            "auto_advance": auto_advance,
        }
        if description:
            params["description"] = description

        invoice = stripe.Invoice.create(**params)
        return {"ok": True, "invoice_id": invoice.id, "invoice": invoice}
    except stripe.error.StripeError as exc:
        return {"ok": False, "error": str(exc.user_message or exc)}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}
