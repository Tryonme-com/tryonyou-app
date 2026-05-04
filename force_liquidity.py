#!/usr/bin/env python3
"""
Orquestador mínimo de liquidez (TryOnYou búnker).

Por defecto:
  1) Un ciclo de polling Qonto → ``force_qonto_collection.py --once``
  2) Mensaje de siguiente paso para payout Stripe real → ``logic/finance_bridge.py``
     (solo se ejecuta si ``FINANCE_BRIDGE_FORCE_STEP=1`` en entorno; evita payout accidental).

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def _run(script: str, *args: str) -> int:
    cmd = [sys.executable, str(ROOT / script), *args]
    print(f"[force_liquidity] {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=str(ROOT)).returncode


def main() -> int:
    guard = _run("dossier_fatality_guard.py")
    if guard == 0:
        print("[force_liquidity] Dossier Fatality: activado con evidencia verificable.")
    else:
        print("[force_liquidity] Dossier Fatality: pendiente; no se activa protección sin evidencia.")

    r = _run("force_qonto_collection.py", "--once")
    if r != 0:
        print(
            "[force_liquidity] Qonto: revisa QONTO_API_KEY o QONTO_LOGIN+QONTO_SECRET_KEY, "
            "TARGET_AMOUNT_*, FORCE_QONTO_COLLECTION_MODE.",
            file=sys.stderr,
        )

    if (os.environ.get("FINANCE_BRIDGE_FORCE_STEP") or "").strip() == "1":
        print("[force_liquidity] FINANCE_BRIDGE_FORCE_STEP=1 → ejecutando logic/finance_bridge.py …")
        r2 = _run("logic/finance_bridge.py")
        if r2 != 0:
            return r2
    else:
        print(
            "[force_liquidity] Stripe payout: no ejecutado. "
            "Para intentar payout real: FINANCE_BRIDGE_LIVE_PAYOUT=1, gates de tesorería, "
            "y opcionalmente FINANCE_BRIDGE_FORCE_STEP=1 con este script."
        )

    return r


if __name__ == "__main__":
    raise SystemExit(main())
