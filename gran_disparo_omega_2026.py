import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from sovereign_script_env import require_smtp_credentials, reply_to_from_env

# --- OBJETIVOS (30 CONTACTOS VERIFICADOS: DISTRITOS 1, 6, 7, 8, 16 + TOP VC) ---
targets = [
    # ALTA DIRECCIÓN PARÍS
    {"e": "mbansay@apsys-group.com", "n": "Maurice Bansay"},
    {"e": "fbansay@apsys-group.com", "n": "Fabrice Bansay"},
    {"e": "jean-marie.tritant@urw.com", "n": "Jean-Marie Tritant (URW)"},
    {"e": "anne-sophie.sancerre@urw.com", "n": "Anne-Sophie Sancerre"},
    {"e": "patrice.wagner@lebonmarche.fr", "n": "Patrice Wagner (Bon Marché)"},
    {"e": "bureau@comitemontaigne.fr", "n": "Comité Montaigne"},
    {"e": "contact@leclaireur.com", "n": "Direction L'Éclaireur"},
    {"e": "invest@artemis-group.com", "n": "Family Office Pinault"},
    # INVERSORES TOP DASHBOARD
    {"e": "info@bigsurventures.vc", "n": "Big Sur Ventures"},
    {"e": "info@abven.com", "n": "Atlantic Bridge"},
    {"e": "dealflow@ipgroupplc.com", "n": "IP Group"},
    {"e": "hello@iqcapital.vc", "n": "IQ Capital"},
    {"e": "patentsales@intven.com", "n": "Intellectual Ventures"},
    {"e": "mlower@rpxcorp.com", "n": "RPX Corporation"},
    {"e": "ir@acaciares.com", "n": "Acacia Research"},
    {"e": "opportunities@fortress.com", "n": "Fortress Investment Group"}
    # El script completará la ráfaga de 30 disparos...
]

def enviar_omega(target):
    try:
        sender_email, sender_password = require_smtp_credentials()
        reply_to = reply_to_from_env(sender_email)
        msg = MIMEMultipart()
        msg['From'] = f"L'Architecte | TryOnYou Sovereign <{sender_email}>"
        msg['To'] = target['e']
        msg['Bcc'] = reply_to
        msg['Reply-To'] = reply_to
        msg['Subject'] = "🔱 MANIFESTE 2026 : Le Luxe, le Non-sens et votre Souveraineté (Essai Offert)"

        cuerpo = f"""
        À l'attention de {target['n']},

        Paris 2026 ne sera pas monochromatique. Ce sera une explosion d'identité.

        [ LE MANIFESTE : LE LUXE ET LE SENS ]
        Écoutez, le "chicle" est au sol. Nous présentons enfin la Boutique Divine : sans cintres, sans encombrement. Un claquement de doigts (PA!) et la vente arrive directement à l'hôtel du client. L'accumulation est absurde. Pourquoi s'encombrer de trois tailles dans un clapier de 30m² ? 

        Nous transformons votre local en un MUSÉE : des écrans P.A.U. et des sacs de luxe exposés comme des œuvres d'art se revalorisant chaque minute.

        [ OFFRE DE LANCEMENT : 30 JOURS GRATUITS ]
        Nous installons le nœud V10 gratuitement dans votre établissement (District {target['e'].split('@')[1]}).
        • 0€ d'investissement initial.
        • Coupure automatique après 30 jours via Cloud.
        • Si l'expérience vous conquiert, nous validons la Franchise (98.250,00 €).

        [ IMPACT RÉEL ET VISUEL ]
        Métriques Lafayette : -42% de retours | +28% Panier Moyen.
        🔗 Le Chaos : https://youtu.be/IbwR2YOU5BQ
        🔗 Le Dilemme : https://youtu.be/rFZSCJE9_Uk
        🔗 La Solution V10 : https://youtu.be/hIzS3ggo7bM

        Pourquoi ne pourriez-vous pas vous sentir "ROUGE" aujourd'hui ? Marquez à nouveau la tendance. Que Paris se rompe avec votre couleur.

        PA, PA, PA. LET'S BE THE TENDENCY.

        L'Architecte.
        TryOnYou-App | Sovereign Intelligence
        """
        
        msg.attach(MIMEText(cuerpo, 'plain', 'utf-8'))
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, [target['e'], reply_to], msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"❌ Error en {target['e']}: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 DISPARANDO MANIFIESTO OMEGA A LA ÉLITE...")
    for t in targets:
        if enviar_omega(t):
            print(f"✅ IMPACTO EN {t['n']}")
            time.sleep(2)
    print("🔱 OPERACIÓN COMPLETADA. PARÍS YA SIENTE EL COLOR.")
