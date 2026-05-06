"""
Stripe Agent — TryOnYou / Divineo V10.
Product and price management via Stripe API.

Handles:
- Product creation, retrieval, listing, and archival
- Price creation, retrieval, listing, and deactivation

Requires env var: STRIPE_SECRET_KEY_FR (Paris) o legado STRIPE_SECRET_KEY (sk_live_… / sk_test_…).
"""

from __future__ import annotations

import os
import sys
import threading
import time
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import stripe

from stripe_fr_resolve import resolve_stripe_secret_fr


_list_cache_lock = threading.Lock()
_list_cache: dict[str, tuple[float, dict[str, Any]]] = {}
_LEGAL_METADATA: dict[str, str] = {
    "siren": "943 610 196",
    "patent": "PCT/EP2025/067317",
}


def _with_legal_metadata(metadata: dict[str, str] | None = None) -> dict[str, str]:
    merged = dict(metadata or {})
    for key, value in _LEGAL_METADATA.items():
        merged.setdefault(key, value)
    return merged


def _list_cache_ttl_seconds() -> float:
    raw = (os.getenv("STRIPE_LIST_CACHE_TTL_SECONDS") or "120").strip()
    try:
        v = float(raw)
    except ValueError:
        v = 120.0
    return max(0.0, v)


def clear_stripe_list_cache() -> None:
    """Vacía la caché en memoria de list_products / list_prices (tests o tras cambios de catálogo)."""
    with _list_cache_lock:
        _list_cache.clear()


def _list_cache_key(kind: str, **parts: Any) -> str:
    flat = tuple(sorted(parts.items()))
    return f"{kind}|{flat}"


def _cache_get(key: str) -> dict[str, Any] | None:
    ttl = _list_cache_ttl_seconds()
    if ttl <= 0:
        return None
    now = time.monotonic()
    with _list_cache_lock:
        hit = _list_cache.get(key)
        if not hit:
            return None
        ts, payload = hit
        if now - ts > ttl:
            del _list_cache[key]
            return None
        return payload


def _cache_set(key: str, payload: dict[str, Any]) -> None:
    if _list_cache_ttl_seconds() <= 0:
        return
    with _list_cache_lock:
        _list_cache[key] = (time.monotonic(), payload)


def _stripe_list_items(result: Any, *, paginate: bool) -> list[Any]:
    """
    Una sola página por defecto (``result.data``) para evitar ráfagas GET /v1/prices|products.
    Con ``paginate=True`` se usa ``auto_paging_iter()`` (catálogos grandes; más peticiones).
    """
    if paginate:
        return list(result.auto_paging_iter())
    data = getattr(result, "data", None)
    if isinstance(data, list):
        return list(data)
    return list(result.auto_paging_iter())


def _valid_product_id(product_id: str) -> bool:
    return bool(product_id and str(product_id).strip().startswith("prod_"))


def _valid_price_id(price_id: str) -> bool:
    return bool(price_id and str(price_id).strip().startswith("price_"))


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
        params["metadata"] = _with_legal_metadata(metadata)
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
    if not _valid_product_id(product_id):
        return {
            "ok": False,
            "error": "invalid_product_id_expected_prod_prefix",
        }
    stripe.api_key = _get_stripe_client()
    try:
        product = stripe.Product.retrieve(product_id)
        return {"ok": True, "product": product}
    except stripe.error.StripeError as exc:
        return {"ok": False, "error": str(exc.user_message or exc)}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def list_products(
    active: bool | None = None,
    limit: int = 100,
    *,
    paginate: bool = False,
) -> dict[str, Any]:
    """
    List Stripe products.

    Args:
        active: Filter by active status. None returns all.
        limit: Maximum number of products to return (1–100).
        paginate: If False (default), solo la primera página (menos tráfico API).

    Returns:
        dict with 'ok' and 'products' list on success.
    """
    stripe.api_key = _get_stripe_client()
    try:
        params: dict[str, Any] = {"limit": max(1, min(limit, 100))}
        if active is not None:
            params["active"] = active
        cache_key = _list_cache_key(
            "products",
            active=active,
            limit=params["limit"],
            paginate=paginate,
        )
        cached = _cache_get(cache_key)
        if cached is not None:
            return cached
        result = stripe.Product.list(**params)
        out = {"ok": True, "products": _stripe_list_items(result, paginate=paginate)}
        _cache_set(cache_key, out)
        return out
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
    if not _valid_product_id(product_id):
        return {"ok": False, "error": "invalid_product_id_expected_prod_prefix"}
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
    if not _valid_product_id(product_id):
        return {"ok": False, "error": "invalid_product_id_expected_prod_prefix"}
    stripe.api_key = _get_stripe_client()
    try:
        params: dict[str, Any] = {
            "product": product_id,
            "unit_amount": unit_amount,
            "currency": currency.lower(),
        }
        if recurring:
            params["recurring"] = recurring
        params["metadata"] = _with_legal_metadata(metadata)
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
    if not _valid_price_id(price_id):
        return {"ok": False, "error": "invalid_price_id_expected_price_prefix"}
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
    *,
    paginate: bool = False,
) -> dict[str, Any]:
    """
    List Stripe prices.

    Args:
        product_id: Optionally filter by product ID (prod_…).
        active: Filter by active status. None returns all.
        limit: Maximum number of prices to return (1–100).
        paginate: If False (default), solo la primera página (menos tráfico API).

    Returns:
        dict with 'ok' and 'prices' list on success.
    """
    if product_id and not _valid_product_id(product_id):
        return {"ok": False, "error": "invalid_product_id_expected_prod_prefix"}
    stripe.api_key = _get_stripe_client()
    params: dict[str, Any] = {"limit": max(1, min(limit, 100))}
    if product_id:
        params["product"] = product_id
    if active is not None:
        params["active"] = active
    cache_key = _list_cache_key(
        "prices",
        product_id=product_id,
        active=active,
        limit=params["limit"],
        paginate=paginate,
    )
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached
    try:
        result = stripe.Price.list(**params)
        out = {"ok": True, "prices": _stripe_list_items(result, paginate=paginate)}
        _cache_set(cache_key, out)
        return out
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
    if not _valid_price_id(price_id):
        return {"ok": False, "error": "invalid_price_id_expected_price_prefix"}
    stripe.api_key = _get_stripe_client()
    try:
        price = stripe.Price.modify(price_id, active=False)
        return {"ok": True, "price_id": price.id}
    except stripe.error.StripeError as exc:
        return {"ok": False, "error": str(exc.user_message or exc)}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}
