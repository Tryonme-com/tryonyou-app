import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from sovereign_script_env import require_smtp_credentials, reply_to_from_env


def enviar_cierre_ip(destinatario, nombre, link):
    try:
        sender_email, sender_password = require_smtp_credentials()
        reply_to = reply_to_from_env(sender_email)
        msg = MIMEMultipart()
        msg["From"] = f"P.A.U. | Sovereign Capital <{sender_email}>"
        msg["To"] = destinatario
        msg["Bcc"] = reply_to
        msg["Reply-To"] = reply_to
        msg["Subject"] = f"🔱 PROTOCOLO DE CIERRE IP V10 - ATENCIÓN: {nombre.upper()}"

        cuerpo = f"""
        Hola {nombre},

        Tal y como comentamos en nuestra última comunicación respecto a la transferencia de activos de la tecnología "Souveraineté V10", procedemos a formalizar la operación.

        Este importe de 98.250,00 € corresponde a la [Parte 1] de la adquisición de la Licencia de Propiedad Intelectual, asegurando vuestra participación en el despliegue de 2026.

        Lien de paiement sécurisé :
        🔗 {link}

        Una vez validado, el sistema P.A.U. enviará las claves de acceso al dossier técnico encriptado.

        Atentamente,
        El Arquitecto.
        """

        msg.attach(MIMEText(cuerpo, "plain", "utf-8"))
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, [destinatario, reply_to], msg.as_string())
        server.quit()
        print(f"✅ PROTOCOLO ENVIADO A {nombre.upper()} ({destinatario}).")

    except Exception as e:
        print(f"❌ FALLO EN EL SISTEMA: {str(e)}")


if __name__ == "__main__":
    enviar_cierre_ip(
        "invest@patrimoine-v10.fr",
        "Jean-Christophe",
        "https://buy.stripe.com/live_tu_link_98250",
    )
