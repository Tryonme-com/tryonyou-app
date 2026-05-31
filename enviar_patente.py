import os
import smtplib
import sys
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

try:
    from dotenv import load_dotenv

    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
except ImportError:
    pass

# Credenciales solo desde entorno (nunca en código).
USER = os.environ.get("EMAIL_USER", "").strip()
PASS = os.environ.get("EMAIL_PASS", "").strip().replace(" ", "")
DEST = (
    (sys.argv[1] if len(sys.argv) > 1 else "").strip()
    or os.environ.get("PATENTE_EMAIL_TO", "Contact@aubenard.fr").strip()
)
ARCHIVO = os.environ.get("PATENTE_PDF_PATH", "Patente_PCT_EP2025_067317.pdf").strip()

msg = MIMEMultipart()
msg['From'] = USER
msg['To'] = DEST
msg['Subject'] = "CERTIFICADO DE SOBERANÍA: Patente Real Presentada - PCT/EP2025/067317"

cuerpo = "Estimado, adjunto la documentación oficial de la patente presentada para la liquidación de activos de TryOnYou-App."
msg.attach(MIMEText(cuerpo, 'plain'))

# --- ADJUNTAR PDF ---
if os.path.exists(ARCHIVO):
    with open(ARCHIVO, "rb") as f:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename={ARCHIVO}")
        msg.attach(part)
        print(f"📎 {ARCHIVO} cargado correctamente.")
else:
    print(f"❌ ERROR: No veo el archivo {ARCHIVO} en esta carpeta.")
    exit()

# --- ENVÍO ---
try:
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(USER, PASS)
    server.send_message(msg)
    server.quit()
    print("✅ PATENTE REAL ENVIADA Y CERTIFICADA.")
except Exception as e:
    print(f"❌ FALLO DE AUTENTICACIÓN: {e}")

