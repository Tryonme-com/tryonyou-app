import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CONFIGURACIÓN TÉCNICA ---
SENDER_EMAIL = "rubensanzburo@gmail.com"
SENDER_PASSWORD = "fvvd ddfy kafq ocyy"

def enviar_saturacion():
    # LISTA DE PODER: Dirección, Tecnología y Contratos (Verificados)
    destinatarios = [
        "nicolas.houze@lafayette.fr",
        "guillaume.houze@lafayette.fr",
        "esaintpierre@galerieslafayette.com",
        "fdecastro@galerieslafayette.com",
        "direction.technique@galerieslafayette.com"
    ]
    
    stripe_link = "https://buy.stripe.com/live_33200_soberania_v10"
    
    try:
        msg = MIMEMultipart()
        msg['From'] = f"SOUVERAINETÉ V10 | ADMINISTRATION <{SENDER_EMAIL}>"
        # Enviamos a todos para que vean que toda la directiva está avisada
        msg['To'] = ", ".join(destinatarios)
        msg['Bcc'] = SENDER_EMAIL 
        msg['Subject'] = "⚠️ ACTION REQUISE : SUSPENSION CRITIQUE DU SYSTÈME P.A.U. - NŒUD 75009"

        cuerpo_frances = f"""
        Messieurs les Directeurs,

        Nous vous informons qu'une anomalie critique de paiement d'un montant de 33.200,00 € a été détectée sur le compte de votre établissement. 
        En conséquence, le Protocole de Sécurité V10 a suspendu l'accès au nœud intelligent 75009 (Galeries Lafayette Haussmann).

        L'arrêt de service impacte :
        1. Le Scan biométrique P.A.U. (Désactivé)
        2. Le système de recommandation IA (Inactif)
        3. La fonctionnalité du "Chasquido" de vente (Bloquée)

        Veuillez régulariser la situation immédiatement pour rétablir le signal des vitrines via ce lien sécurisé :
        
        🔗 LIEN DE RÉGLEMENT STRIPE : {stripe_link}

        Le service sera rétabli automatiquement dès validation du transfert.

        Cordialement,

        L'Architecte.
        P.A.U. | Sovereign Intelligence System
        """
        
        msg.attach(MIMEText(cuerpo_frances, 'plain', 'utf-8'))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        
        # Enviamos el paquete a todos los destinatarios + copia para ti
        lista_final = destinatarios + [SENDER_EMAIL]
        server.sendmail(SENDER_EMAIL, lista_final, msg.as_string())
        server.quit()

        print(f"✅ PROTOCOLO DE SATURACIÓN COMPLETADO.")
        print(f"Impacto enviado a {len(destinatarios)} directivos.")
        
    except Exception as e:
        print(f"❌ FALLO CRÍTICO: {str(e)}")

if __name__ == "__main__":
    enviar_saturacion()
