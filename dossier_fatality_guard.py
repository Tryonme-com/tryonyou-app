from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


TARGET_AMOUNT_CENTS = 45_000_000
PARIS_TZ = ZoneInfo("Europe/Paris")


@dataclass(frozen=True)
class FatalityDecision:
    status: str
    ready: bool
    reasons: list[str]
    target_amount_cents: int = TARGET_AMOUNT_CENTS

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "ready": self.ready,
            "reasons": self.reasons,
            "target_amount_cents": self.target_amount_cents,
        }


def _parse_now(value: str | None) -> datetime:
    if not value:
        return datetime.now(PARIS_TZ)
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=PARIS_TZ)
    return parsed.astimezone(PARIS_TZ)


def _load_evidence(env: dict[str, str]) -> dict[str, Any]:
    raw = env.get("DOSSIER_FATALITY_EVIDENCE_JSON", "").strip()
    path = env.get("DOSSIER_FATALITY_EVIDENCE_PATH", "").strip()
    if raw:
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError("DOSSIER_FATALITY_EVIDENCE_JSON debe ser un objeto JSON")
        return data
    if path:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("DOSSIER_FATALITY_EVIDENCE_PATH debe contener un objeto JSON")
        return data
    return {}


def _amount_cents(evidence: dict[str, Any]) -> int:
    for key in ("amount_cents", "received_amount_cents", "qonto_amount_cents"):
        value = evidence.get(key)
        if value is not None:
            return int(value)
    value_eur = evidence.get("amount_eur") or evidence.get("received_amount_eur")
    if value_eur is None:
        return 0
    return int(round(float(value_eur) * 100))


def evaluate_fatality_guard(
    *,
    now: datetime | None = None,
    env: dict[str, str] | None = None,
) -> FatalityDecision:
    runtime_env = dict(os.environ if env is None else env)
    current = (now or datetime.now(PARIS_TZ)).astimezone(PARIS_TZ)
    reasons: list[str] = []

    if current.weekday() != 1 or current.hour != 8:
        reasons.append("outside_tuesday_0800_paris")

    if runtime_env.get("DOSSIER_FATALITY_ARM", "").strip() != "1":
        reasons.append("fatality_arm_not_enabled")

    try:
        evidence = _load_evidence(runtime_env)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        reasons.append(f"invalid_evidence:{exc}")
        evidence = {}

    amount = _amount_cents(evidence)
    currency = str(evidence.get("currency", "")).upper().strip()
    reference = str(evidence.get("reference", "")).strip()
    source = str(evidence.get("source", "")).lower().strip()

    if amount < TARGET_AMOUNT_CENTS:
        reasons.append("amount_below_450000_eur")
    if currency != "EUR":
        reasons.append("currency_not_eur")
    if not reference:
        reasons.append("missing_bank_reference")
    if source not in {"qonto", "bank", "treasury"}:
        reasons.append("missing_verified_source")

    if reasons:
        return FatalityDecision("PENDING_VALIDATION", False, reasons)
    return FatalityDecision("DOSSIER_FATALITY_READY", True, ["verified_450000_eur_window"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Guard verificable Dossier Fatality 450k.")
    parser.add_argument("--now", help="ISO datetime para pruebas controladas.")
    parser.add_argument("--json", action="store_true", help="Emite JSON compacto.")
    args = parser.parse_args()

    decision = evaluate_fatality_guard(now=_parse_now(args.now) if args.now else None)
    payload = decision.as_dict()
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    else:
        print(f"{payload['status']}: {', '.join(payload['reasons'])}")
    return 0 if decision.ready else 3


if __name__ == "__main__":
    raise SystemExit(main())
