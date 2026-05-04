"""Guard seguro para Dossier Fatality.

No confirma ingresos bancarios reales. Solo permite marcar el dossier como
activable cuando coinciden tres pruebas locales: ventana temporal martes 08:00,
confirmacion explicita por entorno y evidencia JSON con importe suficiente.
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

MIN_CAPITAL_CENTS = 45_000_000
DEFAULT_EVIDENCE_PATH = Path("docs/legal/compliance/capital_450k_evidence.json")


def _parse_now(value: str | None) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _load_evidence(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _amount_cents(evidence: dict[str, Any]) -> int:
    raw = evidence.get("amount_cents")
    if isinstance(raw, int):
        return raw
    amount_eur = evidence.get("amount_eur")
    if isinstance(amount_eur, (int, float)):
        return int(round(float(amount_eur) * 100))
    return 0


def evaluate_fatality_guard(
    *,
    now: datetime | None = None,
    evidence_path: Path = DEFAULT_EVIDENCE_PATH,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    env_map = os.environ if env is None else env
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    evidence = _load_evidence(evidence_path)
    amount_cents = _amount_cents(evidence)

    checks = {
        "is_tuesday": current.weekday() == 1,
        "is_0800_utc": current.hour == 8 and current.minute == 0,
        "capital_flag": env_map.get("TRYONYOU_CAPITAL_450K_CONFIRMED", "").strip() == "1",
        "evidence_file": evidence_path.is_file(),
        "amount_minimum": amount_cents >= MIN_CAPITAL_CENTS,
        "currency_eur": str(evidence.get("currency", "EUR")).upper() == "EUR",
    }
    active = all(checks.values())
    if not checks["is_tuesday"] or not checks["is_0800_utc"]:
        reason = "outside_tuesday_0800_window"
    elif not checks["capital_flag"]:
        reason = "missing_confirmation_flag"
    elif not checks["evidence_file"]:
        reason = "missing_evidence_file"
    elif not checks["amount_minimum"]:
        reason = "insufficient_evidence_amount"
    elif not checks["currency_eur"]:
        reason = "unsupported_currency"
    else:
        reason = "ready"

    return {
        "status": "DOSSIER_FATALITY_ARMED" if active else "PENDING_VALIDATION",
        "activated": active,
        "reason": reason,
        "checked_at": current.isoformat(),
        "required_window": "Tuesday 08:00 UTC",
        "minimum_capital_cents": MIN_CAPITAL_CENTS,
        "evidence_path": str(evidence_path),
        "evidence_amount_cents": amount_cents,
        "amount_cents": amount_cents,
        "checks": checks,
        "message": (
            "Dossier Fatality activable con evidencia local verificable."
            if active
            else "No se confirma entrada bancaria real ni se activa Dossier Fatality sin evidencia completa."
        ),
    }


def evaluate(
    *,
    now: datetime | None = None,
    evidence_path: Path = DEFAULT_EVIDENCE_PATH,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Alias estable para tests y orquestadores externos."""
    return evaluate_fatality_guard(now=now, evidence_path=evidence_path, env=env)


def main() -> int:
    parser = argparse.ArgumentParser(description="Evalua Dossier Fatality sin asumir liquidez real.")
    parser.add_argument("--now", help="ISO datetime para pruebas, por defecto hora actual UTC.")
    parser.add_argument(
        "--evidence",
        default=str(DEFAULT_EVIDENCE_PATH),
        help="Ruta JSON con amount_cents/amount_eur y currency=EUR.",
    )
    parser.add_argument("--json", action="store_true", help="Imprime solo JSON.")
    args = parser.parse_args()

    result = evaluate_fatality_guard(now=_parse_now(args.now), evidence_path=Path(args.evidence))
    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    else:
        print(f"[dossier_fatality_guard] {result['status']}: {result['message']}")
        print(json.dumps(result["checks"], ensure_ascii=False, sort_keys=True))
    return 0 if result["activated"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
