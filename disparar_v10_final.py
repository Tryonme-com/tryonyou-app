import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from sovereign_script_env import require_smtp_credentials, reply_to_from_env


def enviar_soberania():
    destinatarios = [
        "nicolas.houze@lafayette.fr",
        "g.houze@lafayette.fr",
        "egandini@lafayette.fr",
    ]
    link_mensual = "https://buy.stripe.com/live_tu_link_33200"
    link_anual = "https://buy.stripe.com/live_tu_link_98000"

    try:
        sender_email, sender_password = require_smtp_credentials()
        reply_to = reply_to_from_env(sender_email)
        msg = MIMEMultipart()
        msg["From"] = f"Souveraineté V10 Administration <{sender_email}>"
        msg["To"] = ", ".join(destinatarios)
        msg["Reply-To"] = reply_to
        msg["Bcc"] = sender_email
        msg["Subject"] = (
            "⚠️ URGENT : RÉTABLISSEMENT DU SERVICE V10 - GALERIES LAFAYETTE"
        )

        cuerpo = f"""
        Monsieur,

        Suite à une anomalie détectée dans le protocole de paiement (33.200,00 €), le système P.A.U. a suspendu l'accès au nœud intelligent 75009 (Haussmann).

        Pour rétablir immédiatement le service et la fonctionnalité de vos vitrines, deux options sont disponibles :

        1. RÉGULARISATION MENSUELLE (33.200 €) : {link_mensual}
        2. FORFAIT ANNUEL PRIVILÈGE (98.000 €) : {link_anual}
           (Garantit le service ininterrompu pour toute l'année 2026).

        Le signal sera rétabli de manière autonome dès validation du transfert.

        Cordialement,
        L'Architecte.
        TryOnYou-App | Sovereign Intelligence
        """
        msg.attach(MIMEText(cuerpo, "plain", "utf-8"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, destinatarios + [sender_email], msg.as_string())
        server.quit()
        print("✅ PROTOCOLO ENVIADO A LA DIRECTIVA. COPIA EN TU BANDEJA.")

    except Exception as e:
        print(f"❌ FALLO EN EL ENVÍO: {str(e)}")


if __name__ == "__main__":
    enviar_soberania()
