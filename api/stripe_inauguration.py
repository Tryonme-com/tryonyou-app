"""
Checkout inaugural 12.500 € — stripe.checkout.Session (modo payment).

1) Si STRIPE_INAUGURATION_PRICE_ID (o alias) es price_… → line_items con ese precio.
2) Si no → pago único vía price_data: EUR, nombre por defecto «Inauguración V10.2 Lafayette».

STRIPE_SECRET_KEY_FR: obligatoria (sk_live_… cuenta Paris; ver stripe_fr_resolve).
Opcional: STRIPE_CONNECT_ACCOUNT_ID_FR=acct_… para cobro directo Connect en cuenta conectada FR.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from urllib.parse import urlparse

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import stripe
from stripe_fr_resolve import resolve_stripe_secret_fr, stripe_api_call_kwargs

_DEFAULT_PRODUCT_NAME = "Inauguración V10.2 Lafayette"
_DEFAULT_AMOUNT_CENTS = 1_250_000  # 12.500,00 €
_MANIFEST_PATENT = "PCT/EP2025/067317"


def _session_id_suffix(success_url: str) -> str:
    sep = "&" if "?" in success_url else "?"
    return f"{sep}session_id={{CHECKOUT_SESSION_ID}}"


def _resolve_line_items() -> list[dict]:
    price_id = (
        os.getenv("STRIPE_INAUGURATION_PRICE_ID")
        or os.getenv("STRIPE_PRICE_INAUGURATION_12500")
        or ""
    ).strip()
    if price_id.startswith("price_"):
        return [{"price": price_id, "quantity": 1}]
    name = (os.getenv("STRIPE_INAUGURATION_PRODUCT_NAME") or _DEFAULT_PRODUCT_NAME).strip()
    raw_cents = (os.getenv("STRIPE_INAUGURATION_AMOUNT_CENTS") or "").strip()
    try:
        amount = int(raw_cents) if raw_cents else _DEFAULT_AMOUNT_CENTS
    except ValueError:
        amount = _DEFAULT_AMOUNT_CENTS
    return [
        {
            "quantity": 1,
            "price_data": {
                "currency": "eur",
                "unit_amount": amount,
                "product_data": {"name": name},
            },
        }
    ]


def create_inauguration_checkout_session(origin_header: str | None) -> tuple[dict, int]:
    sk = resolve_stripe_secret_fr()
    if not sk.startswith("sk_live_"):
        return {
            "status": "error",
            "message": "stripe_live_secret_required",
            "hint": "STRIPE_SECRET_KEY_FR (o legado STRIPE_SECRET_KEY) debe ser sk_live_… de la cuenta Paris.",
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
    line_items = _resolve_line_items()
    meta_product = (os.getenv("STRIPE_INAUGURATION_PRODUCT_NAME") or "").strip() or _DEFAULT_PRODUCT_NAME
    if line_items and "price_data" in line_items[0]:
        meta_product = (
            line_items[0]
            .get("price_data", {})
            .get("product_data", {})
            .get("name", meta_product)
        )

    connect_kw = stripe_api_call_kwargs()
    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=line_items,
            success_url=success_with_session,
            cancel_url=cancel,
            locale="fr",
            billing_address_collection="required",
            phone_number_collection={"enabled": True},
            metadata={
                "patent": _MANIFEST_PATENT,
                "flow": "v10_2_inauguration",
                "product_name": meta_product,
                "billing_country_default": "FR",
            },
            **connect_kw,
        )
        url = session.url
        if not url:
            return {"status": "error", "message": "stripe_no_checkout_url"}, 502
        return {"status": "ok", "url": url, "session_id": session.id}, 200
    except stripe.error.StripeError as e:
        return {"status": "error", "message": str(e.user_message or e)}, 502
    except Exception as e:
        return {"status": "error", "message": str(e)}, 502
