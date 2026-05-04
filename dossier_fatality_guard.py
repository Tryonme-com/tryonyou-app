#!/usr/bin/env python3
"""
Guard operativo para Dossier Fatality.

No confirma capital por narrativa. Solo activa el estado si coinciden:
  - ventana martes 08:00 UTC,
  - flag explicito TRYONYOU_CAPITAL_450K_CONFIRMED=1,
  - evidencia JSON local con origen bancario/Qonto y minimo 450.000 EUR.

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberania V10 - Founder: Ruben
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
DEFAULT_EVIDENCE_PATH = ROOT / "capital_450k_evidence.json"
DEFAULT_STATE_PATH = ROOT / "dossier_fatality_state.json"
MIN_CAPITAL_CENTS = 45_000_000

ALLOWED_SOURCES = {"qonto", "bank", "banking", "treasury_monitor"}


@dataclass(frozen=True)
class FatalityDecision:
    status: str
    activated: bool
    reason: str
    amount_cents: int = 0
    evidence_ref: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "activated": self.activated,
            "reason": self.reason,
            "amount_cents": self.amount_cents,
            "evidence_ref": self.evidence_ref,
        }


def parse_now(raw: str | None) -> datetime:
    if not raw:
        return datetime.now(timezone.utc)
    value = raw.strip()
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def is_tuesday_0800(now: datetime) -> bool:
    return now.weekday() == 1 and now.hour == 8


def read_evidence(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def amount_to_cents(data: dict[str, Any]) -> int:
    raw = data.get("amount_cents")
    if raw is None:
        raw = data.get("confirmed_amount_cents")
    if raw is not None:
        try:
            return int(raw)
        except (TypeError, ValueError):
            return 0

    euros = data.get("amount_eur")
    if euros is None:
        euros = data.get("confirmed_amount_eur")
    if euros is None:
        return 0
    try:
        return int(round(float(str(euros).replace(",", ".")) * 100))
    except (TypeError, ValueError):
        return 0


def evaluate(now: datetime, evidence: dict[str, Any], env: dict[str, str] | None = None) -> FatalityDecision:
    environ = env if env is not None else os.environ
    if not is_tuesday_0800(now):
        return FatalityDecision("PENDING_VALIDATION", False, "outside_tuesday_0800_window")

    if environ.get("TRYONYOU_CAPITAL_450K_CONFIRMED", "").strip() != "1":
        return FatalityDecision("PENDING_VALIDATION", False, "missing_explicit_capital_confirmation")

    source = str(evidence.get("source") or "").strip().lower()
    if source not in ALLOWED_SOURCES:
        return FatalityDecision("PENDING_VALIDATION", False, "missing_verifiable_bank_source")

    amount_cents = amount_to_cents(evidence)
    if amount_cents < MIN_CAPITAL_CENTS:
        return FatalityDecision("PENDING_VALIDATION", False, "capital_below_450k", amount_cents)

    evidence_ref = str(evidence.get("reference") or evidence.get("transaction_id") or "").strip()
    if not evidence_ref:
        return FatalityDecision("PENDING_VALIDATION", False, "missing_evidence_reference", amount_cents)

    return FatalityDecision("DOSSIER_FATALITY_ACTIVE", True, "capital_verified", amount_cents, evidence_ref)


def evaluate_guard(
    now: datetime | None = None,
    evidence_path: Path | str = DEFAULT_EVIDENCE_PATH,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    current = now or datetime.now(timezone.utc)
    decision = evaluate(current, read_evidence(Path(evidence_path)), env=env)
    reasons = [] if decision.activated else [decision.reason]
    return {
        "status": decision.status,
        "activated": decision.activated,
        "reasons": reasons,
        "reason": decision.reason,
        "amount_cents": decision.amount_cents,
        "evidence_ref": decision.evidence_ref,
    }


def write_state(path: Path, now: datetime, decision: FatalityDecision) -> None:
    payload = {
        "ts": now.isoformat(),
        "protocol": "DOSSIER_FATALITY",
        "minimum_required_cents": MIN_CAPITAL_CENTS,
        **decision.to_dict(),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida activacion segura del Dossier Fatality.")
    parser.add_argument("--now", help="ISO datetime para ejecuciones controladas/tests.")
    parser.add_argument("--evidence", default=str(DEFAULT_EVIDENCE_PATH), help="Ruta JSON de evidencia bancaria.")
    parser.add_argument("--state", default=str(DEFAULT_STATE_PATH), help="Ruta de salida del estado.")
    args = parser.parse_args()

    now = parse_now(args.now)
    evidence_path = Path(args.evidence)
    state_path = Path(args.state)
    decision = evaluate(now, read_evidence(evidence_path))
    write_state(state_path, now, decision)
    print(json.dumps({"now": now.isoformat(), **decision.to_dict()}, ensure_ascii=False, indent=2))
    return 0 if decision.activated else 2


if __name__ == "__main__":
    raise SystemExit(main())
