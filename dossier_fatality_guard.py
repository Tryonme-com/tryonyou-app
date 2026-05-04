#!/usr/bin/env python3
"""
Guard seguro para Dossier Fatality.

No confirma movimientos bancarios por sí mismo. Solo activa el estado operativo si:
- la ejecución cae en martes a las 08:00,
- existe confirmación explícita por entorno,
- y hay evidencia local verificable con importe EUR >= 450.000.
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

MINIMUM_AMOUNT_CENTS = 45_000_000
DEFAULT_EVIDENCE_PATH = Path("capital_450k_evidence.json")
DEFAULT_TIMEZONE = "Europe/Paris"
ACTIVE_STATUS = "DOSSIER_FATALITY_ACTIVE"
PENDING_STATUS = "PENDING_VALIDATION"
ENV_EVIDENCE_PATH = "TRYONYOU_CAPITAL_450K_EVIDENCE_PATH"
ENV_TIMEZONE = "TRYONYOU_FATALITY_TIMEZONE"


@dataclass(frozen=True)
class FatalityDecision:
    status: str
    reason: str
    amount_cents: int = 0
    reference: str = ""
    source: str = ""

    @property
    def active(self) -> bool:
        return self.status == ACTIVE_STATUS

    def to_dict(self) -> dict[str, object]:
        return {
            "active": self.active,
            "status": self.status,
            "reason": self.reason,
            "amount_cents": self.amount_cents,
            "reference": self.reference,
            "source": self.source,
        }


def parse_now(raw: str | None, tz_name: str = DEFAULT_TIMEZONE) -> datetime:
    tz = ZoneInfo(tz_name)
    if not raw:
        return datetime.now(tz)
    normalized = raw.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=tz)
    return parsed.astimezone(tz)


def is_tuesday_0800(now: datetime) -> bool:
    return now.weekday() == 1 and now.hour == 8


def confirmation_enabled() -> bool:
    return os.environ.get("TRYONYOU_CAPITAL_450K_CONFIRMED", "").strip() == "1"


def load_evidence(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def amount_to_cents(payload: dict[str, object]) -> int:
    cents = payload.get("amount_cents")
    if isinstance(cents, int):
        return cents
    euros = payload.get("amount_eur")
    if isinstance(euros, (int, float)):
        return int(round(float(euros) * 100))
    if isinstance(euros, str):
        try:
            return int(round(float(euros.replace(",", ".")) * 100))
        except ValueError:
            return 0
    return 0


def evaluate_fatality_guard(
    *,
    now: datetime | None = None,
    evidence_path: Path = DEFAULT_EVIDENCE_PATH,
) -> FatalityDecision:
    current = now or parse_now(None)
    if not is_tuesday_0800(current):
        return FatalityDecision(PENDING_STATUS, "outside_tuesday_0800_window")
    if not confirmation_enabled():
        return FatalityDecision(PENDING_STATUS, "missing_explicit_capital_confirmation")

    evidence = load_evidence(evidence_path)
    amount_cents = amount_to_cents(evidence)
    source = str(evidence.get("source") or "").strip()
    reference = str(evidence.get("reference") or "").strip()

    if amount_cents < MINIMUM_AMOUNT_CENTS:
        return FatalityDecision(PENDING_STATUS, "evidence_amount_below_450000_eur", amount_cents)
    if source.lower() not in {"qonto", "bank", "banking", "stripe_verified_bank_settlement"}:
        return FatalityDecision(PENDING_STATUS, "evidence_source_not_bank_or_qonto", amount_cents, reference, source)
    if not reference:
        return FatalityDecision(PENDING_STATUS, "missing_evidence_reference", amount_cents, reference, source)

    return FatalityDecision(ACTIVE_STATUS, "capital_verified_and_guard_window_valid", amount_cents, reference, source)


def main() -> int:
    parser = argparse.ArgumentParser(description="Evalua el guard Dossier Fatality 450k.")
    parser.add_argument("--now", help="Fecha ISO para pruebas, ej. 2026-05-05T08:00:00+02:00")
    parser.add_argument("--timezone", default=os.environ.get(ENV_TIMEZONE, DEFAULT_TIMEZONE))
    parser.add_argument("--evidence", default=os.environ.get(ENV_EVIDENCE_PATH, str(DEFAULT_EVIDENCE_PATH)))
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    decision = evaluate_fatality_guard(
        now=parse_now(args.now, args.timezone),
        evidence_path=Path(args.evidence),
    )
    if args.as_json:
        print(json.dumps(decision.to_dict(), ensure_ascii=False, sort_keys=True))
    else:
        print(f"{decision.status}: {decision.reason}")
    return 0 if decision.active else 3


if __name__ == "__main__":
    raise SystemExit(main())
