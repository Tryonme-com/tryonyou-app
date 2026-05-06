"""
Dossier Fatality guard — verificacion conservadora de entrada 450.000 EUR.

No confirma capital por narrativa: exige ventana operativa, armado explicito y
evidencia Qonto/bancaria estructurada antes de activar el dossier.
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


TARGET_AMOUNT_CENTS = 45_000_000
PARIS_TZ = ZoneInfo("Europe/Paris")


def _truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class FatalityStatus:
    status: str
    active: bool
    reason: str
    amount_cents: int | None = None
    currency: str | None = None
    reference: str | None = None


def _load_evidence() -> dict[str, Any]:
    raw_json = (os.environ.get("DOSSIER_FATALITY_EVIDENCE_JSON") or "").strip()
    raw_path = (os.environ.get("DOSSIER_FATALITY_EVIDENCE_PATH") or "").strip()
    if raw_json:
        data = json.loads(raw_json)
        return data if isinstance(data, dict) else {}
    if raw_path:
        path = Path(raw_path)
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    return {}


def _amount_cents(evidence: dict[str, Any]) -> int | None:
    raw_cents = evidence.get("amount_cents")
    if raw_cents is not None:
        try:
            return int(raw_cents)
        except (TypeError, ValueError):
            return None
    raw_eur = evidence.get("amount_eur")
    try:
        return int(round(float(raw_eur) * 100))
    except (TypeError, ValueError):
        return None


def evaluate_fatality_guard(now: datetime | None = None) -> FatalityStatus:
    current = now.astimezone(PARIS_TZ) if now else datetime.now(PARIS_TZ)
    if current.weekday() != 1 or current.hour != 8:
        return FatalityStatus(
            status="PENDING_VALIDATION",
            active=False,
            reason="outside_tuesday_0800_paris",
        )
    if not _truthy(os.environ.get("DOSSIER_FATALITY_ARM")):
        return FatalityStatus(
            status="PENDING_VALIDATION",
            active=False,
            reason="fatality_not_armed",
        )

    try:
        evidence = _load_evidence()
    except (OSError, json.JSONDecodeError):
        return FatalityStatus(
            status="PENDING_VALIDATION",
            active=False,
            reason="invalid_evidence",
        )

    cents = _amount_cents(evidence)
    currency = str(evidence.get("currency") or "").upper() or None
    reference = str(evidence.get("reference") or evidence.get("transaction_id") or "").strip() or None
    status = str(evidence.get("status") or evidence.get("state") or "").strip().lower()
    source = str(evidence.get("source") or evidence.get("provider") or "").strip().lower()

    if cents is None or cents < TARGET_AMOUNT_CENTS:
        return FatalityStatus("PENDING_VALIDATION", False, "amount_below_450000_eur", cents, currency, reference)
    if currency != "EUR":
        return FatalityStatus("PENDING_VALIDATION", False, "currency_not_eur", cents, currency, reference)
    if not reference:
        return FatalityStatus("PENDING_VALIDATION", False, "missing_bank_reference", cents, currency, reference)
    if status and status not in {"completed", "settled", "confirmed", "booked"}:
        return FatalityStatus("PENDING_VALIDATION", False, "bank_status_not_completed", cents, currency, reference)
    if source and "qonto" not in source and "bank" not in source:
        return FatalityStatus("PENDING_VALIDATION", False, "source_not_bank_or_qonto", cents, currency, reference)

    return FatalityStatus("DOSSIER_FATALITY_READY", True, "verified_450000_eur", cents, currency, reference)


def main() -> int:
    parser = argparse.ArgumentParser(description="Evalua Dossier Fatality 450k sin side effects bancarios.")
    parser.add_argument("--json", action="store_true", help="Imprime JSON estable.")
    args = parser.parse_args()
    result = evaluate_fatality_guard()
    if args.json:
        print(json.dumps(asdict(result), ensure_ascii=False, sort_keys=True))
    else:
        print(f"{result.status}: {result.reason}")
    return 0 if result.active else 1


if __name__ == "__main__":
    raise SystemExit(main())
