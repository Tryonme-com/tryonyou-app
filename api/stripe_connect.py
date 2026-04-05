"""
Stripe Connect seller dashboard API.

Routes (mounted under /api/stripe by api/index.py):
  POST /stripe/connect/onboard   – create/resume Stripe Connect onboarding
  GET  /stripe/connect/status    – retrieve account capabilities
  POST /stripe/products          – publish a relic as a Stripe Product + PaymentLink
  GET  /stripe/products          – list all active relics
"""

from __future__ import annotations

import os
from typing import Optional

import stripe
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_stripe_key() -> str:
    return os.environ.get("STRIPE_SECRET_KEY", "")


def _stripe_configured() -> bool:
    return bool(_get_stripe_key())


def _init_stripe() -> None:
    stripe.api_key = _get_stripe_key()


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

class OnboardRequest(BaseModel):
    seller_id: str
    account_id: Optional[str] = None


class PublishRelicRequest(BaseModel):
    seller_id: str
    name: str
    price_cents: int
    description: Optional[str] = None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post("/stripe/connect/onboard")
async def onboard_seller(req: OnboardRequest) -> dict:
    """
    Create (or resume) a Stripe Express account and return an onboarding URL.
    """
    if not _stripe_configured():
        raise HTTPException(status_code=503, detail="Stripe not configured")

    _init_stripe()

    return_url = os.environ.get(
        "STRIPE_CONNECT_RETURN_URL", "https://tryonyou.app/vendor"
    )
    refresh_url = os.environ.get(
        "STRIPE_CONNECT_REFRESH_URL", "https://tryonyou.app/vendor"
    )

    account_id = req.account_id or ""
    if not account_id:
        account = stripe.Account.create(type="express")
        account_id = account.id

    link = stripe.AccountLink.create(
        account=account_id,
        refresh_url=refresh_url,
        return_url=return_url,
        type="account_onboarding",
    )

    return {"account_id": account_id, "onboarding_url": link.url}


@router.get("/stripe/connect/status")
async def get_account_status(account_id: str) -> dict:
    """Return the onboarding/capability status of a Stripe Connect account."""
    if not _stripe_configured():
        raise HTTPException(status_code=503, detail="Stripe not configured")

    if not account_id:
        raise HTTPException(status_code=400, detail="account_id is required")

    _init_stripe()

    try:
        account = stripe.Account.retrieve(account_id)
    except stripe.InvalidRequestError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return {
        "account_id": account_id,
        "charges_enabled": account.charges_enabled,
        "payouts_enabled": account.payouts_enabled,
        "details_submitted": account.details_submitted,
    }


@router.post("/stripe/products")
async def publish_relic(req: PublishRelicRequest) -> dict:
    """
    Publish a relic: creates a Stripe Product + Price + PaymentLink.
    Returns the payment link URL so the storefront can link to it.
    """
    if not _stripe_configured():
        raise HTTPException(status_code=503, detail="Stripe not configured")

    if req.price_cents <= 0:
        raise HTTPException(status_code=400, detail="price_cents must be positive")

    _init_stripe()

    product = stripe.Product.create(
        name=req.name,
        description=req.description or "",
        metadata={"seller_id": req.seller_id, "type": "relic"},
    )

    price = stripe.Price.create(
        product=product.id,
        unit_amount=req.price_cents,
        currency="eur",
    )

    payment_link = stripe.PaymentLink.create(
        line_items=[{"price": price.id, "quantity": 1}],
    )

    return {
        "product_id": product.id,
        "price_id": price.id,
        "payment_link": payment_link.url,
        "name": req.name,
        "price_cents": req.price_cents,
        "description": req.description,
    }


@router.get("/stripe/products")
async def list_relics() -> dict:
    """Return all active relics published via Stripe Products."""
    if not _stripe_configured():
        return {"products": []}

    _init_stripe()

    result = stripe.Product.list(active=True, expand=["data.default_price"])

    items = []
    for p in result.data:
        if p.metadata.get("type") != "relic":
            continue
        price_obj = getattr(p, "default_price", None)
        items.append(
            {
                "id": p.id,
                "name": p.name,
                "description": p.description or "",
                "price_cents": price_obj.unit_amount if price_obj else None,
                "currency": price_obj.currency if price_obj else "eur",
            }
        )

    return {"products": items}
