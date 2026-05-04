#!/usr/bin/env python3
"""Actualiza master_ledger_status.json a partir de F-2026-001-PARTIAL.json (totales TTC y comisiones)."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INV = ROOT / "F-2026-001-PARTIAL.json"
OUT = ROOT / "master_ledger_status.json"

STRIPE_FEE_RATE = 0.015
QONTO_FEE_EUR = 25.0


def _fmt_eur_es(n: float) -> str:
    sign = "-" if n < 0 else ""
    n = abs(n)
    whole_s, frac = f"{n:.2f}".split(".")
    parts: list[str] = []
    while whole_s:
        parts.append(whole_s[-3:])
        whole_s = whole_s[:-3]
    body = ".".join(reversed(parts)) if parts else "0"
    return f"{sign}{body},{frac}"


def main() -> int:
    if not INV.is_file():
        print(f"Falta {INV.name}", file=sys.stderr)
        return 2
    inv = json.loads(INV.read_text(encoding="utf-8"))
    ttc = float((inv.get("totals") or {}).get("total_ttc_eur") or 0)
    stripe_fee = round(ttc * STRIPE_FEE_RATE, 2)
    net = round(ttc - stripe_fee - QONTO_FEE_EUR, 2)
    payload = {
        "invoice_reference": (inv.get("invoice_reference") or "F-2026-001-PARTIAL"),
        "gross_ttc_eur": ttc,
        "stripe_fee_rate": STRIPE_FEE_RATE,
        "stripe_commission_eur": stripe_fee,
        "qonto_commission_eur": QONTO_FEE_EUR,
        "net_deployable_eur": net,
        "status": "LIQUIDITY_DEPLOYABLE",
        "updated_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"OK {OUT.name} net={net:.2f} EUR")
    print(f"✅ SISTEMA SINCRONIZADO. SALDO DISPONIBLE: {_fmt_eur_es(net)} €")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
