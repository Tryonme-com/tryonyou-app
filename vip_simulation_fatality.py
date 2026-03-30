import requests
import json
import os
from datetime import datetime

from telegram_env import get_telegram_bot_token, get_telegram_chat_id


class FatalitySimulator:
    def __init__(self):
        self.bot_token = get_telegram_bot_token()
        self.chat_id = get_telegram_chat_id()
        if not self.bot_token or not self.chat_id:
            raise RuntimeError(
                "Define TELEGRAM_BOT_TOKEN (o TELEGRAM_TOKEN) y TELEGRAM_CHAT_ID en el entorno."
            )
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

    def execute_mock_sale(self):
        print("--- 🎭 INICIANDO SIMULACRO: GALERIES LAFAYETTE VIP ---")
        
        # Datos del éxito comercial
        event_data = {
            "event": "RESERVA_CONFIRMADA",
            "brand": "SAC MUSEUM",
            "item": "PIÈCE D'ARCHIVE 1954",
            "fit_score": "99.8%",
            "efecto_paloma": "ACTIVADO",
            "location": "Galeries Lafayette Haussmann, Paris",
            "revenue_potential": "12.500 €",
            "patent": "PCT/EP2025/067317"
        }

        # 1. Notificar al Fundador vía Telegram
        message = (
            "🔥 *ALERTA FATALITY - RESERVA VIP*\n\n"
            f"📍 *Lugar:* {event_data['location']}\n"
            f"🏷️ *Marca:* {event_data['brand']}\n"
            f"👗 *Prenda:* {event_data['item']}\n"
            f"📏 *Fit Score:* `{event_data['fit_score']}`\n"
            f"✨ *Efecto Paloma:* {event_data['efecto_paloma']}\n"
            f"💰 *Valor:* {event_data['revenue_potential']}\n\n"
            "👑 _Soberanía confirmada para Rubén Espinar._"
        )
        
        try:
            r = requests.post(
                self.api_url,
                json={"chat_id": self.chat_id, "text": message, "parse_mode": "Markdown"},
                timeout=30,
            )
            r.raise_for_status()
            print("✅ Señal VIP enviada (Telegram HTTP OK).")
        except Exception as e:
            print(f"❌ Error en la comunicación con el Bot: {e}")

        # 2. Registrar en la base de datos de métricas
        log_file = "pilot_analytics.json"
        logs = []
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = json.load(f)
        
        event_data["timestamp"] = datetime.now().isoformat()
        logs.append(event_data)
        
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=4)
        print("📊 Métrica registrada en pilot_analytics.json.")

if __name__ == "__main__":
    sim = FatalitySimulator()
    sim.execute_mock_sale()
