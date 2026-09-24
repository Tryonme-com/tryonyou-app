from __future__ import annotations

from typing import Any

import stripe

from api.config import settings


def construct_event(payload: bytes, sig_header: str) -> dict[str, Any]:
    if not settings.stripe_endpoint_secret:
        raise RuntimeError("STRIPE_ENDPOINT_SECRET is missing")
    if settings.stripe_api_key:
        stripe.api_key = settings.stripe_api_key
    return stripe.Webhook.construct_event(payload, sig_header, settings.stripe_endpoint_secret)


def create_payment_intent(amount_cents: int, idempotency_key: str) -> str:
    """Create a Stripe PaymentIntent and return its client_secret.

    The caller must supply a stable idempotency_key (e.g. derived from the
    order ID) so that retries don't create duplicate charges.
    """
    secret_key = settings.stripe_secret_key or settings.stripe_api_key
    if not secret_key:
        raise RuntimeError("STRIPE_SECRET_KEY is missing")
    stripe.api_key = secret_key
    intent = stripe.PaymentIntent.create(
        amount=amount_cents,
        currency="eur",
        automatic_payment_methods={"enabled": True},
        idempotency_key=idempotency_key,
    )
    return intent.client_secret  # type: ignore[return-value]
