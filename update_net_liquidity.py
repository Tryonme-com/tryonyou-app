#!/usr/bin/env python3
"""Calcule le solde net gaspisable et écrit ``master_ledger_status.json`` (racine)."""
from __future__ import annotations

import json
import sys
from decimal import Decimal
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
INVOICE = ROOT / "F-2026-001-PARTIAL.json"
LEDGER = ROOT / "master_ledger_status.json"

GROSS = Decimal("484908.00")
STRIPE_PCT = Decimal("0.015")
QONTO_FEE = Decimal("25.00")


def _format_fr_eur(amount: Decimal) -> str:
    q = amount.quantize(Decimal("0.01"))
    sign = "-" if q < 0 else ""
    s = f"{abs(q):.2f}"
    ip, frac = s.split(".")
    parts: list[str] = []
    while len(ip) > 3:
        parts.insert(0, ip[-3:])
        ip = ip[:-3]
    if ip:
        parts.insert(0, ip)
    return f"{sign}{'.'.join(parts)},{frac} €"


def main() -> int:
    gross = GROSS
    if INVOICE.is_file():
        try:
            inv = json.loads(INVOICE.read_text(encoding="utf-8"))
            t = (inv.get("totals") or {}).get("total_ttc")
            if t is not None:
                gross = Decimal(str(t))
        except (OSError, json.JSONDecodeError, ValueError):
            pass

    stripe_fee = (gross * STRIPE_PCT).quantize(Decimal("0.01"))
    net = (gross - stripe_fee - QONTO_FEE).quantize(Decimal("0.01"))

    payload = {
        "schema": "master_ledger_status_v1",
        "invoice_ref": "F-2026-001-PARTIAL",
        "contract_ref": "DIVINEO-V10",
        "currency": "EUR",
        "gross_ttc": float(gross),
        "stripe_fee_rate": float(STRIPE_PCT),
        "stripe_fee_amount": float(stripe_fee),
        "qonto_fee_amount": float(QONTO_FEE),
        "net_deployable": float(net),
        "net_deployable_formatted": _format_fr_eur(net),
        "status": "LIQUIDITY_DEPLOYABLE",
        "last_sync_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }

    LEDGER.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"✅ SISTEMA SINCRONIZADO. SALDO DISPONIBLE: {_format_fr_eur(net)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
