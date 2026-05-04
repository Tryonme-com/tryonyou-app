#!/usr/bin/env python3
"""Guard seguro para Dossier Fatality.

No confirma fondos por si mismo. Solo activa el estado de proteccion si existe
evidencia local verificable de entrada bancaria/Qonto y la ventana operativa es
martes a las 08:00.
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MIN_CAPITAL_CENTS = 45_000_000
DEFAULT_EVIDENCE_PATH = "capital_450k_evidence.json"
VALID_SOURCES = {"qonto", "bank", "bank_statement", "sepa_credit", "qonto_transaction"}
ACTIVE_STATUS = "DOSSIER_FATALITY_ACTIVE"
PENDING_STATUS = "PENDING_VALIDATION"


@dataclass(frozen=True)
class GuardResult:
    status: str
    reason: str
    now: str
    required_amount_cents: int = MIN_CAPITAL_CENTS
    evidence_path: str = DEFAULT_EVIDENCE_PATH

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "reason": self.reason,
            "now": self.now,
            "required_amount_cents": self.required_amount_cents,
            "evidence_path": self.evidence_path,
        }


def parse_now(raw: str | None = None) -> datetime:
    if not raw:
        return datetime.now(timezone.utc)
    normalized = raw.strip()
    if normalized.endswith("Z"):
        normalized = f"{normalized[:-1]}+00:00"
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def is_tuesday_0800_utc(now: datetime) -> bool:
    return now.weekday() == 1 and now.hour == 8


def confirmation_flag_enabled(env: dict[str, str] | None = None) -> bool:
    source = env if env is not None else os.environ
    return source.get("TRYONYOU_CAPITAL_450K_CONFIRMED", "").strip() == "1"


def _amount_to_cents(value: Any) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(round(value * 100))
    if isinstance(value, str):
        cleaned = value.replace(" ", "").replace("_", "").replace(",", ".")
        return int(round(float(cleaned) * 100))
    raise ValueError("amount is missing or invalid")


def load_evidence(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("evidence must be a JSON object")
    return data


def validate_evidence(data: dict[str, Any]) -> str | None:
    source = str(data.get("source", "")).strip().lower()
    if source not in VALID_SOURCES:
        return "missing_valid_source"

    try:
        cents = (
            _amount_to_cents(data["amount_cents"])
            if "amount_cents" in data
            else _amount_to_cents(data.get("amount_eur"))
        )
    except (KeyError, TypeError, ValueError):
        return "missing_valid_amount"

    if cents < MIN_CAPITAL_CENTS:
        return "amount_below_required_450k"

    currency = str(data.get("currency", "EUR")).strip().upper()
    if currency != "EUR":
        return "currency_not_eur"

    reference = str(data.get("reference", "")).strip()
    confirmed_at = str(data.get("confirmed_at", "")).strip()
    if not reference or not confirmed_at:
        return "missing_reference_or_confirmed_at"

    return None


def evaluate_guard(
    now: datetime | None = None,
    evidence_path: str | Path | None = None,
    env: dict[str, str] | None = None,
) -> GuardResult:
    current = now or parse_now()
    path = Path(evidence_path or os.environ.get("TRYONYOU_CAPITAL_450K_EVIDENCE", DEFAULT_EVIDENCE_PATH))

    if not is_tuesday_0800_utc(current):
        return GuardResult(
            status=PENDING_STATUS,
            reason="outside_tuesday_0800_utc_window",
            now=current.isoformat(),
            evidence_path=str(path),
        )

    if not confirmation_flag_enabled(env):
        return GuardResult(
            status=PENDING_STATUS,
            reason="missing_TRYONYOU_CAPITAL_450K_CONFIRMED_flag",
            now=current.isoformat(),
            evidence_path=str(path),
        )

    if not path.exists():
        return GuardResult(
            status=PENDING_STATUS,
            reason="missing_capital_evidence_file",
            now=current.isoformat(),
            evidence_path=str(path),
        )

    try:
        evidence = load_evidence(path)
        invalid_reason = validate_evidence(evidence)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        invalid_reason = f"invalid_capital_evidence:{exc.__class__.__name__}"

    if invalid_reason:
        return GuardResult(
            status=PENDING_STATUS,
            reason=invalid_reason,
            now=current.isoformat(),
            evidence_path=str(path),
        )

    return GuardResult(
        status=ACTIVE_STATUS,
        reason="verified_capital_evidence_present",
        now=current.isoformat(),
        evidence_path=str(path),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Dossier Fatality guard 450k")
    parser.add_argument("--now", help="ISO datetime override, interpreted as UTC if naive")
    parser.add_argument("--evidence", default=None, help="Path to local Qonto/bank evidence JSON")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    args = parser.parse_args(argv)

    result = evaluate_guard(now=parse_now(args.now), evidence_path=args.evidence)
    if args.json:
        print(json.dumps(result.as_dict(), ensure_ascii=False, sort_keys=True))
    else:
        print(f"{result.status}: {result.reason}")
    return 0 if result.status == ACTIVE_STATUS else 2


if __name__ == "__main__":
    raise SystemExit(main())
