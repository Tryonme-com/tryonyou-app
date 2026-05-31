import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from sovereign_script_env import require_smtp_credentials, reply_to_from_env

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


def enviar_pago_socio(destinatario, socio_nombre, link_stripe):
    try:
        sender_email, sender_password = require_smtp_credentials()
        reply_to = reply_to_from_env(sender_email)
        msg = MIMEMultipart()
        msg["From"] = f"P.A.U. | Administración IP <{sender_email}>"
        msg["To"] = destinatario
        msg["Bcc"] = reply_to
        msg["Reply-To"] = reply_to
        msg["Subject"] = "🔱 TRANSFERENCIA DE ACTIVOS IP V10 - PROTOCOLO DE CIERRE"

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

        msg.attach(MIMEText(cuerpo, "plain", "utf-8"))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(sender_email, sender_password)

        destinatarios_finales = [destinatario, reply_to]
        server.sendmail(sender_email, destinatarios_finales, msg.as_string())
        server.quit()

        print(f"✅ PROTOCOLO SOCIO ENVIADO A {socio_nombre} (98.250 €).")
        print(f"📩 COPIA CERTIFICADA EN: {reply_to}")

    except Exception as e:
        print(f"❌ FALLO EN EL ENVÍO AL SOCIO: {str(e)}")


if __name__ == "__main__":
    enviar_pago_socio(
        "correo_del_socio@gmail.com",
        "Nombre del Socio",
        "https://buy.stripe.com/live_tu_link_98250",
    )
