import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from sovereign_script_env import require_smtp_credentials, reply_to_from_env

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


def enviar_v10_lvmh(email_destinatario, nombre_contacto, departamento):
    link_deployment = "https://buy.stripe.com/live_tu_link_25000_LVMH"
    link_mensual = "https://buy.stripe.com/live_tu_link_9900"
    link_anual = "https://buy.stripe.com/live_tu_link_98000"

    try:
        sender_email, sender_password = require_smtp_credentials()
        reply_to = reply_to_from_env(sender_email)
        msg = MIMEMultipart()
        msg["From"] = f"P.A.U. | Direction TryOnYou <{sender_email}>"
        msg["To"] = email_destinatario
        msg["Bcc"] = reply_to
        msg["Reply-To"] = reply_to
        msg['Subject'] = f"🔱 DÉPLOIEMENT SOUVERAINETÉ V10 - LVMH GROUP ({departamento})"

        cuerpo = f"""
        Cher {nombre_contacto},

        Conformément à nos échanges concernant l'intégration de la technologie "Souveraineté V10" au sein de vos points de vente stratégiques, nous avons l'honneur de vous soumettre le protocole d'activation finale.

        Cette étape permet d'initialiser le déploiement des 10 premiers nœuds intelligents sur vos sites sélectionnés (Marais / Rive Gauche).

        1️⃣ DÉPLOIEMENT INITIAL ET MISE EN SERVICE
        Lien pour l'installation multi-site (25.000 €) : {link_deployment}

        2️⃣ MODALITÉS DE MAINTENANCE IA (Options de gestion) :
        
        • OPTION A (Mensuelle) : 9.900 € / mois (+ 8% commissions sur ventes)
          Lien d'activation : {link_mensual}

        • OPTION B (Annuelle - Privilège Group) : 98.000 € / an (+ 8% commissions)
          *Cette option optimise votre budget annuel avec une réduction de 20.800 €.*
          Lien de règlement prioritaire : {link_anual}

        Le système P.A.U. est prêt pour la synchronisation immédiate dès réception de la validation des transferts.

        Nous restos à votre disposition pour assurer l'excellence opérationnelle de ce partenariat.

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

        print(f"✅ PROTOCOLO LVMH ENVIADO. COPIA CERTIFICADA EN TU BANDEJA.")
        
    except Exception as e:
        print(f"❌ FALLO EN EL ENVÍO LVMH: {str(e)}")

if __name__ == "__main__":
    # DISPARO A LVMH (Ejemplo: Dirección de Innovación o Retail)
    enviar_v10_lvmh(
        "digital-innovation@lvmh.com", 
        "Monsieur le Directeur", 
        "Rive Gauche / Marais"
    )
