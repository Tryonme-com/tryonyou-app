"""
Guard de seguridad financiera (martes 08:00) para activar Dossier Fatality
solo con evidencia verificable de entrada de 450.000 €.

Uso:
  python3 dossier_fatality_guard.py

Variables de entorno:
  TRYONYOU_SETTLEMENT_FILE=/ruta/al/json
    JSON esperado (ejemplo):
      {"amount_eur": 450000, "currency": "EUR", "status": "confirmed"}
  TRYONYOU_FATALITY_OUTPUT=/ruta/salida (default: dossier_fatality_status.json)
  TRYONYOU_FATALITY_SIMULATE_OK=1
    Permite simular confirmación para entorno de pruebas.
"""
from __future__ import annotations

import json
import os
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import requests

BOT_NAME = os.environ.get("TRYONYOU_DEPLOY_BOT_NAME", "@tryonyou_deploy_bot").strip()
BOT_TOKEN = (
    os.environ.get("TRYONYOU_DEPLOY_BOT_TOKEN", "").strip()
    or os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    or os.environ.get("TELEGRAM_TOKEN", "").strip()
)
BOT_CHAT_ID = (
    os.environ.get("TRYONYOU_DEPLOY_CHAT_ID", "").strip()
    or os.environ.get("TELEGRAM_CHAT_ID", "").strip()
)
SETTLEMENT_FILE = Path(
    os.environ.get("TRYONYOU_SETTLEMENT_FILE", "").strip()
    or os.environ.get("FATALITY_EVIDENCE_PATH", "").strip()
    or "settlement_confirmation.json"
)
OUTPUT_FILE = Path(
    os.environ.get("TRYONYOU_FATALITY_OUTPUT", "").strip() or "dossier_fatality_status.json"
)
DOSSIER_FILE = Path(
    os.environ.get("FATALITY_DOSSIER_PATH", "").strip() or "dossier_fatality.json"
)
ARMED_FILE = Path(
    os.environ.get("FATALITY_ARMED_PATH", "").strip() or "dossier_fatality_armed.json"
)
SIMULATE_OK = os.environ.get("TRYONYOU_FATALITY_SIMULATE_OK", "").strip() in (
    "1",
    "true",
    "yes",
)


def _send_bot(text: str) -> None:
    if not BOT_TOKEN or not BOT_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(
            url,
            data={"chat_id": BOT_CHAT_ID, "text": f"{BOT_NAME} :: {text}"},
            timeout=30,
        )
    except Exception:
        # No romper el flujo principal por un fallo de red del bot.
        return


def _is_target_slot(now: datetime) -> bool:
    # datetime.weekday(): martes == 1
    return now.weekday() == 1 and now.hour == 8


def _load_settlement() -> Dict[str, Any]:
    if SIMULATE_OK:
        return {"amount_eur": 450000, "currency": "EUR", "status": "confirmed"}
    if not SETTLEMENT_FILE.exists():
        return {}
    try:
        return json.loads(SETTLEMENT_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _is_confirmed_450k(data: Dict[str, Any]) -> bool:
    if not data:
        return False
    amount = data.get("amount_eur")
    currency = str(data.get("currency", "")).upper()
    status = str(data.get("status", "")).lower()
    try:
        amount_num = float(amount)
    except (TypeError, ValueError):
        return False
    return amount_num >= 450000 and currency == "EUR" and status == "confirmed"


def _parse_amount(amount_text: str) -> float:
    clean = str(amount_text).strip().replace(".", "").replace(",", ".")
    return float(clean)


def should_activate(now: datetime, amount_text: str, evidence_verified: bool) -> bool:
    if not _is_target_slot(now):
        return False
    if not evidence_verified:
        return False
    try:
        amount = _parse_amount(amount_text)
    except (TypeError, ValueError):
        return False
    return amount >= 450000


def summarize_activation(now: datetime, amount_text: str, evidence_verified: bool) -> str:
    active = should_activate(now, amount_text, evidence_verified)
    if active:
        return "DOSSIER FATALITY ACTIVADO: entrada 450.000€ validada en martes 08:00."
    return "DOSSIER FATALITY NO ACTIVADO: falta ventana, evidencia o importe mínimo."


def _write_status(payload: Dict[str, Any]) -> None:
    OUTPUT_FILE.write_text(
        json.dumps(payload, ensure_ascii=True, indent=2),
        encoding="utf-8",
    )


def _load_dossier() -> Dict[str, Any]:
    if not DOSSIER_FILE.exists():
        return {}
    try:
        return json.loads(DOSSIER_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _arm_dossier(base_payload: Dict[str, Any]) -> bool:
    dossier = _load_dossier()
    if not dossier:
        return False
    armed_payload = deepcopy(dossier)
    armed_payload["armed_at"] = base_payload["timestamp"]
    armed_payload["armed_by"] = "dossier_fatality_guard.py"
    armed_payload["activation_reason"] = base_payload["reason"]
    ARMED_FILE.write_text(
        json.dumps(armed_payload, ensure_ascii=True, indent=2),
        encoding="utf-8",
    )
    return True


def main() -> int:
    now = datetime.now()
    base_payload: Dict[str, Any] = {
        "timestamp": now.isoformat(timespec="seconds"),
        "protocol": "Dossier Fatality Guard",
        "target_slot": "Tuesday 08:00",
        "activated": False,
        "reason": "",
    }

    if not _is_target_slot(now):
        base_payload["reason"] = "Fuera de ventana (martes 08:00)."
        _write_status(base_payload)
        print(base_payload["reason"])
        return 0

    settlement = _load_settlement()
    base_payload["evidence_file"] = str(SETTLEMENT_FILE)
    base_payload["evidence_present"] = bool(settlement)

    if _is_confirmed_450k(settlement):
        base_payload["activated"] = True
        base_payload["reason"] = "Entrada 450.000 € confirmada con evidencia verificable."
        base_payload["capital_protected"] = True
        base_payload["dossier_source"] = str(DOSSIER_FILE)
        base_payload["dossier_armed_path"] = str(ARMED_FILE)
        base_payload["dossier_armed"] = _arm_dossier(base_payload)
        _write_status(base_payload)
        _send_bot("✅ Entrada 450.000€ confirmada y Dossier Fatality activado.")
        print(base_payload["reason"])
        return 0

    base_payload["reason"] = (
        "Sin confirmación verificable de 450.000 €; Dossier Fatality NO activado."
    )
    _write_status(base_payload)
    _send_bot("⚠️ Martes 08:00: sin evidencia verificable de 450.000€ (no activado).")
    print(base_payload["reason"])
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
