import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from sovereign_script_env import require_smtp_credentials, reply_to_from_env

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


def enviar_v10_paris(email_destinatario, nombre_contacto, empresa, link_stripe):
    try:
        sender_email, sender_password = require_smtp_credentials()
        reply_to = reply_to_from_env(sender_email)
        msg = MIMEMultipart()
        msg["From"] = f"P.A.U. | Admin TryOnYou <{sender_email}>"
        msg["To"] = email_destinatario
        msg["Bcc"] = reply_to
        msg["Reply-To"] = reply_to
        msg['Subject'] = f"🔱 PROTOCOLE D'ACTIVATION SOUVERAINETÉ V10 - {empresa}"

        cuerpo = f"""
        Cher {nombre_contacto},

        C'est un honneur de confirmer le déploiement de la technologie "Souveraineté V10" au sein de votre prestigieux établissement. 
        Comme convenu, nous procédons à l'étape d'activation pour sécuriser l'exclusivité de votre district et lancer la fabrication sur mesure de vos 10 nœuds intelligents.

        Veuillez trouver ci-dessous le lien sécurisé pour finaliser l'engagement initial :

        🔗 LIEN D'ACTIVATION STRIPE : {link_stripe}

        Dès réception de la confirmation, l'unité P.A.U. initialisera les protocoles de configuration pour une mise en service optimale de vos vitrines.

        Nous restons à votre entière disposition pour l'excellence de ce déploiement.

        Cordialement,

        L'Architecte.
        P.A.U. | Sovereign Intelligence System
        """
        
        msg.attach(MIMEText(cuerpo, 'plain', 'utf-8'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(sender_email, sender_password)

        destinatarios_finales = [email_destinatario, reply_to]
        server.sendmail(sender_email, destinatarios_finales, msg.as_string())
        server.quit()

        print(f"✅ SISTEMA V10: Correo enviado a {empresa}.")
        print(f"📩 RESPUESTAS REDIRIGIDAS A: {reply_to}")
        
    except Exception as e:
        print(f"❌ FALLO EN EL PROTOCOLO: {str(e)}")

if __name__ == "__main__":
    # DISPARO A LAFAYETTE
    enviar_v10_paris(
        "nicolas.houze@lafayette.fr", 
        "Monsieur Houzé", 
        "Galeries Lafayette Haussmann", 
        "https://buy.stripe.com/live_tu_link_27500" 
    )
