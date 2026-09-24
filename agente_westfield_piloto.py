import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from sovereign_script_env import require_smtp_credentials, reply_to_from_env

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


def enviar_v10_westfield(email_destinatario, nombre_contacto, centros):
    link_piloto = "https://buy.stripe.com/live_tu_link_12500_Westfield"
    link_mensual = "https://buy.stripe.com/live_tu_link_9900"
    link_anual = "https://buy.stripe.com/live_tu_link_98000"

    try:
        sender_email, sender_password = require_smtp_credentials()
        reply_to = reply_to_from_env(sender_email)
        msg = MIMEMultipart()
        msg["From"] = f"P.A.U. | Innovation TryOnYou <{sender_email}>"
        msg["To"] = email_destinatario
        msg["Bcc"] = reply_to
        msg["Reply-To"] = reply_to
        msg['Subject'] = f"🔱 PROTOCOLE PILOTE SOUVERAINETÉ V10 - WESTFIELD PARIS"

        cuerpo = f"""
        Cher {nombre_contacto},

        Suite à nos échanges concernant la phase pilote de la technologie "Souveraineté V10", nous avons le plaisir de vous transmettre le protocole d'activation pour vos centres stratégiques ({centros}).

        Ce déploiement initial est conçu pour valider l'augmentation des flux et l'engagement client via nos nœuds intelligents.

        1️⃣ ACTIVATION DE LA PHASE PILOTE
        Lien pour l'initialisation et calibration (12.500 €) : {link_piloto}

        2️⃣ OPTIONS DE MAINTENANCE IA (Après installation) :
        
        • OPTION A (Mensuelle) : 9.900 € / mois (+ 8% commissions sur transactions)
          Lien de souscription : {link_mensual}

        • OPTION B (Annuelle - Partenaire Premium) : 98.000 € / an (+ 8% commissions)
          *Cette option prioritaire inclut une réduction de 20.800 € sur l'année.*
          Lien de règlement annuel : {link_anual}

        Le système P.A.U. commencera la synchronisation des données dès la confirmation du règlement.

        Nous restons à votre entière disposition pour faire de ce pilote un succès historique pour le groupe Westfield.

        Cordialement,

        L'Architecte.
        P.A.U. | Sovereign Intelligence System
        """
        
        msg.attach(MIMEText(cuerpo, 'plain', 'utf-8'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, [email_destinatario, reply_to], msg.as_string())
        server.quit()

        print(f"✅ PROTOCOLO PILOTO WESTFIELD (12.500€) ENVIADO.")
        
    except Exception as e:
        print(f"❌ ERROR EN PILOTO WESTFIELD: {str(e)}")

if __name__ == "__main__":
    # DISPARO A WESTFIELD (Madame Sancerre o responsable de innovación)
    enviar_v10_westfield(
        "anne-sophie.sancerre@urw.com", 
        "Madame Sancerre", 
        "Westfield Forum des Halles / Les 4 Temps"
    )
