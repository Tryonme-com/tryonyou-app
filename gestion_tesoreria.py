"""
Gestión de tesorería — control de supervivencia operativa (Jules V7, ejecución diaria).

  export TESORERIA_SALDO='600'
  python3 gestion_tesoreria.py
"""

from __future__ import annotations

import os
import sys


def control_supervivencia(saldo_actual: float) -> str:
    gastos_fijos = {
        "Vercel": 20.00,
        "Google_Cloud": 50.00,
        "Logistica_Bunker": 500.00,  # comida y básicos (búnker)
    }
    total_mes = sum(gastos_fijos.values())
    if saldo_actual < total_mes:
        return (
            "⚠️ ALERTA: Riesgo de corte de servicios. Activar Bridge Financiero."
        )
    return "✅ Operativa asegurada hasta el 9 de Mayo."


def main() -> int:
    raw = os.environ.get("TESORERIA_SALDO", "").strip()
    if not raw:
        print("Set TESORERIA_SALDO and run again.", file=sys.stderr)
        return 1
    try:
        saldo = float(raw.replace(",", "."))
    except ValueError:
        print("TESORERIA_SALDO must be a number.", file=sys.stderr)
        return 1
    print(control_supervivencia(saldo))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
