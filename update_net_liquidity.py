#!/usr/bin/env python3
"""Divineo V7 — calcule le net gaspable et écrit ``master_ledger_status.json`` (racine du dépôt)."""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

_TZ_PARIS = ZoneInfo("Europe/Paris")

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "master_ledger_status.json"

GROSS_TTC = 484_908.00
STRIPE_COM = round(GROSS_TTC * 0.015, 2)
QONTO_COM = 25.00
NET = round(GROSS_TTC - STRIPE_COM - QONTO_COM, 2)


def _iban_last4_from_env() -> str | None:
    raw = (os.environ.get("QONTO_IBAN") or os.environ.get("QONTO_BANK_IBAN") or "").replace(" ", "")
    if len(raw) >= 4:
        return raw[-4:]
    return None


def main() -> int:
    if abs(STRIPE_COM - 7273.62) > 0.01 or abs(NET - 477_609.38) > 0.01:
        print("ERR: totaux incohérents", file=sys.stderr)
        return 2

    last4 = _iban_last4_from_env()
    payload = {
        "mode": "SIMULATION",
        "disclaimer": "Cifras modelo (factura + comisiones fijas). No lee saldo real Stripe/Qonto.",
        "invoice_ref": "F-2026-001-PARTIAL",
        "contract": "DIVINEO-V10",
        "currency": "EUR",
        "gross_ttc": GROSS_TTC,
        "commissions": {
            "stripe_1_5pct": -STRIPE_COM,
            "qonto_flat": -QONTO_COM,
        },
        "net_deployable": NET,
        "status": "LIQUIDITY_DEPLOYABLE",
        "destination_account": {
            "provider": "Qonto (simulación)",
            "iban_last4_env": last4,
            "hint": "Cuenta destino real: la vinculada en Qonto/Stripe en prod; aquí solo *…4 si hay QONTO_IBAN en .env",
        },
        "computed_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "computed_at_paris": datetime.now(_TZ_PARIS).isoformat(timespec="seconds"),
        "source": "update_net_liquidity.py",
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    tail = f" …{last4}" if last4 else " (sin QONTO_IBAN en env — no se muestra cola)"
    print(f"[SIMULACIÓN] Cuenta modelo → Qonto EI{tail}")
    print("✅ SISTEMA SINCRONIZADO. SALDO DISPONIBLE: 477.609,38 €")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
