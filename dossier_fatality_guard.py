#!/usr/bin/env python3
"""Guard rail for the 450k capital protection gate.

The Dossier Fatality can only be activated with verifiable local evidence and an
explicit operator flag. This script never confirms bank/Qonto movements by
itself.
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from datetime import datetime, time, timezone
from pathlib import Path
from zoneinfo import ZoneInfo


MINIMUM_AMOUNT_CENTS = 45_000_000
DEFAULT_EVIDENCE_PATH = Path("capital_450k_evidence.json")
ALLOWED_SOURCES = {"bank", "qonto", "qonto_bank", "bank_statement"}


@dataclass(frozen=True)
class GuardResult:
    status: str
    reason: str
    evidence_path: str
    checked_at: str

    def as_dict(self) -> dict[str, str]:
        return {
            "status": self.status,
            "reason": self.reason,
            "evidence_path": self.evidence_path,
            "checked_at": self.checked_at,
        }


def _parse_now(value: str | None, tz_name: str) -> datetime:
    tz = ZoneInfo(tz_name)
    if not value:
        return datetime.now(tz)
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=tz)
    return parsed.astimezone(tz)


def _is_tuesday_eight(now: datetime) -> bool:
    return now.weekday() == 1 and now.time().replace(second=0, microsecond=0) == time(8, 0)


def _load_evidence(path: Path) -> tuple[dict[str, object] | None, str | None]:
    if not path.exists():
        return None, "evidencia local ausente"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return None, f"evidencia no legible: {exc}"
    if not isinstance(data, dict):
        return None, "evidencia invalida: se esperaba objeto JSON"
    return data, None


def _validate_evidence(data: dict[str, object]) -> str | None:
    source = str(data.get("source", "")).strip().lower()
    reference = str(data.get("reference", "")).strip()
    currency = str(data.get("currency", "")).strip().upper()
    amount = data.get("amount_cents")

    if source not in ALLOWED_SOURCES:
        return "fuente no verificable: usa bank/qonto con referencia bancaria"
    if not reference:
        return "referencia bancaria/Qonto ausente"
    if currency != "EUR":
        return "divisa invalida: se exige EUR"
    if not isinstance(amount, int) or amount < MINIMUM_AMOUNT_CENTS:
        return "importe insuficiente: se exige minimo 450000 EUR en centimos"
    return None


def evaluate_guard(
    *,
    now_value: str | None = None,
    timezone_name: str = "UTC",
    evidence_path: Path = DEFAULT_EVIDENCE_PATH,
    env: dict[str, str] | None = None,
) -> GuardResult:
    env = env if env is not None else os.environ
    if evidence_path == DEFAULT_EVIDENCE_PATH and env.get("TRYONYOU_CAPITAL_EVIDENCE_PATH"):
        evidence_path = Path(env["TRYONYOU_CAPITAL_EVIDENCE_PATH"])
    now = _parse_now(now_value, timezone_name)
    checked_at = now.astimezone(timezone.utc).isoformat()
    evidence_display = str(evidence_path)

    if not _is_tuesday_eight(now):
        return GuardResult(
            "PENDING_VALIDATION",
            "fuera de ventana martes 08:00",
            evidence_display,
            checked_at,
        )
    if env.get("TRYONYOU_CAPITAL_450K_CONFIRMED") != "1":
        return GuardResult(
            "PENDING_VALIDATION",
            "flag TRYONYOU_CAPITAL_450K_CONFIRMED no activado",
            evidence_display,
            checked_at,
        )

    evidence, error = _load_evidence(evidence_path)
    if error:
        return GuardResult("PENDING_VALIDATION", error, evidence_display, checked_at)

    validation_error = _validate_evidence(evidence or {})
    if validation_error:
        return GuardResult("PENDING_VALIDATION", validation_error, evidence_display, checked_at)

    return GuardResult(
        "DOSSIER_FATALITY_ACTIVE",
        "capital 450000 EUR validado por evidencia local y flag operatorio",
        evidence_display,
        checked_at,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Evalua la puerta Dossier Fatality 450k.")
    parser.add_argument("--now", help="Datetime ISO para ejecuciones controladas.")
    parser.add_argument("--timezone", default="UTC", help="Zona horaria de la ventana martes 08:00.")
    parser.add_argument("--evidence", default=str(DEFAULT_EVIDENCE_PATH), help="JSON local de evidencia.")
    parser.add_argument("--json", action="store_true", help="Imprime resultado JSON.")
    args = parser.parse_args()

    result = evaluate_guard(
        now_value=args.now,
        timezone_name=args.timezone,
        evidence_path=Path(args.evidence),
    )
    if args.json:
        print(json.dumps(result.as_dict(), ensure_ascii=False, sort_keys=True))
    else:
        print(f"{result.status}: {result.reason}")
    return 0 if result.status == "DOSSIER_FATALITY_ACTIVE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
