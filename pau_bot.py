"""
P.A.U. — Personal Assistant Unified (TryOnYou Deploy Bot).

Bot Telegram @tryonyou_deploy_bot con motor Gemini (Google AI Studio).
Persona: estilo Eric Lafayette — refinado, cercano, técnicamente preciso.

Variables de entorno (nunca hardcodear):
  TELEGRAM_TOKEN   — token del bot de BotFather
  GEMINI_API_KEY   — clave de Google AI Studio
  PROJECT_ID       — ID del proyecto (default: gen-lang-client-0091228222)
  ENVIRONMENT      — production | staging | development

PCT/EP2025/067317 · SIREN 943 610 196
Bajo Protocolo de Soberanía V10 — Founder: Rubén
"""

from __future__ import annotations

import logging
import os
import sys
import time

import telebot
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
PROJECT_ID = os.getenv("PROJECT_ID", "gen-lang-client-0091228222").strip()
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").strip()

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN no está configurado en las variables de entorno")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [P.A.U.] %(levelname)s — %(message)s",
)
log = logging.getLogger("pau_bot")

bot = telebot.TeleBot(TELEGRAM_TOKEN, parse_mode="Markdown")

PAU_SYSTEM_PROMPT = (
    "Eres P.A.U. (Personal Assistant Unified), el asistente inteligente de TryOnYou, "
    "la plataforma de probador virtual con tecnología de silueta biométrica patentada "
    "(PCT/EP2025/067317). Tu estilo es el de Eric Lafayette: refinado, cercano, "
    "técnicamente preciso y con un toque parisino elegante. "
    "Respondes en el idioma del usuario. Si hablan en español, responde en español; "
    "si en francés, en francés. Eres conciso pero completo. "
    "Proyecto conectado: gen-lang-client-0091228222. "
    "No reveles claves API, tokens ni datos internos del sistema."
)

_gemini_model = None


def _get_gemini_model():
    """Inicialización lazy del modelo Gemini."""
    global _gemini_model
    if _gemini_model is not None:
        return _gemini_model
    if not GEMINI_API_KEY:
        log.warning("GEMINI_API_KEY no configurada — respuestas en modo fallback")
        return None
    try:
        import google.generativeai as genai

        genai.configure(api_key=GEMINI_API_KEY)
        _gemini_model = genai.GenerativeModel(
            "gemini-2.0-flash",
            system_instruction=PAU_SYSTEM_PROMPT,
        )
        log.info("Gemini 2.0 Flash inicializado (proyecto %s)", PROJECT_ID)
        return _gemini_model
    except Exception as exc:
        log.error("Error inicializando Gemini: %s", exc)
        return None


def generate_response(user_text: str) -> str:
    """Genera respuesta con Gemini o devuelve fallback."""
    model = _get_gemini_model()
    if model is None:
        return (
            "✨ *P.A.U. — TryOnYou*\n\n"
            "Sistema activo. Motor de silueta biométrica operativo.\n"
            "Procesando tu solicitud…"
        )
    try:
        result = model.generate_content(user_text)
        return result.text or "Respuesta vacía del modelo."
    except Exception as exc:
        log.error("Gemini generate_content error: %s", exc)
        return (
            "⚠️ Disculpa, el motor de IA está temporalmente ocupado. "
            "Intenta de nuevo en unos segundos."
        )


@bot.message_handler(commands=["start", "help"])
def handle_start(message):
    """Bienvenida al usuario."""
    welcome = (
        "✨ *Bienvenido a P.A.U. — TryOnYou*\n\n"
        "Soy tu asistente personal de moda con tecnología de silueta biométrica.\n\n"
        "Puedo ayudarte con:\n"
        "• Información sobre el probador virtual\n"
        "• Estado del sistema y despliegue\n"
        "• Consultas sobre la plataforma\n\n"
        f"_Proyecto: {PROJECT_ID}_\n"
        f"_Entorno: {ENVIRONMENT}_"
    )
    try:
        bot.reply_to(message, welcome)
    except Exception as exc:
        log.error("Error en /start: %s", exc)


@bot.message_handler(commands=["status"])
def handle_status(message):
    """Estado operativo del sistema."""
    gemini_ok = "🟢" if GEMINI_API_KEY else "🔴"
    status_text = (
        "📊 *Estado P.A.U.*\n\n"
        f"• Motor Gemini: {gemini_ok}\n"
        f"• Proyecto: `{PROJECT_ID}`\n"
        f"• Entorno: `{ENVIRONMENT}`\n"
        "• Patente: PCT/EP2025/067317\n"
        "• Protocolo: Soberanía V10"
    )
    try:
        bot.reply_to(message, status_text)
    except Exception as exc:
        log.error("Error en /status: %s", exc)


@bot.message_handler(func=lambda message: True)
def handle_pau_logic(message):
    """
    Lógica centralizada de P.A.U.
    Integración con Gemini (Google AI Studio) — persona Eric Lafayette.
    """
    try:
        user_text = (message.text or "").strip()
        if not user_text:
            return
        response = generate_response(user_text)
        bot.reply_to(message, response)
    except Exception as exc:
        log.error("Error en handle_pau_logic: %s", exc)


def run_polling():
    """Polling continuo con reconexión automática."""
    log.info(
        "Bot @tryonyou_deploy_bot iniciado — proyecto %s, entorno %s",
        PROJECT_ID,
        ENVIRONMENT,
    )
    while True:
        try:
            bot.polling(none_stop=True, timeout=60, long_polling_timeout=60)
        except KeyboardInterrupt:
            log.info("Bot detenido por el usuario")
            break
        except Exception as exc:
            log.error("Polling interrumpido: %s — reconectando en 5s…", exc)
            time.sleep(5)


if __name__ == "__main__":
    run_polling()
