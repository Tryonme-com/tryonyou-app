import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from sovereign_script_env import require_smtp_credentials


def enviar_soberania():
    destinatarios = [
        "nicolas.houze@lafayette.fr",
        "g.houze@lafayette.fr",
        "egandini@lafayette.fr",
    ]
    link_mensual = "https://buy.stripe.com/live_33200_soberania_v10"
    link_anual = "https://buy.stripe.com/live_98000_anual_v10"

    try:
        sender_email, sender_password = require_smtp_credentials()
        msg = MIMEMultipart()
        msg["From"] = f"Rubén Sanz | Souveraineté V10 <{sender_email}>"
        msg["To"] = ", ".join(destinatarios)
        msg["Subject"] = "⚠️ URGENT : SUSPENSION DU SERVICE V10 - GALERIES LAFAYETTE"

        cuerpo = f"""
        Monsieur,

        En tant que responsable du système P.A.U., je vous informe que le nœud intelligent 75009 (Haussmann) a été suspendu suite à une anomalie de paiement de 33.200,00 €.

        Pour rétablir immédiatement le service dans vos vitrines, deux options sont à votre disposition :

        1. RÉGULARISATION MENSUELLE (33.200 €) : {link_mensual}
        2. FORFAIT ANNUEL PRIVILÈGE (98.000 €) : {link_anual}

        Le signal sera rétabli dès validation du transfert.

        Cordialement,
        Rubén Sanz.
        L'Architecte | TryOnYou
        """
        msg.attach(MIMEText(cuerpo, "plain", "utf-8"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, destinatarios + [sender_email], msg.as_string())
        server.quit()
        print("✅ PROTOCOLO ENVIADO DESDE GMAIL PERSONAL. ÉXITO.")

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")


if __name__ == "__main__":
    enviar_soberania()
