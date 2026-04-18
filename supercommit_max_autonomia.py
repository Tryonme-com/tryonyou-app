#!/usr/bin/env python3
"""
Orquestador autónomo TryOnYou:
1) Ejecuta Supercommit_Max para sincronizar búnker Oberkampf (75011) y galería web.
2) Reporta cada éxito por Telegram usando credenciales de entorno.
3) Martes 08:00 (Europe/Paris): confirma entrada >= 450.000€ y activa Dossier Fatality.

Nunca hardcodea secretos en el código.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import requests

ROOT = Path(__file__).resolve().parent
DOSSIER_FILE = ROOT / "dossier_fatality.json"
ACTIVATION_DIR = ROOT / "logs"
ACTIVATION_LOG = ACTIVATION_DIR / "dossier_fatality_activations.jsonl"
PATENT = "PCT/EP2025/067317"

REQUIRED_STAMPS = (
    "@CertezaAbsoluta @lo+erestu PCT/EP2025/067317 "
    "Bajo Protocolo de Soberanía V10 - Founder: Rubén"
)


def _truthy(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _safe_float(raw: str, fallback: float = 0.0) -> float:
    try:
        return float(str(raw).strip())
    except (TypeError, ValueError):
        return fallback


def _security_timezone() -> ZoneInfo:
    tz_name = (os.getenv("TRYONYOU_SECURITY_TIMEZONE") or "Europe/Paris").strip()
    try:
        return ZoneInfo(tz_name)
    except Exception:
        return ZoneInfo("Europe/Paris")


def _security_window(now: datetime) -> bool:
    # weekday(): lunes=0 ... martes=1
    return now.weekday() == 1 and now.hour == 8


def _confirmed_inbound_amount() -> float:
    # Fuente de verdad operativa por entorno; nunca se simula en código.
    if os.getenv("TRYONYOU_CONFIRMED_INBOUND_EUR"):
        return _safe_float(os.getenv("TRYONYOU_CONFIRMED_INBOUND_EUR", ""), 0.0)
    if os.getenv("TREASURY_CONFIRMED_INBOUND_EUR"):
        return _safe_float(os.getenv("TREASURY_CONFIRMED_INBOUND_EUR", ""), 0.0)
    return 0.0


def _load_dossier() -> dict[str, Any]:
    if not DOSSIER_FILE.exists():
        return {
            "estrategia": "DOSSIER FATALITY V10",
            "sello_legal": "Patente PCT/EP2025/067317 | SIRET 94361019600017",
        }
    with DOSSIER_FILE.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _activation_marker(now: datetime) -> Path:
    return ACTIVATION_DIR / f"dossier_fatality_{now.strftime('%Y%m%d_%H')}.lock"


def _log_sovereignty_event(event_type: str, detail: str, amount_eur: float = 0.0) -> None:
    try:
        from api.financial_guard import log_sovereignty_event

        log_sovereignty_event(
            event_type=event_type,
            detail=detail,
            session_id="autonomia_supercommit_max",
            amount_eur=amount_eur,
        )
    except Exception:
        # No bloquea el flujo si la capa de log no está disponible.
        pass


@dataclass
class TelegramReporter:
    token: str
    chat_id: str

    @classmethod
    def from_env(cls) -> "TelegramReporter":
        token = (
            os.getenv("TRYONYOU_DEPLOY_BOT_TOKEN", "").strip()
            or os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
            or os.getenv("TELEGRAM_TOKEN", "").strip()
        )
        chat_id = (
            os.getenv("TRYONYOU_DEPLOY_CHAT_ID", "").strip()
            or os.getenv("TELEGRAM_CHAT_ID", "").strip()
        )
        return cls(token=token, chat_id=chat_id)

    @property
    def configured(self) -> bool:
        return bool(self.token and self.chat_id)

    def send_success(self, message: str) -> bool:
        if not self.configured:
            print("ℹ️ Telegram no configurado (faltan token/chat_id).")
            return False
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": (
                "TRYONYOU AUTONOMIA TOTAL\n\n"
                f"✅ {message}\n\n"
                f"Patente: {PATENT}"
            ),
        }
        try:
            resp = requests.post(url, json=payload, timeout=30)
            if resp.status_code == 200:
                return True
            print(f"⚠️ Telegram HTTP {resp.status_code}: {resp.text[:240]}", file=sys.stderr)
        except requests.RequestException as exc:
            print(f"⚠️ Telegram error: {exc}", file=sys.stderr)
        return False


def run_supercommit(*, fast_mode: bool, dry_run: bool, reporter: TelegramReporter) -> None:
    msg_base = (
        "OMEGA_DEPLOY: Supercommit_Max sincronizando búnker Oberkampf 75011 con galería web "
        f"{REQUIRED_STAMPS}"
    )
    cmd = ["bash", str(ROOT / "TRYONYOU_SUPERCOMMIT_MAX.sh"), "--msg", msg_base]
    if fast_mode:
        cmd.append("--fast")

    if dry_run:
        print("🧪 DRY RUN supercommit:", " ".join(cmd))
        return

    subprocess.run(cmd, cwd=str(ROOT), check=True)
    reporter.send_success("Supercommit_Max ejecutado con sincronización Oberkampf ↔ galería web.")
    _log_sovereignty_event(
        "supercommit_max_success",
        "Sincronización Oberkampf 75011 y galería web completada.",
        amount_eur=0.0,
    )


def activate_dossier_fatality(*, now: datetime, inbound_amount: float, reporter: TelegramReporter) -> dict[str, Any]:
    ACTIVATION_DIR.mkdir(parents=True, exist_ok=True)
    marker = _activation_marker(now)
    if marker.exists():
        return {
            "status": "already_active",
            "message": "Dossier Fatality ya estaba activado en esta ventana horaria.",
        }

    dossier = _load_dossier()
    activation = {
        "status": "activated",
        "activated_at": now.isoformat(),
        "capital_confirmed_eur": inbound_amount,
        "threshold_eur": 450000.0,
        "protocol": "Dossier Fatality",
        "dossier": dossier,
        "patent": PATENT,
    }

    with ACTIVATION_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(activation, ensure_ascii=False) + "\n")
    marker.write_text("activated\n", encoding="utf-8")

    reporter.send_success(
        "Entrada de 450.000€ confirmada y Dossier Fatality activado para blindaje de capital."
    )
    _log_sovereignty_event(
        "dossier_fatality_activated",
        "Entrada confirmada y blindaje activado en ventana de seguridad.",
        amount_eur=inbound_amount,
    )
    return activation


def run_security_protocol(*, force: bool, dry_run: bool, reporter: TelegramReporter) -> dict[str, Any]:
    now = datetime.now(_security_timezone())
    in_window = _security_window(now)
    inbound = _confirmed_inbound_amount()

    if not force and not in_window:
        return {
            "status": "skipped",
            "message": "Fuera de ventana de seguridad (martes 08:00 Europe/Paris).",
            "now": now.isoformat(),
        }

    if inbound < 450000.0:
        return {
            "status": "blocked",
            "message": "Entrada no confirmada: se requieren 450.000€ o más.",
            "confirmed_inbound_eur": inbound,
            "required_eur": 450000.0,
        }

    if dry_run:
        return {
            "status": "dry_run",
            "message": "DRY RUN: activación de Dossier Fatality simulada.",
            "confirmed_inbound_eur": inbound,
            "at": now.isoformat(),
        }

    return activate_dossier_fatality(now=now, inbound_amount=inbound, reporter=reporter)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Autonomía total TryOnYou con Supercommit_Max.")
    parser.add_argument("--fast", action="store_true", help="Ejecuta Supercommit_Max en modo --fast.")
    parser.add_argument("--skip-supercommit", action="store_true", help="Omite la fase Supercommit_Max.")
    parser.add_argument(
        "--security-force",
        action="store_true",
        help="Fuerza la evaluación de seguridad aunque no sea martes 08:00.",
    )
    parser.add_argument("--dry-run", action="store_true", help="No ejecuta cambios ni llamadas externas.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    reporter = TelegramReporter.from_env()

    try:
        if not args.skip_supercommit:
            run_supercommit(fast_mode=args.fast, dry_run=args.dry_run, reporter=reporter)

        security_result = run_security_protocol(
            force=args.security_force,
            dry_run=args.dry_run,
            reporter=reporter,
        )
        print(json.dumps(security_result, ensure_ascii=False, indent=2))

        if security_result.get("status") == "blocked":
            return 2
        return 0
    except subprocess.CalledProcessError as exc:
        print(f"❌ Supercommit_Max falló con código {exc.returncode}.", file=sys.stderr)
        return exc.returncode or 1


if __name__ == "__main__":
    raise SystemExit(main())
