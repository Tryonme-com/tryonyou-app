"""
Liquidacion Stripe -> payout al banco vinculado (solo LIVE).

Por defecto solo muestra el plan. Para ejecutar payout real exige:
  STRIPE_PAYOUT_CONFIRM=1
  STRIPE_PAYOUT_EXECUTION_REF=<referencia-operativa>

El importe ya no es "todo el capital" a ciegas: respeta reserva minima,
importe maximo opcional e idempotencia. PCT/EP2025/067317.
Bajo Protocolo de Soberania V10 - Founder: Ruben
"""
from __future__ import annotations

import hashlib
import os
import sys

from stripe_verify_secret_env import resolve_stripe_secret

_DEFAULT_RESERVE_CENTS = 10_000
_TRUTHY = {"1", "true", "yes", "on"}


def _env_bool(name: str, default: bool = False) -> bool:
    raw = (os.environ.get(name) or "").strip().lower()
    return default if not raw else raw in _TRUTHY


def _env_int(name: str, default: int) -> int:
    raw = (os.environ.get(name) or "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _as_amount_currency(x: object) -> tuple[int, str]:
    if isinstance(x, dict):
        return int(x.get("amount", 0)), str(x.get("currency", "")).lower()
    amt = int(getattr(x, "amount", 0) or 0)
    cur = str(getattr(x, "currency", "") or "").lower()
    return amt, cur


def _pick_available_eur(balance: object) -> tuple[int, str]:
    """Devuelve (amount_cents, currency) para la moneda pedida; si no hay match, el primer available."""
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


def _compute_payout_amount_cents(available_cents: int) -> int:
    reserve = max(0, _env_int("STRIPE_PAYOUT_RESERVE_CENTS", _DEFAULT_RESERVE_CENTS))
    max_amount = max(0, _env_int("STRIPE_PAYOUT_MAX_CENTS", 0))
    payout_amount = max(0, available_cents - reserve)
    if max_amount:
        payout_amount = min(payout_amount, max_amount)
    return payout_amount


def _execution_ref() -> str:
    return (os.environ.get("STRIPE_PAYOUT_EXECUTION_REF") or "").strip()


def _idempotency_key(amount_cents: int, currency: str, execution_ref: str) -> str:
    explicit = (os.environ.get("STRIPE_PAYOUT_IDEMPOTENCY_KEY") or "").strip()
    if explicit:
        return explicit[:255]
    digest = hashlib.sha256(f"{execution_ref}|{amount_cents}|{currency}".encode("utf-8")).hexdigest()
    return f"tryonyou-liquidation-{digest[:32]}"


def liquidacion_inmediata(*, dry_run: bool | None = None) -> int:
    sk = resolve_stripe_secret()
    if not sk:
        print(
            "Define STRIPE_SECRET_KEY_FR (Paris) o STRIPE_SECRET_KEY_NUEVA / STRIPE_SECRET_KEY.",
            file=sys.stderr,
        )
        return 1
    if not sk.startswith("sk_live_"):
        print(
            "Los payouts a banco en produccion exigen sk_live_. Modo test no liquida igual.",
            file=sys.stderr,
        )
        return 2

    confirm = _env_bool("STRIPE_PAYOUT_CONFIRM")
    if dry_run is None:
        dry_run = not confirm

    import stripe

    stripe.api_key = sk
    try:
        balance = stripe.Balance.retrieve()
    except Exception as e:
        print(f"No se pudo leer balance: {e}", file=sys.stderr)
        return 3

    disponible, cur = _pick_available_eur(balance)
    if disponible <= 0:
        print(
            f"No hay fondos 'available' en {cur.upper()} (>0). "
            "Puede estar todo en 'pending' (liquidación de cargo en curso)."
        )
        return 0

    payout_amount = _compute_payout_amount_cents(disponible)
    reserve = max(0, disponible - payout_amount)
    if payout_amount <= 0:
        print(
            f"Fondos available {disponible/100:.2f} {cur.upper()} preservados: "
            f"reserva configurada {reserve/100:.2f} {cur.upper()}."
        )
        return 0

    eur_display = payout_amount / 100.0
    desc = (os.environ.get("STRIPE_PAYOUT_DESCRIPTOR", "DIVINEO LIQ") or "DIVINEO LIQ")[:22]

    if dry_run:
        print(
            f"[DRY-RUN] Se enviarian {eur_display:.2f} {cur.upper()} al banco vinculado en Stripe. "
            f"Reserva preservada: {reserve/100:.2f} {cur.upper()}. Descriptor sugerido: {desc!r}"
        )
        print(
            "Para payout real: STRIPE_PAYOUT_CONFIRM=1 "
            "STRIPE_PAYOUT_EXECUTION_REF=<referencia> python3 stripe_liquidation_payout_env.py"
        )
        return 0

    execution_ref = _execution_ref()
    if not execution_ref:
        print(
            "Bloqueado: defina STRIPE_PAYOUT_EXECUTION_REF con una referencia operativa verificable.",
            file=sys.stderr,
        )
        return 4

    try:
        payout = stripe.Payout.create(
            amount=payout_amount,
            currency=cur,
            statement_descriptor=desc,
            metadata={
                "source": "stripe_liquidation_payout_env",
                "execution_ref": execution_ref[:120],
                "available_cents": str(disponible),
                "reserve_cents": str(reserve),
                "patent": "PCT/EP2025/067317",
            },
            idempotency_key=_idempotency_key(payout_amount, cur, execution_ref),
        )
        pid = getattr(payout, "id", "?")
        print(f"OK - Payout creado: {eur_display:.2f} {cur.upper()} id={pid}")
    except Exception as e:
        print(f"Error creando Payout: {e}", file=sys.stderr)
        return 5
    return 0


if __name__ == "__main__":
    raise SystemExit(liquidacion_inmediata())
