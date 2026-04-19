#!/usr/bin/env python3
"""
dossier_fatality_guard.py

Guardia de seguridad para activar Dossier Fatality solo cuando:
1) Es martes a las 08:00 (hora local), y
2) Existe evidencia verificable de entrada de 450000.00 EUR.

Sin ambas condiciones, el estado queda en PENDING_VALIDATION.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

TARGET_AMOUNT = 450000.00
TARGET_WEEKDAY = 1  # Monday=0, Tuesday=1
TARGET_HOUR = 8

ROOT = Path(__file__).resolve().parent
EMERGENCY_PAYOUT_FILE = ROOT / ".emergency_payout"
STATUS_FILE = ROOT / "dossier_fatality_status.json"


@dataclass
class GuardResult:
    status: str
    reason: str
    amount_confirmed: float
    schedule_ok: bool


def _parse_amount_file(path: Path) -> float:
    if not path.exists():
        return 0.0

    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("AMOUNT="):
            try:
                return float(line.split("=", 1)[1].strip())
            except ValueError:
                return 0.0
    return 0.0


def _is_tuesday_0800(now: datetime) -> bool:
    return now.weekday() == TARGET_WEEKDAY and now.hour == TARGET_HOUR


def evaluate_guard(now: datetime | None = None) -> GuardResult:
    now = now or datetime.now()
    amount_in_file = _parse_amount_file(EMERGENCY_PAYOUT_FILE)

    # Confirmación explícita desde entorno para evitar afirmaciones no verificadas.
    env_confirmed = os.getenv("TRYONYOU_CAPITAL_450K_CONFIRMED", "").strip() == "1"
    amount_ok = abs(amount_in_file - TARGET_AMOUNT) < 0.0001
    schedule_ok = _is_tuesday_0800(now)

    if schedule_ok and amount_ok and env_confirmed:
        return GuardResult(
            status="DOSSIER_FATALITY_ARMED",
            reason="Ventana martes 08:00 + monto 450000 EUR validado y confirmado.",
            amount_confirmed=amount_in_file,
            schedule_ok=True,
        )

    reason_parts = []
    if not schedule_ok:
        reason_parts.append("Fuera de ventana martes 08:00")
    if not amount_ok:
        reason_parts.append("Monto no verificable en .emergency_payout")
    if not env_confirmed:
        reason_parts.append("Falta TRYONYOU_CAPITAL_450K_CONFIRMED=1")

    return GuardResult(
        status="PENDING_VALIDATION",
        reason="; ".join(reason_parts),
        amount_confirmed=amount_in_file,
        schedule_ok=schedule_ok,
    )


def persist_result(result: GuardResult, now: datetime | None = None) -> None:
    now = now or datetime.now()
    payload = {
        "status": result.status,
        "reason": result.reason,
        "amount_confirmed": result.amount_confirmed,
        "target_amount": TARGET_AMOUNT,
        "schedule_ok": result.schedule_ok,
        "timestamp": now.isoformat(),
    }
    STATUS_FILE.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    result = evaluate_guard()
    persist_result(result)
    print(f"[DOSSIER_FATALITY] status={result.status}")
    print(f"[DOSSIER_FATALITY] reason={result.reason}")
    return 0 if result.status == "DOSSIER_FATALITY_ARMED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
