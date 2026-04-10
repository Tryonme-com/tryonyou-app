"""
Checkout inaugural 12.500 € — sesión Stripe con price_id LIVE únicamente.
Nunca uses sk_test_ aquí en producción: el handler lo rechaza.

Includes SIREN 943 610 196 in session metadata for legal traceability
(Stripe Support / Isabella).
"""

from __future__ import annotations

import os
from urllib.parse import urlparse

import stripe

SIREN = "943 610 196"
PATENT = "PCT/EP2025/067317"


def _session_id_suffix(success_url: str) -> str:
    sep = "&" if "?" in success_url else "?"
    return f"{sep}session_id={{CHECKOUT_SESSION_ID}}"


def create_inauguration_checkout_session(origin_header: str | None) -> tuple[dict, int]:
    sk = (os.getenv("STRIPE_SECRET_KEY") or "").strip()
    price_id = (
        os.getenv("STRIPE_INAUGURATION_PRICE_ID")
        or os.getenv("STRIPE_PRICE_INAUGURATION_12500")
        or ""
    ).strip()

    if not sk.startswith("sk_live_"):
        return {
            "status": "error",
            "message": "stripe_live_secret_required",
            "hint": "STRIPE_SECRET_KEY debe ser sk_live_… (modo prueba no permitido para inauguración).",
        }, 503

    if not price_id.startswith("price_"):
        return {
            "status": "error",
            "message": "stripe_inauguration_price_id_required",
            "hint": "Define STRIPE_INAUGURATION_PRICE_ID=price_… (Live) en Vercel.",
        }, 503

    stripe.api_key = sk

    base = (origin_header or "").strip().rstrip("/")
    if not base:
        pub = (os.getenv("TRYONYOU_PUBLIC_DOMAIN") or "").strip()
        base = f"https://{pub}" if pub else "https://tryonyou.app"

    success = (os.getenv("STRIPE_INAUGURATION_SUCCESS_URL") or f"{base}/?inauguration=merci").strip()
    cancel = (os.getenv("STRIPE_INAUGURATION_CANCEL_URL") or f"{base}/?inauguration=annule").strip()

    for name, u in (("success", success), ("cancel", cancel)):
        try:
            p = urlparse(u)
            if p.scheme not in ("https", "http"):
                raise ValueError("invalid_scheme")
        except Exception:
            return {
                "status": "error",
                "message": f"invalid_{name}_url",
            }, 500

    success_with_session = f"{success}{_session_id_suffix(success)}"

    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=success_with_session,
            cancel_url=cancel,
            metadata={
                "siren": SIREN,
                "patent": PATENT,
                "platform": "TryOnYou_V10",
                "flow": "inauguration",
            },
            payment_intent_data={
                "metadata": {
                    "siren": SIREN,
                    "patent": PATENT,
                    "platform": "TryOnYou_V10",
                    "flow": "inauguration",
                },
            },
        )
        url = session.url
        if not url:
            return {"status": "error", "message": "stripe_no_checkout_url"}, 502
        return {"status": "ok", "url": url}, 200
    except stripe.error.StripeError as e:
        return {"status": "error", "message": str(e.user_message or e)}, 502
    except Exception as e:
        return {"status": "error", "message": str(e)}, 502
