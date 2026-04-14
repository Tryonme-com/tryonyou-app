#!/usr/bin/env python3
"""
Autonomia total TryOnYou:
- Ejecuta Supercommit_Max.
- Reporta cada exito por Telegram usando @tryonyou_deploy_bot.
- En martes 08:00 valida entrada de 450000 EUR y activa Dossier Fatality.

Importante:
- No hardcodea secretos. Usa solo variables de entorno.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Sequence

import requests

BOT_USERNAME = "@tryonyou_deploy_bot"
PATENT = "PCT/EP2025/067317"
PROTOCOL = "Bajo Protocolo de Soberania V10 - Founder: Ruben"
SECURITY_TARGET_EUR = 450000.0
SECURITY_WEEKDAY = 1  # Tuesday in datetime.weekday() (Mon=0)
SECURITY_HOUR = 8

ROOT = Path(__file__).resolve().parent
DEFAULT_DOSSIER = ROOT / "dossier_fatality.json"
DEFAULT_ACTIVATION_LOG = ROOT / "dossier_fatality_activation_log.json"


@dataclass(frozen=True)
class TelegramConfig:
    token: str
    chat_id: str


@dataclass(frozen=True)
class SecurityEvaluation:
    due_now: bool
    amount_eur: float
    capital_confirmed: bool
    should_activate: bool
    reason: str


def _parse_bool(raw: str) -> bool:
    return raw.strip().lower() in {"1", "true", "yes", "on", "si", "y"}


def parse_eur_amount(raw: str) -> float:
    """
    Admite formatos como:
    - 450000
    - 450000.00
    - 450.000
    - 450.000,00
    - EUR 450,000.00
    """
    text = raw.strip()
    if not text:
        return 0.0

    filtered = re.sub(r"[^0-9,.\-]", "", text)
    if not filtered:
        return 0.0

    if "," in filtered and "." in filtered:
        # Si la coma va despues del punto, asumimos formato europeo.
        if filtered.rfind(",") > filtered.rfind("."):
            normalized = filtered.replace(".", "").replace(",", ".")
        else:
            # Formato tipo 450,000.50
            normalized = filtered.replace(",", "")
    elif "," in filtered:
        # Puede ser decimal o miles.
        parts = filtered.split(",")
        normalized = filtered.replace(",", "") if len(parts[-1]) == 3 else filtered.replace(",", ".")
    else:
        # Solo puntos: 450.000 o 450000.00
        parts = filtered.split(".")
        normalized = filtered.replace(".", "") if len(parts) > 2 else filtered

    try:
        return float(normalized)
    except ValueError:
        return 0.0


def is_security_window(now: datetime, window_minutes: int = 15) -> bool:
    if now.weekday() != SECURITY_WEEKDAY:
        return False
    if now.hour != SECURITY_HOUR:
        return False
    return 0 <= now.minute < max(1, window_minutes)


def evaluate_security(now: datetime, amount_raw: str, capital_confirmed: bool, force_due: bool = False) -> SecurityEvaluation:
    amount = parse_eur_amount(amount_raw)
    due = force_due or is_security_window(
        now, window_minutes=int(os.getenv("TRYONYOU_SECURITY_WINDOW_MINUTES", "15"))
    )

    if not due:
        return SecurityEvaluation(
            due_now=False,
            amount_eur=amount,
            capital_confirmed=capital_confirmed,
            should_activate=False,
            reason="Fuera de ventana de seguridad (martes 08:00).",
        )
    if not capital_confirmed:
        return SecurityEvaluation(
            due_now=True,
            amount_eur=amount,
            capital_confirmed=False,
            should_activate=False,
            reason="Capital no confirmado por entorno (TRYONYOU_CAPITAL_CONFIRMED).",
        )
    if amount < SECURITY_TARGET_EUR:
        return SecurityEvaluation(
            due_now=True,
            amount_eur=amount,
            capital_confirmed=True,
            should_activate=False,
            reason="Capital confirmado pero inferior a 450000 EUR.",
        )
    return SecurityEvaluation(
        due_now=True,
        amount_eur=amount,
        capital_confirmed=True,
        should_activate=True,
        reason="Condiciones cumplidas: activar Dossier Fatality.",
    )


def load_telegram_config() -> TelegramConfig:
    token = (
        os.getenv("TRYONYOU_DEPLOY_BOT_TOKEN", "").strip()
        or os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        or os.getenv("TELEGRAM_TOKEN", "").strip()
    )
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat_id:
        raise RuntimeError(
            "Falta token/chat para Telegram. Define TRYONYOU_DEPLOY_BOT_TOKEN (o TELEGRAM_BOT_TOKEN) y TELEGRAM_CHAT_ID."
        )
    return TelegramConfig(token=token, chat_id=chat_id)


def send_success_report(config: TelegramConfig, title: str, detail: str, dry_run: bool = False) -> bool:
    text = (
        f"✅ {title}\n"
        f"Bot: {BOT_USERNAME}\n"
        f"{detail}\n"
        f"Patente: {PATENT}\n"
        f"{PROTOCOL}"
    )
    if dry_run:
        print("[DRY-RUN][Telegram] Mensaje preparado:")
        print(text)
        return True

    url = f"https://api.telegram.org/bot{config.token}/sendMessage"
    resp = requests.post(
        url,
        json={"chat_id": config.chat_id, "text": text[:4000]},
        timeout=30,
    )
    if resp.status_code == 200:
        print("Telegram: notificacion de exito enviada.")
        return True
    print(f"Telegram fallo HTTP {resp.status_code}: {resp.text[:300]}", file=sys.stderr)
    return False


def activate_dossier_fatality(
    now: datetime,
    amount_eur: float,
    source: str,
    activation_log_path: Path = DEFAULT_ACTIVATION_LOG,
    dossier_path: Path = DEFAULT_DOSSIER,
    dry_run: bool = False,
) -> dict:
    dossier_payload: dict = {}
    if dossier_path.is_file():
        try:
            dossier_payload = json.loads(dossier_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            dossier_payload = {"warning": "dossier_fatality.json no es JSON valido"}

    payload = {
        "event": "DOSSIER_FATALITY_ACTIVATED",
        "activated_at": now.isoformat(timespec="seconds"),
        "capital_confirmed_eur": amount_eur,
        "source": source or "NO_SOURCE_PROVIDED",
        "bot_username": BOT_USERNAME,
        "security_window": "Tuesday 08:00",
        "patent": PATENT,
        "protocol": PROTOCOL,
        "dossier_snapshot": dossier_payload,
    }
    if dry_run:
        print("[DRY-RUN] Dossier Fatality a activar:")
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return payload

    activation_log_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Dossier Fatality activado. Registro: {activation_log_path}")
    return payload


def run_supercommit(extra_args: Sequence[str]) -> int:
    cmd = ["bash", "supercommit_max.sh", *extra_args]
    print("Ejecutando:", " ".join(cmd))
    completed = subprocess.run(cmd, cwd=ROOT, check=False)
    return completed.returncode


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Orquestador de autonomia total para Supercommit_Max + seguridad martes 08:00."
    )
    parser.add_argument("--fast", action="store_true", help="Ejecuta supercommit_max en modo --fast.")
    parser.add_argument("--deploy", action="store_true", help="Ejecuta supercommit_max con --deploy.")
    parser.add_argument("--msg", default="", help="Mensaje custom para supercommit_max.sh")
    parser.add_argument(
        "--skip-supercommit",
        action="store_true",
        help="No ejecuta supercommit_max.sh (solo logica de seguridad/notificacion).",
    )
    parser.add_argument(
        "--security-check-now",
        action="store_true",
        help="Fuerza la evaluacion de seguridad aunque no sea martes 08:00.",
    )
    parser.add_argument("--dry-run", action="store_true", help="No envia Telegram ni escribe activacion.")
    parser.add_argument(
        "--allow-missing-telegram",
        action="store_true",
        help="No falla si no hay credenciales Telegram (modo local).",
    )
    args = parser.parse_args(argv)

    telegram_config: TelegramConfig | None = None
    try:
        telegram_config = load_telegram_config()
    except RuntimeError as exc:
        if not args.allow_missing_telegram:
            print(str(exc), file=sys.stderr)
            return 2
        print(f"Aviso: {exc}", file=sys.stderr)

    supercommit_args: list[str] = []
    if args.fast:
        supercommit_args.append("--fast")
    if args.deploy:
        supercommit_args.append("--deploy")
    if args.msg:
        supercommit_args.extend(["--msg", args.msg])

    if not args.skip_supercommit:
        rc = run_supercommit(supercommit_args)
        if rc != 0:
            print(f"Supercommit_Max fallo con codigo {rc}.", file=sys.stderr)
            return rc
        if telegram_config:
            send_success_report(
                telegram_config,
                "Supercommit_Max OK",
                "Bunker Oberkampf (75011) sincronizado con la galeria web.",
                dry_run=args.dry_run,
            )

    now = datetime.now()
    amount_raw = os.getenv("TRYONYOU_CAPITAL_INFLOW_EUR", "")
    confirmed = _parse_bool(os.getenv("TRYONYOU_CAPITAL_CONFIRMED", "0"))
    eval_result = evaluate_security(
        now=now,
        amount_raw=amount_raw,
        capital_confirmed=confirmed,
        force_due=args.security_check_now,
    )
    print(f"Seguridad: {eval_result.reason}")

    if not eval_result.due_now:
        return 0
    if not eval_result.should_activate:
        # No mentir confirmaciones financieras sin soporte.
        return 3

    source = os.getenv("TRYONYOU_CAPITAL_SOURCE", "manual_env_check")
    activate_dossier_fatality(
        now=now,
        amount_eur=eval_result.amount_eur,
        source=source,
        dry_run=args.dry_run,
    )
    if telegram_config:
        send_success_report(
            telegram_config,
            "Dossier Fatality ACTIVADO",
            f"Capital confirmado: {eval_result.amount_eur:,.2f} EUR.",
            dry_run=args.dry_run,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
