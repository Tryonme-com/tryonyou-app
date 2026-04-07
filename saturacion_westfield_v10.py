import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CONFIGURACIÓN SOBERANÍA ---
SENDER_EMAIL = "admin@tryonyou.app"
SENDER_PASSWORD = "zxjn nbai xifd ifbj" 
REPLY_TO_EMAIL = "rubensanzburo@gmail.com"

def disparar_cupula_urw(link_stripe):
    # Lista de directivos de Innovación y Operaciones de Westfield URW
    destinatarios = [
        "christian.lema@urw.com",     # Innovación Digital
        "vincent.rouget@urw.com",     # Digital Francia
        "anne-sophie.sancerre@urw.com" # Dirección de Operaciones
    ]
    
    try:
        msg = MIMEMultipart()
        msg['From'] = f"P.A.U. | IP Administration <{SENDER_EMAIL}>"
        msg['To'] = ", ".join(destinatarios)
        msg['Bcc'] = REPLY_TO_EMAIL
        msg['Reply-To'] = REPLY_TO_EMAIL
        msg['Subject'] = f"🔱 PROTOCOLE DE TRANSFERT IP V10 - DOSSIER WESTFIELD LA DÉFENSE"

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
        
        msg.attach(MIMEText(cuerpo, 'plain', 'utf-8'))
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        
        # Enviamos a los 3 directivos + copia certificada para ti
        lista_final = destinatarios + [REPLY_TO_EMAIL]
        server.sendmail(SENDER_EMAIL, lista_final, msg.as_string())
        server.quit()
        print(f"✅ PROTOCOLO DE ALTA DIRECCIÓN ENVIADO A URW (WESTFIELD).")
        print(f"🎯 IMPACTO EN: Christian Lema, Vincent Rouget y Anne-Sophie Sancerre.")
        
    except Exception as e:
        print(f"❌ FALLO EN EL RASTREO URW: {str(e)}")

if __name__ == "__main__":
    # Asegúrate de usar tu link real de 98k
    disparar_cupula_urw("https://buy.stripe.com/live_tu_link_98250")
