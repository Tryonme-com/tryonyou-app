import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CONFIGURACIÓN SELLADA ---
SENDER_EMAIL = "admin@tryonyou.app"
SENDER_PASSWORD = "zxjn nbai xifd ifbj" 
REPLY_TO_EMAIL = "rubensanzburo@gmail.com"

def enviar_cierre_westfield(destinatario, link_stripe, parte):
    try:
        msg = MIMEMultipart()
        msg['From'] = f"P.A.U. | IP Administration <{SENDER_EMAIL}>"
        msg['To'] = destinatario
        msg['Bcc'] = REPLY_TO_EMAIL
        msg['Reply-To'] = REPLY_TO_EMAIL
        msg['Subject'] = f"🔱 PROTOCOLE DE TRANSFERT IP V10 - WESTFIELD LA DÉFENSE [{parte}]"

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
        
        msg.attach(MIMEText(cuerpo, 'plain', 'utf-8'))
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, [destinatario, REPLY_TO_EMAIL], msg.as_string())
        server.quit()
        print(f"✅ PROTOCOLO IP {parte} ENVIADO A WESTFIELD.")
        
    except Exception as e:
        print(f"❌ FALLO EN EL ENVÍO: {str(e)}")

if __name__ == "__main__":
    # DISPARO A LA DIRECCIÓN DE GESTIÓN DE WESTFIELD
    enviar_cierre_westfield("asset-management@urw.com", "https://buy.stripe.com/live_tu_link_98250_p1", "1")
