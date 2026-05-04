"""
update_stripe.py — Crea/actualiza productos y precios V10 en Stripe.

Requiere la variable de entorno STRIPE_SECRET_KEY_FR (o STRIPE_SECRET_KEY_NUEVA /
STRIPE_SECRET_KEY). Nunca hardcodees secretos en el código fuente.

Uso:
    export STRIPE_SECRET_KEY_FR=sk_live_...
    python3 update_stripe.py

Patente PCT/EP2025/067317 — @CertezaAbsoluta
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import stripe

from sovereign_script_env import require_stripe_secret

_PRODUCTOS: list[dict[str, object]] = [
    {"name": "V10-LAFAYETTE-ENTRY-P1", "amount": 2750000, "desc": "Activación V10: Setup 10 Nodos + Exclusividad D9."},
    {"name": "V10-ENTRY-GLOBAL",       "amount": 2500000, "desc": "Despliegue V10: Instalación 10 Nodos (LVMH/Otros)."},
    {"name": "IP-TRANSFER-V10-P1",     "amount": 9825000, "desc": "Transferencia de Activos/Licencia IP (Parte 1)."},
    {"name": "IP-TRANSFER-V10-P2",     "amount": 9825000, "desc": "Transferencia de Activos/Licencia IP (Parte 2)."},
    {"name": "V10-ANUAL-PREPAGO",      "amount": 9800000, "desc": "Abono Anual 10 nodos (Ahorro 20k) + 8% Comisión sobre ventas."},
]


def crear_productos_v10() -> int:
    """Crea los productos/precios V10 en Stripe. Devuelve 0 si todo fue bien, 1 si hubo algún error."""
    stripe.api_key = require_stripe_secret()
    print("🚀 Iniciando inyección de productos en Stripe...")
    errors = 0

    for p in _PRODUCTOS:
        try:
            prod = stripe.Product.create(name=p["name"], description=p["desc"])
            stripe.Price.create(
                unit_amount=p["amount"],
                currency="eur",
                product=prod.id,
            )
            print(f"✅ Creado: {p['name']} ({p['amount'] / 100:.2f}€)")
        except Exception as e:
            print(f"❌ Error en {p['name']}: {e}")
            errors += 1

    # Suscripción mensual (9.900 €)
    try:
        mensual = stripe.Product.create(
            name="V10-MANTENIMIENTO-MENSUAL",
            description="Canon mensual 10 nodos + 8% Comisión sobre ventas.",
        )
        stripe.Price.create(
            unit_amount=990000,
            currency="eur",
            recurring={"interval": "month"},
            product=mensual.id,
        )
        print("✅ Suscripción Mensual Creada: 9.900€")
    except Exception as e:
        print(f"❌ Error en Suscripción: {e}")
        errors += 1

    return 0 if errors == 0 else 1


def main() -> int:
    return crear_productos_v10()


if __name__ == "__main__":
    raise SystemExit(main())
