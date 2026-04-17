"""
Lectura del balance Stripe (disponible / pending) con STRIPE_SECRET_KEY_FR (Paris) o resolve legado.
Sin git: nunca `git add .` desde un script de cobro.

Uso:
  export STRIPE_SECRET_KEY_FR=sk_live_...
  python3 stripe_balance_check_env.py

Orden de clave: STRIPE_SECRET_KEY_FR → STRIPE_SECRET_KEY_NUEVA → STRIPE_SECRET_KEY.

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import sys

from stripe_verify_secret_env import resolve_stripe_secret


def _print_amounts(label: str, items: object) -> None:
    if not isinstance(items, list) or not items:
        print(f"  {label}: —")
        return
    for x in items:
        if not isinstance(x, dict):
            continue
        try:
            amount = int(x.get("amount", 0)) / 100.0
        except (TypeError, ValueError):
            amount = 0.0
        cur = str(x.get("currency", "?")).upper()
        print(f"  {label}: {amount:.2f} {cur}")


def main() -> int:
    sk = resolve_stripe_secret()
    if not sk:
        print(
            "Define STRIPE_SECRET_KEY_FR (Paris) o STRIPE_SECRET_KEY_NUEVA / STRIPE_SECRET_KEY.",
            file=sys.stderr,
        )
        return 1
    if sk.startswith("sk_test_"):
        print("Modo test (sk_test_). Para LIVE operativo usa sk_live_.", file=sys.stderr)

    import stripe

    stripe.api_key = sk
    try:
        bal = stripe.Balance.retrieve()
    except Exception as e:
        print(f"No se pudo leer Balance: {e}", file=sys.stderr)
        return 2

    print("Stripe Balance.retrieve()")
    _print_amounts("available", getattr(bal, "available", None) or bal.get("available"))
    _print_amounts("pending", getattr(bal, "pending", None) or bal.get("pending"))
    print("\nSiguiente paso: commit/push manual y acotado — sin automatizar git desde aquí.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
