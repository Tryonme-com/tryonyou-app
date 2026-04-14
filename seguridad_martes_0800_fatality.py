#!/usr/bin/env python3
"""
Guardia de seguridad TryOnYou (martes 08:00) para capital 450.000 EUR.

Objetivo:
- Verificar una confirmacion documental de ingreso (ledger JSON).
- Activar el Dossier Fatality de forma auditable.
- Notificar exito por Telegram (bot operativo).

Uso (cron recomendado):
  # martes 08:00 Europa/Paris
  0 8 * * 2 cd /workspace && /usr/bin/env TZ=Europe/Paris \
    python3 seguridad_martes_0800_fatality.py

Variables opcionales:
- BUNKER_TIMEZONE=Europe/Paris
- BUNKER_TARGET_AMOUNT_EUR=450000
- BUNKER_CAPITAL_LEDGER=/workspace/capital_ingresos.json
- BUNKER_DOSSIER_FILE=/workspace/dossier_fatality.json
- BUNKER_ENFORCE_TUESDAY_WINDOW=1
- TRYONYOU_DEPLOY_BOT_TOKEN / TELEGRAM_BOT_TOKEN / TELEGRAM_TOKEN
- TRYONYOU_DEPLOY_CHAT_ID / TELEGRAM_CHAT_ID
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import requests

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover
    ZoneInfo = None  # type: ignore[assignment]


PATENT = "PCT/EP2025/067317"
BOT_NAME = "@tryonyou_deploy_bot"


@dataclass
class CapitalEntry:
    amount_eur: float
    currency: str
    status: str
    reference: str
    received_at: str
    source: str


def _load_json(path: Path) -> dict:
    if not path.is_file():
        raise FileNotFoundError(f"No existe el archivo requerido: {path}")
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _now_in_timezone(tz_name: str) -> datetime:
    if ZoneInfo is None:
        return datetime.now()
    try:
        return datetime.now(ZoneInfo(tz_name))
    except Exception:
        return datetime.now()


def _is_tuesday_0800_window(now: datetime) -> bool:
    return now.weekday() == 1 and now.hour == 8


def _parse_entry(raw: dict) -> CapitalEntry:
    amount_raw = raw.get("amount_eur", 0)
    try:
        amount = float(amount_raw)
    except (TypeError, ValueError):
        amount = 0.0
    return CapitalEntry(
        amount_eur=amount,
        currency=str(raw.get("currency", "EUR")),
        status=str(raw.get("status", "")).lower(),
        reference=str(raw.get("reference", "N/A")),
        received_at=str(raw.get("received_at", "")),
        source=str(raw.get("source", "ledger")),
    )


def _find_confirmed_entry(ledger_data: dict, target_amount: float) -> CapitalEntry | None:
    entries = ledger_data.get("entries", [])
    if not isinstance(entries, list):
        return None
    for item in entries:
        if not isinstance(item, dict):
            continue
        entry = _parse_entry(item)
        if (
            entry.status in {"confirmed", "settled"}
            and entry.currency.upper() == "EUR"
            and abs(entry.amount_eur - target_amount) < 0.01
        ):
            return entry
    return None


def _notify_telegram(message: str) -> bool:
    token = (
        os.environ.get("TRYONYOU_DEPLOY_BOT_TOKEN", "").strip()
        or os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
        or os.environ.get("TELEGRAM_TOKEN", "").strip()
    )
    chat_id = (
        os.environ.get("TRYONYOU_DEPLOY_CHAT_ID", "").strip()
        or os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    )
    if not token or not chat_id:
        print(
            "⚠️ Notificacion omitida: faltan token/chat_id de Telegram en entorno.",
            file=sys.stderr,
        )
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    try:
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            return True
        print(
            f"⚠️ Telegram HTTP {response.status_code}: {response.text[:300]}",
            file=sys.stderr,
        )
    except requests.RequestException as exc:
        print(f"⚠️ Telegram error de red: {exc}", file=sys.stderr)
    return False


def _activate_dossier(dossier_file: Path, entry: CapitalEntry, now: datetime) -> None:
    dossier = _load_json(dossier_file)
    dossier["fatality_activation"] = {
        "active": True,
        "trigger": "capital-confirmed",
        "target_amount_eur": entry.amount_eur,
        "reference": entry.reference,
        "received_at": entry.received_at,
        "source": entry.source,
        "activated_at": now.isoformat(),
        "location_sync": "Oberkampf 75011 -> galeria web",
        "safety_protocol": "Dossier Fatality",
        "patent": PATENT,
    }
    with dossier_file.open("w", encoding="utf-8") as fh:
        json.dump(dossier, fh, indent=4, ensure_ascii=False)
        fh.write("\n")


def main() -> int:
    tz_name = os.environ.get("BUNKER_TIMEZONE", "Europe/Paris").strip() or "Europe/Paris"
    target_amount = float(os.environ.get("BUNKER_TARGET_AMOUNT_EUR", "450000").strip())
    enforce_window = os.environ.get("BUNKER_ENFORCE_TUESDAY_WINDOW", "1").strip() not in {
        "0",
        "false",
        "False",
        "no",
    }

    ledger_file = Path(
        os.environ.get("BUNKER_CAPITAL_LEDGER", "/workspace/capital_ingresos.json").strip()
    )
    dossier_file = Path(
        os.environ.get("BUNKER_DOSSIER_FILE", "/workspace/dossier_fatality.json").strip()
    )

    now = _now_in_timezone(tz_name)
    in_window = _is_tuesday_0800_window(now)
    print(f"[INFO] Ahora: {now.isoformat()} ({tz_name})")
    print(f"[INFO] Ventana martes 08:00: {'SI' if in_window else 'NO'}")
    print(f"[INFO] Objetivo de capital: {target_amount:,.2f} EUR")

    if enforce_window and not in_window:
        print("ℹ️ Fuera de ventana de ejecucion. No se activa protocolo.")
        return 0

    try:
        ledger_data = _load_json(ledger_file)
    except Exception as exc:
        print(f"❌ No se pudo leer ledger de capital: {exc}", file=sys.stderr)
        return 2

    entry = _find_confirmed_entry(ledger_data, target_amount)
    if not entry:
        print(
            "❌ No hay confirmacion documental para 450000 EUR en estado confirmed/settled.",
            file=sys.stderr,
        )
        return 3

    try:
        _activate_dossier(dossier_file, entry, now)
    except Exception as exc:
        print(f"❌ Error activando dossier fatality: {exc}", file=sys.stderr)
        return 4

    message = (
        "TRYONYOU SECURITY SUCCESS\n"
        f"Bot: {BOT_NAME}\n"
        f"Capital confirmado: {entry.amount_eur:,.2f} EUR\n"
        f"Referencia: {entry.reference}\n"
        "Accion: Dossier Fatality ACTIVADO\n"
        "Ubicacion: Oberkampf 75011 sincronizado con galeria web\n"
        f"Patente: {PATENT}"
    )
    notified = _notify_telegram(message)
    print("✅ Dossier Fatality activado y registrado.")
    if notified:
        print("✅ Notificacion Telegram enviada.")
    else:
        print("⚠️ Activacion completada sin confirmacion de Telegram.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
