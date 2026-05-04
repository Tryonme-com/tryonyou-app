#!/usr/bin/env python3
"""
Guardia de activacion Dossier Fatality.

No confirma ingresos bancarios por narrativa. Solo devuelve ``ACTIVATED`` si:
  1) La ventana soberana es martes 08:00.
  2) Existe confirmacion explicita en entorno.
  3) Hay evidencia JSON local con importe minimo verificable.

Patente: PCT/EP2025/067317 - @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberania V10 - Founder: Ruben
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
DEFAULT_EVIDENCE_PATH = ROOT / "logs" / "qonto_450k_evidence.json"
DEFAULT_STATUS_PATH = ROOT / "logs" / "dossier_fatality_guard_status.json"
MIN_AMOUNT_CENTS = 45_000_000


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def is_tuesday_0800(dt: datetime) -> bool:
    """UTC by default; callers may pass a localized datetime if needed."""
    return dt.weekday() == 1 and dt.hour == 8


def _amount_cents_from_evidence(payload: dict[str, Any]) -> int:
    for key in ("amount_cents", "confirmed_amount_cents", "total_balance_cents"):
        value = payload.get(key)
        if value is None:
            continue
        try:
            return int(value)
        except (TypeError, ValueError):
            continue

    eur = payload.get("amount_eur") or payload.get("confirmed_amount_eur")
    if eur is None:
        return 0
    try:
        return int(round(float(str(eur).replace(",", ".")) * 100))
    except (TypeError, ValueError):
        return 0


def load_evidence(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def evaluate_guard(*, now: datetime | None = None, evidence_path: Path | None = None) -> dict[str, Any]:
    now = now or _utc_now()
    evidence_path = evidence_path or DEFAULT_EVIDENCE_PATH
    confirm = (os.environ.get("TRYONYOU_CAPITAL_450K_CONFIRMED") or "").strip() == "1"
    window_ok = is_tuesday_0800(now)
    evidence = load_evidence(evidence_path)
    amount_cents = _amount_cents_from_evidence(evidence or {})
    evidence_ok = amount_cents >= MIN_AMOUNT_CENTS

    reasons: list[str] = []
    if not window_ok:
        reasons.append("fuera_de_ventana_martes_0800")
    if not confirm:
        reasons.append("falta_TRYONYOU_CAPITAL_450K_CONFIRMED=1")
    if not evidence_ok:
        reasons.append("evidencia_qonto_450k_ausente_o_insuficiente")

    activated = not reasons
    return {
        "status": "ACTIVATED" if activated else "PENDING_VALIDATION",
        "dossier": "DOSSIER_FATALITY",
        "checked_at_utc": now.isoformat().replace("+00:00", "Z"),
        "window_tuesday_0800": window_ok,
        "explicit_confirmation": confirm,
        "evidence_path": str(evidence_path.relative_to(ROOT) if evidence_path.is_relative_to(ROOT) else evidence_path),
        "evidence_amount_cents": amount_cents,
        "min_required_cents": MIN_AMOUNT_CENTS,
        "reasons": reasons,
        "policy": "No activar proteccion de capital sin evidencia bancaria verificable.",
    }


def write_status(status: dict[str, Any], path: Path = DEFAULT_STATUS_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(status, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Valida activacion segura del Dossier Fatality.")
    parser.add_argument("--evidence", default=str(DEFAULT_EVIDENCE_PATH), help="JSON local de evidencia Qonto/tesoreria.")
    parser.add_argument("--status-out", default=str(DEFAULT_STATUS_PATH), help="Ruta de salida del estado JSON.")
    parser.add_argument("--now", default="", help="ISO datetime para pruebas/control operativo.")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    now = datetime.fromisoformat(args.now.replace("Z", "+00:00")) if args.now else None
    status = evaluate_guard(now=now, evidence_path=Path(args.evidence))
    write_status(status, Path(args.status_out))
    print(json.dumps(status, indent=2, ensure_ascii=False))
    return 0 if status["status"] == "ACTIVATED" else 3


if __name__ == "__main__":
    raise SystemExit(main())
