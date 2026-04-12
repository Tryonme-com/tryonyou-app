"""
Guardia soberana: martes 08:00 (Paris) confirma 450000 EUR y activa Dossier Fatality.

Uso recomendado (cron):
  0 8 * * 2 cd /workspace && /usr/bin/env \
    TRYONYOU_DEPLOY_BOT_TOKEN=... TRYONYOU_DEPLOY_CHAT_ID=... \
    TRYONYOU_CONFIRMED_CAPITAL_EUR=450000 \
    python3 martes_0800_dossier_fatality.py

Flags:
  --force                 Ejecuta fuera de la ventana martes 08:00.
  --confirmed-eur <num>   Monto confirmado (si no, usa entorno).
  --tz Europe/Paris       Zona horaria para la ventana.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import requests

ROOT = Path(__file__).resolve().parent
DOSSIER_PATH = ROOT / "dossier_fatality.json"
STATUS_PATH = ROOT / "logs" / "dossier_fatality_activation.json"

BOT_HANDLE = "@tryonyou_deploy_bot"
PATENT = "PCT/EP2025/067317"
REQUIRED_WEEKDAY = 1  # Tuesday
REQUIRED_HOUR = 8
REQUIRED_AMOUNT_EUR = Decimal("450000")


@dataclass
class DeployNotifier:
    token: str
    chat_id: str

    @classmethod
    def from_env(cls) -> "DeployNotifier":
        token = (
            os.environ.get("TRYONYOU_DEPLOY_BOT_TOKEN", "").strip()
            or os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
            or os.environ.get("TELEGRAM_TOKEN", "").strip()
        )
        chat_id = (
            os.environ.get("TRYONYOU_DEPLOY_CHAT_ID", "").strip()
            or os.environ.get("TELEGRAM_CHAT_ID", "").strip()
        )
        return cls(token=token, chat_id=chat_id)

    @property
    def enabled(self) -> bool:
        return bool(self.token and self.chat_id)

    def send(self, text: str) -> bool:
        if not self.enabled:
            return False
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {"chat_id": self.chat_id, "text": text}
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
        except requests.RequestException as exc:
            print(f"⚠ Telegram no disponible: {exc}", file=sys.stderr)
            return False
        return True


def parse_decimal(raw: str) -> Decimal:
    cleaned = raw.strip().replace(" ", "").replace("_", "").replace(",", "")
    if not cleaned:
        raise InvalidOperation("empty")
    return Decimal(cleaned)


def confirmed_capital_from_env() -> Decimal | None:
    for var in (
        "TRYONYOU_CONFIRMED_CAPITAL_EUR",
        "CONFIRMED_CAPITAL_EUR",
        "TRYONYOU_ENTRY_CONFIRMED_EUR",
    ):
        value = os.environ.get(var, "").strip()
        if not value:
            continue
        try:
            return parse_decimal(value)
        except InvalidOperation:
            print(f"⚠ Valor invalido en {var}: {value!r}", file=sys.stderr)
            return None
    return None


def vip_flow_rate_from_env() -> Decimal | None:
    value = os.environ.get("VIP_FLOW_RATE", "").strip()
    if not value:
        return None
    try:
        return parse_decimal(value)
    except InvalidOperation:
        return None


def in_required_window(now_local: datetime) -> bool:
    return now_local.weekday() == REQUIRED_WEEKDAY and now_local.hour == REQUIRED_HOUR


def load_dossier(path: Path = DOSSIER_PATH) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"No existe {path}")
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("dossier_fatality.json debe ser un objeto JSON")
    return data


def build_activation_record(
    *,
    now_local: datetime,
    confirmed_eur: Decimal,
    dossier: dict[str, Any],
    vip_flow_rate: Decimal | None,
) -> dict[str, Any]:
    vip_alert = vip_flow_rate is not None and vip_flow_rate < Decimal("99")
    return {
        "status": "DOSSIER_FATALITY_ACTIVATED",
        "activation_window": "Tuesday 08:00",
        "timezone": str(now_local.tzinfo),
        "capital_confirmed_eur": f"{confirmed_eur:.2f}",
        "required_minimum_eur": f"{REQUIRED_AMOUNT_EUR:.2f}",
        "activated_local": now_local.isoformat(timespec="seconds"),
        "activated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "bot_handle": BOT_HANDLE,
        "patent": PATENT,
        "dossier_strategy": dossier.get("estrategia", "DOSSIER FATALITY V10"),
        "sello_legal": dossier.get("sello_legal", ""),
        "efecto_paloma": {
            "vip_flow_rate": str(vip_flow_rate) if vip_flow_rate is not None else "unknown",
            "vip_flow_alert": vip_alert,
        },
    }


def notify_success(notifier: DeployNotifier, stage: str, details: str) -> None:
    if not notifier.enabled:
        print(
            "⚠ Notificador no configurado (TRYONYOU_DEPLOY_BOT_TOKEN/TRYONYOU_DEPLOY_CHAT_ID).",
            file=sys.stderr,
        )
        return
    message = (
        "✅ TRYONYOU CAPITAL SECURITY\n"
        f"Bot: {BOT_HANDLE}\n"
        f"Etapa: {stage}\n"
        f"Detalle: {details}\n"
        f"Patente: {PATENT}"
    )
    if not notifier.send(message):
        print(f"⚠ No se pudo notificar la etapa {stage}.", file=sys.stderr)


def activate_dossier_fatality(
    *,
    force: bool,
    tz_name: str,
    confirmed_eur: Decimal | None,
    notifier: DeployNotifier | None = None,
    now_local: datetime | None = None,
    dossier_path: Path = DOSSIER_PATH,
    status_path: Path = STATUS_PATH,
) -> int:
    notifier = notifier or DeployNotifier.from_env()

    try:
        zone = ZoneInfo(tz_name)
    except ZoneInfoNotFoundError:
        print(f"❌ Zona horaria invalida: {tz_name}", file=sys.stderr)
        return 2

    now_local = now_local or datetime.now(zone)
    if not force and not in_required_window(now_local):
        print(
            f"⏱ Ventana cerrada: {now_local.isoformat(timespec='seconds')} "
            "(se requiere martes 08:00)."
        )
        return 2

    if confirmed_eur is None:
        confirmed_eur = confirmed_capital_from_env()
    if confirmed_eur is None:
        print("❌ No hay monto confirmado en entorno ni en --confirmed-eur.", file=sys.stderr)
        return 3
    if confirmed_eur < REQUIRED_AMOUNT_EUR:
        print(
            f"❌ Capital insuficiente: {confirmed_eur:.2f} < {REQUIRED_AMOUNT_EUR:.2f}",
            file=sys.stderr,
        )
        return 3

    notify_success(
        notifier,
        "CapitalConfirmation",
        f"entrada confirmada de {confirmed_eur:.2f} EUR",
    )

    try:
        dossier = load_dossier(dossier_path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"❌ Error leyendo dossier: {exc}", file=sys.stderr)
        return 4

    record = build_activation_record(
        now_local=now_local,
        confirmed_eur=confirmed_eur,
        dossier=dossier,
        vip_flow_rate=vip_flow_rate_from_env(),
    )

    status_path.parent.mkdir(parents=True, exist_ok=True)
    with status_path.open("w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    notify_success(
        notifier,
        "DossierFatality",
        f"Dossier activado ({status_path.name})",
    )
    print(f"✅ Dossier Fatality activado y registrado en {status_path}.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Confirma 450000 EUR y activa Dossier Fatality martes 08:00."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Permite ejecutar fuera de la ventana martes 08:00.",
    )
    parser.add_argument(
        "--confirmed-eur",
        default="",
        help="Monto confirmado en EUR (si se omite, usa entorno).",
    )
    parser.add_argument(
        "--tz",
        default=os.environ.get("TRYONYOU_SECURITY_TZ", "Europe/Paris"),
        help="Zona horaria de control.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    confirmed_eur: Decimal | None = None
    if args.confirmed_eur:
        try:
            confirmed_eur = parse_decimal(args.confirmed_eur)
        except InvalidOperation:
            print("❌ --confirmed-eur invalido.", file=sys.stderr)
            return 3
    return activate_dossier_fatality(
        force=args.force,
        tz_name=args.tz,
        confirmed_eur=confirmed_eur,
    )


if __name__ == "__main__":
    raise SystemExit(main())
