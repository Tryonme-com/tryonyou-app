import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from sovereign_script_env import require_smtp_credentials, reply_to_from_env


def disparar_cupula_urw(link_stripe):
    # Lista de directivos de Innovación y Operaciones de Westfield URW
    destinatarios = [
        "christian.lema@urw.com",  # Innovación Digital
        "vincent.rouget@urw.com",  # Digital Francia
        "anne-sophie.sancerre@urw.com",  # Dirección de Operaciones
    ]

    try:
        sender_email, sender_password = require_smtp_credentials()
        reply_to = reply_to_from_env(sender_email)
        msg = MIMEMultipart()
        msg["From"] = f"P.A.U. | IP Administration <{sender_email}>"
        msg["To"] = ", ".join(destinatarios)
        msg["Bcc"] = reply_to
        msg["Reply-To"] = reply_to
        msg["Subject"] = "🔱 PROTOCOLE DE TRANSFERT IP V10 - DOSSIER WESTFIELD LA DÉFENSE"

        cuerpo = f"""
        À l'attention de la Direction de l'Innovation et des Opérations,

        Suite à l'audit technique de la technologie "Souveraineté V10", nous procédons à la formalisation du transfert de licence IP pour l'infrastructure de Westfield Les 4 Temps.

        Ce transfert d'actifs (Partie 1 - 98.250,00 €) sécurise le déploiement des nœuds intelligents au sein du district de La Défense.

        Veuillez procéder au règlement prioritaire via le terminal sécurisé ci-dessous :

        🔗 LIEN D'ACTIVATION IP : {link_stripe}

        Dès réception, le dossier de propriété intellectuelle P.A.U. sera synchronisé avec vos serveurs de gestion d'actifs.

        Cordialement,

        L'Architecte.
        P.A.U. | Sovereign Intelligence System
        """

        msg.attach(MIMEText(cuerpo, "plain", "utf-8"))
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)

        lista_final = destinatarios + [reply_to]
        server.sendmail(sender_email, lista_final, msg.as_string())
        server.quit()
        print("✅ PROTOCOLO DE ALTA DIRECCIÓN ENVIADO A URW (WESTFIELD).")
        print("🎯 IMPACTO EN: Christian Lema, Vincent Rouget y Anne-Sophie Sancerre.")

    except Exception as e:
        print(f"❌ FALLO EN EL RASTREO URW: {str(e)}")


if __name__ == "__main__":
    disparar_cupula_urw("https://buy.stripe.com/live_tu_link_98250")
