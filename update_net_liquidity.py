#!/usr/bin/env python3
"""Divineo V7 — calcul net + écriture ``master_ledger_status.json`` (local)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "master_ledger_status.json"

GROSS_EUR = 484_908.00
STRIPE_FEE_EUR = 7_273.62  # 1,5 %
QONTO_FEE_EUR = 25.00
NET_EUR = round(GROSS_EUR - STRIPE_FEE_EUR - QONTO_FEE_EUR, 2)


def main() -> None:
    if NET_EUR != 477_609.38:
        raise SystemExit(f"NET incohérent: {NET_EUR}")
    payload = {
        "schema": "divineo_v7_net_liquidity_v1",
        "updated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "invoice_ref": "F-2026-001-PARTIAL",
        "gross_eur": GROSS_EUR,
        "stripe_fee_eur": STRIPE_FEE_EUR,
        "qonto_fee_eur": QONTO_FEE_EUR,
        "net_deployable_eur": NET_EUR,
        "status": "LIQUIDITY_DEPLOYABLE",
        "currency": "EUR",
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    cents_total = int(round(NET_EUR * 100 + 1e-9))
    mag, c = divmod(cents_total, 100)
    body = f"{mag:,}".replace(",", ".")
    print(f"✅ SISTEMA SINCRONIZADO. SALDO DISPONIBLE: {body},{c:02d} €")


if __name__ == "__main__":
    main()
