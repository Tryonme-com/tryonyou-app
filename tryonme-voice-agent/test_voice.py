"""
Prueba el cerebro (Gemini + tools) sin teléfono ni Twilio.

  cd tryonme-voice-agent && python3 test_voice.py

Requiere .env con GEMINI_API_KEY o GOOGLE_API_KEY.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parent
load_dotenv(_ROOT / ".env")

from agent_70 import VoiceOrchestrator
import prompts
from tools import TryOnMeTools


def main() -> int:
    if not (
        os.environ.get("GEMINI_API_KEY", "").strip()
        or os.environ.get("GOOGLE_API_KEY", "").strip()
    ):
        print("Define GEMINI_API_KEY o GOOGLE_API_KEY en .env", file=sys.stderr)
        return 1

    orch = VoiceOrchestrator(
        name="Luna",
        brand="TryOnMe",
        llm=os.environ.get("GEMINI_MODEL", "gemini-1.5-flash"),
        tools=TryOnMeTools.get_all(),
        system_prompt=prompts.SYSTEM_PROMPT,
    )

    cases = [
        "Hola, quiero saber si hay chaquetas Balmain en stock para probarme.",
        "Mi pedido TY-8844, ¿dónde está el envío?",
    ]
    for q in cases:
        print("---")
        print("Transcripción simulada:", q)
        reply = orch.reply(q)
        print("Respuesta Luna:", reply)
        if len(reply) < 4:
            print("ERROR: respuesta demasiado corta", file=sys.stderr)
            return 2
    print("---")
    print("OK — test_voice pasó (red real a Gemini).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
