"""
Envío SMTP opcional a contactos STATION F / programmes (solo con E50_SMTP_SEND=1).

Por defecto DRY-RUN: muestra destinatarios y no conecta. Evita disparos accidentales y spam.

Variables:
  EMAIL_USER / EMAIL_PASS (o E50_SMTP_USER / E50_SMTP_PASS)
  E50_SMTP_HOST (defecto smtp.gmail.com), E50_SMTP_PORT (587)
  E50_SMTP_SEND=1 para enviar de verdad
  E50_SMTP_TO_OVERRIDE=correo@tuyo.com  → un solo destinatario (prueba)

Responsabilidad del remitente: veracidad del contenido, opt-out, RGPD, políticas del destinatario.

Ejecutar: python3 asalto_station_f_jules.py
          E50_SMTP_SEND=1 python3 asalto_station_f_jules.py
"""

from __future__ import annotations

import os
import smtplib
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def _on(x: str) -> bool:
    return os.environ.get(x, "").strip().lower() in ("1", "true", "yes", "on")


def _cred() -> tuple[str, str]:
    user = (
        os.environ.get("EMAIL_USER", "").strip()
        or os.environ.get("E50_SMTP_USER", "").strip()
    )
    pwd = (
        os.environ.get("EMAIL_PASS", "").strip()
        or os.environ.get("E50_SMTP_PASS", "").strip()
    )
    return user, pwd


def asalto_station_f_jules() -> int:
    print("🚀 JULES: Flujo STATION F (SMTP con dry-run por defecto)...")

    sender_email, password = _cred()
    if not sender_email or not password:
        print("❌ Faltan EMAIL_USER/EMAIL_PASS (o E50_SMTP_USER/E50_SMTP_PASS).")
        return 1

    destinatarios: dict[str, str] = {
        "F/ai Program": "ai@stationf.co",
        "Fighters Program": "fighters@stationf.co",
        "LVMH La Maison": "contact@lamaisondesstartups.lvmh.com",
    }

    override = os.environ.get("E50_SMTP_TO_OVERRIDE", "").strip()
    if override:
        destinatarios = {"PRUEBA (override)": override}

    mensaje_fr = """
Objet : Candidature TryOnYou - Infrastructure Biométrique "Zéro Retour" (Brevet PCT/EP2025/067317)

À l'attention de l'équipe de STATION F,

Nous soumettons par la présente la candidature de TryOnYou pour intégrer votre écosystème d'innovation.

Alors que le retail de luxe à Paris perd plus de 400M€ par an en logistique de retours, notre infrastructure basée sur le "Double Numérique" et l'ajustement invisible réduit ce taux à moins de 2%.

Points clés :
1. Technologie : Algorithme biométrique propriétaire (33 points de précision).
2. Impact : Suppression de la "Loterie des Tailles" et réduction drastique de l'empreinte CO2.
3. Traction : +55% d'intérêt direct depuis les sièges sociaux à Paris (Natixis, LVMH).

Nous sommes prêts pour un déploiement immédiat.

Cordialement,

Jules Agent - Au nom de Rubén Espinar Rodríguez
TryOnYou France
"""

    host = os.environ.get("E50_SMTP_HOST", "smtp.gmail.com").strip()
    try:
        port = int(os.environ.get("E50_SMTP_PORT", "587").strip() or "587")
    except ValueError:
        port = 587

    if not _on("E50_SMTP_SEND"):
        print("ℹ️  DRY-RUN: no se envía nada. Exporta E50_SMTP_SEND=1 para enviar.")
        for programa, addr in destinatarios.items():
            print(f"   → {programa}: {addr}")
        print(f"   SMTP {host}:{port} · remitente {sender_email}")
        return 0

    try:
        with smtplib.SMTP(host, port, timeout=30) as server:
            server.starttls()
            server.login(sender_email, password)
            for programa, email_destino in destinatarios.items():
                msg = MIMEMultipart()
                msg["From"] = sender_email
                msg["To"] = email_destino
                msg["Subject"] = f"Candidature Stratégique TryOnYou - {programa}"
                msg.attach(MIMEText(mensaje_fr, "plain", "utf-8"))
                server.send_message(msg)
                print(f"✅ Enviado a: {programa} ({email_destino})")
        print("\n🔥 Envío SMTP terminado.")
        return 0
    except OSError as e:
        print(f"❌ Error de red/SMTP: {e}")
        return 1
    except smtplib.SMTPException as e:
        print(f"❌ Error SMTP: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(asalto_station_f_jules())
