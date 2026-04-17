"""
Stripe Agent — TryOnYou / Divineo V10.
Product and price management via Stripe API.

Handles:
- Product creation, retrieval, listing, and archival
- Price creation, retrieval, listing, and deactivation

Requires env var: STRIPE_SECRET_KEY_FR (Paris) o legado STRIPE_SECRET_KEY (sk_live_… / sk_test_…).
"""

from __future__ import annotations

from typing import Any

import stripe

from stripe_fr_resolve import resolve_stripe_secret_fr


def _get_stripe_client() -> str:
    """Return validated Stripe secret key from environment (cuenta Paris prioritaria)."""
    sk = resolve_stripe_secret_fr()
    if not sk.startswith(("sk_live_", "sk_test_")):
        raise EnvironmentError(
            "STRIPE_SECRET_KEY_FR (o STRIPE_SECRET_KEY) must be set and start with sk_live_ or sk_test_"
        )
    return sk


# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------


def create_product(
    name: str,
    description: str = "",
    metadata: dict[str, str] | None = None,
) -> dict[str, Any]:
    """
    Create a Stripe product.

    Args:
        name: Product name.
        description: Optional product description.
        metadata: Optional key/value metadata dict.

    Returns:
        dict with 'ok', 'product_id', and 'product' on success,
        or 'ok': False and 'error' on failure.
    """
    stripe.api_key = _get_stripe_client()
    try:
        params: dict[str, Any] = {"name": name}
        if description:
            params["description"] = description
        if metadata:
            params["metadata"] = metadata
        product = stripe.Product.create(**params)
        return {"ok": True, "product_id": product.id, "product": product}
    except stripe.error.StripeError as exc:
        return {"ok": False, "error": str(exc.user_message or exc)}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def retrieve_product(product_id: str) -> dict[str, Any]:
    """
    Retrieve a Stripe product by ID.

    Returns:
        dict with 'ok' and 'product' on success, or 'ok': False and 'error'.
    """
    stripe.api_key = _get_stripe_client()
    try:
        product = stripe.Product.retrieve(product_id)
        return {"ok": True, "product": product}
    except stripe.error.StripeError as exc:
        return {"ok": False, "error": str(exc.user_message or exc)}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def list_products(active: bool | None = None, limit: int = 100) -> dict[str, Any]:
    """
    List Stripe products.

    Args:
        active: Filter by active status. None returns all.
        limit: Maximum number of products to return (1–100).

    Returns:
        dict with 'ok' and 'products' list on success.
    """
    stripe.api_key = _get_stripe_client()
    try:
        params: dict[str, Any] = {"limit": max(1, min(limit, 100))}
        if active is not None:
            params["active"] = active
        result = stripe.Product.list(**params)
        return {"ok": True, "products": list(result.auto_paging_iter())}
    except stripe.error.StripeError as exc:
        return {"ok": False, "error": str(exc.user_message or exc)}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def archive_product(product_id: str) -> dict[str, Any]:
    """
    Archive (deactivate) a Stripe product.

    Returns:
        dict with 'ok' and 'product_id' on success.
    """
    stripe.api_key = _get_stripe_client()
    try:
        product = stripe.Product.modify(product_id, active=False)
        return {"ok": True, "product_id": product.id}
    except stripe.error.StripeError as exc:
        return {"ok": False, "error": str(exc.user_message or exc)}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


# ---------------------------------------------------------------------------
# Prices
# ---------------------------------------------------------------------------


def create_price(
    product_id: str,
    unit_amount: int,
    currency: str = "eur",
    recurring: dict[str, Any] | None = None,
    metadata: dict[str, str] | None = None,
) -> dict[str, Any]:
    """
    Create a Stripe price for a product.

    Args:
        product_id: Stripe product ID (prod_…).
        unit_amount: Price in the smallest currency unit (e.g. cents for EUR).
        currency: ISO 4217 currency code, lowercase (default: 'eur').
        recurring: Optional dict for subscription prices, e.g.
            {'interval': 'month', 'interval_count': 1}.
        metadata: Optional key/value metadata dict.

    Returns:
        dict with 'ok', 'price_id', and 'price' on success.
    """
    stripe.api_key = _get_stripe_client()
    try:
        params: dict[str, Any] = {
            "product": product_id,
            "unit_amount": unit_amount,
            "currency": currency.lower(),
        }
        if recurring:
            params["recurring"] = recurring
        if metadata:
            params["metadata"] = metadata
        price = stripe.Price.create(**params)
        return {"ok": True, "price_id": price.id, "price": price}
    except stripe.error.StripeError as exc:
        return {"ok": False, "error": str(exc.user_message or exc)}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def retrieve_price(price_id: str) -> dict[str, Any]:
    """
    Retrieve a Stripe price by ID.

    Returns:
        dict with 'ok' and 'price' on success, or 'ok': False and 'error'.
    """
    stripe.api_key = _get_stripe_client()
    try:
        price = stripe.Price.retrieve(price_id)
        return {"ok": True, "price": price}
    except stripe.error.StripeError as exc:
        return {"ok": False, "error": str(exc.user_message or exc)}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def list_prices(
    product_id: str | None = None,
    active: bool | None = None,
    limit: int = 100,
) -> dict[str, Any]:
    """
    List Stripe prices.

    Args:
        product_id: Optionally filter by product ID.
        active: Filter by active status. None returns all.
        limit: Maximum number of prices to return (1–100).

    Returns:
        dict with 'ok' and 'prices' list on success.
    """
    stripe.api_key = _get_stripe_client()
    try:
        params: dict[str, Any] = {"limit": max(1, min(limit, 100))}
        if product_id:
            params["product"] = product_id
        if active is not None:
            params["active"] = active
        result = stripe.Price.list(**params)
        return {"ok": True, "prices": list(result.auto_paging_iter())}
    except stripe.error.StripeError as exc:
        return {"ok": False, "error": str(exc.user_message or exc)}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def deactivate_price(price_id: str) -> dict[str, Any]:
    """
    Deactivate a Stripe price (prices cannot be deleted, only deactivated).

    Returns:
        dict with 'ok' and 'price_id' on success.
    """
    stripe.api_key = _get_stripe_client()
    try:
        price = stripe.Price.modify(price_id, active=False)
        return {"ok": True, "price_id": price.id}
    except stripe.error.StripeError as exc:
        return {"ok": False, "error": str(exc.user_message or exc)}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}
