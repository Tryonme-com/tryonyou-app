#!/usr/bin/env python3
"""
Guard de capital TryOnYou: no activa Dossier Fatality sin evidencia verificable.

Condiciones obligatorias:
  - ventana operativa martes 08:00 Europe/Paris (configurable por CLI para tests);
  - TRYONYOU_CAPITAL_450K_CONFIRMED=1;
  - evidencia JSON local con fuente bancaria/Qonto y mínimo 45.000.000 céntimos EUR.

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
DEFAULT_EVIDENCE_PATH = ROOT / "capital_450k_evidence.json"
MIN_CAPITAL_CENTS = 45_000_000
ALLOWED_SOURCES = {"qonto", "bank", "bank_transfer", "qonto_transaction"}
PARIS_TZ = ZoneInfo("Europe/Paris")


@dataclass(frozen=True)
class GuardResult:
    status: str
    reason: str
    amount_cents: int = 0
    source: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "reason": self.reason,
            "amount_cents": self.amount_cents,
            "source": self.source,
        }


def parse_now(raw: str | None = None) -> datetime:
    if not raw:
        return datetime.now(timezone.utc)
    normalized = raw.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def is_tuesday_0800_paris(now: datetime) -> bool:
    current = now.astimezone(PARIS_TZ)
    return current.weekday() == 1 and current.hour == 8 and current.minute == 0


def _amount_cents(data: dict[str, Any]) -> int:
    raw = data.get("amount_cents", data.get("amount_eur_cents", 0))
    if isinstance(raw, bool):
        return 0
    if isinstance(raw, int):
        return raw
    if isinstance(raw, float):
        return int(raw)
    if isinstance(raw, str) and raw.strip().isdigit():
        return int(raw.strip())
    amount_eur = data.get("amount_eur")
    if isinstance(amount_eur, (int, float)) and not isinstance(amount_eur, bool):
        return int(round(float(amount_eur) * 100))
    return 0


def read_evidence(path: Path) -> tuple[dict[str, Any], str]:
    if not path.exists():
        return {}, "evidence_missing"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}, "evidence_unreadable"
    if not isinstance(data, dict):
        return {}, "evidence_invalid"
    return data, ""


def evaluate_guard(now: datetime, evidence_path: Path | None = None) -> GuardResult:
    evidence = evidence_path or Path(
        (os.environ.get("DOSSIER_FATALITY_EVIDENCE_PATH") or "").strip()
        or str(DEFAULT_EVIDENCE_PATH)
    )
    if not is_tuesday_0800_paris(now):
        return GuardResult("PENDING_VALIDATION", "outside_tuesday_0800_paris")

    if (os.environ.get("TRYONYOU_CAPITAL_450K_CONFIRMED") or "").strip() != "1":
        return GuardResult("PENDING_VALIDATION", "confirmation_flag_missing")

    data, error = read_evidence(evidence)
    if error:
        return GuardResult("PENDING_VALIDATION", error)

    source = str(data.get("source", "")).strip().lower()
    reference = str(data.get("reference", "")).strip()
    currency = str(data.get("currency", "")).strip().upper()
    amount_cents = _amount_cents(data)

    if source not in ALLOWED_SOURCES:
        return GuardResult("PENDING_VALIDATION", "source_not_bank_or_qonto", amount_cents, source)
    if not reference:
        return GuardResult("PENDING_VALIDATION", "reference_missing", amount_cents, source)
    if currency != "EUR":
        return GuardResult("PENDING_VALIDATION", "currency_not_eur", amount_cents, source)
    if amount_cents < MIN_CAPITAL_CENTS:
        return GuardResult("PENDING_VALIDATION", "amount_below_450k_eur", amount_cents, source)

    return GuardResult("DOSSIER_FATALITY_ACTIVE", "verified_capital_guard_active", amount_cents, source)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Guard Dossier Fatality 450k TryOnYou")
    parser.add_argument("--now", help="ISO timestamp para ejecucion controlada/tests")
    parser.add_argument("--evidence", default=str(DEFAULT_EVIDENCE_PATH), help="Ruta JSON de evidencia bancaria/Qonto")
    parser.add_argument("--json", action="store_true", help="Imprimir salida JSON")
    args = parser.parse_args(argv)

    result = evaluate_guard(parse_now(args.now), Path(args.evidence))
    if args.json:
        print(json.dumps(result.as_dict(), ensure_ascii=False, sort_keys=True))
    else:
        print(f"{result.status}: {result.reason}")
    return 0 if result.status == "DOSSIER_FATALITY_ACTIVE" else 10


if __name__ == "__main__":
    raise SystemExit(main())
