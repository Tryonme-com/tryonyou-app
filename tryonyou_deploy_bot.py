"""TryOnYou Deploy Bot — @tryonyou_deploy_bot.

Credenciales sólo por entorno (nunca en código):
  export TELEGRAM_BOT_TOKEN='<token de BotFather>'   # o TELEGRAM_TOKEN
  python3 tryonyou_deploy_bot.py

Patente: PCT/EP2025/067317
"""

from __future__ import annotations

import os
import sys

try:
    import telebot  # pyTelegramBotAPI
except ImportError:  # pragma: no cover
    print("Instala pyTelegramBotAPI: pip install pyTelegramBotAPI", file=sys.stderr)
    sys.exit(1)

WELCOME_MESSAGE = "Sistema Abvet / TryOnYou Activo. Esperando comandos de despliegue."


def _get_token() -> str:
    token = (
        os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
        or os.environ.get("TELEGRAM_TOKEN", "").strip()
    )
    if not token:
        raise RuntimeError(
            "Define TELEGRAM_BOT_TOKEN (o TELEGRAM_TOKEN) en el entorno antes de ejecutar."
        )
    return token


def initialize_tryonyou_bot(token: str) -> None:
    """Inicializa y arranca el bot de despliegue @tryonyou_deploy_bot."""
    try:
        bot = telebot.TeleBot(token)

        @bot.message_handler(commands=["start", "help"])
        def send_welcome(message: telebot.types.Message) -> None:  # type: ignore[name-defined]
            bot.reply_to(message, WELCOME_MESSAGE)

        print("Conexión establecida con @tryonyou_deploy_bot")
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Error de conexión: {e}", file=sys.stderr)
        raise


if __name__ == "__main__":
    initialize_tryonyou_bot(_get_token())
