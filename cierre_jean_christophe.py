import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CONFIGURACIÓN BLINDADA ---
SENDER_EMAIL = "admin@tryonyou.app"
SENDER_PASSWORD = "zxjn nbai xifd ifbj" 
REPLY_TO_EMAIL = "rubensanzburo@gmail.com"

def enviar_cierre_ip(destinatario, nombre, link):
    try:
        msg = MIMEMultipart()
        msg['From'] = f"P.A.U. | Sovereign Capital <{SENDER_EMAIL}>"
        msg['To'] = destinatario
        msg['Bcc'] = REPLY_TO_EMAIL
        msg['Reply-To'] = REPLY_TO_EMAIL
        msg['Subject'] = f"🔱 PROTOCOLO DE CIERRE IP V10 - ATENCIÓN: {nombre.upper()}"

        cuerpo = f"""
        Hola {nombre},

        Tal y como comentamos en nuestra última comunicación respecto a la transferencia de activos de la tecnología "Souveraineté V10", procedemos a formalizar la operación.

        Este importe de 98.250,00 € corresponde a la [Parte 1] de la adquisición de la Licencia de Propiedad Intelectual, asegurando vuestra participación en el despliegue de 2026.

        Lien de paiement sécurisé :
        🔗 {link}

        Una vez validado, el sistema P.A.U. enviará las claves de acceso al dossier técnico encriptado.

        Atentamente,
        El Arquitecto.
        """
        
        msg.attach(MIMEText(cuerpo, 'plain', 'utf-8'))
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, [destinatario, REPLY_TO_EMAIL], msg.as_string())
        server.quit()
        print(f"✅ PROTOCOLO ENVIADO A {nombre.upper()} ({destinatario}).")
        
    except Exception as e:
        print(f"❌ FALLO EN EL SISTEMA: {str(e)}")

if __name__ == "__main__":
    enviar_cierre_ip("invest@patrimoine-v10.fr", "Jean-Christophe", "https://buy.stripe.com/live_tu_link_98250")
