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
