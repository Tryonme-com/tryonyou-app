"""
Dossier Fatality guard — capital protection gate.

This module never confirms treasury inflows by itself. It only activates
``DOSSIER_FATALITY_ACTIVE`` when all local, auditable gates are present:

1. The execution timestamp is Tuesday at 08:00 in the configured timezone.
2. ``TRYONYOU_CAPITAL_450K_CONFIRMED=1`` (or an accepted alias) is set.
3. A local evidence JSON file proves a banking/Qonto source, reference, and
   an amount of at least 450,000 EUR.

Patente: PCT/EP2025/067317
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

MIN_AMOUNT_CENTS = 45_000_000
DEFAULT_TIMEZONE = "Europe/Paris"
DEFAULT_EVIDENCE_PATH = "capital_450k_evidence.json"
ACCEPTED_SOURCES = {"qonto", "bank", "banking", "sepa", "wire_transfer"}
CONFIRMATION_ENV_KEYS = (
    "TRYONYOU_CAPITAL_450K_CONFIRMED",
    "DOSSIER_FATALITY_CAPITAL_CONFIRMED",
    "GLOBAL_SETTLEMENT_CAPITAL_CONFIRMED",
)


@dataclass(frozen=True)
class GuardResult:
    status: str
    activated: bool
    reason: str
    checked_at: str
    required_amount_cents: int = MIN_AMOUNT_CENTS

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "activated": self.activated,
            "reason": self.reason,
            "checked_at": self.checked_at,
            "required_amount_cents": self.required_amount_cents,
        }


def _parse_timestamp(raw: str | None, timezone_name: str) -> datetime:
    tz = ZoneInfo(timezone_name)
    if not raw:
        return datetime.now(tz)
    normalized = raw.strip()
    if normalized.endswith("Z"):
        normalized = f"{normalized[:-1]}+00:00"
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=tz)
    return parsed.astimezone(tz)


def _is_tuesday_0800(moment: datetime) -> bool:
    return moment.weekday() == 1 and moment.hour == 8


def _confirmation_flag_present() -> bool:
    return any(os.getenv(key, "").strip() == "1" for key in CONFIRMATION_ENV_KEYS)


def _load_evidence(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _amount_cents(payload: dict[str, Any]) -> int:
    raw_cents = payload.get("amount_cents")
    if raw_cents is not None:
        try:
            return int(raw_cents)
        except (TypeError, ValueError):
            return 0

    raw_eur = payload.get("amount_eur")
    try:
        return int(round(float(raw_eur) * 100))
    except (TypeError, ValueError):
        return 0


def _evidence_is_valid(payload: dict[str, Any] | None) -> bool:
    if not payload:
        return False
    source = str(payload.get("source", "")).strip().lower()
    reference = str(payload.get("reference", "")).strip()
    currency = str(payload.get("currency", "EUR")).strip().upper()
    return (
        source in ACCEPTED_SOURCES
        and bool(reference)
        and currency == "EUR"
        and _amount_cents(payload) >= MIN_AMOUNT_CENTS
    )


def evaluate_dossier_fatality(
    *,
    now: str | None = None,
    timezone_name: str = DEFAULT_TIMEZONE,
    evidence_path: str | Path = DEFAULT_EVIDENCE_PATH,
) -> GuardResult:
    moment = _parse_timestamp(now, timezone_name)
    checked_at = moment.isoformat()

    if not _is_tuesday_0800(moment):
        return GuardResult(
            status="PENDING_VALIDATION",
            activated=False,
            reason="outside_tuesday_0800_window",
            checked_at=checked_at,
        )

    if not _confirmation_flag_present():
        return GuardResult(
            status="PENDING_VALIDATION",
            activated=False,
            reason="missing_explicit_capital_confirmation",
            checked_at=checked_at,
        )

    payload = _load_evidence(Path(evidence_path))
    if not _evidence_is_valid(payload):
        return GuardResult(
            status="PENDING_VALIDATION",
            activated=False,
            reason="missing_or_invalid_banking_evidence",
            checked_at=checked_at,
        )

    os.environ["DOSSIER_FATALITY_ACTIVE"] = "1"
    return GuardResult(
        status="DOSSIER_FATALITY_ACTIVE",
        activated=True,
        reason="capital_confirmed_with_banking_evidence",
        checked_at=checked_at,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate Dossier Fatality activation gates.")
    parser.add_argument("--now", help="ISO timestamp override, e.g. 2026-05-05T08:00:00+02:00")
    parser.add_argument("--timezone", default=os.getenv("DOSSIER_FATALITY_TIMEZONE", DEFAULT_TIMEZONE))
    parser.add_argument(
        "--evidence",
        default=os.getenv("DOSSIER_FATALITY_EVIDENCE_PATH", DEFAULT_EVIDENCE_PATH),
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args(argv)

    result = evaluate_dossier_fatality(
        now=args.now,
        timezone_name=args.timezone,
        evidence_path=args.evidence,
    )
    if args.json:
        print(json.dumps(result.to_dict(), sort_keys=True))
    else:
        print(f"{result.status}: {result.reason}")
    return 0 if result.activated else 3


if __name__ == "__main__":
    raise SystemExit(main())
