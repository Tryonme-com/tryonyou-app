"""
Liquidación Stripe → payout al banco (solo LIVE, STRIPE_SECRET_KEY en entorno).

⚠️ Mueve fondos reales: por defecto solo MUESTRA balance y el importe que se enviaría.
Para ejecutar payout: STRIPE_PAYOUT_CONFIRM=1

  export STRIPE_SECRET_KEY=sk_live_...
  python3 stripe_liquidation_payout_env.py              # dry-run (solo lectura + plan)
  STRIPE_PAYOUT_CONFIRM=1 python3 stripe_liquidation_payout_env.py

Opcional: STRIPE_PAYOUT_CURRENCY=eur (default eur)

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import os
import sys

from stripe_verify_secret_env import resolve_stripe_secret


def _as_amount_currency(x: object) -> tuple[int, str]:
    if isinstance(x, dict):
        return int(x.get("amount", 0)), str(x.get("currency", "")).lower()
    amt = int(getattr(x, "amount", 0) or 0)
    cur = str(getattr(x, "currency", "") or "").lower()
    return amt, cur


def _pick_available_eur(balance: object) -> tuple[int, str]:
    """Devuelve (amount_cents, currency) para la moneda pedida (default eur); si no hay match, el primer available."""
    items = getattr(balance, "available", None) or (
        balance.get("available") if hasattr(balance, "get") else None
    )
    if not items:
        return 0, "eur"
    want = (os.environ.get("STRIPE_PAYOUT_CURRENCY", "eur") or "eur").strip().lower()
    for x in items:
        amt, cur = _as_amount_currency(x)
        if cur == want:
            return amt, cur
    amt0, cur0 = _as_amount_currency(items[0])
    return amt0, cur0 or "eur"


def liquidacion_inmediata(*, dry_run: bool | None = None) -> int:
    sk = resolve_stripe_secret()
    if not sk:
        print("Define STRIPE_SECRET_KEY o STRIPE_SECRET_KEY_NUEVA.", file=sys.stderr)
        return 1
    if not sk.startswith("sk_live_"):
        print(
            "Los payouts a banco en producción exigen sk_live_. Modo test no liquida igual.",
            file=sys.stderr,
        )

    confirm = (os.environ.get("STRIPE_PAYOUT_CONFIRM", "").strip().lower() in ("1", "true", "yes"))
    if dry_run is None:
        dry_run = not confirm

    import stripe

    stripe.api_key = sk
    try:
        balance = stripe.Balance.retrieve()
    except Exception as e:
        print(f"No se pudo leer balance: {e}", file=sys.stderr)
        return 2

    disponible, cur = _pick_available_eur(balance)
    if disponible <= 0:
        print(
            f"No hay fondos 'available' en {cur.upper()} (>0). "
            "Puede estar todo en 'pending' (liquidación de cargo en curso)."
        )
        return 0

    eur_display = disponible / 100.0
    desc = (os.environ.get("STRIPE_PAYOUT_DESCRIPTOR", "DIVINEO LIQ") or "DIVINEO LIQ")[:22]

    if dry_run:
        print(
            f"[DRY-RUN] Se enviarían {eur_display:.2f} {cur.upper()} al banco vinculado en Stripe. "
            f"Descriptor sugerido: {desc!r}"
        )
        print("Para payout real: STRIPE_PAYOUT_CONFIRM=1 python3 stripe_liquidation_payout_env.py")
        return 0

    try:
        payout = stripe.Payout.create(
            amount=disponible,
            currency=cur,
            statement_descriptor=desc,
        )
        pid = getattr(payout, "id", "?")
        print(f"OK — Payout creado: {eur_display:.2f} {cur.upper()} id={pid}")
    except Exception as e:
        print(f"Error creando Payout: {e}", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(liquidacion_inmediata())
