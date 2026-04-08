"""
Protocolo Fatality — radar inversores vía SMTP (variables Jules / oficina).

Entorno (nunca hardcodear credenciales ni listas en código):
  OFFICE_EMAIL o EMAIL_USER
  OFFICE_PASS o EMAIL_PASS (contraseña de aplicación si Gmail)
  JULES_INVESTOR_EMAILS — correos separados por coma (ej. a@x.com,b@y.com)

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import os
import smtplib
import sys
from email.message import EmailMessage


def _sender_credentials() -> tuple[str, str]:
    user = (
        os.environ.get("OFFICE_EMAIL", "").strip()
        or os.environ.get("EMAIL_USER", "").strip()
    )
    pw = (
        os.environ.get("OFFICE_PASS", "").strip()
        or os.environ.get("EMAIL_PASS", "").strip()
    )
    return user, pw


def _targets() -> list[str]:
    raw = os.environ.get("JULES_INVESTOR_EMAILS", "").strip()
    if not raw:
        return []
    return [x.strip() for x in raw.split(",") if x.strip()]


def shoot_dossier_fatality() -> int:
    print("Fatality — protocolo inversores (TryOnYou / Zero-Size)")
    email_sender, email_pass = _sender_credentials()
    investors = _targets()
    if not email_sender or not email_pass:
        print(
            "Faltan OFFICE_EMAIL+OFFICE_PASS o EMAIL_USER+EMAIL_PASS.",
            file=sys.stderr,
        )
        return 1
    if not investors:
        print(
            "Define JULES_INVESTOR_EMAILS (lista separada por comas).",
            file=sys.stderr,
        )
        return 2

    smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com").strip()
    smtp_port = int(os.environ.get("SMTP_PORT", "465") or "465")
    use_ssl = smtp_port == 465

    for target in investors:
        msg = EmailMessage()
        msg["Subject"] = (
            "DEEPTECH: Protocolo Zero-Size / Piloto Lafayette (métricas bajo NDA)"
        )
        msg["From"] = email_sender
        msg["To"] = target
        msg.set_content(
            f"""Arquitecto / PAU — TryOnYou

Protocolo Zero-Size desplegado en tryonyou.app.
Patente: PCT/EP2025/067317.

Propuesta: reunión corta para números bajo NDA.

— Pau (Divineo V11)
"""
        )
        try:
            if use_ssl:
                with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=30) as smtp:
                    smtp.login(email_sender, email_pass)
                    smtp.send_message(msg)
            else:
                with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as smtp:
                    smtp.starttls()
                    smtp.login(email_sender, email_pass)
                    smtp.send_message(msg)
            print(f"OK — enviado a {target}")
        except OSError as e:
            print(f"Fallo SMTP {target}: {e}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(shoot_dossier_fatality())
