"""
Diagnóstico Stripe Connect (Hito 2 / SacMuseum) + opción de payout explícita.

- Clave SOLO desde entorno (nunca en código): STRIPE_SECRET_KEY_FR u aliases en
  stripe_verify_secret_env.resolve_stripe_secret.
- **sk_test_ está prohibido:** el script termina con error (solo sk_live_ para acción real).
- Cuenta conectada: STRIPE_SACMUSEUM_ACCOUNT_ID, STRIPE_CONNECT_ACCOUNT_ID_FR o
  STRIPE_ACCOUNT_ID (acct_…; alias para scripts legacy).

Por defecto: desglose Hito 2 con **prima 15 %** (27.500 € bruto → 4.125 € prima → 23.375 € neto).
Payout real: STRIPE_PAYOUT_CONFIRM=1 (mueve fondos reales).

Cargar .env local (opcional): si tienes ``python-dotenv`` instalado, define
``SACMUSEUM_LOAD_DOTENV=1`` para leer ``.env`` en la raíz del repo.

  export STRIPE_SECRET_KEY_FR=sk_live_...
  export STRIPE_SACMUSEUM_ACCOUNT_ID=acct_...
  python3 scripts/sacmuseum_h2_stripe.py
  STRIPE_PAYOUT_CONFIRM=1 python3 scripts/sacmuseum_h2_stripe.py

Variables opcionales:
  HITO2_BRUTO_EUR=27500  PRIMA_RATE=0.15  STRIPE_PAYOUT_DESCRIPTOR=SACT_H2_FINAL

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from stripe_verify_secret_env import resolve_stripe_secret  # noqa: E402


def _maybe_load_dotenv() -> None:
    if (os.environ.get("SACMUSEUM_LOAD_DOTENV") or "").strip() != "1":
        return
    try:
        from dotenv import load_dotenv
    except ImportError:
        print(
            "SACMUSEUM_LOAD_DOTENV=1 requiere: pip install python-dotenv",
            file=sys.stderr,
        )
        return
    load_dotenv(_ROOT / ".env")


def _req_field(obj: object, *path: str) -> object:
    cur: object = obj
    for p in path:
        if cur is None:
            return None
        if isinstance(cur, dict):
            cur = cur.get(p)
        else:
            cur = getattr(cur, p, None)
    return cur


def _print_balance_lines(label: str, items: object) -> None:
    if not items:
        print(f"  {label}: —")
        return
    if not isinstance(items, list):
        print(f"  {label}: {items!r}")
        return
    for x in items:
        if isinstance(x, dict):
            amt = int(x.get("amount", 0)) / 100.0
            cur = str(x.get("currency", "?")).upper()
        else:
            amt = int(getattr(x, "amount", 0) or 0) / 100.0
            cur = str(getattr(x, "currency", "?") or "?").upper()
        print(f"  {label}: {amt:.2f} {cur}")


def main() -> int:
    sk = resolve_stripe_secret()
    if not sk:
        print(
            "Define STRIPE_SECRET_KEY_FR (u otra clave secreta de la plataforma) en el entorno.",
            file=sys.stderr,
        )
        return 1

    acct_id = (
        (os.environ.get("STRIPE_SACMUSEUM_ACCOUNT_ID") or "").strip()
        or (os.environ.get("STRIPE_CONNECT_ACCOUNT_ID_FR") or "").strip()
        or (os.environ.get("STRIPE_ACCOUNT_ID") or "").strip()
    )
    if not acct_id.startswith("acct_"):
        print(
            "Define STRIPE_SACMUSEUM_ACCOUNT_ID=acct_…, STRIPE_CONNECT_ACCOUNT_ID_FR=acct_… "
            "o STRIPE_ACCOUNT_ID=acct_…",
            file=sys.stderr,
        )
        return 1

    try:
        bruto = float((os.environ.get("HITO2_BRUTO_EUR") or "27500").replace(",", "."))
    except ValueError:
        bruto = 27500.0
    try:
        tasa = float((os.environ.get("PRIMA_RATE") or "0.15").replace(",", "."))
    except ValueError:
        tasa = 0.15
    prima = bruto * tasa
    neto = bruto - prima
    neto_cents = int(round(neto * 100))

    confirm = os.environ.get("STRIPE_PAYOUT_CONFIRM", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )
    currency = (os.environ.get("STRIPE_PAYOUT_CURRENCY") or "eur").strip().lower()
    stmt_desc = (
        (os.environ.get("STRIPE_PAYOUT_DESCRIPTOR") or "SACT_H2_FINAL").strip()
    )[:22]

    import stripe

    stripe.api_key = sk

    payout_id = "— (no ejecutado)"
    verif_summary = "—"
    docs_pending = "—"

    print(f"SacMuseum / Hito 2 — {datetime.now().isoformat(timespec='seconds')}")
    print("-" * 70)

    try:
        acc = stripe.Account.retrieve(acct_id)
    except stripe.error.StripeError as e:
        print(f"Cuenta: error Stripe — {e.user_message or e}", file=sys.stderr)
        return 2

    disabled = _req_field(acc, "requirements", "disabled_reason")
    currently_due = _req_field(acc, "requirements", "currently_due") or []
    details_submitted = _req_field(acc, "details_submitted")
    charges_enabled = _req_field(acc, "charges_enabled")
    payouts_enabled = _req_field(acc, "payouts_enabled")

    if not isinstance(currently_due, list):
        currently_due = list(currently_due) if currently_due else []

    verif_summary = (
        f"details_submitted={details_submitted}; charges_enabled={charges_enabled}; "
        f"payouts_enabled={payouts_enabled}; disabled_reason={disabled or '—'}"
    )
    docs_pending = (
        "; ".join(str(x) for x in currently_due) if currently_due else "(ninguno en currently_due)"
    )

    print(f"Cuenta: {acct_id}")
    print(verif_summary)
    print(f"requirements.currently_due: {docs_pending}")

    print("-" * 70)
    print("Liquidación (referencia interna; no asesoría fiscal):")
    print(f"  Bruto:        {bruto:,.2f} €")
    print(f"  Prima ({tasa*100:g}%): {prima:,.2f} €")
    print(f"  Neto a enviar: {neto:,.2f} € ({neto_cents} céntimos)")

    try:
        bal = stripe.Balance.retrieve(stripe_account=acct_id)
    except stripe.error.StripeError as e:
        print(f"Balance (conectada): error — {e.user_message or e}", file=sys.stderr)
        return 3

    print("-" * 70)
    print("Balance (cuenta conectada):")
    _print_balance_lines("available", getattr(bal, "available", None))
    _print_balance_lines("pending", getattr(bal, "pending", None))

    if not confirm:
        print("-" * 70)
        print("[DRY-RUN] No se creó payout. Para ejecutar: STRIPE_PAYOUT_CONFIRM=1")
        print("-" * 70)
        _print_final_table(
            acct_id,
            verif_summary,
            docs_pending,
            payout_id,
            neto,
            stmt_desc,
        )
        return 0

    # Importe disponible en la moneda pedida
    available = getattr(bal, "available", None) or []
    avail_cents = 0
    for x in available:
        if isinstance(x, dict):
            cur = str(x.get("currency", "")).lower()
            amt = int(x.get("amount", 0))
        else:
            cur = str(getattr(x, "currency", "") or "").lower()
            amt = int(getattr(x, "amount", 0) or 0)
        if cur == currency:
            avail_cents = amt
            break
    if avail_cents == 0 and available:
        first = available[0]
        if isinstance(first, dict):
            avail_cents = int(first.get("amount", 0))
            currency = str(first.get("currency", currency)).lower()
        else:
            avail_cents = int(getattr(first, "amount", 0) or 0)
            currency = str(getattr(first, "currency", currency) or currency).lower()

    if avail_cents < neto_cents:
        print(
            f"No hay fondos available suficientes ({avail_cents/100:.2f} < {neto:.2f} {currency.upper()}).",
            file=sys.stderr,
        )
        print("-" * 70)
        _print_final_table(
            acct_id,
            verif_summary,
            docs_pending,
            "— (saldo available insuficiente)",
            neto,
            stmt_desc,
        )
        return 4

    try:
        payout = stripe.Payout.create(
            amount=neto_cents,
            currency=currency,
            description="Liquidación Hito 2 - SacMuseum",
            statement_descriptor=stmt_desc,
            stripe_account=acct_id,
        )
        payout_id = str(getattr(payout, "id", "?"))
        print("-" * 70)
        print(f"Payout creado: {payout_id}")
    except stripe.error.StripeError as e:
        print(f"Payout: error — {e.user_message or e}", file=sys.stderr)
        payout_id = f"ERROR: {e.user_message or e}"
        print("-" * 70)
        _print_final_table(
            acct_id,
            verif_summary,
            docs_pending,
            payout_id,
            neto,
            stmt_desc,
        )
        return 5

    print("-" * 70)
    _print_final_table(
        acct_id,
        verif_summary,
        docs_pending,
        payout_id,
        neto,
        stmt_desc,
    )
    return 0


def _print_final_table(
    acct_id: str,
    verif_summary: str,
    docs_pending: str,
    payout_id: str,
    neto: float,
    stmt_desc: str,
) -> None:
    print("TABLA RESUMEN")
    print(f"{'Campo':<22} | Valor")
    print("-" * 70)
    print(f"{'ID cuenta':<22} | {acct_id}")
    print(f"{'Estado verificación':<22} | {verif_summary[:200]}")
    print(f"{'Documentos pending':<22} | {docs_pending[:200]}")
    print(f"{'Neto objetivo (€)':<22} | {neto:,.2f}")
    print(f"{'Descriptor':<22} | {stmt_desc}")
    print(f"{'Payout ID (po_…)':<22} | {payout_id}")


if __name__ == "__main__":
    raise SystemExit(main())
