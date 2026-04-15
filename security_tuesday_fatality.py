#!/usr/bin/env python3
"""
Validacion de seguridad del hito financiero:
- Martes a las 08:00 (hora local): verificar ingreso objetivo (450000 EUR por defecto).
- Si se confirma, activar el Dossier Fatality en logs operativos.

No usa secretos en codigo: toda credencial externa se inyecta por entorno.
"""

from __future__ import annotations

import csv
import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
PAYMENTS_CSV = Path(os.getenv("FATALITY_PAYMENTS_CSV", str(ROOT / "registro_pagos_hoy.csv")))
DOSSIER_SOURCE = Path(os.getenv("FATALITY_DOSSIER_SOURCE", str(ROOT / "dossier_fatality.json")))
REPORT_PATH = Path(
    os.getenv("FATALITY_REPORT_PATH", str(ROOT / "logs" / "dossier_fatality_activation.json"))
)
EXPECTED_AMOUNT = float(os.getenv("FATALITY_EXPECTED_AMOUNT_EUR", "450000"))


@dataclass
class FatalityResult:
    status: str
    detail: str
    schedule_ok: bool
    amount_confirmed: float
    expected_amount: float
    timestamp: str


def _now() -> datetime:
    # Permite pruebas reproducibles sin tocar reloj del sistema.
    fake_now = os.getenv("FATALITY_NOW_ISO", "").strip()
    if fake_now:
        return datetime.fromisoformat(fake_now)
    return datetime.now()


def _is_tuesday_8am(dt: datetime) -> bool:
    # Tuesday=1; aceptamos cualquier minuto de la hora 08 para ejecucion por cron.
    return dt.weekday() == 1 and dt.hour == 8


def _sum_confirmed_amount(csv_path: Path) -> float:
    if not csv_path.is_file():
        return 0.0
    total = 0.0
    with csv_path.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            state = str(row.get("estado", "")).strip().upper()
            if state != "CONFIRMADO":
                continue
            raw_amount = str(row.get("importe_eur", "0")).strip().replace(",", ".")
            try:
                total += float(raw_amount)
            except ValueError:
                continue
    return total


def _load_dossier_seed() -> dict[str, Any]:
    if not DOSSIER_SOURCE.is_file():
        return {"dossier_source": str(DOSSIER_SOURCE), "warning": "source_not_found"}
    try:
        return json.loads(DOSSIER_SOURCE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"dossier_source": str(DOSSIER_SOURCE), "warning": "invalid_json"}


def _write_report(result: FatalityResult) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    seed = _load_dossier_seed()
    payload = {
        "security_protocol": "Dossier Fatality",
        "activation": {
            "status": result.status,
            "detail": result.detail,
            "schedule_ok": result.schedule_ok,
            "expected_amount_eur": result.expected_amount,
            "confirmed_amount_eur": result.amount_confirmed,
            "timestamp_local": result.timestamp,
        },
        "dossier_seed": seed,
    }
    REPORT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def run_security_check() -> FatalityResult:
    now = _now()
    schedule_ok = _is_tuesday_8am(now)
    confirmed_amount = _sum_confirmed_amount(PAYMENTS_CSV)

    if not schedule_ok:
        result = FatalityResult(
            status="PENDING_SCHEDULE",
            detail="Fuera de ventana de ejecucion: se requiere martes 08:00.",
            schedule_ok=False,
            amount_confirmed=confirmed_amount,
            expected_amount=EXPECTED_AMOUNT,
            timestamp=now.isoformat(timespec="seconds"),
        )
        _write_report(result)
        return result

    if confirmed_amount >= EXPECTED_AMOUNT:
        result = FatalityResult(
            status="ACTIVATED",
            detail="Ingreso confirmado; Dossier Fatality activado para blindaje de capital.",
            schedule_ok=True,
            amount_confirmed=confirmed_amount,
            expected_amount=EXPECTED_AMOUNT,
            timestamp=now.isoformat(timespec="seconds"),
        )
        _write_report(result)
        return result

    result = FatalityResult(
        status="PENDING_FUNDS",
        detail="No se alcanza el umbral objetivo en pagos confirmados.",
        schedule_ok=True,
        amount_confirmed=confirmed_amount,
        expected_amount=EXPECTED_AMOUNT,
        timestamp=now.isoformat(timespec="seconds"),
    )
    _write_report(result)
    return result


def main() -> int:
    result = run_security_check()
    print(
        "[FATALITY]",
        f"status={result.status}",
        f"schedule_ok={result.schedule_ok}",
        f"confirmed={result.amount_confirmed:.2f}",
        f"expected={result.expected_amount:.2f}",
    )
    print(f"[FATALITY] {result.detail}")
    print(f"[FATALITY] Reporte: {REPORT_PATH}")
    # Retorno 0 para no bloquear despliegues, salvo que se solicite modo estricto.
    strict = os.getenv("FATALITY_STRICT", "").strip().lower() in {"1", "true", "yes", "on"}
    if strict and result.status != "ACTIVATED":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
