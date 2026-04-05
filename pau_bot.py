import os
import telebot
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Cargar configuración segura (.env)
load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
PROJECT_ID = "gen-lang-client-0091228222"

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN no está configurado en las variables de entorno")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY no está configurado en las variables de entorno")

# 2. Configurar motor de IA (Jules / P.A.U.)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Inicializar Bot
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# 3. Lógica del Agente (Identidad Eric Lafayette)
SYSTEM_PROMPT = """
Actúa como P.A.U., un asesor de imagen refinado y cercano, inspirado en Eric Lafayette.
Tu tono es profesional, elegante y directo. No inventes datos. 
Si el usuario pregunta por el espejo digital, explica las funciones: 
'Mi Selección Perfecta', 'Reservar en Probador' y 'Guardar Silueta'.
"""

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = "Bienvenido a la experiencia TryOnYou. Soy P.A.U., su asistente personal. ¿Desea iniciar el escaneo de silueta?"
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def handle_agent_response(message):
    try:
        # Consultar al motor de IA con la identidad de P.A.U.
        chat = model.start_chat(history=[])
        response = chat.send_message(f"{SYSTEM_PROMPT}\nUsuario dice: {message.text}")

        # Enviar respuesta refinada al usuario
        bot.reply_to(message, response.text)

        # Notificación interna (puedes conectar esto a Slack)
        print(f"Log: Mensaje procesado para {message.from_user.first_name}")

    except Exception as e:
        bot.reply_to(message, "Disculpe las molestias, estoy ajustando los detalles de su probador. Inténtelo en un momento.")
        print(f"Error Técnico: {e}")

if __name__ == "__main__":
    print(f"🚀 Agente P.A.U. activo en @tryonyou_deploy_bot")
    bot.polling(none_stop=True)
