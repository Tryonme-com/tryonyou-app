import smtplib
from email.message import EmailMessage

remitente = "rubon.espinar.10@icloud.com"
destinatario = "relationfournisseur@galerieslafayette.com"
password = "TU_CONTRASEÑA_DE_APP" # REEMPLAZA ESTO

msg = EmailMessage()
msg['Subject'] = "URGENTE: Relance Facture F-2026-007 - TRYONYOU"
msg['From'] = remitente
msg['To'] = destinatario
msg['Cc'] = "rubon.espinar.10@icloud.com"

msg.set_content("""
Madame, Monsieur,

Sauf erreur de notre part, la facture F-2026-007 émise le 08/06/2026 pour un montant total de 39 888,00 € TTC n’a pas été réglée à ce jour, malgré l'échéance du 23/05/2026.

Nous vous prions de bien vouloir vérifier le statut de cette facture dans votre comptabilité. 

- Référence Facture : F-2026-007
- Bénéficiaire : EL - ESPINAR RODRIGUEZ RUBEN (TRYONYOU)
- Montant : 39 888,00 € TTC
- Référence de paiement : pi_3TjayHEo7sd7ud7H1xjkyyNY

Cordialement,

Rubén Espinar Rodríguez
CEO, TRYONYOU
""")

try:
    with open("F-2026-007.pdf", "rb") as f:
        msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename="F-2026-007.pdf")
    
    with smtplib.SMTP_SSL("smtp.mail.me.com", 465) as smtp:
        smtp.login(remitente, password)
        smtp.send_message(msg)
    print("Correo enviado con éxito.")
except Exception as e:
    print(f"Error al enviar: {e}")
