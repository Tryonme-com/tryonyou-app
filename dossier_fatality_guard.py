#!/usr/bin/env python3
"""
Guard financiero para Dossier Fatality.

No confirma entradas bancarias por sí mismo: solo activa el estado protegido si
la ventana operativa, el flag manual y una evidencia local verificable coinciden.
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

REQUIRED_AMOUNT_CENTS = 45_000_000
MIN_CAPITAL_CENTS = REQUIRED_AMOUNT_CENTS
STATUS_ACTIVE = "DOSSIER_FATALITY_ACTIVE"
STATUS_PENDING = "PENDING_VALIDATION"
DEFAULT_EVIDENCE_PATH = "capital_450k_evidence.json"
ALLOWED_EVIDENCE_SOURCES = {"qonto", "bank", "banking", "treasury", "manual_bank_review"}


@dataclass(frozen=True)
class FatalityDecision:
    status: str
    active: bool
    reason: str
    checked_at: str
    evidence_path: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "active": self.active,
            "reason": self.reason,
            "checked_at": self.checked_at,
            "evidence_path": self.evidence_path,
        }


def parse_now(value: str | None, timezone: str) -> datetime:
    tz = ZoneInfo(timezone)
    if value:
        normalized = value.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalized)
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=tz)
        return parsed.astimezone(tz)
    return datetime.now(tz)


def is_activation_window(now: datetime) -> bool:
    return now.weekday() == 1 and now.hour == 8


def env_confirms_capital() -> bool:
    return os.environ.get("TRYONYOU_CAPITAL_450K_CONFIRMED", "").strip() == "1"


def _amount_to_cents(data: dict[str, Any]) -> int:
    if data.get("amount_cents") is not None:
        return int(data["amount_cents"])
    amount_eur = data.get("amount_eur", 0)
    return int(float(amount_eur) * 100)


def load_evidence(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {"ok": False, "error": "evidence_not_found"}
    except json.JSONDecodeError as exc:
        return {"ok": False, "error": f"invalid_json:{exc.msg}"}

    try:
        amount_cents = _amount_to_cents(data)
    except (TypeError, ValueError):
        return {"ok": False, "error": "invalid_amount"}
    currency = str(data.get("currency", "")).lower()
    source = str(data.get("source", "")).lower()
    reference = str(data.get("reference", "")).strip()
    if currency != "eur":
        return {"ok": False, "error": "currency_must_be_eur"}
    if amount_cents < MIN_CAPITAL_CENTS:
        return {"ok": False, "error": "amount_below_450k_eur"}
    if source not in ALLOWED_EVIDENCE_SOURCES:
        return {"ok": False, "error": "evidencia_no_bancaria_o_qonto"}
    if not reference:
        return {"ok": False, "error": "missing_reference"}
    return {"ok": True, "amount_cents": amount_cents, "source": source, "reference": reference}


def evaluate(
    *,
    now: datetime,
    evidence_path: Path,
    require_window: bool = True,
) -> FatalityDecision:
    checked_at = now.isoformat()
    if require_window and not is_activation_window(now):
        return FatalityDecision(
            status=STATUS_PENDING,
            active=False,
            reason="fuera_de_ventana_martes_08",
            checked_at=checked_at,
            evidence_path=str(evidence_path),
        )
    if not env_confirms_capital():
        return FatalityDecision(
            status=STATUS_PENDING,
            active=False,
            reason="missing_TRYONYOU_CAPITAL_450K_CONFIRMED",
            checked_at=checked_at,
            evidence_path=str(evidence_path),
        )
    evidence = load_evidence(evidence_path)
    if not evidence.get("ok"):
        return FatalityDecision(
            status=STATUS_PENDING,
            active=False,
            reason=str(evidence.get("error", "invalid_evidence")),
            checked_at=checked_at,
            evidence_path=str(evidence_path),
        )
    return FatalityDecision(
        status=STATUS_ACTIVE,
        active=True,
        reason="Dossier Fatality activo: evidencia de capital verificada",
        checked_at=checked_at,
        evidence_path=str(evidence_path),
    )


def evaluate_dossier_fatality(*, now_iso: str | None = None) -> dict[str, Any]:
    """API estable para tests y orquestadores: devuelve dict serializable."""
    timezone = os.environ.get("TRYONYOU_FATALITY_TIMEZONE", "UTC")
    evidence = (
        os.environ.get("TRYONYOU_CAPITAL_450K_EVIDENCE_PATH")
        or os.environ.get("TRYONYOU_CAPITAL_450K_EVIDENCE")
        or DEFAULT_EVIDENCE_PATH
    )
    return evaluate(
        now=parse_now(now_iso, timezone),
        evidence_path=Path(evidence),
    ).to_dict()


def main() -> int:
    parser = argparse.ArgumentParser(description="Evalua la activacion segura del Dossier Fatality.")
    parser.add_argument("--now", help="ISO datetime para ejecucion controlada/tests.")
    parser.add_argument("--timezone", default=os.environ.get("TRYONYOU_FATALITY_TIMEZONE", "UTC"))
    parser.add_argument(
        "--evidence",
        default=(
            os.environ.get("TRYONYOU_CAPITAL_450K_EVIDENCE_PATH")
            or os.environ.get("TRYONYOU_CAPITAL_450K_EVIDENCE")
            or DEFAULT_EVIDENCE_PATH
        ),
    )
    parser.add_argument("--no-window", action="store_true", help="Solo para pruebas controladas.")
    parser.add_argument("--json", action="store_true", help="Salida JSON.")
    args = parser.parse_args()

    now = parse_now(args.now, args.timezone)
    decision = evaluate(
        now=now,
        evidence_path=Path(args.evidence),
        require_window=not args.no_window,
    )
    if args.json:
        print(json.dumps(decision.to_dict(), ensure_ascii=False, sort_keys=True))
    else:
        print(f"{decision.status}: {decision.reason}")
    return 0 if decision.active else 2


if __name__ == "__main__":
    raise SystemExit(main())
