#!/usr/bin/env python3
"""
Guardia Dossier Fatality:
- Verifica el hito de 450.000 EUR.
- Activa el dossier en la ventana objetivo (martes 08:00 local).
- Reporta cada exito por Telegram usando variables de entorno (sin secretos hardcodeados).
"""

from __future__ import annotations

import argparse
import csv
import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

import requests


ROOT = Path(__file__).resolve().parent
LEDGER_PATH = ROOT / "registro_pagos_hoy.csv"
EMERGENCY_PATH = ROOT / ".emergency_payout"
STATUS_PATH = ROOT / "logs" / "dossier_fatality_status.json"
DOSSIER_PATH = ROOT / "dossier_fatality.json"


@dataclass(frozen=True)
class FatalityConfig:
    target_amount_eur: float
    target_weekday: int
    target_hour: int
    target_minute: int


def _now_local() -> datetime:
    return datetime.now().astimezone()


def _parse_emergency_amount(path: Path) -> float | None:
    if not path.exists():
        return None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("AMOUNT="):
            raw = line.split("=", 1)[1].strip()
            try:
                return float(raw)
            except ValueError:
                return None
    return None


def _iter_ledger_amounts(path: Path) -> Iterable[tuple[float, str, str]]:
    if not path.exists():
        return []
    rows: list[tuple[float, str, str]] = []
    with path.open("r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            raw_amount = (row.get("importe_eur") or "").strip()
            status = (row.get("estado") or "").strip().upper()
            txn_id = (row.get("id_transaccion") or "").strip()
            if not raw_amount:
                continue
            try:
                rows.append((float(raw_amount), status, txn_id))
            except ValueError:
                continue
    return rows


def _is_target_window(now: datetime, cfg: FatalityConfig) -> bool:
    return (
        now.weekday() == cfg.target_weekday
        and now.hour == cfg.target_hour
        and now.minute == cfg.target_minute
    )


def _payment_confirmed(cfg: FatalityConfig) -> tuple[bool, str]:
    tolerance = 0.01
    emergency_amount = _parse_emergency_amount(EMERGENCY_PATH)
    if emergency_amount is not None and abs(emergency_amount - cfg.target_amount_eur) <= tolerance:
        return True, f".emergency_payout AMOUNT={emergency_amount:.2f}"

    for amount, status, txn_id in _iter_ledger_amounts(LEDGER_PATH):
        if abs(amount - cfg.target_amount_eur) <= tolerance and status in {"CONFIRMADO", "CONFIRMED", "OK"}:
            ref = txn_id or "SIN_TXN"
            return True, f"registro_pagos_hoy.csv {amount:.2f} ({status}) [{ref}]"
    return False, "No existe confirmacion del importe objetivo en fuentes locales."


def _telegram_creds() -> tuple[str, str]:
    token = (
        os.getenv("TRYONYOU_DEPLOY_BOT_TOKEN", "").strip()
        or os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        or os.getenv("TELEGRAM_TOKEN", "").strip()
    )
    chat_id = (
        os.getenv("TRYONYOU_DEPLOY_CHAT_ID", "").strip()
        or os.getenv("TELEGRAM_CHAT_ID", "").strip()
    )
    return token, chat_id


def _send_telegram(message: str) -> None:
    token, chat_id = _telegram_creds()
    if not token or not chat_id:
        raise RuntimeError(
            "Faltan credenciales Telegram. Define TRYONYOU_DEPLOY_BOT_TOKEN/TELEGRAM_BOT_TOKEN y TRYONYOU_DEPLOY_CHAT_ID/TELEGRAM_CHAT_ID."
        )
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    response = requests.post(
        url,
        json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"},
        timeout=30,
    )
    response.raise_for_status()


def _write_status(payload: dict) -> None:
    STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATUS_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _load_dossier_summary() -> str:
    if not DOSSIER_PATH.exists():
        return "dossier_fatality.json no encontrado"
    try:
        data = json.loads(DOSSIER_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return "dossier_fatality.json inválido"
    strategy = data.get("estrategia", "DOSSIER_FATALITY")
    return str(strategy)


def run(force: bool, cfg: FatalityConfig) -> int:
    now = _now_local()
    payment_ok, source = _payment_confirmed(cfg)
    in_window = _is_target_window(now, cfg)

    payload = {
        "timestamp_local": now.isoformat(),
        "target_window": {
            "weekday": cfg.target_weekday,
            "hour": cfg.target_hour,
            "minute": cfg.target_minute,
        },
        "in_window": in_window,
        "force_mode": force,
        "target_amount_eur": cfg.target_amount_eur,
        "payment_confirmed": payment_ok,
        "payment_source": source,
        "dossier_strategy": _load_dossier_summary(),
        "activated": False,
    }

    if not payment_ok:
        _write_status(payload)
        print("❌ Fatality pendiente: no hay confirmación del ingreso objetivo.")
        print(f"   Detalle: {source}")
        return 2

    if not force and not in_window:
        _write_status(payload)
        print("⏳ Ingreso confirmado, pero fuera de ventana Martes 08:00. Sin activación.")
        return 0

    payload["activated"] = True
    payload["activation_note"] = "Dossier Fatality activado para protección de capital."
    _write_status(payload)

    msg = (
        "✅ *TryOnYou Dossier Fatality ACTIVADO*\n"
        f"💶 Ingreso confirmado: `{cfg.target_amount_eur:.2f} EUR`\n"
        f"🧾 Fuente: `{source}`\n"
        f"🛡️ Dossier: `{payload['dossier_strategy']}`\n"
        "🤖 Reporte emitido por @tryonyou_deploy_bot"
    )
    _send_telegram(msg)
    print("✅ Dossier Fatality activado y reportado por Telegram.")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Activador seguro del Dossier Fatality.")
    parser.add_argument("--force", action="store_true", help="Ignora la ventana Martes 08:00.")
    parser.add_argument("--target-amount", type=float, default=450000.0, help="Importe objetivo en EUR.")
    parser.add_argument(
        "--target-weekday",
        type=int,
        default=1,
        help="Día objetivo (lunes=0 ... domingo=6). Por defecto martes=1.",
    )
    parser.add_argument("--target-hour", type=int, default=8, help="Hora objetivo local.")
    parser.add_argument("--target-minute", type=int, default=0, help="Minuto objetivo local.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cfg = FatalityConfig(
        target_amount_eur=args.target_amount,
        target_weekday=args.target_weekday,
        target_hour=args.target_hour,
        target_minute=args.target_minute,
    )
    return run(force=args.force, cfg=cfg)


if __name__ == "__main__":
    raise SystemExit(main())
