#!/usr/bin/env python3
"""
Orquestador autónomo TryOnYou:
- Notifica hitos por Telegram con @tryonyou_deploy_bot (credenciales por entorno).
- Ejecuta Supercommit_Max para sincronización búnker Oberkampf (75011) y galería web.
- Evalúa compuerta de seguridad del martes 08:00 (Europe/Paris) para 450.000 EUR.
- Activa Dossier Fatality con trazabilidad local cuando aplica.

Patente: PCT/EP2025/067317
Bajo Protocolo de Soberanía V10 - Founder: Rubén
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
from zoneinfo import ZoneInfo

import requests

BOT_USERNAME = "@tryonyou_deploy_bot"
PATENT = "PCT/EP2025/067317"
FOUNDER_LINE = "Bajo Protocolo de Soberanía V10 - Founder: Rubén"
PARIS_TZ = ZoneInfo("Europe/Paris")
TARGET_DAY = 1  # martes = 1 (lunes=0)
TARGET_HOUR = 8
TARGET_MINUTE = 0
TARGET_CAPITAL_EUR = 450000.0

ROOT = Path(__file__).resolve().parent
DOSSIER_FILE = ROOT / "dossier_fatality.json"
LOG_DIR = ROOT / "logs"
SECURITY_LOG_FILE = LOG_DIR / "dossier_fatality_activation.json"


@dataclass
class TelegramConfig:
    token: str
    chat_id: str

    @property
    def is_ready(self) -> bool:
        return bool(self.token and self.chat_id)


def _sanitize_token(raw: str) -> str:
    return re.sub(r"\s+", "", raw or "")


def _parse_amount(raw: str) -> float | None:
    txt = (raw or "").strip()
    if not txt:
        return None
    normalized = txt.replace("€", "").replace("EUR", "").replace(".", "").replace(",", ".")
    normalized = normalized.strip()
    try:
        return float(normalized)
    except ValueError:
        return None


def telegram_config() -> TelegramConfig:
    token = _sanitize_token(
        os.getenv("TRYONYOU_DEPLOY_BOT_TOKEN", "")
        or os.getenv("TELEGRAM_BOT_TOKEN", "")
        or os.getenv("TELEGRAM_TOKEN", "")
    )
    chat_id = (
        os.getenv("TRYONYOU_DEPLOY_CHAT_ID", "").strip()
        or os.getenv("TELEGRAM_CHAT_ID", "").strip()
        or BOT_USERNAME
    )
    return TelegramConfig(token=token, chat_id=chat_id)


def notify(stage: str, ok: bool, detail: str, cfg: TelegramConfig) -> None:
    status = "✅ ÉXITO" if ok else "⚠️ ALERTA"
    text = (
        f"{status} | {stage}\n"
        f"Bot: {BOT_USERNAME}\n"
        f"Detalle: {detail}\n"
        f"Patente: {PATENT}\n"
        f"{FOUNDER_LINE}"
    )
    print(f"[telegram] {stage}: {detail}")
    if not cfg.is_ready:
        print("[telegram] omitido: faltan token/chat_id en entorno.")
        return
    url = f"https://api.telegram.org/bot{cfg.token}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": cfg.chat_id, "text": text}, timeout=30)
        if r.status_code != 200:
            print(f"[telegram] HTTP {r.status_code}: {r.text[:180]}", file=sys.stderr)
    except requests.RequestException as exc:
        print(f"[telegram] error de red: {exc}", file=sys.stderr)


def run_cmd(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=str(ROOT), capture_output=True, text=True)


def run_supercommit() -> tuple[bool, str]:
    cmd = [str(ROOT / "supercommit_max.sh")]
    commit_msg = (
        "chore: Supercommit_Max Oberkampf 75011 -> galería web "
        "@CertezaAbsoluta @lo+erestu PCT/EP2025/067317 "
        "Bajo Protocolo de Soberanía V10 - Founder: Rubén"
    )
    cmd.append(commit_msg)
    proc = run_cmd(cmd)
    if proc.returncode == 0:
        return True, "Supercommit_Max ejecutado y sincronización completada."
    tail = (proc.stderr or proc.stdout or "").strip().splitlines()
    resume = tail[-1] if tail else "Fallo sin salida"
    return False, f"Supercommit_Max falló: {resume}"


def _is_security_window(now: datetime) -> bool:
    return (
        now.weekday() == TARGET_DAY
        and now.hour == TARGET_HOUR
        and now.minute >= TARGET_MINUTE
    )


def _activate_dossier(now: datetime, capital: float) -> tuple[bool, str]:
    if not DOSSIER_FILE.is_file():
        return False, "No existe dossier_fatality.json para activación."
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "activated_at": now.isoformat(timespec="seconds"),
        "timezone": "Europe/Paris",
        "capital_confirmed_eur": capital,
        "threshold_eur": TARGET_CAPITAL_EUR,
        "dossier_file": str(DOSSIER_FILE.name),
        "status": "ACTIVATED",
    }
    SECURITY_LOG_FILE.write_text(
        json.dumps(payload, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    return True, f"Dossier Fatality activado y registrado en {SECURITY_LOG_FILE.name}."


def security_protocol(force: bool = False) -> tuple[bool, str]:
    now = datetime.now(PARIS_TZ)
    should_execute = force or _is_security_window(now)
    capital = _parse_amount(os.getenv("TRYONYOU_CAPITAL_EUR", ""))

    if not should_execute:
        return True, (
            f"Compuerta en espera: se ejecuta martes 08:00 Europe/Paris. "
            f"Ahora: {now.isoformat(timespec='minutes')}"
        )

    if capital is None:
        return False, (
            "Capital no definido; exporta TRYONYOU_CAPITAL_EUR para validar 450000 EUR."
        )

    if capital < TARGET_CAPITAL_EUR:
        return False, (
            f"Capital insuficiente ({capital:.2f} EUR), requerido: {TARGET_CAPITAL_EUR:.2f} EUR."
        )

    return _activate_dossier(now, capital)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Orquestador autónomo Supercommit_Max")
    parser.add_argument(
        "--force-security",
        action="store_true",
        help="fuerza evaluación de seguridad sin esperar martes 08:00",
    )
    parser.add_argument(
        "--skip-supercommit",
        action="store_true",
        help="omite ejecución de supercommit_max.sh",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cfg = telegram_config()

    notify(
        stage="Inicio de misión autónoma",
        ok=True,
        detail="Orquestador activo para búnker 75011 y galería web.",
        cfg=cfg,
    )

    if not args.skip_supercommit:
        ok_supercommit, detail_supercommit = run_supercommit()
        notify("Supercommit_Max", ok_supercommit, detail_supercommit, cfg)
        if not ok_supercommit:
            return 1
    else:
        notify(
            stage="Supercommit_Max",
            ok=True,
            detail="Omitido por bandera --skip-supercommit.",
            cfg=cfg,
        )

    ok_security, detail_security = security_protocol(force=args.force_security)
    notify("Dossier Fatality", ok_security, detail_security, cfg)

    return 0 if ok_security else 1


if __name__ == "__main__":
    raise SystemExit(main())
