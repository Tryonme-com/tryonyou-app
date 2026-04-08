"""
Stripe Agent — gestión de productos y precios (TryOnYou V10).

Crea, recupera y lista productos y precios en Stripe sin depender
de un framework web: diseñado para ser importado por api/index.py
o ejecutado como script de operaciones.

Funciones principales:
  - ensure_product      : crea o recupera un producto Stripe activo por nombre.
  - create_price        : crea un precio (unit_amount, currency, recurring opcional).
  - list_active_prices  : lista precios activos de un producto.

Variables de entorno requeridas:
  STRIPE_SECRET_KEY — clave secreta Stripe (sk_live_… o sk_test_…).
"""

from __future__ import annotations

import os
from typing import Any

import stripe


def _configure_stripe() -> None:
    """Configura stripe.api_key desde la variable STRIPE_SECRET_KEY."""
    sk = (os.getenv("STRIPE_SECRET_KEY") or "").strip()
    if not sk:
        raise ValueError(
            "STRIPE_SECRET_KEY not set or empty — define la clave secreta Stripe en el entorno."
        )
    stripe.api_key = sk


def ensure_product(
    name: str,
    *,
    description: str = "",
    metadata: dict[str, str] | None = None,
) -> dict[str, Any]:
    """
    Crea o recupera un producto Stripe activo con el nombre dado.

    Busca primero un producto activo con ese nombre exacto mediante la
    Search API de Stripe.  Si no existe (o si la búsqueda no está disponible
    en la cuenta), crea uno nuevo.

    Args:
        name:        Nombre del producto (requerido, no vacío).
        description: Descripción opcional del producto.
        metadata:    Metadatos opcionales (dict de cadenas).

    Returns:
        Dict JSON-serializable con los campos del objeto Product de Stripe.

    Raises:
        ValueError: si ``name`` está vacío o STRIPE_SECRET_KEY no está configurada.
        stripe.error.StripeError: si la llamada a la API de Stripe falla.
    """
    name = (name or "").strip()
    if not name:
        raise ValueError("name is required for ensure_product")

    _configure_stripe()

    try:
        results = stripe.Product.search(
            query=f'name:"{name}" AND active:"true"',
            limit=1,
        )
        if results.data:
            return dict(results.data[0])
    except stripe.error.InvalidRequestError:
        # Search API no disponible en cuentas de prueba limitadas; continuar con create.
        pass

    params: dict[str, Any] = {"name": name, "active": True}
    if description:
        params["description"] = description
    if metadata:
        params["metadata"] = metadata

    return dict(stripe.Product.create(**params))


def create_price(
    product_id: str,
    unit_amount: int,
    currency: str = "eur",
    *,
    recurring: dict[str, Any] | None = None,
    metadata: dict[str, str] | None = None,
) -> dict[str, Any]:
    """
    Crea un precio en Stripe para un producto existente.

    Args:
        product_id:  ID del producto Stripe (ej. «prod_…»).
        unit_amount: Importe en céntimos/centavos (ej. 9800 = 98,00 €).
        currency:    Código ISO-4217 en minúsculas (por defecto «eur»).
        recurring:   Configuración de recurrencia, p.ej. ``{"interval": "month"}``
                     para precios de suscripción.
        metadata:    Metadatos opcionales (dict de cadenas).

    Returns:
        Dict JSON-serializable con los campos del objeto Price de Stripe.

    Raises:
        ValueError: si ``product_id`` está vacío, ``unit_amount`` < 0 o
                    STRIPE_SECRET_KEY no está configurada.
        stripe.error.StripeError: si la llamada a la API de Stripe falla.
    """
    product_id = (product_id or "").strip()
    if not product_id:
        raise ValueError("product_id is required for create_price")
    if unit_amount < 0:
        raise ValueError("unit_amount must be >= 0")

    _configure_stripe()

    params: dict[str, Any] = {
        "product": product_id,
        "unit_amount": unit_amount,
        "currency": currency.lower(),
    }
    if recurring:
        params["recurring"] = recurring
    if metadata:
        params["metadata"] = metadata

    return dict(stripe.Price.create(**params))


def list_active_prices(product_id: str) -> list[dict[str, Any]]:
    """
    Lista todos los precios activos de un producto Stripe.

    Args:
        product_id: ID del producto Stripe (ej. «prod_…»).

    Returns:
        Lista de dicts JSON-serializables con los campos de cada objeto Price.

    Raises:
        ValueError: si ``product_id`` está vacío o STRIPE_SECRET_KEY no está configurada.
        stripe.error.StripeError: si la llamada a la API de Stripe falla.
    """
    product_id = (product_id or "").strip()
    if not product_id:
        raise ValueError("product_id is required for list_active_prices")

    _configure_stripe()

    prices = stripe.Price.list(product=product_id, active=True)
    return [dict(p) for p in prices.auto_paging_iter()]
