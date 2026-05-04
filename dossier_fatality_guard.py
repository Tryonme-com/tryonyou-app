"""Safe guard for Dossier Fatality capital protection.

The guard never confirms bank movements by itself. Activation requires:
- Tuesday at 08:00 in the configured timezone (UTC by default).
- TRYONYOU_CAPITAL_450K_CONFIRMED=1 in the environment.
- Local evidence JSON proving at least 450,000 EUR in cents.

SIRET 94361019600017 | PCT/EP2025/067317
Bajo Protocolo de Soberania V10 - Founder: Ruben
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

MIN_CAPITAL_CENTS = 45_000_000
DEFAULT_EVIDENCE_PATH = "capital_450k_evidence.json"
DEFAULT_TIMEZONE = "UTC"
ACTIVATION_STATUS = "DOSSIER_FATALITY_ACTIVE"
PENDING_STATUS = "PENDING_VALIDATION"


@dataclass(frozen=True)
class GuardResult:
    status: str
    active: bool
    reason: str
    checked_at: str
    required_amount_cents: int = MIN_CAPITAL_CENTS

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "active": self.active,
            "reason": self.reason,
            "checked_at": self.checked_at,
            "required_amount_cents": self.required_amount_cents,
        }


def _parse_now(raw: str | None, tz_name: str) -> datetime:
    tz = ZoneInfo(tz_name)
    if not raw:
        return datetime.now(tz)
    normalized = raw.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=tz)
    return parsed.astimezone(tz)


def _is_tuesday_0800(moment: datetime) -> bool:
    return moment.weekday() == 1 and moment.hour == 8 and moment.minute == 0


def _load_evidence(path: Path) -> tuple[dict[str, Any] | None, str]:
    if not path.exists():
        return None, "missing_evidence"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None, "invalid_evidence_json"
    if not isinstance(data, dict):
        return None, "invalid_evidence_shape"
    return data, ""


def _evidence_is_valid(data: dict[str, Any] | None) -> tuple[bool, str]:
    if data is None:
        return False, "missing_evidence"

    currency = str(data.get("currency", "")).upper().strip()
    source = str(data.get("source", "")).lower().strip()
    reference = str(data.get("reference", "")).strip()
    try:
        amount_cents = int(data.get("amount_cents", 0))
    except (TypeError, ValueError):
        amount_cents = 0

    if currency != "EUR":
        return False, "evidence_currency_not_eur"
    if amount_cents < MIN_CAPITAL_CENTS:
        return False, "evidence_amount_below_450k"
    if source not in {"qonto", "bank", "bank_statement", "banking"}:
        return False, "evidence_source_not_banking"
    if not reference:
        return False, "evidence_reference_required"
    return True, "evidence_valid"


def evaluate_guard(
    *,
    now: str | None = None,
    evidence_path: str | Path | None = None,
    timezone_name: str | None = None,
) -> GuardResult:
    tz_name = timezone_name or os.getenv("TRYONYOU_FATALITY_TIMEZONE", DEFAULT_TIMEZONE)
    moment = _parse_now(now, tz_name)
    checked_at = moment.isoformat()

    if not _is_tuesday_0800(moment):
        return GuardResult(
            status=PENDING_STATUS,
            active=False,
            reason="outside_tuesday_0800_window",
            checked_at=checked_at,
        )

    if os.getenv("TRYONYOU_CAPITAL_450K_CONFIRMED", "").strip() != "1":
        return GuardResult(
            status=PENDING_STATUS,
            active=False,
            reason="capital_confirmation_flag_missing",
            checked_at=checked_at,
        )

    path = Path(evidence_path or os.getenv("TRYONYOU_CAPITAL_450K_EVIDENCE", DEFAULT_EVIDENCE_PATH))
    evidence, load_error = _load_evidence(path)
    if load_error:
        return GuardResult(
            status=PENDING_STATUS,
            active=False,
            reason=load_error,
            checked_at=checked_at,
        )

    valid, reason = _evidence_is_valid(evidence)
    if not valid:
        return GuardResult(
            status=PENDING_STATUS,
            active=False,
            reason=reason,
            checked_at=checked_at,
        )

    return GuardResult(
        status=ACTIVATION_STATUS,
        active=True,
        reason="capital_verified_and_window_valid",
        checked_at=checked_at,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate Dossier Fatality activation guard.")
    parser.add_argument("--now", default=None, help="ISO timestamp override for controlled runs.")
    parser.add_argument("--evidence-path", default=None, help="Path to local evidence JSON.")
    parser.add_argument("--timezone", default=None, help="IANA timezone, default UTC.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args(argv)

    result = evaluate_guard(
        now=args.now,
        evidence_path=args.evidence_path,
        timezone_name=args.timezone,
    )
    payload = result.as_dict()
    if args.json:
        print(json.dumps(payload, ensure_ascii=True, sort_keys=True))
    else:
        print(f"{payload['status']}: {payload['reason']} at {payload['checked_at']}")
    return 0 if result.active else 2


if __name__ == "__main__":
    raise SystemExit(main())
