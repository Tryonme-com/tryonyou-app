"""
Seguridad soberana TryOnYou:
- Martes 08:00: confirma entrada de 450.000 EUR.
- Si se confirma, activa Dossier Fatality para proteger capital.

Uso:
  python3 seguridad_martes_0800.py
  python3 seguridad_martes_0800.py --run-now

Cron sugerido:
  0 8 * * 2 cd /workspace && /usr/bin/env FATALITY_SEND_TELEGRAM=1 \
  TELEGRAM_BOT_TOKEN=... TELEGRAM_CHAT_ID=... python3 seguridad_martes_0800.py

Patente: PCT/EP2025/067317
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOSSIER_FILE = ROOT / "dossier_fatality.json"
ACTIVATION_FILE = ROOT / "dossier_fatality_activation.json"
DEFAULT_PAYMENTS_FILE = ROOT / "registro_pagos_hoy.csv"
EXPECTED_CAPITAL_EUR = float(os.environ.get("FATALITY_EXPECTED_CAPITAL_EUR", "450000"))


def should_run_now(now: datetime, force: bool) -> bool:
    if force:
        return True
    # Python: Monday=0 ... Sunday=6, Tuesday=1
    return now.weekday() == 1 and now.hour == 8


def parse_amount(value: str) -> float:
    raw = (value or "").strip()
    if not raw:
        return 0.0

    # Regla:
    # - Si hay coma, asumimos coma decimal y puntos de miles: 450.000,00
    # - Si no hay coma, float estándar: 450000.0
    if "," in raw:
        normalized = raw.replace(".", "").replace(",", ".")
    else:
        normalized = raw
    return float(normalized)


def confirmed_total_from_csv(csv_path: Path) -> float:
    if not csv_path.is_file():
        return 0.0
    total = 0.0
    with csv_path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            estado = (row.get("estado") or "").strip().upper()
            if estado != "CONFIRMADO":
                continue
            total += parse_amount(row.get("importe_eur", "0"))
    return total


def telegram_notify(text: str) -> bool:
    if os.environ.get("FATALITY_SEND_TELEGRAM", "").strip().lower() not in {
        "1",
        "true",
        "yes",
    }:
        return True

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
        print("⚠️ Telegram omitido: faltan token/chat_id.")
        return False

    try:
        import requests
    except ImportError:
        print("⚠️ Telegram omitido: requests no disponible.")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        response = requests.post(
            url,
            json={"chat_id": chat, "text": text},
            timeout=30,
        )
        if response.status_code == 200:
            return True
        print(f"⚠️ Telegram HTTP {response.status_code}: {response.text[:180]}")
        return False
    except Exception as exc:  # pragma: no cover
        print(f"⚠️ Telegram no disponible: {exc}")
        return False


def activate_dossier(now: datetime, confirmed_total: float) -> dict:
    base_payload: dict = {}
    if DOSSIER_FILE.is_file():
        base_payload = json.loads(DOSSIER_FILE.read_text(encoding="utf-8"))

    hash_source = json.dumps(base_payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    activation = {
        "status": "ACTIVATED",
        "activated_at": now.isoformat(timespec="seconds"),
        "expected_capital_eur": EXPECTED_CAPITAL_EUR,
        "confirmed_capital_eur": round(confirmed_total, 2),
        "dossier_sha256": hashlib.sha256(hash_source).hexdigest(),
        "bot_channel": "@tryonyou_deploy_bot",
        "patent": "PCT/EP2025/067317",
    }
    ACTIVATION_FILE.write_text(
        json.dumps(activation, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return activation


def main() -> int:
    parser = argparse.ArgumentParser(description="Guardia de seguridad martes 08:00 (TryOnYou).")
    parser.add_argument("--run-now", action="store_true", help="Ejecuta sin validar día/hora.")
    parser.add_argument(
        "--payments-csv",
        default=str(DEFAULT_PAYMENTS_FILE),
        help="Ruta CSV de pagos (columnas: estado, importe_eur).",
    )
    args = parser.parse_args()

    now = datetime.now()
    if not should_run_now(now, args.run_now):
        print("Ventana fuera de horario (martes 08:00). No se ejecuta activación.")
        return 0

    payments_path = Path(args.payments_csv)
    confirmed_total = confirmed_total_from_csv(payments_path)
    print(f"Capital confirmado acumulado: {confirmed_total:,.2f} EUR")

    if confirmed_total < EXPECTED_CAPITAL_EUR:
        msg = (
            "🚨 Seguridad TryOnYou: capital insuficiente para activar Dossier Fatality.\n"
            f"Confirmado: {confirmed_total:,.2f} EUR\n"
            f"Esperado: {EXPECTED_CAPITAL_EUR:,.2f} EUR\n"
            "Acción: revisar tesorería y bloquear despliegues sensibles."
        )
        print(msg)
        telegram_notify(msg)
        return 1

    activation = activate_dossier(now, confirmed_total)
    msg = (
        "✅ Seguridad TryOnYou: entrada de 450.000 EUR confirmada.\n"
        "Dossier Fatality ACTIVADO para proteger capital.\n"
        f"Registro: {ACTIVATION_FILE.name}\n"
        f"Hash dossier: {activation['dossier_sha256'][:12]}…\n"
        "Bot: @tryonyou_deploy_bot"
    )
    print(msg)
    telegram_notify(msg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
