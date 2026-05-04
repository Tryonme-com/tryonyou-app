"""Guard soberano para Dossier Fatality.

No confirma capital ni activa protecciones financieras sin una evidencia local
explícita. Diseñado para automatizaciones: salida JSON predecible, sin secretos.
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUIRED_AMOUNT_CENTS = 45_000_000
CONFIRMATION_ENV = "TRYONYOU_CAPITAL_450K_CONFIRMED"
EVIDENCE_ENV = "TRYONYOU_CAPITAL_EVIDENCE_JSON"


@dataclass(frozen=True)
class FatalityGuardResult:
    status: str
    activated: bool
    reason: str
    required_amount_cents: int
    observed_amount_cents: int | None
    checked_at: str


def parse_now(raw_now: str | None = None) -> datetime:
    if not raw_now:
        return datetime.now(timezone.utc)

    normalized = raw_now.strip().replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def is_tuesday_0800(now: datetime) -> bool:
    current = now.astimezone(timezone.utc)
    return current.weekday() == 1 and current.hour == 8


def _amount_to_cents(value: Any) -> int | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(round(value * 100))
    if isinstance(value, str):
        cleaned = value.strip().replace(" ", "").replace("_", "")
        if not cleaned:
            return None
        if "," in cleaned and "." not in cleaned:
            cleaned = cleaned.replace(",", ".")
        try:
            amount = float(cleaned)
        except ValueError:
            return None
        return int(round(amount * 100))
    return None


def load_evidence(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("fatality_evidence_must_be_json_object")
    return payload


def observed_amount_cents(evidence: dict[str, Any]) -> int | None:
    for key in ("amount_cents", "confirmed_amount_cents", "gross_amount_cents"):
        cents = _amount_to_cents(evidence.get(key))
        if cents is not None:
            return cents
    for key in ("amount_eur", "confirmed_amount_eur", "gross_amount_eur"):
        raw = evidence.get(key)
        if isinstance(raw, int):
            return raw * 100
        cents = _amount_to_cents(raw)
        if cents is not None:
            return cents
    return None


def evaluate_fatality_guard(
    *,
    now: datetime | None = None,
    confirmed_env: str | None = None,
    evidence_path: Path | None = None,
) -> FatalityGuardResult:
    checked_at = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    evidence = load_evidence(evidence_path)
    observed = observed_amount_cents(evidence)

    if not is_tuesday_0800(checked_at):
        return FatalityGuardResult(
            status="PENDING_VALIDATION",
            activated=False,
            reason="outside_tuesday_0800_utc_window",
            required_amount_cents=REQUIRED_AMOUNT_CENTS,
            observed_amount_cents=observed,
            checked_at=checked_at.isoformat(),
        )

    if confirmed_env != "1":
        return FatalityGuardResult(
            status="PENDING_QONTO_VERIFICATION",
            activated=False,
            reason=f"{CONFIRMATION_ENV}_not_set",
            required_amount_cents=REQUIRED_AMOUNT_CENTS,
            observed_amount_cents=observed,
            checked_at=checked_at.isoformat(),
        )

    if observed is None or observed < REQUIRED_AMOUNT_CENTS:
        return FatalityGuardResult(
            status="PENDING_EVIDENCE",
            activated=False,
            reason="missing_or_insufficient_capital_evidence",
            required_amount_cents=REQUIRED_AMOUNT_CENTS,
            observed_amount_cents=observed,
            checked_at=checked_at.isoformat(),
        )

    return FatalityGuardResult(
        status="DOSSIER_FATALITY_ACTIVE",
        activated=True,
        reason="capital_evidence_verified",
        required_amount_cents=REQUIRED_AMOUNT_CENTS,
        observed_amount_cents=observed,
        checked_at=checked_at.isoformat(),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Evalua activacion segura del Dossier Fatality.")
    parser.add_argument("--now", help="ISO datetime para pruebas deterministas.")
    parser.add_argument(
        "--evidence",
        default=os.environ.get(EVIDENCE_ENV),
        help=f"Ruta JSON de evidencia bancaria local. Fallback: {EVIDENCE_ENV}.",
    )
    args = parser.parse_args()

    result = evaluate_fatality_guard(
        now=parse_now(args.now),
        confirmed_env=os.environ.get(CONFIRMATION_ENV),
        evidence_path=Path(args.evidence) if args.evidence else None,
    )
    print(json.dumps(asdict(result), ensure_ascii=False, sort_keys=True))
    return 0 if result.activated else 3


if __name__ == "__main__":
    raise SystemExit(main())
