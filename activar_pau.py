"""
Activar P.A.U. (Personal Assistant Unified) — punto de entrada unificado.

Modos disponibles (variable PAU_MODE):
  bot         — arranca el bot Telegram P.A.U. (requiere TELEGRAM_TOKEN)
  orquesta    — ejecuta el orquestador total (orquestador_pau_total.py)
  vigilancia  — inicia la vigilancia en bucle (vigilancia_pau.py)
  status      — muestra el estado del sistema y sale (default)

Variables de entorno:
  PAU_MODE         bot | orquesta | vigilancia | status  (default: status)
  TELEGRAM_TOKEN   token del bot de BotFather
  GEMINI_API_KEY   clave de Google AI Studio (opcional para modo bot)

Ejecutar:
  python3 activar_pau.py
  PAU_MODE=bot python3 activar_pau.py
  PAU_MODE=orquesta python3 activar_pau.py
  PAU_MODE=vigilancia python3 activar_pau.py

PCT/EP2025/067317 · SIREN 943 610 196
Bajo Protocolo de Soberanía V10 — Founder: Rubén
"""

from __future__ import annotations

import os
import sys

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

VALID_MODES = ("bot", "orquesta", "vigilancia", "status")


def _mostrar_estado() -> None:
    telegram_ok = "🟢" if os.getenv("TELEGRAM_TOKEN", "").strip() else "🔴"
    gemini_ok = "🟢" if os.getenv("GEMINI_API_KEY", "").strip() else "🔴"
    print(
        "\n🦚 P.A.U. — Personal Assistant Unified\n"
        "═══════════════════════════════════════\n"
        f"  Telegram Token : {telegram_ok}\n"
        f"  Gemini API Key : {gemini_ok}\n"
        "  Patente        : PCT/EP2025/067317\n"
        "  Protocolo      : Soberanía V10\n"
        "═══════════════════════════════════════\n"
        "Modos: PAU_MODE=bot | orquesta | vigilancia | status\n"
    )


def _iniciar_bot() -> None:
    token = os.getenv("TELEGRAM_TOKEN", "").strip()
    if not token:
        print("❌ TELEGRAM_TOKEN no está configurado. El bot no puede arrancar.")
        sys.exit(1)
    from pau_bot import run_polling

    print("🤖 Iniciando bot Telegram P.A.U. ...")
    run_polling()


def _iniciar_orquesta() -> None:
    from orquestador_pau_total import orquestar

    orquestar()


def _iniciar_vigilancia() -> None:
    from vigilancia_pau import vigilancia_silenciosa

    vigilancia_silenciosa()


def activar_pau() -> int:
    mode = os.getenv("PAU_MODE", "status").strip().lower()
    if mode not in VALID_MODES:
        print(f"⚠️  PAU_MODE={mode!r} no reconocido. Usa: {', '.join(VALID_MODES)}")
        return 1

    _mostrar_estado()

    handlers = {
        "status": lambda: None,
        "bot": _iniciar_bot,
        "orquesta": _iniciar_orquesta,
        "vigilancia": _iniciar_vigilancia,
    }
    handlers[mode]()
    return 0


if __name__ == "__main__":
    sys.exit(activar_pau())
