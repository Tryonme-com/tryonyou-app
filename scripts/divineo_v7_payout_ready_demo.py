#!/usr/bin/env python3
"""
Demo narrativa «liquidez lista» (Jules / Divineo) — SOLO SIMULACIÓN LOCAL.

No sustituye ``financial_compliance``, Qonto ni Stripe. No afirmar verificación real.
Salida JSON: ``logs/divineo_v7_payout_ready_demo.json`` (no toca ``master_omega_vault.json``).

Variables opcionales (solo copy / demo):
  DEMO_PAYOUT_ENTITY_LABEL   etiqueta entidad (default genérico)
  DEMO_PAYOUT_ACCOUNT_HINT   texto acct_… (no es validación Stripe)

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_LOG = _ROOT / "logs" / "divineo_v7_payout_ready_demo.json"


def trigger_payout_ready_demo() -> int:
    print("[SIMULACIÓN] [DIVINEO V7] — guión local de liberación de liquidez (no es compliance real)")
    print("-" * 55)

    print("Paso 1 (demo): narrativa de cruce factura vs saldo — sin datos reales inyectados.")
    time.sleep(0.4)

    entity = (os.environ.get("DEMO_PAYOUT_ENTITY_LABEL") or "(definir entidad en env si usas demo)").strip()
    acct_hint = (os.environ.get("DEMO_PAYOUT_ACCOUNT_HINT") or "acct_… (conectar STRIPE_CONNECT_ACCOUNT_ID_FR en motor real)").strip()

    wallet_status = {
        "mode": "SIMULATION_ONLY",
        "account_hint": acct_hint,
        "entity_label": entity,
        "currency": "EUR",
        "status": "NARRATIVE_DEMO_NOT_DEPLOYABLE",
        "last_sync_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "note": "Para liquidez real: logic/finance_bridge.py + gates audit_log / financial_compliance.",
    }

    try:
        _LOG.parent.mkdir(parents=True, exist_ok=True)
        _LOG.write_text(json.dumps(wallet_status, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Paso 2: JSON demo escrito en {_LOG.relative_to(_ROOT)}")
    except OSError as e:
        print(f"Error al escribir log demo: {e}", file=sys.stderr)
        return 1

    print("\nResultado (demo): guión terminado. No implica capital gastable en producción.")
    print("Orquestación real: motor FinanceBridge / tesorería según variables del búnker.")
    print("-" * 55)
    return 0


if __name__ == "__main__":
    raise SystemExit(trigger_payout_ready_demo())
