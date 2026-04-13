"""
Planificador diario — estado operacional del Día 10.

  python3 daily_planner.py

Patente: PCT/EP2025/067317 | SIREN ref.: 943 610 196
"""

from __future__ import annotations

import datetime
import os
import subprocess
from pathlib import Path
from typing import Sequence

import requests

OBJETIVO_BANCO: float = 27500.00
OBJETIVO_CAPITAL_EUR: float = 450000.00
SIREN_REF = "943 610 196"
DEPLOY_BOT_NAME = "@tryonyou_deploy_bot"
HORA_DOSSIER_FATALITY = 8


def _ahora(ahora: datetime.datetime | None = None) -> datetime.datetime:
    if ahora is not None:
        return ahora
    return datetime.datetime.now()


def _formato_eur(valor: float) -> str:
    """
    Formatea en estilo europeo: 450.000,00 €.
    """
    base = f"{valor:,.2f}"
    return base.replace(",", "_").replace(".", ",").replace("_", ".") + " €"


def status_dia_10(ahora: datetime.datetime | None = None) -> str:
    """Devuelve el estado operacional del Día 10 según la hora actual."""
    current = _ahora(ahora)

    print(f"--- [ESTADO DE OPERACIÓN: {current.strftime('%H:%M:%S')}] ---")
    print(f"ESTATUS SIREN: {SIREN_REF} (Verificado)")
    print(f"ESTATUS JEI: Activo (Bpifrance Dossier Enviado)")

    if current.weekday() == 1 and current.hour >= HORA_DOSSIER_FATALITY:
        return (
            "SEGURIDAD: Martes 08:00+ confirmado. Verifica entrada de "
            f"{_formato_eur(OBJETIVO_CAPITAL_EUR)} y activa Dossier Fatality."
        )
    if current.weekday() == 1 and current.hour < HORA_DOSSIER_FATALITY:
        return (
            "ALERTA: Martes pre-08:00. Preparar confirmación de capital "
            f"({_formato_eur(OBJETIVO_CAPITAL_EUR)}) y activar Dossier Fatality en punto."
        )
    if current.hour < 9:
        return (
            f"ALERTA: Faltan horas para la apertura bancaria. "
            f"Objetivo: {OBJETIVO_BANCO} €."
        )
    return (
        "ACCIÓN: Comprueba tu banca online ahora. "
        "El clearing debería haber finalizado."
    )


def enviar_notificacion_exito(
    mensaje: str,
    token: str | None = None,
    chat_id: str | None = None,
    timeout: int = 20,
) -> bool:
    """
    Notifica éxitos operativos vía Telegram.

    Importante: el token se toma de entorno para no hardcodear secretos.
    """
    bot_token = (
        token
        or os.getenv("TRYONYOU_DEPLOY_BOT_TOKEN", "")
        or os.getenv("TELEGRAM_BOT_TOKEN", "")
        or os.getenv("TELEGRAM_TOKEN", "")
    ).strip()
    chat = (
        chat_id
        or os.getenv("TRYONYOU_DEPLOY_CHAT_ID", "")
        or os.getenv("TELEGRAM_CHAT_ID", "")
    ).strip()

    if not bot_token:
        return False
    if not chat:
        return False

    payload = {"chat_id": chat, "text": f"{DEPLOY_BOT_NAME} {mensaje}"}
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    try:
        response = requests.post(url, json=payload, timeout=timeout)
    except requests.RequestException:
        return False
    return response.status_code == 200


def ejecutar_supercommit_max(extra_args: Sequence[str] | None = None) -> int:
    """
    Ejecuta Supercommit_Max para sincronizar búnker y galería web.
    """
    script = Path(__file__).resolve().parent / "supercommit_max.sh"
    args = list(extra_args or [])
    syntax = subprocess.run(["bash", "-n", str(script)], check=False)
    if syntax.returncode != 0:
        return syntax.returncode
    proc = subprocess.run(["bash", str(script), *args], check=False)
    return proc.returncode


if __name__ == "__main__":
    print(status_dia_10())
