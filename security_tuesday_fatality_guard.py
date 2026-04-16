#!/usr/bin/env python3
"""
Guardia de seguridad para martes 08:00:
- Verifica entrada de 450.000€ en registro CSV.
- Activa Dossier Fatality de forma auditable.
- Notifica por Telegram usando credenciales de entorno (sin hardcodear secretos).

Variables de entorno opcionales:
  SECURITY_EXPECTED_AMOUNT_EUR=450000
  SECURITY_PAYMENT_FILE=/workspace/registro_pagos_hoy.csv
  SECURITY_DOSSIER_PATH=/workspace/dossier_fatality.json
  SECURITY_EVENT_LOG=/workspace/logs/fatality_activation_log.jsonl
  SECURITY_ENFORCE_WINDOW=1  # fuerza validación de martes 08:00 local
  SUPERCOMMIT_TELEGRAM_TOKEN o TELEGRAM_BOT_TOKEN o TELEGRAM_TOKEN
  SUPERCOMMIT_TELEGRAM_CHAT_ID o TELEGRAM_CHAT_ID
"""
from __future__ import annotations

import csv
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parent
DEFAULT_PAYMENT_FILE = ROOT / "registro_pagos_hoy.csv"
DEFAULT_DOSSIER_PATH = ROOT / "dossier_fatality.json"
DEFAULT_EVENT_LOG = ROOT / "logs" / "fatality_activation_log.jsonl"


def _get_float(name: str, default: float) -> float:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _now_local() -> datetime:
    return datetime.now().astimezone()


def _within_tuesday_window(now_local: datetime) -> bool:
    # Tuesday=1 (Monday=0); ventana de 08:00 a 08:59 local.
    return now_local.weekday() == 1 and now_local.hour == 8


def _check_payment(payment_file: Path, expected_amount: float) -> tuple[bool, str]:
    if not payment_file.exists():
        return False, f"archivo de pagos no encontrado: {payment_file}"

    with payment_file.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            estado = (row.get("estado") or "").strip().upper()
            if estado != "CONFIRMADO":
                continue
            amount_raw = (row.get("importe_eur") or "").strip()
            try:
                amount = float(amount_raw)
            except ValueError:
                continue
            if abs(amount - expected_amount) < 0.0001:
                tx = (row.get("id_transaccion") or "").strip() or "SIN_ID"
                return True, f"entrada confirmada: {amount:.2f}€ ({tx})"

    return False, f"no existe movimiento CONFIRMADO por {expected_amount:.2f}€"


def _activate_dossier(dossier_path: Path, activation_note: str, now_local: datetime) -> None:
    payload: dict[str, object]
    if dossier_path.exists():
        try:
            payload = json.loads(dossier_path.read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                payload = {}
        except json.JSONDecodeError:
            payload = {}
    else:
        payload = {}

    payload["fatality_activated"] = True
    payload["fatality_activated_at_local"] = now_local.isoformat()
    payload["fatality_activation_note"] = activation_note
    payload["fatality_protocol"] = "Dossier Fatality"
    payload["capital_protected"] = True
    payload["capital_target_eur"] = 450000

    dossier_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _append_event_log(event_log: Path, item: dict[str, object]) -> None:
    event_log.parent.mkdir(parents=True, exist_ok=True)
    with event_log.open("a", encoding="utf-8") as f:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")


def _send_telegram_notice(message: str) -> None:
    token = (
        os.environ.get("SUPERCOMMIT_TELEGRAM_TOKEN", "").strip()
        or os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
        or os.environ.get("TELEGRAM_TOKEN", "").strip()
    )
    chat_id = (
        os.environ.get("SUPERCOMMIT_TELEGRAM_CHAT_ID", "").strip()
        or os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    )
    if not token or not chat_id:
        print("ℹ️ Telegram no configurado; notificación omitida.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    try:
        r = requests.post(url, json=payload, timeout=30)
        r.raise_for_status()
        print("📣 Notificación Telegram enviada.")
    except Exception as exc:
        print(f"⚠️ Telegram no entregado: {exc}")


def main() -> int:
    expected_amount = _get_float("SECURITY_EXPECTED_AMOUNT_EUR", 450000.0)
    payment_file = Path(
        os.environ.get("SECURITY_PAYMENT_FILE", str(DEFAULT_PAYMENT_FILE))
    ).resolve()
    dossier_path = Path(
        os.environ.get("SECURITY_DOSSIER_PATH", str(DEFAULT_DOSSIER_PATH))
    ).resolve()
    event_log = Path(os.environ.get("SECURITY_EVENT_LOG", str(DEFAULT_EVENT_LOG))).resolve()

    now_local = _now_local()
    enforce_window = os.environ.get("SECURITY_ENFORCE_WINDOW", "").strip() in {
        "1",
        "true",
        "TRUE",
        "yes",
        "on",
    }
    if enforce_window and not _within_tuesday_window(now_local):
        print("⏳ Fuera de ventana de ejecución (martes 08:00 local).")
        return 2

    ok, reason = _check_payment(payment_file, expected_amount)
    status = "ACTIVATED" if ok else "BLOCKED"
    message = (
        f"🛡️ Seguridad TryOnYou\n"
        f"Estado: {status}\n"
        f"Fecha: {now_local.isoformat()}\n"
        f"Detalle: {reason}"
    )

    if ok:
        _activate_dossier(dossier_path, reason, now_local)
        print("✅ Dossier Fatality activado.")
    else:
        print("⚠️ Dossier Fatality no activado.")

    _append_event_log(
        event_log,
        {
            "timestamp_local": now_local.isoformat(),
            "expected_amount_eur": expected_amount,
            "status": status,
            "detail": reason,
            "payment_file": str(payment_file),
            "dossier_path": str(dossier_path),
        },
    )
    _send_telegram_notice(message)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
