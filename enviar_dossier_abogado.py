import os
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
except ImportError:
    pass

USER = os.environ.get("EMAIL_USER", "rubensanzburo@gmail.com").strip()
PASS = os.environ.get("EMAIL_PASS", "").strip().replace(" ", "")
DEST = (
    (sys.argv[1] if len(sys.argv) > 1 else "").strip()
    or os.environ.get("DOSSIER_ABOGADO_TO", "Contact@aubenard.fr").strip()
)

if not PASS:
    print("ERROR: Define EMAIL_PASS en .env (16 caracteres).", file=sys.stderr)
    sys.exit(2)

msg = MIMEMultipart()
msg["From"] = USER
msg["To"] = DEST
msg["Bcc"] = USER
msg["Subject"] = "Dossier Tecnico-Legal: Sistema Biometrico P.A.U. V9 - TryOnYou"

cuerpo = """
Estimado, adjunto documentacion tecnica del sistema tryonyou-app (V9).

1. Activos IP: Patente Prioridad V9 (Logica Chasquido). Protocolo Anticopy biometria unica.
2. Infracciones: Analisis 20 actores (Falsi-Tryon).
3. Material: https://g.co/gemini/share/48ebddf109dc

Ruben Espinar - Fundador tryonyou-app
"""
msg.attach(MIMEText(cuerpo.strip(), "plain", "utf-8"))

try:
    print("Conectando con Gmail...")
    server = smtplib.SMTP("smtp.gmail.com", 587, timeout=30)
    server.starttls()
    server.login(USER, PASS)
    server.send_message(msg)
    server.quit()
    print("CONFIRMADO: ENVIADO Y COPIADO EN TU GMAIL")
except Exception as e:
    print(f"ERROR: {e}")

