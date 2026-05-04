#!/usr/bin/env python3
"""Guard seguro para la activacion del Dossier Fatality.

No confirma fondos por si mismo. Solo permite activar la proteccion de capital
cuando coinciden tres evidencias: ventana martes 08:00, flag operativo explicito
y prueba local verificable de ingreso bancario/Qonto por al menos 450.000 EUR.
"""
from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

MIN_AMOUNT_CENTS = 45_000_000
DEFAULT_EVIDENCE_PATH = Path("capital_450k_evidence.json")
CONFIRM_ENV = "TRYONYOU_CAPITAL_450K_CONFIRMED"
EVIDENCE_ENV = "TRYONYOU_CAPITAL_EVIDENCE_PATH"
STATUS_ACTIVE = "DOSSIER_FATALITY_ACTIVE"
STATUS_PENDING = "PENDING_VALIDATION"


@dataclass(frozen=True)
class GuardResult:
    status: str
    active: bool
    reason: str
    checked_at: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "active": self.active,
            "reason": self.reason,
            "checked_at": self.checked_at,
        }


def _parse_datetime(value: str | None) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _is_activation_window(moment: datetime) -> bool:
    return moment.weekday() == 1 and moment.hour == 8


def _load_evidence(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        return None
    return data


def _evidence_is_valid(data: dict[str, Any] | None) -> bool:
    if not data:
        return False
    try:
        amount_cents = int(data.get("amount_cents", 0))
    except (TypeError, ValueError):
        return False
    source = str(data.get("source", "")).lower()
    reference = str(data.get("reference", "")).strip()
    currency = str(data.get("currency", "EUR")).upper()
    return (
        amount_cents >= MIN_AMOUNT_CENTS
        and currency == "EUR"
        and reference
        and any(marker in source for marker in ("qonto", "bank", "banque", "bancaria"))
    )


def evaluate_guard(
    *,
    now: datetime | None = None,
    evidence_path: Path | None = None,
    env: dict[str, str] | None = None,
) -> GuardResult:
    env_map = env if env is not None else os.environ
    checked_at = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    resolved_evidence_path = evidence_path or Path(env_map.get(EVIDENCE_ENV, str(DEFAULT_EVIDENCE_PATH)))

    if not _is_activation_window(checked_at):
        return GuardResult(
            status=STATUS_PENDING,
            active=False,
            reason="outside_tuesday_0800_utc_window",
            checked_at=checked_at.isoformat(),
        )

    if env_map.get(CONFIRM_ENV) != "1":
        return GuardResult(
            status=STATUS_PENDING,
            active=False,
            reason="missing_explicit_capital_confirmation_flag",
            checked_at=checked_at.isoformat(),
        )

    evidence = _load_evidence(resolved_evidence_path)
    if not _evidence_is_valid(evidence):
        return GuardResult(
            status=STATUS_PENDING,
            active=False,
            reason="missing_or_invalid_450k_evidence",
            checked_at=checked_at.isoformat(),
        )

    return GuardResult(
        status=STATUS_ACTIVE,
        active=True,
        reason="verified_window_flag_and_local_evidence",
        checked_at=checked_at.isoformat(),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Valida activacion segura del Dossier Fatality.")
    parser.add_argument("--now", default=None, help="Fecha ISO para pruebas controladas.")
    parser.add_argument(
        "--evidence",
        default=None,
        help=f"Ruta JSON de evidencia (por defecto: ${EVIDENCE_ENV} o {DEFAULT_EVIDENCE_PATH}).",
    )
    parser.add_argument("--json", action="store_true", help="Imprime salida JSON compacta.")
    args = parser.parse_args(argv)

    evidence_path = Path(args.evidence) if args.evidence else None
    result = evaluate_guard(now=_parse_datetime(args.now), evidence_path=evidence_path)
    payload = result.as_dict()
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
    return 0 if result.active else 3


if __name__ == "__main__":
    raise SystemExit(main())
