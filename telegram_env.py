"""Resolución única del token y chat de Telegram (entorno; nunca en código).

Prioridad: TELEGRAM_BOT_TOKEN, luego TELEGRAM_TOKEN; ambos se normalizan con strip()
antes del fallback para que espacios en blanco no bloqueen el token alternativo.

Patente: PCT/EP2025/067317
"""

from __future__ import annotations

import os


def get_telegram_bot_token() -> str:
    return (
        os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
        or os.environ.get("TELEGRAM_TOKEN", "").strip()
    )


def get_telegram_chat_id() -> str:
    return os.environ.get("TELEGRAM_CHAT_ID", "").strip()
