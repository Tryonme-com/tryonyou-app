#!/usr/bin/env python3
"""
Guardia de seguridad financiera V10.

Objetivo:
- El martes a las 08:00 (hora local) verificar evidencia de entrada >= 450000 EUR.
- Si se confirma, activar Dossier Fatality de forma auditable (sin tocar sistemas externos).
- Notificar exito por Telegram via @tryonyou_deploy_bot cuando haya credenciales en entorno.

Uso:
  python3 seguridad_450k_martes_0800.py

Variables opcionales:
  TRYONYOU_NOW_ISO=2026-04-21T08:00:00   # para pruebas
  TRYONYOU_TIMEZONE=Europe/Paris
  TRYONYOU_REQUIRED_AMOUNT_EUR=450000
  TRYONYOU_LEDGER_CSV=registro_pagos_hoy.csv
  TRYONYOU_FATALITY_FILE=dossier_fatality.json
  TRYONYOU_DEPLOY_BOT_TOKEN=...          # prioridad sobre TELEGRAM_BOT_TOKEN/TELEGRAM_TOKEN
  TRYONYOU_DEPLOY_CHAT_ID=...            # prioridad sobre TELEGRAM_CHAT_ID
"""

from __future__ import annotations

import csv
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

PATENT = "PCT/EP2025/067317"
PROTOCOL = "Bajo Protocolo de Soberania V10 - Founder: Ruben"
BOT_NAME = "@tryonyou_deploy_bot"
SOVEREIGN_ZONE_DEFAULT = "Europe/Paris"
TRIGGER_WEEKDAY = 1  # Tuesday
TRIGGER_HOUR = 8
TRIGGER_MINUTE = 0


@dataclass
class VerificationResult:
    total_confirmed: float
    required_amount: float
    ledger_path: Path
    matched_rows: int

    @property
    def success(self) -> bool:
        return self.total_confirmed >= self.required_amount


def _now_local() -> datetime:
    tz_name = os.environ.get("TRYONYOU_TIMEZONE", SOVEREIGN_ZONE_DEFAULT).strip()
    tz = ZoneInfo(tz_name)
    now_override = os.environ.get("TRYONYOU_NOW_ISO", "").strip()
    if now_override:
        parsed = datetime.fromisoformat(now_override)
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=tz)
        return parsed.astimezone(tz)
    return datetime.now(tz)


def _trigger_window(now_local: datetime) -> bool:
    return (
        now_local.weekday() == TRIGGER_WEEKDAY
        and now_local.hour == TRIGGER_HOUR
        and now_local.minute == TRIGGER_MINUTE
    )


def _parse_amount(raw: str) -> float:
    value = raw.strip().replace(" ", "").replace(",", ".")
    return float(value)


def _read_confirmed_total(ledger_path: Path, required_amount: float) -> VerificationResult:
    if not ledger_path.is_file():
        raise FileNotFoundError(f"No existe el ledger CSV: {ledger_path}")

    total = 0.0
    matched = 0
    with ledger_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            state = (row.get("estado") or "").strip().upper()
            if state != "CONFIRMADO":
                continue
            amount_raw = row.get("importe_eur") or "0"
            try:
                amount = _parse_amount(amount_raw)
            except ValueError:
                continue
            total += amount
            matched += 1
    return VerificationResult(
        total_confirmed=round(total, 2),
        required_amount=required_amount,
        ledger_path=ledger_path,
        matched_rows=matched,
    )


def _telegram_notify(text: str) -> bool:
    token = (
        os.environ.get("TRYONYOU_DEPLOY_BOT_TOKEN", "").strip()
        or os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
        or os.environ.get("TELEGRAM_TOKEN", "").strip()
    )
    chat = (
        os.environ.get("TRYONYOU_DEPLOY_CHAT_ID", "").strip()
        or os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    )
    if not token or not chat:
        print("Telegram omitido: faltan token/chat_id.")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat, "text": text}
    response = requests.post(url, json=payload, timeout=30)
    if response.ok:
        print("Notificacion Telegram enviada.")
        return True
    print(f"Telegram HTTP {response.status_code}: {response.text[:200]}", file=sys.stderr)
    return False


def _activate_fatality_file(
    fatality_path: Path,
    now_local: datetime,
    verification: VerificationResult,
) -> dict:
    base_payload: dict
    if fatality_path.is_file():
        with fatality_path.open("r", encoding="utf-8") as handle:
            base_payload = json.load(handle)
    else:
        base_payload = {}

    base_payload["fatality_guard"] = {
        "status": "ACTIVE",
        "activated_at_local": now_local.isoformat(timespec="seconds"),
        "activation_rule": "martes_08_00_confirmacion_450000",
        "required_amount_eur": verification.required_amount,
        "confirmed_amount_eur": verification.total_confirmed,
        "matched_rows": verification.matched_rows,
        "ledger_source": str(verification.ledger_path),
        "capital_protection": "ENFORCED",
        "bot": BOT_NAME,
        "patent": PATENT,
        "protocol": PROTOCOL,
    }

    with fatality_path.open("w", encoding="utf-8") as handle:
        json.dump(base_payload, handle, ensure_ascii=True, indent=2)
        handle.write("\n")
    return base_payload


def main() -> int:
    now_local = _now_local()
    required_amount = float(os.environ.get("TRYONYOU_REQUIRED_AMOUNT_EUR", "450000"))
    ledger_path = Path(
        os.environ.get("TRYONYOU_LEDGER_CSV", "registro_pagos_hoy.csv").strip()
    ).resolve()
    fatality_path = Path(
        os.environ.get("TRYONYOU_FATALITY_FILE", "dossier_fatality.json").strip()
    ).resolve()

    print(
        f"[Seguridad] Ahora local: {now_local.isoformat(timespec='seconds')} "
        f"(disparo martes 08:00)."
    )
    if not _trigger_window(now_local):
        print("[Seguridad] Ventana no activa. No se ejecuta activacion.")
        return 0

    try:
        verification = _read_confirmed_total(ledger_path, required_amount)
    except FileNotFoundError as exc:
        print(f"[Seguridad] {exc}", file=sys.stderr)
        return 2

    print(
        "[Seguridad] Total confirmado: "
        f"{verification.total_confirmed:.2f} EUR "
        f"(requerido: {verification.required_amount:.2f} EUR)."
    )
    if not verification.success:
        print("[Seguridad] Capital insuficiente. Dossier Fatality no activado.", file=sys.stderr)
        return 3

    _activate_fatality_file(fatality_path, now_local, verification)
    message = (
        "EXITO TRYONYOU\n"
        f"Bot: {BOT_NAME}\n"
        "Operacion: Confirmacion martes 08:00 completada.\n"
        f"Capital confirmado: {verification.total_confirmed:.2f} EUR.\n"
        "Dossier Fatality activado para proteccion de capital.\n"
        f"{PATENT}\n"
        f"{PROTOCOL}"
    )
    _telegram_notify(message)
    print("[Seguridad] Dossier Fatality activado correctamente.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
