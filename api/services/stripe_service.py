"""
Stripe signature verification — decoupled from Flask.

The webhook route calls verify_webhook(); everything else in this file is
internal.  No Flask imports here.
"""
from __future__ import annotations

import logging

import stripe

from config import Config

logger = logging.getLogger(__name__)


class WebhookVerificationError(Exception):
    """
    Raised on any verification failure.
    The message is a short safe slug (no secrets, no raw payload).
    """


def verify_webhook(payload: bytes, sig_header: str) -> dict:
    """
    Verify Stripe webhook signature and return the parsed event dict.

    Args:
        payload:    Raw request body bytes.
        sig_header: Value of the Stripe-Signature header.

    Returns:
        Parsed event as a plain dict.

    Raises:
        WebhookVerificationError with a safe slug on any failure.
    """
    if not Config.STRIPE_ENDPOINT_SECRET:
        logger.error("[stripe_service] STRIPE_ENDPOINT_SECRET not configured")
        raise WebhookVerificationError("missing_config")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, Config.STRIPE_ENDPOINT_SECRET
        )
    except ValueError:
        logger.warning("[stripe_service] invalid payload (bad JSON or encoding)")
        raise WebhookVerificationError("invalid_payload")
    except stripe.error.SignatureVerificationError:
        logger.warning("[stripe_service] signature verification failed")
        raise WebhookVerificationError("invalid_signature")
    except Exception as exc:
        logger.exception("[stripe_service] unexpected verification error: %s", exc)
        raise WebhookVerificationError("verification_error")

    return dict(event)
