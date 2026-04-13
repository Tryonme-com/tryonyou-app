import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# --- CREDENCIALES ---
USER = "tu_correo@gmail.com"  # <--- TU GMAIL
PASS = "tu_clave_app"         # <--- TU CLAVE DE 16 DÍGITOS
DEST = "Contact@aubenard.fr"
# Escribe aquí el nombre exacto de tu PDF (ejemplo: patente.pdf)
ARCHIVO = "Patente_PCT_EP2025_067317.pdf" 

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

