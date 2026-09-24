"""
Extrae el número de expediente (dossier) desde el último correo de Bpifrance en Gmail (IMAP).

Credenciales solo por entorno (nunca en el código):
  EMAIL_USER / EMAIL_PASS
  o E50_SMTP_USER / E50_SMTP_PASS (alias compat)

Opcional:
  IMAP_SERVER   (default: imap.gmail.com)
  IMAP_FOLDER   (default: INBOX)

  python3 extraer_expediente_bpifrance_imap.py
"""

from __future__ import annotations

import email
import imaplib
import os
import re
import sys

IMAP_SERVER = os.environ.get("IMAP_SERVER", "imap.gmail.com").strip()
IMAP_FOLDER = os.environ.get("IMAP_FOLDER", "INBOX").strip()


def _credentials() -> tuple[str, str]:
    user = (
        os.environ.get("EMAIL_USER", "").strip()
        or os.environ.get("E50_SMTP_USER", "").strip()
    )
    password = (
        os.environ.get("EMAIL_PASS", "").strip()
        or os.environ.get("E50_SMTP_PASS", "").strip()
    )
    return user, password


def _decode_part(part: email.message.Message) -> str:
    payload = part.get_payload(decode=True)
    if not payload:
        return ""
    charset = part.get_content_charset() or "utf-8"
    try:
        return payload.decode(charset, errors="replace")
    except LookupError:
        return payload.decode("utf-8", errors="replace")


def _message_plain_text(msg: email.message.Message) -> str:
    if msg.is_multipart():
        chunks: list[str] = []
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                chunks.append(_decode_part(part))
        return "\n".join(chunks)
    return _decode_part(msg)


def _find_dossier_number(body: str, subject: str) -> re.Match[str] | None:
    patterns = [
        r"Dossier\s+n[°ºo]\s*(\d+)",
        r"dossier\s+n[°ºo]\s*(\d+)",
        r"n[°ºo]\s*(\d{6,})",
        r"référence\s*:?\s*(\d{6,})",
        r"reference\s*:?\s*(\d{6,})",
    ]
    for pat in patterns:
        m = re.search(pat, body, re.IGNORECASE)
        if m:
            return m
    for pat in patterns:
        m = re.search(pat, subject or "", re.IGNORECASE)
        if m:
            return m
    return None


def extract_bpifrance_dossier() -> str | None:
    user, password = _credentials()
    if not user or not password:
        print(
            "❌ Faltan EMAIL_USER/EMAIL_PASS (o E50_SMTP_USER/E50_SMTP_PASS) en el entorno.",
            file=sys.stderr,
        )
        return None

    print("🚀 Conectando al nodo IMAP para sincronización Bpifrance...")
    mail: imaplib.IMAP4_SSL | None = None
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(user, password)
        mail.select(IMAP_FOLDER)

        status, messages = mail.search(None, '(FROM "bpifrance.fr")')
        if status != "OK" or not messages or not messages[0]:
            print("⚠️ No se encontraron correos de Bpifrance aún.")
            return None

        ids = messages[0].split()
        last_msg_id = ids[-1]
        res, msg_data = mail.fetch(last_msg_id, "(RFC822)")
        if res != "OK" or not msg_data:
            print("⚠️ No se pudo leer el último mensaje.")
            return None

        for response_part in msg_data:
            if not isinstance(response_part, tuple):
                continue
            msg = email.message_from_bytes(response_part[1])
            subject = msg.get("subject") or ""
            body = _message_plain_text(msg)
            match = _find_dossier_number(body, subject)
            if match:
                num_dossier = match.group(1)
                print(f"✅ Número de expediente hallado: {num_dossier}")
                print("📍 Estado sugerido: revisar cuerpo del correo en Gmail.")
                return num_dossier
            print("❌ Correo recibido pero sin número de expediente reconocible.")
            return None

        print("⚠️ Respuesta IMAP sin cuerpo RFC822 esperado.")
        return None
    except Exception as e:
        print(f"🔴 Error en la conexión: {e}", file=sys.stderr)
        return None
    finally:
        if mail is not None:
            try:
                mail.close()
            except Exception:
                pass
            try:
                mail.logout()
            except Exception:
                pass


if __name__ == "__main__":
    out = extract_bpifrance_dossier()
    sys.exit(0 if out else 1)
