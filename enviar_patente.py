"""
Envío por SMTP del PDF de patente (Gmail + adjunto local).

Variables: EMAIL_USER, EMAIL_PASS (clave de aplicación, sin espacios en el valor real).
Opcional: DOSSIER_ABOGADO_TO (destinatario), PATENTE_PDF_PATH (ruta al PDF).

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import os
import smtplib
import sys
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parent / ".env")
except ImportError:
    pass

ROOT = Path(__file__).resolve().parent
USER = (os.environ.get("EMAIL_USER") or "").strip()
PASS = (os.environ.get("EMAIL_PASS") or "").strip().replace(" ", "")
DEST = (os.environ.get("DOSSIER_ABOGADO_TO") or "Contact@aubenard.fr").strip()
ARCHIVO = (os.environ.get("PATENTE_PDF_PATH") or "Patente_PCT_EP2025_067317.pdf").strip()
PDF_PATH = ROOT / ARCHIVO if not Path(ARCHIVO).is_absolute() else Path(ARCHIVO)


def main() -> int:
    if not USER or not PASS:
        print(
            "ERROR: Define EMAIL_USER y EMAIL_PASS en .env (clave de aplicación Gmail, 16 caracteres).",
            file=sys.stderr,
        )
        return 2

    if not PDF_PATH.is_file():
        print(f"ERROR: No existe el PDF: {PDF_PATH}", file=sys.stderr)
        return 1

    msg = MIMEMultipart()
    msg["From"] = USER
    msg["To"] = DEST
    msg["Subject"] = (
        "CERTIFICADO DE SOBERANÍA: Patente Real Presentada - PCT/EP2025/067317"
    )

    cuerpo = (
        "Estimado, adjunto la documentación oficial de la patente presentada "
        "para la liquidación de activos de TryOnYou-App."
    )
    msg.attach(MIMEText(cuerpo, "plain", "utf-8"))

    with PDF_PATH.open("rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        f"attachment; filename={PDF_PATH.name}",
    )
    msg.attach(part)
    print(f"Adjunto: {PDF_PATH.name}")

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=30)
        server.starttls()
        server.login(USER, PASS)
        server.send_message(msg)
        server.quit()
        print("OK: mensaje enviado.")
    except Exception as e:
        print(f"ERROR SMTP: {e}", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
