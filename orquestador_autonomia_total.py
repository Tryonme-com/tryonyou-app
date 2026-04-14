#!/usr/bin/env python3
"""
Orquestador de autonomia total para TryOnYou.

Objetivo:
1) Ejecutar Supercommit_Max para sincronizar bunker (75011) con la galeria web.
2) Verificar hito financiero de 450000 EUR en martes 08:00 (Europe/Paris).
3) Activar Dossier Fatality para blindaje de capital.
4) Notificar cada exito por Telegram con @tryonyou_deploy_bot.

Seguridad:
- Nunca hardcodear secretos.
- Token/chat solo por entorno:
  TRYONYOU_DEPLOY_BOT_TOKEN o TELEGRAM_BOT_TOKEN o TELEGRAM_TOKEN
  TRYONYOU_DEPLOY_CHAT_ID o TELEGRAM_CHAT_ID
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

from api.treasury_monitor import get_treasury_status

BOT_USERNAME = "@tryonyou_deploy_bot"
EXPECTED_CAPITAL_EUR = 450_000.0
TIMEZONE_PARIS = "Europe/Paris"
DOSSIER_DIR = Path("dossiers") / "fatality"
SUPERCOMMIT_SCRIPT = Path("supercommit_max.sh")
DEFAULT_DEPLOY_CHAT_ID = "7868120279"


@dataclass
class StepResult:
    name: str
    success: bool
    detail: str


def now_paris() -> datetime:
    return datetime.now(ZoneInfo(TIMEZONE_PARIS))


def is_tuesday_0800(
    dt: datetime,
    expected_weekday: int = 1,
    expected_hour: int = 8,
    tolerance_minutes: int = 10,
) -> bool:
    """True si dt cae en martes 08:00 con tolerancia."""
    if dt.weekday() != expected_weekday:
        return False
    anchor = dt.replace(hour=expected_hour, minute=0, second=0, microsecond=0)
    delta_seconds = abs((dt - anchor).total_seconds())
    return delta_seconds <= tolerance_minutes * 60


def _env(name: str) -> str:
    return (os.getenv(name) or "").strip()


def telegram_credentials() -> tuple[str, str]:
    token = (
        _env("TRYONYOU_DEPLOY_BOT_TOKEN")
        or _env("TELEGRAM_BOT_TOKEN")
        or _env("TELEGRAM_TOKEN")
    )
    chat_id = (
        _env("TRYONYOU_DEPLOY_CHAT_ID")
        or _env("TELEGRAM_CHAT_ID")
        or DEFAULT_DEPLOY_CHAT_ID
    )
    return token, chat_id


def notify_telegram(message: str) -> StepResult:
    token, chat_id = telegram_credentials()
    if not token or not chat_id:
        return StepResult(
            name="telegram",
            success=False,
            detail=(
                "Falta token/chat_id en entorno. Configure TRYONYOU_DEPLOY_BOT_TOKEN/"
                "TELEGRAM_BOT_TOKEN y TRYONYOU_DEPLOY_CHAT_ID/TELEGRAM_CHAT_ID."
            ),
        )

    try:
        import requests
    except ImportError:
        return StepResult("telegram", False, "Falta dependencia: requests.")

    payload = {"chat_id": chat_id, "text": message}
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            return StepResult("telegram", True, "Notificacion enviada.")
        return StepResult(
            "telegram",
            False,
            f"Telegram HTTP {response.status_code}: {response.text[:220]}",
        )
    except requests.RequestException as exc:
        return StepResult("telegram", False, f"Error de red Telegram: {exc}")


def run_supercommit(fast_mode: bool, deploy_mode: bool) -> StepResult:
    if not SUPERCOMMIT_SCRIPT.exists():
        return StepResult(
            "supercommit",
            False,
            f"No existe {SUPERCOMMIT_SCRIPT} en la raiz del repositorio.",
        )

    cmd = ["bash", str(SUPERCOMMIT_SCRIPT)]
    if fast_mode:
        cmd.append("--fast")
    if deploy_mode:
        cmd.append("--deploy")
    cmd.extend(
        [
            "--msg",
            (
                "chore: sincronizacion bunker Oberkampf 75011 con galeria web "
                f"{BOT_USERNAME}"
            ),
        ]
    )

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode == 0:
        return StepResult("supercommit", True, "Supercommit_Max ejecutado.")
    if proc.stderr.strip():
        detail = proc.stderr.strip().splitlines()[-1]
    else:
        detail = "Supercommit_Max fallo sin detalle."
    return StepResult("supercommit", False, f"{detail} (exit={proc.returncode}).")


def has_capital_entry(treasury_status: dict[str, Any], expected_eur: float) -> bool:
    capital = float(treasury_status.get("capital_eur", 0.0))
    return capital >= expected_eur


def _vip_flow_rate() -> float:
    raw = _env("VIP_FLOW_RATE")
    if not raw:
        return 100.0
    try:
        return float(raw)
    except ValueError:
        return 100.0


def activate_fatality_dossier(
    treasury_status: dict[str, Any],
    now: datetime,
    expected_eur: float,
    output_dir: Path = DOSSIER_DIR,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    file_name = now.strftime("fatality_%Y%m%d_%H%M%S.json")
    path = output_dir / file_name

    vip_flow_rate = _vip_flow_rate()
    payload = {
        "protocol": "Dossier Fatality",
        "status": "ACTIVE",
        "capital_target_eur": expected_eur,
        "capital_reported_eur": float(treasury_status.get("capital_eur", 0.0)),
        "capital_label": treasury_status.get("capital_label", "Capital Social Blindado"),
        "reserve_eur": float(treasury_status.get("reserve_eur", 0.0)),
        "verification_window": "Tuesday 08:00 Europe/Paris",
        "verified_at_paris": now.isoformat(),
        "location": "Bunker Oberkampf 75011",
        "gallery_sync": "Web gallery TryOnYou",
        "bot": BOT_USERNAME,
        "patent": "PCT/EP2025/067317",
        "siret": "94361019600017",
        "vip_flow_rate": vip_flow_rate,
        "vip_flow_alert": vip_flow_rate < 99.0,
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def _report_success(step: str, detail: str) -> None:
    message = f"✅ {step}: {detail}\nBot: {BOT_USERNAME}"
    tg = notify_telegram(message)
    if not tg.success:
        print(f"⚠️ {tg.detail}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Orquestador TryOnYou autonomia total.")
    parser.add_argument(
        "--skip-supercommit",
        action="store_true",
        help="No ejecuta Supercommit_Max.",
    )
    parser.add_argument(
        "--supercommit-fast",
        action="store_true",
        help="Ejecuta Supercommit_Max con --fast.",
    )
    parser.add_argument(
        "--deploy",
        action="store_true",
        help="Pasa --deploy a Supercommit_Max.",
    )
    parser.add_argument(
        "--force-time-window",
        action="store_true",
        help="Permite ejecutar fuera de martes 08:00 Europe/Paris.",
    )
    parser.add_argument(
        "--expected-capital",
        type=float,
        default=EXPECTED_CAPITAL_EUR,
        help="Importe minimo esperado para confirmar capital.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    now = now_paris()

    if not args.skip_supercommit:
        supercommit = run_supercommit(
            fast_mode=args.supercommit_fast or not args.deploy,
            deploy_mode=args.deploy,
        )
        if not supercommit.success:
            print(f"❌ {supercommit.detail}", file=sys.stderr)
            return 1
        print(f"✅ {supercommit.detail}")
        _report_success("Supercommit_Max", supercommit.detail)

    if not (args.force_time_window or is_tuesday_0800(now)):
        print(
            "❌ Ventana de seguridad invalida: se exige martes 08:00 Europe/Paris. "
            "Use --force-time-window para contingencia controlada.",
            file=sys.stderr,
        )
        return 2

    treasury_status = get_treasury_status()
    if not has_capital_entry(treasury_status, args.expected_capital):
        print(
            "❌ Capital no confirmado. "
            f"Capital actual: {treasury_status.get('capital_eur', 0)} EUR | "
            f"Minimo exigido: {args.expected_capital} EUR.",
            file=sys.stderr,
        )
        return 3

    print(
        f"✅ Entrada de capital confirmada: {treasury_status.get('capital_eur')} EUR "
        f"(umbral {args.expected_capital} EUR)."
    )
    _report_success(
        "Tesoreria",
        (
            f"Capital confirmado {treasury_status.get('capital_eur')} EUR "
            "en ventana critica."
        ),
    )

    dossier_path = activate_fatality_dossier(
        treasury_status=treasury_status,
        now=now,
        expected_eur=args.expected_capital,
    )
    print(f"✅ Dossier Fatality activado: {dossier_path}")
    _report_success("Dossier Fatality", f"Activado en {dossier_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
