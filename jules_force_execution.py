import os
import ssl
import sys
from email.message import EmailMessage

import smtplib


class Jules_Force_Execution:
    def __init__(self):
        self.patente = "PCT/EP2025/067317"
        self.v10_4 = "V10.4 Stealth Edition"
        self.tu_email = os.getenv("GMAIL_USER", "").strip()
        self.app_password = os.getenv("GMAIL_APP_PASSWORD", "").strip()

    def disparar_prueba_real(self, destinatario: str) -> None:
        if not self.tu_email or not self.app_password:
            print(
                "❌ Define GMAIL_USER y GMAIL_APP_PASSWORD en el entorno "
                "(contraseña de aplicación de Google, no la contraseña normal)."
            )
            return

        destinatario = destinatario.strip()
        if not destinatario:
            print("❌ Falta destinatario.")
            return

        print(f"🔥 Jules: Iniciando Disparo Forzado a {destinatario}...")

        msg = EmailMessage()
        msg["Subject"] = "NOTIFICACIÓN ePCT: Regularización V10.4 - EXP TYY-2026-001"
        msg["From"] = self.tu_email
        msg["To"] = destinatario

        contenido = (
            f"EXPEDIENTE DE CUMPLIMIENTO: TYY-2026-001\n"
            f"VALIDADOR: Nicolas T. (Galeries Lafayette)\n"
            f"ENTIDAD: PRUEBA DE GALA DIVINEO\n"
            f"{'—' * 60}\n\n"
            f"Estimado/a,\n\n"
            f"Bajo la simetría técnica de la patente {self.patente}, notificamos la "
            f"regularización necesaria para habilitar la {self.v10_4}.\n\n"
            f"Este sistema asegura una experiencia sin complejos para el usuario "
            f"y una reducción drástica de devoluciones en el Cluster Haussmann.\n\n"
            f"Certeza absoluta junto a @CertezaAbsoluta @lo+erestu en el mensaje final.\n\n"
            f"Atentamente,\n\n"
            f"Paloma Lafayette\n"
            f"Mirror Sanctuary Orchestrator\n"
            f"P.A.U. Global Systems\n"
        )
        msg.set_content(contenido)

        context = ssl.create_default_context()

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(self.tu_email, self.app_password)
                server.send_message(msg)
            print("✅ ¡BOOM! Email enviado con éxito. Revisa la bandeja del destinatario.")
        except Exception as e:
            print(f"❌ Error en el Force-Mode: {e}")
            print("💡 Jules: Activa la contraseña de aplicación en la cuenta de Google.")


if __name__ == "__main__":
    dest = (sys.argv[1] if len(sys.argv) > 1 else os.getenv("JULES_TEST_DEST", "")).strip()
    if not dest:
        print(
            "⚠️  Uso: JULES_TEST_DEST=correo@ejemplo.com python3 jules_force_execution.py\n"
            "   o: python3 jules_force_execution.py correo@ejemplo.com\n"
            "   Credenciales: GMAIL_USER + GMAIL_APP_PASSWORD en el entorno."
        )
    else:
        Jules_Force_Execution().disparar_prueba_real(dest)
