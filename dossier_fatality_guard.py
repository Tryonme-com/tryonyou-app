#!/usr/bin/env python3
"""
Guardia de seguridad financiera TryOnYou (martes 08:00, Europe/Paris).

Objetivo:
- Confirmar entrada verificable de 450.000 EUR.
- Activar Dossier Fatality solo si se cumple ventana y evidencia.
- Notificar resultado por Telegram usando @tryonyou_deploy_bot.

Sin secretos en código. Variables de entorno:
  TRYONYOU_DEPLOY_BOT_TOKEN o TELEGRAM_BOT_TOKEN/TELEGRAM_TOKEN
  TRYONYOU_DEPLOY_CHAT_ID o TELEGRAM_CHAT_ID
  TRYONYOU_DEPLOY_BOT_NAME (default: @tryonyou_deploy_bot)
  FATALITY_TARGET_AMOUNT_EUR (default: 450000)
  FATALITY_TIMEZONE (default: Europe/Paris)
  FATALITY_STRICT_TUESDAY_0800 (default: 1)
  FATALITY_EVIDENCE_FILE (default: registro_pagos_hoy.csv)
  FATALITY_NOW_ISO (opcional, pruebas)
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import requests

PATENT = "PCT/EP2025/067317"
PROTOCOL = "Bajo Protocolo de Soberanía V10 - Founder: Rubén"
BOT_NAME_DEFAULT = "@tryonyou_deploy_bot"
DEFAULT_TARGET = 450000.0
DEFAULT_TZ = "Europe/Paris"
DEFAULT_EVIDENCE = "registro_pagos_hoy.csv"
DOSSIER_PATH = Path("dossier_fatality.json")
ACTIVATION_LOG = Path("logs/dossier_fatality_activation.json")


@dataclass
class EvidenceResult:
    confirmed: bool
    detail: str
    amount_eur: float
    source: str


def _truthy(name: str, default: bool = False) -> bool:
    raw = os.getenv(name, "")
    if not raw:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _now_paris() -> datetime:
    override = os.getenv("FATALITY_NOW_ISO", "").strip()
    tz = ZoneInfo(os.getenv("FATALITY_TIMEZONE", DEFAULT_TZ).strip() or DEFAULT_TZ)
    if not override:
        return datetime.now(tz)
    parsed = datetime.fromisoformat(override.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=tz)
    return parsed.astimezone(tz)


def _is_tuesday_0800(now_dt: datetime) -> bool:
    return now_dt.weekday() == 1 and now_dt.hour == 8


def _parse_float(value: Any) -> float:
    txt = str(value or "").strip()
    if not txt:
        return 0.0
    txt = txt.replace("€", "").replace(" ", "")
    if "," in txt and "." in txt:
        if txt.rfind(",") > txt.rfind("."):
            txt = txt.replace(".", "").replace(",", ".")
        else:
            txt = txt.replace(",", "")
    elif "," in txt:
        txt = txt.replace(",", ".")
    try:
        return float(txt)
    except ValueError:
        return 0.0


def _status_confirmed(value: Any) -> bool:
    status = str(value or "").strip().upper()
    return status in {"CONFIRMADO", "CONFIRMED", "SETTLED", "PAGADO", "OK"}


def _evidence_from_json(path: Path, target: float) -> EvidenceResult:
    payload = json.loads(path.read_text(encoding="utf-8"))
    records = payload if isinstance(payload, list) else [payload]
    for rec in records:
        if not isinstance(rec, dict):
            continue
        amount = _parse_float(rec.get("importe_eur") or rec.get("amount_eur"))
        status = rec.get("estado") or rec.get("status")
        if _status_confirmed(status) and amount >= target:
            return EvidenceResult(
                True,
                f"Pago confirmado >= objetivo ({amount:.2f} EUR).",
                amount,
                str(path),
            )
    return EvidenceResult(
        False,
        f"No hay pago confirmado >= {target:.2f} EUR en JSON.",
        0.0,
        str(path),
    )


def _evidence_from_csv(path: Path, target: float) -> EvidenceResult:
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        best = 0.0
        for row in reader:
            amount = _parse_float(row.get("importe_eur") or row.get("amount_eur"))
            status = row.get("estado") or row.get("status")
            if _status_confirmed(status):
                best = max(best, amount)
                if amount >= target:
                    return EvidenceResult(
                        True,
                        f"Pago confirmado >= objetivo ({amount:.2f} EUR).",
                        amount,
                        str(path),
                    )
    return EvidenceResult(
        False,
        f"Máximo confirmado en CSV: {best:.2f} EUR (< {target:.2f} EUR).",
        best,
        str(path),
    )


def check_evidence(target: float) -> EvidenceResult:
    p = Path(os.getenv("FATALITY_EVIDENCE_FILE", DEFAULT_EVIDENCE).strip() or DEFAULT_EVIDENCE)
    if not p.is_absolute():
        p = Path.cwd() / p
    if not p.is_file():
        return EvidenceResult(False, f"Evidencia no encontrada: {p}", 0.0, str(p))
    if p.suffix.lower() == ".json":
        return _evidence_from_json(p, target)
    if p.suffix.lower() == ".csv":
        return _evidence_from_csv(p, target)
    return EvidenceResult(False, f"Formato no soportado: {p.suffix}", 0.0, str(p))


def _bot_creds() -> tuple[str, str, str]:
    token = (
        os.getenv("TRYONYOU_DEPLOY_BOT_TOKEN", "").strip()
        or os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        or os.getenv("TELEGRAM_TOKEN", "").strip()
    )
    chat_id = (
        os.getenv("TRYONYOU_DEPLOY_CHAT_ID", "").strip()
        or os.getenv("TELEGRAM_CHAT_ID", "").strip()
    )
    bot_name = os.getenv("TRYONYOU_DEPLOY_BOT_NAME", BOT_NAME_DEFAULT).strip() or BOT_NAME_DEFAULT
    return bot_name, token, chat_id


def send_telegram(text: str) -> bool:
    bot_name, token, chat_id = _bot_creds()
    if not token or not chat_id:
        print(f"[WARN] {bot_name} sin token/chat configurado; omito aviso Telegram.")
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=30)
        if r.ok:
            return True
        print(f"[WARN] Telegram HTTP {r.status_code}: {r.text[:250]}")
    except requests.RequestException as exc:
        print(f"[WARN] Telegram error de red: {exc}")
    return False


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def activate_dossier(now_dt: datetime, ev: EvidenceResult, target: float) -> dict[str, Any]:
    ACTIVATION_LOG.parent.mkdir(parents=True, exist_ok=True)
    dossier_exists = DOSSIER_PATH.is_file()
    record: dict[str, Any] = {
        "timestamp": now_dt.isoformat(),
        "timezone": str(now_dt.tzinfo),
        "target_amount_eur": target,
        "evidence_confirmed": ev.confirmed,
        "evidence_detail": ev.detail,
        "evidence_source": ev.source,
        "evidence_amount_eur": ev.amount_eur,
        "dossier_file": str(DOSSIER_PATH),
        "dossier_exists": dossier_exists,
        "activated": False,
        "patent": PATENT,
        "protocol": PROTOCOL,
    }
    if dossier_exists:
        record["dossier_sha256"] = _sha256(DOSSIER_PATH)
    if dossier_exists and ev.confirmed:
        record["activated"] = True
    ACTIVATION_LOG.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return record


def run_guard() -> int:
    now_dt = _now_paris()
    target = float(os.getenv("FATALITY_TARGET_AMOUNT_EUR", str(DEFAULT_TARGET)).strip() or DEFAULT_TARGET)
    strict = _truthy("FATALITY_STRICT_TUESDAY_0800", default=True)
    in_window = _is_tuesday_0800(now_dt)
    ev = check_evidence(target)

    if strict and not in_window:
        msg = (
            f"✅ {BOT_NAME_DEFAULT} guardia ejecutada: fuera de ventana martes 08:00 "
            f"({now_dt.isoformat()}). Sin activación de Dossier Fatality."
        )
        print(msg)
        send_telegram(msg)
        return 0

    record = activate_dossier(now_dt, ev, target)
    if record["activated"]:
        msg = (
            f"✅ {BOT_NAME_DEFAULT} Seguridad OK: entrada {ev.amount_eur:,.2f} EUR confirmada. "
            f"Dossier Fatality ACTIVADO. {PATENT}"
        )
        print(msg)
        send_telegram(msg)
        return 0

    msg = (
        f"✅ {BOT_NAME_DEFAULT} guardia ejecutada: NO se activa Dossier Fatality. "
        f"Motivo: {ev.detail}"
    )
    print(msg)
    send_telegram(msg)
    return 0


if __name__ == "__main__":
    raise SystemExit(run_guard())
