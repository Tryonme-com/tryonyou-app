"""
Rastreo de liquidez genérico: compara saldos Hello configurados con umbral en entorno.

Patente PCT/EP2025/067317
"""

from __future__ import annotations

import os
import sys
from typing import Final

_DEFAULT_HELLO_BALANCES_EUR: Final[tuple[float, ...]] = (0.0, 0.0)


def _parse_hello_balances_from_env() -> tuple[float, ...]:
    raw = os.getenv("HELLO_BALANCES_EUR", "").strip()
    if not raw:
        return _DEFAULT_HELLO_BALANCES_EUR
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    if not parts:
        return _DEFAULT_HELLO_BALANCES_EUR
    return tuple(float(p) for p in parts)


def _expected_capital_eur() -> float:
    raw = (os.getenv("TREASURY_EXPECTED_BALANCE_EUR") or "0").strip()
    try:
        return float(raw)
    except ValueError:
        return 0.0


def trace_missing_funds(
    *,
    hello_balances_eur: tuple[float, ...] | None = None,
    expected: float | None = None,
) -> str:
    balances = hello_balances_eur if hello_balances_eur is not None else _parse_hello_balances_from_env()
    target = _expected_capital_eur() if expected is None else float(expected)

    if any(b < 0 for b in balances):
        print("--- RASTREO DE LIQUIDEZ: ERROR ---")
        print("[!] Saldo negativo detectado en alguna cuenta Hello.")
        return "FONDOS_NO_DETECTADOS"

    total = round(sum(balances), 2)
    print("--- RASTREO DE LIQUIDEZ ---")
    for i, saldo in enumerate(balances, start=1):
        print(f"[*] Hello Bank cuenta {i}: {saldo:.2f} EUR.")
    print(f"[*] Disponible agregado Hello: {total:.2f} EUR.")

    if target <= 0:
        print("[*] Sin TREASURY_EXPECTED_BALANCE_EUR configurado. Solo informe, sin umbral.")
        return "FONDOS_OK"

    if total < target:
        print(
            f"[!] Disponible ({total:.2f} EUR) por debajo del umbral configurado "
            f"({target:.2f} EUR)."
        )
        return "FONDOS_NO_DETECTADOS"
    return "FONDOS_OK"


def main() -> int:
    result = trace_missing_funds()
    return 0 if result == "FONDOS_OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
