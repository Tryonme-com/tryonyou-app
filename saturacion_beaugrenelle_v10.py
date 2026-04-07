import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CONFIGURACIÓN DE SOBERANÍA ---
SENDER_EMAIL = "admin@tryonyou.app"
SENDER_PASSWORD = "zxjn nbai xifd ifbj"
REPLY_TO = "rubensanzburo@gmail.com"

def disparar_protocolo_total():
    # Los 5 pilares de decisión en Apsys/Beaugrenelle
    destinatarios = [
        "mbansay@apsys-group.com",    # Presidente
        "fbansay@apsys-group.com",    # CEO
        "mtessier@apsys-group.com",   # Operaciones
        "cdeguillebon@apsys-group.com", # Innovación
        "fagache@apsys-group.com"      # Desarrollo
    ]
    
    try:
        msg = MIMEMultipart()
        msg['From'] = f"L'Architecte | P.A.U. Sovereign <{SENDER_EMAIL}>"
        msg['To'] = ", ".join(destinatarios)
        msg['Bcc'] = REPLY_TO
        msg['Reply-To'] = REPLY_TO
        msg['Subject'] = "🔱 PROTOCOLE SOUVERAINETÉ V10 : Transformation Numérique Beaugrenelle Paris"

        cuerpo = f"""
        À l'attention de la Direction Générale et de l'Innovation,

        Suite au déploiement stratégique de notre technologie "Souveraineté V10" aux Galeries Lafayette, nous activons le protocole d'expansion pour le district 75015 (Beaugrenelle Paris).

        [ IMPACT CERTIFIÉ - PILOTE HAUSSMANN ]
        Notre intelligence P.A.U. a redéfini l'efficience opérationnelle :
        • Réduction drastique des retours (Taille/Fit) : 42%
        • Croissance immédiate du panier moyen : +28%
        • Temps de recommandation biométrique : 14 secondes.

        [ DIAGNOSTIC DU MARCHÉ ]
        Le chaos logistique actuel est le frein majeur de la rentabilité. 
        🔗 Preuve de l'inefficacité : https://youtu.be/IbwR2YOU5BQ
        🔗 Conflit de standardisation (M vs L) : https://youtu.be/rFZSCJE9_Uk

        [ SOLUTION : ÉCOSYSTÈME P.A.U. ]
        Une expérience fluide et sans complexe pour le client de luxe.
        🔗 Démo Système : https://youtu.be/hIzS3ggo7bM

        Ci-joint, vous trouverez notre Dashboard de gestion (PMV) synchronisant les flux de données. Nous ouvrons ce jour la licence de transfert IP pour Beaugrenelle (98.250,00 €).

        Nous restons à votre disposition pour une démonstration technique sur site.

        Cordialement,

        L'Architecte.
        TryOnYou-App | Sovereign Intelligence System
        """
        
        msg.attach(MIMEText(cuerpo, 'plain', 'utf-8'))
        
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        
        # Envío masivo con copia para ti
        server.sendmail(SENDER_EMAIL, destinatarios + [REPLY_TO], msg.as_string())
        server.quit()
        print("✅ SATURACIÓN COMPLETADA: Los 5 responsables de Beaugrenelle han sido notificados.")
        
    except Exception as e:
        print(f"❌ FALLO EN LA RÁFAGA: {str(e)}")

if __name__ == "__main__":
    disparar_protocolo_total()
