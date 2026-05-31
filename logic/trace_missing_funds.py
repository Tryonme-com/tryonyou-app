"""
Rastreo de liquidez Empire: saldos Hello Bank (varias cuentas, todas positivas)
frente al capital esperado Lafayette / SEPA.

Patente PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import os
import sys
from typing import Final

# Saldos por defecto: dos cuentas Hello en positivo (no negativos).
_DEFAULT_HELLO_BALANCES_EUR: Final[tuple[float, ...]] = (63.0, 237.0)
_EXPECTED_CAPITAL_EUR: Final[float] = 27_500.00


def _parse_hello_balances_from_env() -> tuple[float, ...]:
    raw = os.getenv("HELLO_BALANCES_EUR", "").strip()
    if not raw:
        return _DEFAULT_HELLO_BALANCES_EUR
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    if not parts:
        return _DEFAULT_HELLO_BALANCES_EUR
    return tuple(float(p) for p in parts)


def trace_missing_funds(
    *,
    hello_balances_eur: tuple[float, ...] | None = None,
    expected: float = _EXPECTED_CAPITAL_EUR,
) -> str:
    """
    Suma saldos Hello (todos deben ser >= 0) y compara con el capital esperado.
    """
    balances = hello_balances_eur if hello_balances_eur is not None else _parse_hello_balances_from_env()
    if any(b < 0 for b in balances):
        print("--- RASTREO DE SOBERANÍA: ERROR DE LIQUIDEZ ---")
        print("[!] ALERTA: Se detectó saldo negativo en alguna cuenta Hello (revisar extracto).")
        return "FONDOS_NO_DETECTADOS"

    total = round(sum(balances), 2)
    print("--- RASTREO DE SOBERANÍA: ERROR DE LIQUIDEZ ---")
    for i, saldo in enumerate(balances, start=1):
        print(f"[*] Hello Bank cuenta {i}: {saldo:.2f} EUR (positivo).")
    print(f"[*] Disponible agregado Hello: {total:.2f} EUR. Ninguna cuenta en negativo.")

    if total < expected:
        print(
            f"[!] ALERTA: Disponible agregado ({total:.2f} EUR) por debajo del capital "
            f"esperado ({expected:.2f} EUR)."
        )
        print("[!] ESTADO: El capital de Lafayette sigue en la red SEPA.")
        print("[!] ACCIÓN: Jules bloquea pagos hasta recepción real.")
        return "FONDOS_NO_DETECTADOS"
    return "FONDOS_OK"


def main() -> int:
    result = trace_missing_funds()
    return 0 if result == "FONDOS_OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
