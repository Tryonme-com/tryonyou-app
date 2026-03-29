import requests
import json
import os

class TryOnYouSignals:
    def __init__(self):
        # Configuración del canal del Fundador
        self.bot_token = "TU_BOT_TOKEN_AQUI" # Inserta el token de BotFather
        self.chat_id = "TU_CHAT_ID_AQUI"     # Inserta tu Chat ID personal
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

    def send_sovereignty_signal(self, message):
        print(f"--- 📡 ENVIANDO SEÑAL DE SOBERANÍA ---")
        payload = {
            "chat_id": self.chat_id,
            "text": f"👑 MASTER OMEGA ALERT\n\n{message}\n\nPATENTE: PCT/EP2025/067317",
            "parse_mode": "Markdown"
        }
        try:
            requests.post(self.api_url, json=payload)
            print("✅ Señal entregada a RUBENSANZBUROBOT.")
        except Exception as e:
            print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    # Prueba de vida del sistema de señales
    signal = TryOnYouSignals()
    signal.send_sovereignty_signal("🚀 *SISTEMA ACTIVO:* El búnker digital está sincronizado con el Fundador Rubén.")
