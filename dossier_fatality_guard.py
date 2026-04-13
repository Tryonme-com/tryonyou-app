#!/usr/bin/env python3
"""
Guardia de seguridad para activación de Dossier Fatality.

Regla operativa:
  - Solo intenta confirmación automática en martes a las 08:00 (o después).
  - Nunca "inventa" ingresos: requiere evidencia explícita en un ledger JSON.
  - Si detecta el ingreso confirmado (>= 450000 EUR), activa estado fatality.

Uso:
  python3 dossier_fatality_guard.py
  python3 dossier_fatality_guard.py --ledger logs/capital_inflows.json
  python3 dossier_fatality_guard.py --now "2026-04-14T08:00:00"
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_LEDGER = ROOT / "logs" / "capital_inflows.json"
DEFAULT_DOSSIER = ROOT / "dossier_fatality.json"
DEFAULT_STATE = ROOT / "logs" / "dossier_fatality_state.json"
EXPECTED_AMOUNT_EUR = 450_000.00


@dataclass
class GuardResult:
    activated: bool
    reason: str
    evidence: dict[str, Any] | None = None


def is_tuesday_0800_or_later(now: datetime) -> bool:
    # Monday=0 ... Sunday=6; Tuesday=1.
    if now.weekday() != 1:
        return False
    return now.hour >= 8


def _iter_entries(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    if isinstance(payload, dict):
        # Formatos habituales: {"entries":[...]}, {"transactions":[...]} o único registro.
        for key in ("entries", "transactions", "items", "data"):
            value = payload.get(key)
            if isinstance(value, list):
                return [x for x in value if isinstance(x, dict)]
        return [payload]
    return []


def _to_float(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        normalized = value.replace("€", "").replace(" ", "").strip()
        if "," in normalized and "." in normalized:
            # Formato europeo típico: 450.000,00
            normalized = normalized.replace(".", "").replace(",", ".")
        elif "," in normalized:
            # Formato decimal con coma: 450000,00
            normalized = normalized.replace(",", ".")
        try:
            return float(normalized)
        except ValueError:
            return None
    return None


def find_confirmed_inflow(ledger_path: Path, expected_amount: float) -> dict[str, Any] | None:
    if not ledger_path.exists():
        return None
    payload = json.loads(ledger_path.read_text(encoding="utf-8"))
    for row in _iter_entries(payload):
        amount = _to_float(row.get("amount") or row.get("importe") or row.get("monto"))
        if amount is None:
            continue
        currency = str(row.get("currency") or row.get("moneda") or "EUR").upper()
        status = str(row.get("status") or row.get("estado") or "").lower()
        confirmed = bool(row.get("confirmed", False)) or status in {"confirmed", "settled", "ok"}
        if currency == "EUR" and confirmed and amount >= expected_amount:
            return row
    return None


def activate_fatality_state(*, dossier_path: Path, state_path: Path, now: datetime, evidence: dict[str, Any]) -> None:
    if not dossier_path.exists():
        raise FileNotFoundError(f"No existe dossier base: {dossier_path}")

    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_payload = {
        "fatality_active": True,
        "activated_at": now.isoformat(),
        "policy": "Dossier Fatality V10",
        "patent": "PCT/EP2025/067317",
        "founder_protocol": "Bajo Protocolo de Soberanía V10 - Founder: Rubén",
        "evidence": evidence,
    }
    state_path.write_text(
        json.dumps(state_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def run_guard(*, now: datetime, ledger_path: Path, dossier_path: Path, state_path: Path, expected_amount: float) -> GuardResult:
    if not is_tuesday_0800_or_later(now):
        return GuardResult(
            activated=False,
            reason="Fuera de ventana operativa (martes >= 08:00).",
        )

    evidence = find_confirmed_inflow(ledger_path, expected_amount)
    if evidence is None:
        return GuardResult(
            activated=False,
            reason="Sin evidencia confirmada del ingreso esperado en ledger JSON.",
        )

    activate_fatality_state(
        dossier_path=dossier_path,
        state_path=state_path,
        now=now,
        evidence=evidence,
    )
    return GuardResult(
        activated=True,
        reason="Ingreso confirmado y Dossier Fatality activado.",
        evidence=evidence,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Guardia martes 08:00 para Dossier Fatality.")
    parser.add_argument("--ledger", default=str(DEFAULT_LEDGER), help="Ruta ledger JSON de ingresos.")
    parser.add_argument("--dossier", default=str(DEFAULT_DOSSIER), help="Ruta de dossier base.")
    parser.add_argument("--state", default=str(DEFAULT_STATE), help="Ruta de estado fatality.")
    parser.add_argument(
        "--expected-amount",
        type=float,
        default=EXPECTED_AMOUNT_EUR,
        help="Importe mínimo esperado en EUR para activar.",
    )
    parser.add_argument(
        "--now",
        default="",
        help="Timestamp ISO para pruebas (ej. 2026-04-14T08:00:00).",
    )
    args = parser.parse_args(argv)

    now = datetime.fromisoformat(args.now) if args.now else datetime.now()
    result = run_guard(
        now=now,
        ledger_path=Path(args.ledger),
        dossier_path=Path(args.dossier),
        state_path=Path(args.state),
        expected_amount=args.expected_amount,
    )
    print(result.reason)
    if result.evidence:
        print(json.dumps(result.evidence, ensure_ascii=False))
    return 0 if result.activated else 1


if __name__ == "__main__":
    raise SystemExit(main())
