#!/usr/bin/env python3
"""
Dossier Fatality Guard — verificacion bancaria 450.000 EUR.

No confirma ingresos reales por calendario ni por narrativa. El estado solo pasa a
``DOSSIER_FATALITY_READY`` cuando hay ventana operativa, armado explicito y
evidencia Qonto/bancaria con importe suficiente.

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

_DEFAULT_TARGET_CENTS = 45_000_000
_DEFAULT_TZ = "Europe/Paris"


def _env_true(name: str) -> bool:
    return (os.getenv(name) or "").strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    raw = (os.getenv(name) or "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _load_evidence() -> dict[str, Any]:
    raw = (os.getenv("DOSSIER_FATALITY_EVIDENCE_JSON") or "").strip()
    path = (os.getenv("DOSSIER_FATALITY_EVIDENCE_PATH") or "").strip()
    if raw:
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            return {"_error": "invalid_evidence_json"}
        return payload if isinstance(payload, dict) else {"_error": "evidence_json_not_object"}
    if path:
        p = Path(path)
        try:
            payload = json.loads(p.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return {"_error": "evidence_path_missing", "path": str(p)}
        except json.JSONDecodeError:
            return {"_error": "invalid_evidence_file_json", "path": str(p)}
        except OSError as exc:
            return {"_error": "evidence_path_unreadable", "path": str(p), "detail": str(exc)}
        return payload if isinstance(payload, dict) else {"_error": "evidence_file_not_object"}
    return {}


def _amount_cents(evidence: dict[str, Any]) -> int:
    for key in ("amount_cents", "received_amount_cents", "qonto_amount_cents"):
        value = evidence.get(key)
        try:
            cents = int(value)
        except (TypeError, ValueError):
            continue
        if cents > 0:
            return cents
    for key in ("amount_eur", "received_amount_eur", "qonto_amount_eur"):
        value = evidence.get(key)
        try:
            eur = float(str(value).replace(",", "."))
        except (TypeError, ValueError):
            continue
        if eur > 0:
            return int(round(eur * 100))
    return 0


def _operational_window(now: datetime, timezone_name: str) -> tuple[bool, str]:
    current = now.astimezone(ZoneInfo(timezone_name)) if now.tzinfo else now.replace(tzinfo=ZoneInfo(timezone_name))
    if current.weekday() != 1:
        return False, "outside_tuesday"
    if current.hour != 8:
        return False, "outside_0800_hour"
    return True, "tuesday_0800_window"


def evaluate_dossier_fatality(*, now: datetime | None = None) -> dict[str, Any]:
    timezone_name = (os.getenv("DOSSIER_FATALITY_TIMEZONE") or _DEFAULT_TZ).strip() or _DEFAULT_TZ
    current = now or datetime.now(ZoneInfo(timezone_name))
    in_window, window_reason = _operational_window(current, timezone_name)
    armed = _env_true("DOSSIER_FATALITY_ARM")
    target_cents = _env_int("DOSSIER_FATALITY_TARGET_CENTS", _DEFAULT_TARGET_CENTS)
    evidence = _load_evidence()

    if evidence.get("_error"):
        return {
            "status": "PENDING_VALIDATION",
            "reason": evidence["_error"],
            "target_cents": target_cents,
            "window": window_reason,
        }
    if not in_window:
        return {
            "status": "PENDING_VALIDATION",
            "reason": window_reason,
            "target_cents": target_cents,
            "armed": armed,
        }
    if not armed:
        return {
            "status": "PENDING_VALIDATION",
            "reason": "not_armed",
            "target_cents": target_cents,
            "window": window_reason,
        }

    amount_cents = _amount_cents(evidence)
    currency = str(evidence.get("currency") or "").strip().upper()
    reference = str(evidence.get("reference") or evidence.get("transaction_id") or "").strip()
    source = str(evidence.get("source") or evidence.get("provider") or "").strip().lower()
    if amount_cents < target_cents:
        status = "PENDING_VALIDATION"
        reason = "insufficient_evidence_amount"
    elif currency != "EUR":
        status = "PENDING_VALIDATION"
        reason = "currency_not_eur"
    elif not reference:
        status = "PENDING_VALIDATION"
        reason = "missing_reference"
    elif source and source not in {"qonto", "stripe", "bank", "banque"}:
        status = "PENDING_VALIDATION"
        reason = "unsupported_evidence_source"
    else:
        status = "DOSSIER_FATALITY_READY"
        reason = "bank_evidence_verified"

    return {
        "status": status,
        "reason": reason,
        "target_cents": target_cents,
        "amount_cents": amount_cents,
        "currency": currency or None,
        "reference": reference or None,
        "source": source or None,
        "window": window_reason,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evalua el guardia Dossier Fatality 450k.")
    parser.add_argument("--json", action="store_true", help="Imprime salida JSON.")
    args = parser.parse_args(argv)
    result = evaluate_dossier_fatality()
    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    else:
        print(f"{result['status']}: {result['reason']}")
    return 0 if result["status"] == "DOSSIER_FATALITY_READY" else 3


if __name__ == "__main__":
    raise SystemExit(main())
