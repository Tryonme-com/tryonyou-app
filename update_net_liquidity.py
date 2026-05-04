#!/usr/bin/env python3
"""
Calcule le solde net (TTC − commissions) à partir de ``F-2026-001-PARTIAL.json``
et écrit ``master_ledger_status.json`` à la racine du dépôt.

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import json
import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INVOICE = ROOT / "F-2026-001-PARTIAL.json"
LEDGER = ROOT / "master_ledger_status.json"

STRIPE_FEE_RATE = Decimal("0.015")
QONTO_FEE_EUR = Decimal("25.00")


def main() -> int:
    if not INVOICE.is_file():
        print(f"Manque {INVOICE.name}", file=sys.stderr)
        return 2
    data = json.loads(INVOICE.read_text(encoding="utf-8"))
    totals = data.get("totals") or {}
    gross = Decimal(str(totals.get("total_ttc", "0")))
    stripe_fee = (gross * STRIPE_FEE_RATE).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    net = (gross - stripe_fee - QONTO_FEE_EUR).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    payload = {
        "source_invoice": INVOICE.name,
        "contract": (data.get("references") or {}).get("contract"),
        "milestone": (data.get("references") or {}).get("milestone"),
        "currency": "EUR",
        "gross_ttc_eur": float(gross),
        "stripe_fee_rate": float(STRIPE_FEE_RATE),
        "stripe_commission_eur": float(stripe_fee),
        "qonto_commission_eur": float(QONTO_FEE_EUR),
        "net_deployable_eur": float(net),
        "status": "LIQUIDITY_DEPLOYABLE",
    }

    LEDGER.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    def _fmt_eu(d: Decimal) -> str:
        s = f"{d:,.2f}"
        return s.replace(",", "|").replace(".", ",").replace("|", ".")

    print(f"✅ SISTEMA SINCRONIZADO. SALDO DISPONIBLE: {_fmt_eu(net)} €")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
