#!/usr/bin/env python3
"""
Fatality Tuesday Guard
----------------------
Verifica el martes a las 08:00 (configurable) si el capital esperado alcanza
el umbral (por defecto 450000 EUR). Si se cumple, activa el Dossier Fatality
con artefacto local y notificacion Telegram via @tryonyou_deploy_bot.

No realiza operaciones bancarias reales ni imprime secretos.
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

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DOSSIER = ROOT / "dossier_fatality_activation.json"
PATENT = "PCT/EP2025/067317"


@dataclass
class GuardConfig:
    timezone: str
    required_weekday: int
    required_hour: int
    min_amount_eur: float
    amount_env: str
    node_label: str
    strict_schedule: bool
    dossier_path: Path


def _bool_env(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name, "")
    if not raw:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _current_amount(amount_env: str) -> float:
    raw = os.environ.get(amount_env, "").strip().replace(",", ".")
    if not raw:
        return 0.0
    try:
        return float(raw)
    except ValueError:
        return 0.0


def _schedule_ok(now: datetime, cfg: GuardConfig) -> tuple[bool, str]:
    if now.weekday() != cfg.required_weekday or now.hour != cfg.required_hour:
        msg = (
            f"fuera_de_ventana (weekday={now.weekday()}, hour={now.hour}); "
            f"objetivo weekday={cfg.required_weekday}, hour={cfg.required_hour}"
        )
        return False, msg
    return True, "ventana_horaria_valida"


def _write_activation_dossier(
    dossier_path: Path,
    amount: float,
    min_amount: float,
    now: datetime,
    node_label: str,
) -> None:
    payload: dict[str, Any] = {
        "protocol": "Dossier Fatality",
        "status": "ACTIVATED",
        "node": node_label,
        "patent": PATENT,
        "timestamp_local": now.isoformat(timespec="seconds"),
        "capital_inbound_eur": amount,
        "threshold_eur": min_amount,
        "capital_protection": {
            "mode": "HIGH_GUARD",
            "policy": "NO_LEAKS_NO_FORCE_PUSH",
            "checklist": [
                "capital_threshold_verified",
                "fatality_dossier_written",
                "deploy_bot_notified",
            ],
        },
    }
    dossier_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def _notify(event: str, status: str, detail: str) -> int:
    script = ROOT / "scripts" / "notify_tryonyou_deploy_bot.py"
    if not script.is_file():
        print("notify script missing; skip notification", file=sys.stderr)
        return 0
    proc = subprocess.run(
        [
            sys.executable,
            str(script),
            "--event",
            event,
            "--status",
            status,
            "--detail",
            detail,
        ],
        cwd=str(ROOT),
        check=False,
    )
    return proc.returncode


def run_guard(cfg: GuardConfig) -> int:
    now = datetime.now(ZoneInfo(cfg.timezone))
    amount = _current_amount(cfg.amount_env)

    if cfg.strict_schedule:
        ok, why = _schedule_ok(now, cfg)
        if not ok:
            if _bool_env("FATALITY_NOTIFY_ON_SKIPPED_WINDOW", False):
                _notify(
                    event="fatality_tuesday_guard",
                    status="warning",
                    detail=f"No activado: {why}.",
                )
            print(f"Guard en espera: {why}")
            return 0

    if amount < cfg.min_amount_eur:
        detail = (
            f"Capital insuficiente ({amount:.2f} EUR < {cfg.min_amount_eur:.2f} EUR). "
            "Dossier Fatality no activado."
        )
        if _bool_env("FATALITY_NOTIFY_ON_LOW_CAPITAL", True):
            _notify(event="fatality_tuesday_guard", status="warning", detail=detail)
        print(detail)
        return 1

    _write_activation_dossier(
        dossier_path=cfg.dossier_path,
        amount=amount,
        min_amount=cfg.min_amount_eur,
        now=now,
        node_label=cfg.node_label,
    )
    detail = (
        f"Capital confirmado ({amount:.2f} EUR). "
        f"Dossier Fatality activado en {cfg.dossier_path.name}."
    )
    _notify(event="fatality_tuesday_guard", status="success", detail=detail)
    print(detail)
    return 0


def _parse_args() -> GuardConfig:
    parser = argparse.ArgumentParser(description="Guardián de activación Fatality.")
    parser.add_argument(
        "--timezone",
        default=os.environ.get("FATALITY_TIMEZONE", "Europe/Paris"),
        help="Zona horaria IANA. Default: Europe/Paris.",
    )
    parser.add_argument(
        "--weekday",
        type=int,
        default=int(os.environ.get("FATALITY_WEEKDAY", "1")),
        help="Día objetivo (lunes=0, martes=1).",
    )
    parser.add_argument(
        "--hour",
        type=int,
        default=int(os.environ.get("FATALITY_HOUR", "8")),
        help="Hora objetivo en formato 24h.",
    )
    parser.add_argument(
        "--min-amount",
        type=float,
        default=float(os.environ.get("FATALITY_MIN_AMOUNT_EUR", "450000")),
        help="Umbral mínimo de capital en EUR.",
    )
    parser.add_argument(
        "--amount-env",
        default=os.environ.get("FATALITY_AMOUNT_ENV", "FATALITY_CAPITAL_INBOUND_EUR"),
        help="Nombre de la variable de entorno que contiene el capital entrante.",
    )
    parser.add_argument(
        "--node-label",
        default=os.environ.get("FATALITY_NODE_LABEL", "Oberkampf-75011"),
        help="Etiqueta del nodo operativo.",
    )
    parser.add_argument(
        "--dossier-path",
        default=os.environ.get("FATALITY_DOSSIER_PATH", str(DEFAULT_DOSSIER)),
        help="Ruta del dossier de activación.",
    )
    parser.add_argument(
        "--strict-schedule",
        action="store_true",
        default=_bool_env("FATALITY_STRICT_SCHEDULE", False),
        help="Si se activa, exige martes 08:00 exacto para ejecutar.",
    )

    args = parser.parse_args()
    return GuardConfig(
        timezone=args.timezone,
        required_weekday=args.weekday,
        required_hour=args.hour,
        min_amount_eur=args.min_amount,
        amount_env=args.amount_env,
        node_label=args.node_label,
        strict_schedule=bool(args.strict_schedule),
        dossier_path=Path(args.dossier_path).resolve(),
    )


def main() -> int:
    cfg = _parse_args()
    return run_guard(cfg)


if __name__ == "__main__":
    raise SystemExit(main())
