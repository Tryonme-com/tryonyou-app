"""Señales Telegram TryOnYou — credenciales solo por entorno (nunca en código).

Entorno: TELEGRAM_BOT_TOKEN (o TELEGRAM_TOKEN), TELEGRAM_CHAT_ID.
Patente: PCT/EP2025/067317
"""

from __future__ import annotations

import os
import sys

import requests


class TryOnYouSignals:
    def __init__(self) -> None:
        self.bot_token = (
            os.environ.get("TELEGRAM_BOT_TOKEN", "") or os.environ.get("TELEGRAM_TOKEN", "")
        ).strip()
        self.chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
        if not self.bot_token or not self.chat_id:
            raise RuntimeError(
                "Define TELEGRAM_BOT_TOKEN (o TELEGRAM_TOKEN) y TELEGRAM_CHAT_ID en el entorno."
            )
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

    def send_sovereignty_signal(self, message: str) -> None:
        print("--- ENVIANDO SEÑAL DE SOBERANÍA (Telegram) ---")
        payload = {
            "chat_id": self.chat_id,
            "text": f"MASTER OMEGA ALERT\n\n{message}\n\nPATENTE: PCT/EP2025/067317",
            "parse_mode": "Markdown",
        }
        try:
            r = requests.post(self.api_url, json=payload, timeout=30)
            r.raise_for_status()
            print("Señal entregada (HTTP OK).")
        except Exception as e:
            print(f"Error de conexión o respuesta Telegram: {e}", file=sys.stderr)


if __name__ == "__main__":
    signal = TryOnYouSignals()
    signal.send_sovereignty_signal(
        "SISTEMA ACTIVO: búnker digital sincronizado (prueba de vida)."
    )
