"""
Escaneo de entradas reales de capital vía Stripe BalanceTransaction.list.

Uso:
  export STRIPE_SECRET_KEY_FR=sk_live_...
  python3 stripe_inflow_check.py

Orden de clave: STRIPE_SECRET_KEY_FR → STRIPE_SECRET_KEY_NUEVA → STRIPE_SECRET_KEY.

Sin credencial de entorno no se llama a la API de Stripe.

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import os
import sys

from stripe_verify_secret_env import resolve_stripe_secret

# Importe mínimo para considerar un movimiento de «alto volumen» (en céntimos).
# 1 000 € = 100 000 céntimos.
HIGH_VOLUME_THRESHOLD_CENTS = 100_000
ALLOW_TEST_KEY_ENV = "STRIPE_INFLOW_ALLOW_TEST_KEY"


def check_real_inflow(limit: int = 20) -> list[dict]:
    """
    Escanea las últimas `limit` transacciones de balance en Stripe.

    Devuelve lista de movimientos con amount > HIGH_VOLUME_THRESHOLD_CENTS.
    Imprime resultados en stdout; no lanza git ni toca el .env.

    La clave Stripe se resuelve desde el entorno (nunca incrustada en código):
      STRIPE_SECRET_KEY_FR → STRIPE_SECRET_KEY_NUEVA → STRIPE_SECRET_KEY
    """
    sk = resolve_stripe_secret()
    if not sk:
        print(
            "Define STRIPE_SECRET_KEY_FR (Paris) o STRIPE_SECRET_KEY_NUEVA / STRIPE_SECRET_KEY.",
            file=sys.stderr,
        )
        return []
    if sk.startswith("sk_test_") and os.environ.get(ALLOW_TEST_KEY_ENV) != "1":
        print(
            f"Clave sk_test_ rechazada para inflow real; define {ALLOW_TEST_KEY_ENV}=1 solo en pruebas locales.",
            file=sys.stderr,
        )
        return []

    import stripe

    stripe.api_key = sk

    print("--- ESCANEANDO ENTRADAS REALES DE CAPITAL ---")
    try:
        balance_transactions = stripe.BalanceTransaction.list(limit=limit)
    except stripe.error.StripeError as e:
        print(f"Error al consultar BalanceTransaction.list: {e}", file=sys.stderr)
        return []

    found: list[dict] = []
    for bt in balance_transactions.data:
        amount = int(getattr(bt, "amount", 0) or 0)
        if amount > HIGH_VOLUME_THRESHOLD_CENTS:
            status = getattr(bt, "status", "?")
            bt_type = getattr(bt, "type", "?")
            print(
                f"Detectado movimiento: {amount / 100:.2f} € | Estado: {status} | Tipo: {bt_type}"
            )
            found.append({"amount": amount, "status": status, "type": bt_type})

    if not found:
        print("No se detectan entradas de alto volumen en el motor de Stripe.")
    return found


def main() -> int:
    results = check_real_inflow()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
