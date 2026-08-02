"""
Simulación de payout Empire (demo local; no realiza transferencias bancarias).

Patente PCT/EP2025/067317
"""

from __future__ import annotations

import hashlib
import os
import sys
import time
from typing import Any, Final


def _transfer_threshold_eur() -> float:
    raw = (os.getenv("EMPIRE_TRANSFER_THRESHOLD_EUR") or "0").strip()
    try:
        return float(raw)
    except ValueError:
        return 0.0


def monitor_landing_sequence() -> str:
    """Simula comprobación de liquidez sin referencias a clientes ficticios."""
    expected_capital = _transfer_threshold_eur()
    print("--- SECUENCIA DE LIQUIDEZ (DEMO) ---")
    if expected_capital <= 0:
        print("[*] Sin EMPIRE_TRANSFER_THRESHOLD_EUR configurado. Modo demo inactivo.")
        return "DEMO_INACTIVE"
    print(f"[*] Umbral configurado: {expected_capital:.2f} EUR")
    print("[*] No se detectaron transferencias reales en esta simulación.")
    return "PENDING_MANUAL_VALIDATION"


class EmpirePayout:
    """Payout demo: firma temporal por SIREN + timestamp."""

    def __init__(self, amount_eur: float, siren_target: str) -> None:
        if amount_eur < 0:
            raise ValueError("amount_eur no puede ser negativo")
        if not siren_target or not str(siren_target).strip():
            raise ValueError("siren_target requerido")
        self.amount = amount_eur
        self.siren = str(siren_target).strip()
        self.timestamp = time.time()

    def validate_sovereignty(self) -> str:
        payload = f"{self.siren}{self.timestamp}".encode()
        return hashlib.sha256(payload).hexdigest()

    def execute_transfer(self) -> dict[str, Any]:
        threshold = _transfer_threshold_eur()
        if threshold > 0 and self.amount >= threshold:
            return {"status": "TRANSFER_INITIATED", "target_account": "QONTO_EMPIRE"}
        return {"status": "ERROR_FUNDS_NOT_FOUND", "reason": "threshold_not_met_or_unconfigured"}

    def finalize_fatality(self) -> dict[str, Any]:
        print(f"Demo payout: {self.amount} EUR (SIREN {self.siren})")
        return self.execute_transfer()


Empirepayout = EmpirePayout


if __name__ == "__main__":
    status = monitor_landing_sequence()
    if status != "SUCCESS":
        print(f"[*] Estado: {status}.")

    demo_amount = _transfer_threshold_eur()
    payout = EmpirePayout(demo_amount, "943610196")
    print(f"auth_token (demo): {payout.validate_sovereignty()[:16]}...")
    result = payout.finalize_fatality()
    print(result)
    sys.exit(0 if result.get("status") == "TRANSFER_INITIATED" else 1)
