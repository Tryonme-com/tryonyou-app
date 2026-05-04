#!/usr/bin/env python3
"""
Guard de capital 450k para Dossier Fatality.

No confirma entrada bancaria por narrativa: exige ventana operativa, flag explícito
y evidencia JSON de banco/Qonto antes de activar el dossier.

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


TARGET_AMOUNT_CENTS = 45_000_000
PARIS_TZ = ZoneInfo("Europe/Paris")
VALID_SOURCES = {"qonto", "bank", "stripe", "manual_bank_statement"}


@dataclass(frozen=True)
class FatalityDecision:
    status: str
    active: bool
    reason: str
    amount_cents: int = 0
    source: str = ""
    reference: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "active": self.active,
            "reason": self.reason,
            "amount_cents": self.amount_cents,
            "amount_eur": round(self.amount_cents / 100, 2),
            "currency": "EUR",
            "source": self.source,
            "reference": self.reference,
            "target_amount_cents": TARGET_AMOUNT_CENTS,
        }


def _truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "y", "on", "confirmed"}


def _evidence_raw() -> str:
    return (
        os.environ.get("DOSSIER_FATALITY_EVIDENCE_JSON")
        or os.environ.get("TRYONYOU_CAPITAL_450K_EVIDENCE_JSON")
        or ""
    ).strip()


def _evidence_path() -> Path | None:
    raw = _evidence_raw()
    return Path(raw).expanduser() if raw and not raw.startswith("{") else None


def load_evidence() -> dict[str, Any] | None:
    raw = _evidence_raw()
    if not raw:
        return None
    if raw.startswith("{"):
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError("evidence_must_be_json_object")
        return data
    path = Path(raw).expanduser()
    if not path.is_file():
        raise FileNotFoundError(str(path))
    return _read_evidence(path)


def _target_amount_cents() -> int:
    raw = (
        os.environ.get("DOSSIER_FATALITY_TARGET_CENTS")
        or os.environ.get("TRYONYOU_CAPITAL_450K_TARGET_CENTS")
        or ""
    ).strip()
    return int(raw) if raw else TARGET_AMOUNT_CENTS


def _is_tuesday_0800(now: datetime) -> bool:
    local = now.astimezone(PARIS_TZ)
    return local.weekday() == 1 and local.hour == 8


def _read_evidence(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("evidence_must_be_json_object")
    return data


def _amount_cents(data: dict[str, Any]) -> int:
    if "amount_cents" in data:
        return int(data["amount_cents"])
    if "amount_eur" in data:
        return int(round(float(data["amount_eur"]) * 100))
    raise ValueError("missing_amount")


def evaluate_guard(now: datetime | None = None) -> dict[str, Any]:
    now = now or datetime.now(tz=PARIS_TZ)
    target = _target_amount_cents()
    failures: list[str] = []
    evidence: dict[str, Any] | None = None
    amount = 0

    if not _is_tuesday_0800(now):
        failures.append("window_not_reached")
    if not _truthy(os.environ.get("TRYONYOU_CAPITAL_450K_CONFIRMED")):
        failures.append("confirmation_flag_missing")
    if not _truthy(os.environ.get("DOSSIER_FATALITY_ENABLE")):
        failures.append("fatality_enable_missing")

    try:
        evidence = load_evidence()
        if evidence is None:
            failures.append("evidence_missing")
        else:
            amount = _amount_cents(evidence)
            source = str(evidence.get("source") or "").strip().lower()
            reference = str(evidence.get("reference") or "").strip()
            currency = str(evidence.get("currency") or "EUR").strip().upper()
            if currency != "EUR":
                failures.append("currency_not_eur")
            if source not in VALID_SOURCES:
                failures.append("source_invalid")
            if not reference:
                failures.append("reference_missing")
            if amount < target:
                failures.append("amount_below_target")
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        failures.append(f"evidence_invalid:{exc}")

    active = not failures
    return {
        "status": "DOSSIER_FATALITY_ACTIVE" if active else "PENDING_VALIDATION",
        "active": active,
        "capital_target_cents": target,
        "capital_target_eur": round(target / 100, 2),
        "amount_cents": amount,
        "amount_eur": round(amount / 100, 2),
        "currency": "EUR",
        "evidence": evidence or {},
        "checks": {"failures": failures},
    }


def evaluate_fatality_guard(now: datetime | None = None) -> FatalityDecision:
    now = now or datetime.now(tz=PARIS_TZ)

    if not _is_tuesday_0800(now):
        return FatalityDecision("PENDING_VALIDATION", False, "outside_tuesday_0800_window")

    if not _truthy(os.environ.get("TRYONYOU_CAPITAL_450K_CONFIRMED")):
        return FatalityDecision("PENDING_VALIDATION", False, "missing_confirmation_flag")

    if not _truthy(os.environ.get("DOSSIER_FATALITY_ENABLE")):
        return FatalityDecision("PENDING_VALIDATION", False, "missing_fatality_enable_flag")

    if not _evidence_raw():
        return FatalityDecision("PENDING_VALIDATION", False, "missing_evidence_json")

    try:
        evidence = load_evidence()
        if evidence is None:
            return FatalityDecision("PENDING_VALIDATION", False, "missing_evidence_json")
        amount = _amount_cents(evidence)
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        return FatalityDecision("PENDING_VALIDATION", False, f"invalid_evidence:{exc}")

    source = str(evidence.get("source") or "").strip().lower()
    reference = str(evidence.get("reference") or "").strip()
    if source not in VALID_SOURCES:
        return FatalityDecision("PENDING_VALIDATION", False, "invalid_source", amount, source, reference)
    if not reference:
        return FatalityDecision("PENDING_VALIDATION", False, "missing_reference", amount, source, reference)
    if amount < TARGET_AMOUNT_CENTS:
        return FatalityDecision("PENDING_VALIDATION", False, "amount_below_450k", amount, source, reference)

    return FatalityDecision(
        "DOSSIER_FATALITY_ACTIVE",
        True,
        "capital_verified_with_evidence",
        amount,
        source,
        reference,
    )


def main() -> int:
    decision = evaluate_fatality_guard()
    print(json.dumps(decision.as_dict(), indent=2, ensure_ascii=False))
    return 0 if decision.active else 3


if __name__ == "__main__":
    raise SystemExit(main())
