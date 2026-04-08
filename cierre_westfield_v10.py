import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from sovereign_script_env import require_smtp_credentials, reply_to_from_env


def enviar_cierre_westfield(destinatario, link_stripe, parte):
    try:
        sender_email, sender_password = require_smtp_credentials()
        reply_to = reply_to_from_env(sender_email)
        msg = MIMEMultipart()
        msg["From"] = f"P.A.U. | IP Administration <{sender_email}>"
        msg["To"] = destinatario
        msg["Bcc"] = reply_to
        msg["Reply-To"] = reply_to
        msg["Subject"] = (
            f"🔱 PROTOCOLE DE TRANSFERT IP V10 - WESTFIELD LA DÉFENSE [{parte}]"
        )

        cuerpo = f"""
        À l'attention de la Direction Foncière,

        Dans le cadre du déploiement de la technologie "Souveraineté V10" au centre Westfield Les 4 Temps, nous procédons à la formalisation du transfert de licence IP (Partie {parte}).

        Veuillez trouver ci-dessous le lien sécurisé pour finaliser l'acquisition de cet actif technologique :

        🔗 LIEN DE RÈGLEMENT (98.250,00 €) : {link_stripe}

        Dès validation, le dossier technique encripté P.A.U. sera mis à jour pour le nœud de La Défense.

        Cordialement,

        L'Architecte.
        TryOnYou-App | Sovereign Intelligence
        """

        msg.attach(MIMEText(cuerpo, "plain", "utf-8"))
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, [destinatario, reply_to], msg.as_string())
        server.quit()
        print(f"✅ PROTOCOLO IP {parte} ENVIADO A WESTFIELD.")

    except Exception as e:
        print(f"❌ FALLO EN EL ENVÍO: {str(e)}")


if __name__ == "__main__":
    enviar_cierre_westfield(
        "asset-management@urw.com",
        "https://buy.stripe.com/live_tu_link_98250_p1",
        "1",
    )
