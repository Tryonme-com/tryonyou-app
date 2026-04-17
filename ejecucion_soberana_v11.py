"""
Ejecución soberana V11 para liquidación del Hito 2 (SacMuseum).

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import os
import sys
from typing import Any

import stripe


ACCOUNT_ID = "acct_1S5kek6bk9KySTMI"
DESCRIPTOR = "SACT_H2_FINAL"
CAPITAL_BRUTO_EUR = 27500
PRIMA_RATE = 0.15


def _load_env_key(key_name: str, env_path: str) -> str:
    if not os.path.exists(env_path):
        return ""
    value = ""
    with open(env_path, "r", encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[len("export ") :].strip()
            if "=" not in line:
                continue
            k, v = line.split("=", 1)
            if k.strip() != key_name:
                continue
            candidate = v.strip().strip('"').strip("'")
            value = candidate
    return value


def _to_dict(obj: Any) -> dict[str, Any]:
    if isinstance(obj, dict):
        return obj
    if hasattr(obj, "to_dict_recursive"):
        return obj.to_dict_recursive()
    try:
        return dict(obj)
    except Exception:
        return {}


def _format_eur_compact(amount_eur: int) -> str:
    return f"{amount_eur:,}".replace(",", ".") + " €"


def _print_table(status: str, breakdown: str, payout_or_docs: str) -> None:
    headers = [
        "Estado de Verificación",
        "Desglose: Bruto / Prima / Neto",
        "ID de Transferencia po_... / Lista de documentos pendientes",
    ]
    row = [status, breakdown, payout_or_docs]
    widths = [max(len(headers[i]), len(row[i])) for i in range(3)]

    sep = "+" + "+".join("-" * (w + 2) for w in widths) + "+"

    def fmt(cols: list[str]) -> str:
        return "| " + " | ".join(cols[i].ljust(widths[i]) for i in range(3)) + " |"

    print(sep)
    print(fmt(headers))
    print(sep)
    print(fmt(row))
    print(sep)


def main() -> int:
    prima_eur = int(round(CAPITAL_BRUTO_EUR * PRIMA_RATE))
    neto_eur = CAPITAL_BRUTO_EUR - prima_eur
    neto_cents = neto_eur * 100
    desglose = (
        f"{_format_eur_compact(CAPITAL_BRUTO_EUR)} / "
        f"{_format_eur_compact(prima_eur)} / "
        f"{_format_eur_compact(neto_eur)}"
    )

    sk = _load_env_key("STRIPE_SECRET_KEY", os.path.join(os.getcwd(), ".env"))
    if not sk.startswith("sk_live_"):
        if sk.startswith("sk_test_"):
            _print_table("BLOQUEO: Clave de prueba detectada", desglose, "-")
            return 0
        _print_table("BLOQUEO: STRIPE_SECRET_KEY inválida o ausente", desglose, "-")
        return 1

    stripe.api_key = sk

    try:
        account = stripe.Account.retrieve(ACCOUNT_ID)
        account_dict = _to_dict(account)
        account_status = str(account_dict.get("status") or "")
        requirements = account_dict.get("requirements") or {}
        currently_due = requirements.get("currently_due") or []
        if account_status == "pending.onboarding":
            docs = ", ".join(str(x) for x in currently_due) if currently_due else "Sin requisitos currently_due"
            _print_table("pending.onboarding", desglose, docs)
            return 0

        balance = stripe.Balance.retrieve(stripe_account=ACCOUNT_ID)
        balance_dict = _to_dict(balance)
        available = balance_dict.get("available") or []
        available_eur_cents = 0
        for item in available:
            entry = _to_dict(item)
            currency = str(entry.get("currency", "")).lower()
            if currency == "eur":
                available_eur_cents = int(entry.get("amount", 0) or 0)
                break

        if available_eur_cents < neto_cents:
            _print_table(
                f"LIVE OK | balance insuficiente ({available_eur_cents / 100:.2f} EUR)",
                desglose,
                "-",
            )
            return 0

        payout = stripe.Payout.create(
            amount=neto_cents,
            currency="eur",
            statement_descriptor=DESCRIPTOR,
            stripe_account=ACCOUNT_ID,
        )
        payout_id = _to_dict(payout).get("id") or getattr(payout, "id", "")
        payout_cell = str(payout_id) if str(payout_id).startswith("po_") else str(payout_id or "Sin ID")
        _print_table("LIVE OK | payout ejecutado", desglose, payout_cell)
        return 0
    except Exception as exc:
        _print_table("ERROR Stripe", desglose, str(exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
