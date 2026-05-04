#!/usr/bin/env python3
"""Guard de activacion para Dossier Fatality.

El guard no confirma ingresos bancarios por narrativa. Solo activa proteccion de
capital cuando la ventana operativa y la evidencia local verificable coinciden.
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
DEFAULT_DOSSIER_PATH = ROOT / "dossier_fatality.json"
TARGET_AMOUNT_CENTS = 45_000_000
ACTIVE_STATUS = "DOSSIER_FATALITY_ACTIVE"
PENDING_STATUS = "PENDING_VALIDATION"


@dataclass(frozen=True)
class GuardResult:
    status: str
    activated: bool
    reason: str
    checked_utc: str
    evidence_path: str
    dossier_path: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "activated": self.activated,
            "reason": self.reason,
            "checked_utc": self.checked_utc,
            "evidence_path": self.evidence_path,
            "dossier_path": self.dossier_path,
        }


def _parse_now(raw: str | None) -> datetime:
    if not raw:
        return datetime.now(timezone.utc)
    normalized = raw.strip()
    if normalized.endswith("Z"):
        normalized = f"{normalized[:-1]}+00:00"
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def is_tuesday_0800_utc(now: datetime) -> bool:
    """Ventana estricta: martes a las 08:00 UTC."""
    candidate = now.astimezone(timezone.utc)
    return candidate.weekday() == 1 and candidate.hour == 8


def _env_confirmed() -> bool:
    return (os.environ.get("TRYONYOU_CAPITAL_450K_CONFIRMED") or "").strip() == "1"


def _load_evidence(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        payload = json.load(fh)
    if not isinstance(payload, dict):
        raise ValueError("evidence_must_be_json_object")
    return payload


def _evidence_amount_cents(payload: dict[str, Any]) -> int:
    raw = payload.get("amount_cents")
    if raw is None and payload.get("amount_eur") is not None:
        raw = int(round(float(payload["amount_eur"]) * 100))
    return int(raw or 0)


def evidence_is_valid(path: Path) -> tuple[bool, str]:
    if not path.exists():
        return False, "missing_evidence_file"
    try:
        payload = _load_evidence(path)
        amount_cents = _evidence_amount_cents(payload)
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        return False, f"invalid_evidence:{exc}"

    if amount_cents < TARGET_AMOUNT_CENTS:
        return False, "amount_below_450000_eur"

    source = str(payload.get("source") or "").strip().lower()
    if source not in {"qonto", "qonto_api", "qonto_statement", "bank_statement"}:
        return False, "unsupported_evidence_source"

    reference = str(payload.get("reference") or payload.get("transaction_id") or "").strip()
    if not reference:
        return False, "missing_transaction_reference"

    return True, "verified"


def _activate_dossier(path: Path, checked_utc: str) -> None:
    dossier: dict[str, Any]
    if path.exists():
        with path.open("r", encoding="utf-8") as fh:
            loaded = json.load(fh)
        dossier = loaded if isinstance(loaded, dict) else {}
    else:
        dossier = {"estrategia": "DOSSIER FATALITY V10"}

    dossier["capital_protection"] = {
        "status": ACTIVE_STATUS,
        "activated_utc": checked_utc,
        "amount_cents_minimum": TARGET_AMOUNT_CENTS,
        "protocol": "PCT/EP2025/067317",
    }
    with path.open("w", encoding="utf-8") as fh:
        json.dump(dossier, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def evaluate_guard(
    *,
    now: datetime | None = None,
    evidence_path: Path = DEFAULT_EVIDENCE_PATH,
    dossier_path: Path = DEFAULT_DOSSIER_PATH,
    activate: bool = False,
) -> GuardResult:
    checked = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    checked_utc = checked.isoformat().replace("+00:00", "Z")

    if not is_tuesday_0800_utc(checked):
        return GuardResult(
            status=PENDING_STATUS,
            activated=False,
            reason="outside_tuesday_0800_utc_window",
            checked_utc=checked_utc,
            evidence_path=str(evidence_path),
            dossier_path=str(dossier_path),
        )

    if not _env_confirmed():
        return GuardResult(
            status=PENDING_STATUS,
            activated=False,
            reason="missing_TRYONYOU_CAPITAL_450K_CONFIRMED",
            checked_utc=checked_utc,
            evidence_path=str(evidence_path),
            dossier_path=str(dossier_path),
        )

    valid, reason = evidence_is_valid(evidence_path)
    if not valid:
        return GuardResult(
            status=PENDING_STATUS,
            activated=False,
            reason=reason,
            checked_utc=checked_utc,
            evidence_path=str(evidence_path),
            dossier_path=str(dossier_path),
        )

    if activate:
        _activate_dossier(dossier_path, checked_utc)

    return GuardResult(
        status=ACTIVE_STATUS,
        activated=True,
        reason="verified_qonto_evidence",
        checked_utc=checked_utc,
        evidence_path=str(evidence_path),
        dossier_path=str(dossier_path),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Guard Dossier Fatality TryOnYou")
    parser.add_argument("--now", default=None, help="ISO timestamp para validacion determinista")
    parser.add_argument("--evidence", default=str(DEFAULT_EVIDENCE_PATH))
    parser.add_argument("--dossier", default=str(DEFAULT_DOSSIER_PATH))
    parser.add_argument("--activate", action="store_true", help="Escribe activacion si todo verifica")
    args = parser.parse_args(argv)

    result = evaluate_guard(
        now=_parse_now(args.now),
        evidence_path=Path(args.evidence),
        dossier_path=Path(args.dossier),
        activate=args.activate,
    )
    print(json.dumps(result.as_dict(), indent=2, ensure_ascii=False))
    return 0 if result.activated else 3


if __name__ == "__main__":
    raise SystemExit(main())
