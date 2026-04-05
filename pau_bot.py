import os
import telebot
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Configuración de Entorno
load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
PROJECT_ID = "gen-lang-client-0091228222"

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN no está configurado en las variables de entorno")

# 2. Configuración del Agente P.A.U.
genai.configure(api_key=GEMINI_API_KEY)
# Configuración del modelo con las directrices de comportamiento
generation_config = {
    "temperature": 0.7,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

model = genai.GenerativeModel(
    model_name="gemini-pro",
    generation_config=generation_config
)

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Directrices de identidad (Eric Lafayette)
SYSTEM_INSTRUCTIONS = (
    "Eres P.A.U., un asesor de imagen refinado, cercano y profesional. "
    "Tu tono está inspirado en Eric Lafayette: elegante pero no rígido. "
    "No inventes datos, precios o valoraciones. "
    "Si el usuario pregunta por el piloto, conoce perfectamente las funciones: "
    "Mi Selección Perfecta, Reservar en Probador, Ver Combinaciones, "
    "Guardar mi Silueta y Compartir Look. "
    "Responde siempre con sinceridad y basándote en datos reales."
)

@bot.message_handler(commands=['start'])
def welcome(message):
    response = "Bienvenido a TryOnYou. Soy P.A.U., su asistente personal de imagen. ¿En qué puedo asistirle hoy con su silueta?"
    bot.reply_to(message, response)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        # El agente procesa la respuesta usando el motor de IA
        prompt = f"{SYSTEM_INSTRUCTIONS}\nUsuario: {message.text}\nP.A.U.:"
        response = model.generate_content(prompt)

        bot.reply_to(message, response.text)
    except Exception as e:
        print(f"Error en el agente: {e}")
        bot.reply_to(message, "Lo lamento, estoy experimentando una breve interrupción en la conexión del probador.")

if __name__ == "__main__":
    print(f"Agente P.A.U. desplegado en @tryonyou_deploy_bot")
    bot.polling(none_stop=True)
