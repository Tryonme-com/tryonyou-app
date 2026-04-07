import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CONFIGURACIÓN SOBERANÍA ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "admin@tryonyou.app"
SENDER_PASSWORD = "zxjn nbai xifd ifbj" 
REPLY_TO_EMAIL = "rubensanzburo@gmail.com"

def enviar_pago_socio(destinatario, socio_nombre, link_stripe):
    try:
        msg = MIMEMultipart()
        msg['From'] = f"P.A.U. | Administración IP <{SENDER_EMAIL}>"
        msg['To'] = destinatario
        msg['Bcc'] = REPLY_TO_EMAIL
        msg['Reply-To'] = REPLY_TO_EMAIL
        msg['Subject'] = f"🔱 TRANSFERENCIA DE ACTIVOS IP V10 - PROTOCOLO DE CIERRE"

        cuerpo = f"""
        Hola {socio_nombre},

        Tal y como acordamos en la estructura de capital de la tecnología "Soberanía V10", procedemos a formalizar la transferencia de activos y la licencia de explotación.

        Esta inyección de 98.250,00 € certifica tu posición dentro del ecosistema P.A.U. y asegura el despliegue de las infraestructuras que tenemos previstas para este 2026.

        Puedes finalizar la transacción a través de este enlace seguro de Stripe:

        🔗 ENLACE DE TRANSFERENCIA IP: {link_stripe}

        En cuanto se confirme el pago, liberamos el dossier técnico de propiedad intelectual y quedará sincronizado con tu cartera de activos.

        Seguimos adelante con el plan.

        Atentamente,

        El Arquitecto.
        TryOnYou-App | Sovereign Intelligence
        """
        
        msg.attach(MIMEText(cuerpo, 'plain', 'utf-8'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        
        destinatarios_finales = [destinatario, REPLY_TO_EMAIL]
        server.sendmail(SENDER_EMAIL, destinatarios_finales, msg.as_string())
        server.quit()

        print(f"✅ PROTOCOLO SOCIO ENVIADO A {socio_nombre} (98.250 €).")
        print(f"📩 COPIA CERTIFICADA EN: {REPLY_TO_EMAIL}")
        
    except Exception as e:
        print(f"❌ FALLO EN EL ENVÍO AL SOCIO: {str(e)}")

if __name__ == "__main__":
    # DISPARO PARA EL SOCIO (Pon aquí su correo y el link de 98k)
    enviar_pago_socio(
        "correo_del_socio@gmail.com", 
        "Nombre del Socio", 
        "https://buy.stripe.com/live_tu_link_98250"
    )
