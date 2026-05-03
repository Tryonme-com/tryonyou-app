#!/usr/bin/env python3
"""
Envío de la lettre de justification Qonto (Support + Compliance) con registro JSONL.

  QONTO_LETTER_TO       destinatarios separados por coma (obligatorio para envío real)
  QONTO_LETTER_CC       opcional, coma-separado
  QONTO_LETTER_PATH     ruta al .md (default: LETTRE_QONTO_JUSTIFICATION_FONDS.md en raíz)

Credenciales SMTP: EMAIL_USER + EMAIL_PASS (ver sovereign_script_env / enviar_correo_soberano).

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import argparse
import json
import os
import smtplib
import sys
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
LOG_PATH = ROOT / "logs" / "qonto_compliance_mail.jsonl"
DEFAULT_LETTER = ROOT / "LETTRE_QONTO_JUSTIFICATION_FONDS.md"
DEFAULT_SUBJECT = "[TryOnYou V10] Justification trésorerie — Niveau 1 / Cadre F-2026-001"


def _load_env() -> None:
    for name in (".env.production", ".env"):
        p = ROOT / name
        if p.is_file():
            load_dotenv(p, override=False)


def _log_event(payload: dict) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(payload, ensure_ascii=False) + "\n"
    LOG_PATH.open("a", encoding="utf-8").write(line)


def _smtp_send(
    *,
    from_addr: str,
    to_addrs: list[str],
    cc_addrs: list[str],
    subject: str,
    body: str,
    user: str,
    password: str,
    host: str,
    port: int,
) -> None:
    msg = MIMEMultipart()
    msg["From"] = from_addr
    msg["To"] = ", ".join(to_addrs)
    if cc_addrs:
        msg["Cc"] = ", ".join(cc_addrs)
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))
    recipients = list(dict.fromkeys(to_addrs + cc_addrs))
    with smtplib.SMTP(host, port, timeout=45) as server:
        server.starttls()
        server.login(user, password)
        server.sendmail(from_addr, recipients, msg.as_string())


def main() -> int:
    _load_env()
    p = argparse.ArgumentParser(description="Carta Qonto Compliance — envío + log JSONL.")
    p.add_argument("--dry-run", action="store_true", help="No SMTP; solo log y stdout.")
    p.add_argument(
        "--letter-path",
        default=os.environ.get("QONTO_LETTER_PATH", str(DEFAULT_LETTER)),
        help="Ruta al markdown de la carta",
    )
    args = p.parse_args()

    letter_path = Path(args.letter_path)
    if not letter_path.is_file():
        print(f"No existe el fichero de carta: {letter_path}", file=sys.stderr)
        return 2

    body = letter_path.read_text(encoding="utf-8")
    subject = (os.environ.get("QONTO_LETTER_SUBJECT") or DEFAULT_SUBJECT).strip()

    raw_to = (os.environ.get("QONTO_LETTER_TO") or "").strip()
    to_list = [x.strip() for x in raw_to.split(",") if x.strip()]
    cc_raw = (os.environ.get("QONTO_LETTER_CC") or "").strip()
    cc_list = [x.strip() for x in cc_raw.split(",") if x.strip()]

    ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    if args.dry_run or not to_list:
        payload = {
            "event": "qonto_letter_dry_run",
            "subject": subject,
            "to": to_list or ["(non défini — définir QONTO_LETTER_TO pour envoi)"],
            "cc": cc_list,
            "body_chars": len(body),
            "letter_path": str(letter_path),
            "ts": ts,
        }
        _log_event(payload)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        if not args.dry_run and not to_list:
            print("Defina QONTO_LETTER_TO para envío real.", file=sys.stderr)
            return 2
        return 0

    user = (
        os.environ.get("EMAIL_USER", "").strip()
        or os.environ.get("E50_SMTP_USER", "").strip()
        or os.environ.get("FOUNDER_EMAIL", "").strip()
    )
    password = (
        os.environ.get("EMAIL_PASS", "").strip()
        or os.environ.get("E50_SMTP_PASS", "").strip()
    )
    if not user or not password:
        err = {"event": "qonto_letter_smtp_missing", "ts": ts, "subject": subject}
        _log_event(err)
        print("Faltan EMAIL_USER y EMAIL_PASS (o E50_*).", file=sys.stderr)
        return 2

    host = (os.environ.get("SMTP_HOST") or os.environ.get("EMAIL_SMTP_HOST") or "smtp.gmail.com").strip()
    try:
        port = int((os.environ.get("SMTP_PORT") or os.environ.get("EMAIL_SMTP_PORT") or "587").strip())
    except ValueError:
        port = 587
    from_addr = (
        (os.environ.get("REMITENTE") or os.environ.get("EMAIL_FROM") or "").strip() or user
    )

    try:
        _smtp_send(
            from_addr=from_addr,
            to_addrs=to_list,
            cc_addrs=cc_list,
            subject=subject,
            body=body,
            user=user,
            password=password,
            host=host,
            port=port,
        )
        ok = {
            "event": "qonto_letter_sent",
            "subject": subject,
            "to": to_list,
            "cc": cc_list,
            "smtp_host": host,
            "from": from_addr,
            "body_chars": len(body),
            "ts": ts,
        }
        _log_event(ok)
        print(json.dumps(ok, ensure_ascii=False, indent=2))
        return 0
    except (OSError, smtplib.SMTPException) as e:
        fail = {
            "event": "qonto_letter_smtp_error",
            "subject": subject,
            "to": to_list,
            "error": str(e)[:500],
            "ts": ts,
        }
        _log_event(fail)
        print(json.dumps(fail, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
