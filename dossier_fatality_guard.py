#!/usr/bin/env python3
"""Guard rail for the 450k EUR Dossier Fatality activation.

The script prepares the requested automation without pretending that a bank
movement happened. Activation requires the Tuesday 08:00 window, an explicit
arm flag, and verifiable Qonto/banking evidence for at least 450,000 EUR.

Patente: PCT/EP2025/067317
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
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

TARGET_AMOUNT = 450000.00
TARGET_AMOUNT_CENTS = 45_000_000
DEFAULT_TIMEZONE = "Europe/Paris"
ROOT = Path(__file__).resolve().parent
EMERGENCY_PAYOUT_FILE = ROOT / ".emergency_payout"
STATUS_FILE = ROOT / "dossier_fatality_status.json"


@dataclass(frozen=True)
class FatalityEvidence:
    amount_cents: int
    currency: str
    reference: str
    source: str

    @property
    def valid(self) -> bool:
        return (
            self.amount_cents >= TARGET_AMOUNT_CENTS
            and self.currency.upper() == "EUR"
            and bool(self.reference.strip())
        )


def parse_now(value: str) -> datetime:
    return datetime.fromisoformat(value)


def env_confirmed_450k() -> bool:
    return os.getenv("TRYONYOU_CAPITAL_450K_CONFIRMED", "").strip().lower() in {
        "1",
        "true",
        "yes",
    }


def _parse_amount(raw: Any, *, euros: bool = False) -> int:
    if raw is None:
        return 0
    if isinstance(raw, int):
        return raw * 100 if euros else raw
    if isinstance(raw, float):
        return int(round(raw * 100))
    text = str(raw).strip().replace(" ", "").replace("_", "")
    if not text:
        return 0
    if "," in text and "." not in text:
        text = text.replace(",", ".")
    try:
        value = int(text)
        return value * 100 if euros else value
    except ValueError:
        try:
            return int(round(float(text) * 100))
        except ValueError:
            return 0


def _evidence_from_mapping(data: dict[str, Any], source: str) -> FatalityEvidence:
    amount_cents = _parse_amount(
        data.get("amount_cents")
        or data.get("target_amount_cents")
        or data.get("qonto_amount_cents")
    )
    if amount_cents == 0:
        amount_cents = _parse_amount(
            data.get("amount_eur")
            or data.get("target_amount_eur")
            or data.get("qonto_amount_eur")
            or data.get("amount"),
            euros=True,
        )
    return FatalityEvidence(
        amount_cents=amount_cents,
        currency=str(data.get("currency") or data.get("qonto_currency") or "EUR"),
        reference=str(
            data.get("reference")
            or data.get("transaction_id")
            or data.get("qonto_transaction_id")
            or data.get("bank_reference")
            or ""
        ),
        source=source,
    )


def _evidence_from_emergency_file() -> FatalityEvidence:
    if not EMERGENCY_PAYOUT_FILE.exists():
        return FatalityEvidence(0, "EUR", "", str(EMERGENCY_PAYOUT_FILE))
    data: dict[str, str] = {}
    for line in EMERGENCY_PAYOUT_FILE.read_text(encoding="utf-8").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            data[key.strip().lower()] = value.strip()
    return _evidence_from_mapping(
        {
            "amount_eur": data.get("amount"),
            "currency": data.get("currency", "EUR"),
            "reference": data.get("reference") or data.get("transaction_id"),
        },
        str(EMERGENCY_PAYOUT_FILE),
    )


def load_evidence(path: str | None = None) -> FatalityEvidence:
    if path:
        evidence_path = Path(path)
        try:
            data = json.loads(evidence_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return FatalityEvidence(0, "EUR", "", str(evidence_path))
        if isinstance(data, dict):
            return _evidence_from_mapping(data, str(evidence_path))
        return FatalityEvidence(0, "EUR", "", str(evidence_path))

    env_payload = (os.environ.get("DOSSIER_FATALITY_EVIDENCE_JSON") or "").strip()
    if env_payload:
        try:
            data = json.loads(env_payload)
        except json.JSONDecodeError:
            data = {}
        if isinstance(data, dict):
            return _evidence_from_mapping(data, "DOSSIER_FATALITY_EVIDENCE_JSON")

    env_evidence = _evidence_from_mapping(
        {
            "amount_cents": os.environ.get("DOSSIER_FATALITY_AMOUNT_CENTS"),
            "amount_eur": os.environ.get("DOSSIER_FATALITY_AMOUNT_EUR"),
            "currency": os.environ.get("DOSSIER_FATALITY_CURRENCY") or "EUR",
            "reference": os.environ.get("DOSSIER_FATALITY_REFERENCE") or "",
        },
        "environment",
    )
    if env_evidence.amount_cents or env_evidence.reference:
        return env_evidence

    return _evidence_from_emergency_file()


def _timezone(name: str) -> ZoneInfo:
    try:
        return ZoneInfo(name)
    except ZoneInfoNotFoundError:
        return ZoneInfo("UTC")


def is_activation_window(now: datetime | None = None, timezone_name: str | None = None) -> bool:
    tz = _timezone(timezone_name or os.environ.get("DOSSIER_FATALITY_TIMEZONE") or DEFAULT_TIMEZONE)
    local_now = (now or datetime.now(tz)).astimezone(tz)
    return local_now.weekday() == 1 and local_now.hour == 8


def activation_report(
    *,
    now: datetime | None = None,
    evidence_path: str | None = None,
    timezone_name: str | None = None,
    force_arm: bool | None = None,
) -> dict[str, Any]:
    armed = (
        force_arm
        if force_arm is not None
        else (os.environ.get("DOSSIER_FATALITY_ARM") or "").strip() == "1"
    )
    evidence = load_evidence(evidence_path)
    in_window = is_activation_window(now=now, timezone_name=timezone_name)

    if not in_window:
        status = "PENDING_VALIDATION"
        reason = "outside_tuesday_0800_window"
    elif not armed:
        status = "PENDING_VALIDATION"
        reason = "fatality_not_armed"
    elif not evidence.valid:
        status = "PENDING_VALIDATION"
        reason = "missing_or_invalid_450k_evidence"
    else:
        status = "DOSSIER_FATALITY_READY"
        reason = "qonto_evidence_verified_for_activation"

    return {
        "status": status,
        "reason": reason,
        "target_amount_cents": TARGET_AMOUNT_CENTS,
        "evidence": {
            "amount_cents": evidence.amount_cents,
            "currency": evidence.currency.upper(),
            "reference_present": bool(evidence.reference.strip()),
            "source": evidence.source,
        },
        "armed": bool(armed),
        "activation_window": in_window,
        "patent": "PCT/EP2025/067317",
        "protocol": "Bajo Protocolo de Soberania V10 - Founder: Ruben",
    }


def evaluate_dossier_fatality_window(
    now_dt: datetime | None = None,
    capital_confirmed: bool = False,
) -> dict[str, object]:
    report = activation_report(now=now_dt, force_arm=capital_confirmed)
    activation_allowed = report["status"] == "DOSSIER_FATALITY_READY"
    return {
        "status": "ACTIVATION_ALLOWED" if activation_allowed else "PENDING_VALIDATION",
        "activation_allowed": activation_allowed,
        "reason": report["reason"],
        "amount_confirmed": report["evidence"]["amount_cents"] / 100,
        "schedule_ok": report["activation_window"],
    }


def persist_result(report: dict[str, Any], now: datetime | None = None) -> None:
    payload = dict(report)
    payload["timestamp"] = (now or datetime.now()).isoformat()
    STATUS_FILE.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Dossier Fatality 450k activation.")
    parser.add_argument("--evidence", help="Path to Qonto/bank evidence JSON.")
    parser.add_argument("--timezone", default=None, help="IANA timezone, default Europe/Paris.")
    parser.add_argument("--json", action="store_true", help="Emit JSON only.")
    parser.add_argument("--persist", action="store_true", help="Write dossier_fatality_status.json.")
    args = parser.parse_args()

    report = activation_report(evidence_path=args.evidence, timezone_name=args.timezone)
    if args.persist:
        persist_result(report)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    else:
        print(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
