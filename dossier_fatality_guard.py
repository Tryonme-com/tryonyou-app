#!/usr/bin/env python3
"""
Dossier Fatality Guard — proteccion de capital con evidencia Qonto verificable.

Este guard no confirma ingresos bancarios por narrativa. Solo activa el estado
DOSSIER_FATALITY_ACTIVE cuando concurren:
  - ventana operativa martes 08:00 UTC,
  - TRYONYOU_CAPITAL_450K_CONFIRMED=1,
  - evidencia JSON local con fuente bancaria/Qonto y al menos 45.000.000 cents EUR.

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
DEFAULT_EVIDENCE_PATH = ROOT / "capital_450k_evidence.json"
DEFAULT_STATUS_PATH = ROOT / "logs" / "dossier_fatality_status.json"
REQUIRED_CENTS = 45_000_000
REQUIRED_AMOUNT_CENTS = REQUIRED_CENTS
ALLOWED_SOURCES = {"qonto", "qonto_api", "bank", "bank_statement", "bank_export"}


@dataclass(frozen=True)
class GuardResult:
    status: str
    active: bool
    reason: str
    checked_at: str
    required_cents: int = REQUIRED_CENTS
    evidence_path: str = ""
    evidence_reference: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "active": self.active,
            "reason": self.reason,
            "checked_at": self.checked_at,
            "required_cents": self.required_cents,
            "evidence_path": self.evidence_path,
            "evidence_reference": self.evidence_reference,
        }


def parse_now(raw: str | None = None) -> datetime:
    if not raw:
        return datetime.now(timezone.utc)
    normalized = raw.strip()
    if normalized.endswith("Z"):
        normalized = f"{normalized[:-1]}+00:00"
    value = datetime.fromisoformat(normalized)
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def is_tuesday_0800_utc(now: datetime) -> bool:
    normalized = now.astimezone(timezone.utc)
    return normalized.weekday() == 1 and normalized.hour == 8


parse_instant = parse_now
valid_confirmation_window = is_tuesday_0800_utc


def _read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("evidence_json_must_be_object")
    return payload


def validate_evidence(path: Path, required_cents: int = REQUIRED_CENTS) -> tuple[bool, str, str]:
    if not path.is_file():
        return False, "missing_evidence_file", ""
    try:
        payload = _read_json(path)
    except Exception as exc:
        return False, f"invalid_evidence_json:{exc}", ""

    currency = str(payload.get("currency") or "").upper()
    source = str(payload.get("source") or "").strip().lower()
    reference = str(payload.get("reference") or "").strip()
    confirmed = payload.get("confirmed", True) is True

    try:
        amount_cents = int(payload.get("amount_cents"))
    except (TypeError, ValueError):
        return False, "invalid_amount_cents", reference

    if currency != "EUR":
        return False, "currency_not_eur", reference
    if source not in ALLOWED_SOURCES:
        return False, "source_not_bank_or_qonto", reference
    if not reference:
        return False, "missing_reference", reference
    if not confirmed:
        return False, "evidence_not_marked_confirmed", reference
    if amount_cents < required_cents:
        return False, "amount_below_required_450k", reference
    return True, "evidence_valid", reference


def evaluate_guard(
    *,
    now: datetime | None = None,
    evidence_path: Path = DEFAULT_EVIDENCE_PATH,
    required_cents: int = REQUIRED_CENTS,
) -> GuardResult:
    checked_at = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    checked_iso = checked_at.isoformat()

    if not is_tuesday_0800_utc(checked_at):
        return GuardResult(
            status="PENDING_VALIDATION",
            active=False,
            reason="outside_tuesday_0800_utc_window",
            checked_at=checked_iso,
            evidence_path=str(evidence_path),
        )

    if (os.getenv("TRYONYOU_CAPITAL_450K_CONFIRMED") or "").strip() != "1":
        return GuardResult(
            status="PENDING_VALIDATION",
            active=False,
            reason="missing_TRYONYOU_CAPITAL_450K_CONFIRMED_flag",
            checked_at=checked_iso,
            evidence_path=str(evidence_path),
        )

    ok, reason, reference = validate_evidence(evidence_path, required_cents)
    if not ok:
        return GuardResult(
            status="PENDING_VALIDATION",
            active=False,
            reason=reason,
            checked_at=checked_iso,
            evidence_path=str(evidence_path),
            evidence_reference=reference,
        )

    return GuardResult(
        status="DOSSIER_FATALITY_ACTIVE",
        active=True,
        reason="capital_verified_and_protection_enabled",
        checked_at=checked_iso,
        evidence_path=str(evidence_path),
        evidence_reference=reference,
    )


def persist_status(result: GuardResult, path: Path = DEFAULT_STATUS_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.as_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


parse_instant = parse_now
valid_confirmation_window = is_tuesday_0800_utc


def load_evidence(path: Path) -> dict[str, Any]:
    try:
        return _read_json(path)
    except Exception:
        return {}


def build_status(
    *,
    now: datetime,
    evidence: dict[str, Any],
    confirmed_flag: bool,
    required_cents: int = REQUIRED_CENTS,
) -> dict[str, Any]:
    reasons: list[str] = []

    if not valid_confirmation_window(now):
        reasons.append("outside_tuesday_0800_utc_window")
    if not confirmed_flag:
        reasons.append("confirmation_flag_missing")
    if not evidence:
        reasons.append("evidence_missing")
    else:
        try:
            amount_cents = int(evidence.get("amount_cents"))
        except (TypeError, ValueError):
            amount_cents = 0
            reasons.append("invalid_amount_cents")
        if amount_cents < required_cents:
            reasons.append("amount_below_required_450k")
        if str(evidence.get("currency") or "").upper() != "EUR":
            reasons.append("currency_not_eur")
        if str(evidence.get("source") or "").strip().lower() not in ALLOWED_SOURCES:
            reasons.append("source_not_bank_or_qonto")
        if not str(evidence.get("reference") or "").strip():
            reasons.append("missing_reference")

    activated = not reasons
    return {
        "status": "DOSSIER_FATALITY_ACTIVE" if activated else "PENDING_VALIDATION",
        "activated": activated,
        "reasons": reasons,
        "checked_at": now.astimezone(timezone.utc).isoformat(),
        "required_cents": required_cents,
        "evidence": evidence if evidence else {},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate 450k EUR evidence before Dossier Fatality activation.")
    parser.add_argument("--now", default="", help="ISO timestamp override, UTC if no timezone is present.")
    parser.add_argument("--evidence", default=str(DEFAULT_EVIDENCE_PATH), help="Path to local Qonto/bank evidence JSON.")
    parser.add_argument("--status-path", default=str(DEFAULT_STATUS_PATH), help="Where to persist guard status JSON.")
    parser.add_argument("--output", dest="status_path", help=argparse.SUPPRESS)
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args(argv)

    now = parse_now(args.now or None)
    evidence_path = Path(args.evidence)
    evidence = load_evidence(evidence_path)
    confirmed = (os.getenv("TRYONYOU_CAPITAL_450K_CONFIRMED") or "").strip() == "1"
    payload = build_status(now=now, evidence=evidence, confirmed_flag=confirmed)
    payload["evidence_path"] = str(evidence_path)
    Path(args.status_path).parent.mkdir(parents=True, exist_ok=True)
    Path(args.status_path).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"{payload['status']}: {','.join(payload['reasons']) or 'capital_verified'}")

    return 0 if payload["activated"] else 2


if __name__ == "__main__":
    sys.exit(main())
