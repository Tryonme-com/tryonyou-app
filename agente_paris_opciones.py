import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from sovereign_script_env import require_smtp_credentials, reply_to_from_env

# --- CONFIGURACIÓN ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


def enviar_v10_con_opciones(email_destinatario, nombre_contacto, empresa):
    sender_email, sender_password = require_smtp_credentials()
    reply_to = reply_to_from_env(sender_email)
    # LINKS DE STRIPE (Asegúrate de que estos son tus links reales en el dashboard)
    link_activacion = "https://buy.stripe.com/live_tu_link_27500"
    link_mensual = "https://buy.stripe.com/live_tu_link_9900"
    link_anual = "https://buy.stripe.com/live_tu_link_98000"

    try:
        msg = MIMEMultipart()
        msg["From"] = f"P.A.U. | Admin TryOnYou <{sender_email}>"
        msg["To"] = email_destinatario
        msg["Bcc"] = reply_to
        msg["Reply-To"] = reply_to
        msg["Subject"] = f"🔱 OPTIONS D'ACTIVATION SOUVERAINETÉ V10 - {empresa}"

        # Enlaces definidos antes del try; f-string evita dudas de .format() vs placeholders.
        cuerpo = f"""
        Cher {nombre_contacto},

        Pour finaliser le déploiement de vos 10 nœuds intelligents au sein de vos vitrines, nous vous prions de valider l'activation initiale ainsi que votre modalité de service préférée.

        1️⃣ ÉTAPE OBLIGATOIRE : ACTIVATION ET RÉSERVE
        Lien pour la fabrication et l'exclusivité (27.500 €) : {link_activacion}

        2️⃣ ÉTAPE DE SERVICE (Choisissez votre option) :
        
        • OPTION A (Mensuelle) : 9.900 € / mois (+ 8% commissions)
          Lien de souscription : {link_mensual}

        • OPTION B (Annuelle - Privilège) : 98.000 € / an (+ 8% commissions)
          *Cette option vous offre une économie immédiate de 20.800 €.*
          Lien de règlement : {link_anual}

        Le protocole P.A.U. s'activera automatiquement dès la validation de vos sélections.

        Cordialement,

        L'Architecte.
        P.A.U. | Sovereign Intelligence System
        """

        msg.attach(MIMEText(cuerpo, "plain", "utf-8"))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, [email_destinatario, reply_to], msg.as_string())
        server.quit()

        print(f"✅ PROTOCOLO DOBLE ENVIADO A {empresa}. ESPERANDO ELECCIÓN.")
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

if __name__ == "__main__":
    enviar_v10_con_opciones("nicolas.houze@lafayette.fr", "Monsieur Houzé", "Galeries Lafayette")
