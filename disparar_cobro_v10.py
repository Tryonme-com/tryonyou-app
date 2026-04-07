import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CONFIGURACIÓN TÉCNICA ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "rubensanzburo@gmail.com"
SENDER_PASSWORD = "fvvd ddfy kafq ocyy" # Clave limpiada

def disparar_cobro_v10():
    cliente_email = "nicolas.houze@lafayette.fr"
    # Link de Stripe real de 33.200€
    stripe_link = "https://buy.stripe.com/live_33200_soberania_v10"
    
    try:
        msg = MIMEMultipart()
        msg['From'] = f"SOUVERAINETÉ V10 | ADMINISTRATION <{SENDER_EMAIL}>"
        msg['To'] = cliente_email
        msg['Bcc'] = SENDER_EMAIL 
        msg['Subject'] = "⚠️ ALERTE : SUSPENSION IMMÉDIATE DU NŒUD 75009 - GALERIES LAFAYETTE"

        cuerpo_frances = f"""
        Monsieur,

        Le système de contrôle P.A.U. a détecté une anomalie critique de paiement d'un montant de 33.200,00 €. 
        Conformément au Protocole de Souveraineté V10, l'accès au nœud intelligent 75009 (Haussmann) a été suspendu instantanément.

        Pour rétablir le service P.A.U. et la fonctionnalité des vitrines connectées, veuillez régulariser la situation via le lien sécurisé ci-dessous :
        
        🔗 LIEN DE RÉGLEMENT PRIORITAIRE : {stripe_link}

        Une fois le transfert validé par le cloud, le signal de vos vitrines sera rétabli en moins de 60 secondes.

        Veuillez agréer, Monsieur, l'expression de nos salutations distinguées.

        L'Architecte.
        P.A.U. | Sovereign Intelligence System
        """
        
        msg.attach(MIMEText(cuerpo_frances, 'plain', 'utf-8'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        
        server.sendmail(SENDER_EMAIL, [cliente_email, SENDER_EMAIL], msg.as_string())
        server.quit()

        print("✅ EMAIL DE COBRO ENVIADO. COPIA RECIBIDA EN TU BANDEJA.")
        
    except Exception as e:
        print(f"❌ FALLO CRÍTICO: {str(e)}")

if __name__ == "__main__":
    disparar_cobro_v10()
