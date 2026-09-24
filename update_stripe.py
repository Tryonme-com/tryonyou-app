"""
Crea productos Stripe LIVE solo desde catálogo explícito en entorno.

No incluye importes ni clientes ficticios. Tras un contrato firmado, define por ejemplo:

  export STRIPE_PRODUCT_CATALOG_JSON='[
    {"name":"Pilot-Setup","amount_cents":750000,"description":"Setup piloto firmado"}
  ]'

Patente: PCT/EP2025/067317
"""

from __future__ import annotations

import json
import os

import stripe

from sovereign_script_env import require_stripe_secret


def _load_catalog() -> list[dict]:
    raw = (os.getenv("STRIPE_PRODUCT_CATALOG_JSON") or "").strip()
    if not raw:
        return []
    data = json.loads(raw)
    if not isinstance(data, list):
        raise ValueError("STRIPE_PRODUCT_CATALOG_JSON debe ser una lista JSON.")
    return data


def crear_productos_v10() -> int:
    catalog = _load_catalog()
    if not catalog:
        print(
            "ℹ️  Sin STRIPE_PRODUCT_CATALOG_JSON: no se crea ningún producto. "
            "Configura el catálogo tras contrato firmado."
        )
        return 0

    stripe.api_key = require_stripe_secret()
    print("🚀 Creando productos Stripe desde catálogo explícito...")
    created = 0
    for item in catalog:
        name = str(item.get("name") or "").strip()
        amount_cents = int(item.get("amount_cents") or 0)
        desc = str(item.get("description") or "").strip()
        recurring = item.get("recurring")
        if not name or amount_cents <= 0:
            print(f"⚠️  Entrada ignorada (name/amount_cents inválidos): {item!r}")
            continue
        try:
            prod = stripe.Product.create(name=name, description=desc or None)
            params: dict = {
                "unit_amount": amount_cents,
                "currency": str(item.get("currency") or "eur").lower(),
                "product": prod.id,
            }
            if isinstance(recurring, dict) and recurring.get("interval"):
                params["recurring"] = recurring
            stripe.Price.create(**params)
            print(f"✅ Creado: {name} ({amount_cents / 100:.2f} EUR)")
            created += 1
        except Exception as exc:
            print(f"❌ Error en {name}: {exc}")
    return created


if __name__ == "__main__":
    raise SystemExit(0 if crear_productos_v10() >= 0 else 1)
