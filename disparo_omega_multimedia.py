import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from sovereign_script_env import require_smtp_credentials, reply_to_from_env

# --- OBJETIVOS ESTRATÉGICOS ---
inversores = [
    "info@bigsurventures.vc", "info@abven.com", "dealflow@ipgroupplc.com", 
    "hello@iqcapital.vc", "patentsales@intven.com", "mlower@rpxcorp.com",
    "ir@acaciares.com", "opportunities@fortress.com", "contact@elaia.com",
    "info@jolt-capital.com", "contact@otbvc.com", "info@uvcpartners.com",
    "investment@voimaventures.com", "info@inventure.vc", "dealflow@trl13.com",
    "contact@isai.fr", "info@partechpartners.com", "dealflow@idinvest.com"
    # El sistema completará los 30 del Dashboard
]

def enviar_pack_lujo(destinatario):
    try:
        sender_email, sender_password = require_smtp_credentials()
        reply_to = reply_to_from_env(sender_email)
        msg = MIMEMultipart()
        msg['From'] = f"L'Architecte | Sovereign V10 <{sender_email}>"
        msg['To'] = destinatario
        msg['Reply-To'] = reply_to
        msg['Subject'] = "🔱 DOSSIER V10: Métriques Lafayette & Vision Stratégique"

        cuerpo = f"""
        Estimados,

        Como responsable del sistema P.A.U., adjunto el reporte de impacto visual y métrico del despliegue en las Galeries Lafayette.

        [ 📊 DASHBOARD DE RENDIMIENTO - V10 ]
        Hemos digitalizado la experiencia de probador. Pueden ver nuestra arquitectura de nodos y el control de flujos en tiempo real aquí:
        🔗 Ver Dashboard V10: [Enlace a captura de métricas]

        [ ⚠️ EL PROBLEMA: LA INEFICIENCIA DEL LUJO ]
        ¿Por qué perdemos clientes en el probador? El caos de las tallas y la gestión manual:
        • El Caos: https://youtu.be/IbwR2YOU5BQ
        • El Conflicto (M vs L): https://youtu.be/rFZSCJE9_Uk

        [ ✨ LA SOLUCIÓN: EL CHASQUIDO P.A.U. ]
        La IA eliminando la fricción y devolviendo la dignidad al cliente:
        • Demo Operativa: https://youtu.be/hIzS3ggo7bM

        [ MÉTRICAS SELLADAS ]
        • Reducción de devoluciones: 42%
        • Incremento Ticket Medio: +28%
        
        Actualmente estamos cerrando la transferencia de Propiedad Intelectual (98.250 € / bloque).

        Cordialement,

        L'Architecte.
        TryOnYou-App | Sovereign Intelligence
        """
        
        msg.attach(MIMEText(cuerpo, 'plain', 'utf-8'))
        
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, [destinatario, reply_to], msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"❌ Error en {destinatario}: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Disparando ráfaga con imágenes y métricas a 30 inversores...")
    for inv in inversores:
        if enviar_pack_lujo(inv):
            print(f"✅ Notificado con éxito: {inv}")
            time.sleep(1) 
    print("🔱 OPERACIÓN OMEGA COMPLETADA. EL BÚNKER HA HABLADO.")
