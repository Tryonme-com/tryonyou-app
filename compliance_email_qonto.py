#!/usr/bin/env python3
"""
Compliance Email — envoie la lettre de justification des fonds à Qonto.

Usage:
  python3 compliance_email_qonto.py --dry-run
  python3 compliance_email_qonto.py --send

Variables d'environnement (voir .env.example):
  EMAIL_USER, EMAIL_PASS (ou E50_SMTP_USER / E50_SMTP_PASS)
  SMTP_HOST (défaut smtp.gmail.com), SMTP_PORT (défaut 587)
  REMITENTE (optionnel, adresse From)
  QONTO_COMPLIANCE_EMAIL (optionnel, override destinataire)

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import smtplib
import sys
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LETTER_PATH = ROOT / "docs" / "financial" / "LETTRE_QONTO_JUSTIFICATION_FONDS.md"
LOG_PATH = ROOT / "logs" / "compliance_email_qonto.jsonl"

QONTO_DEFAULT_EMAILS = [
    "support@qonto.com",
    "compliance@qonto.com",
]

SUBJECT = (
    "JUST-QONTO-2026-05-001 — Justification des fonds — "
    "EI ESPINAR RODRIGUEZ SIRET 94361019600017"
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("compliance_email_qonto")


def _merge_dotenv() -> None:
    path = ROOT / ".env"
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = val


def _smtp_creds() -> tuple[str, str]:
    user = (
        os.environ.get("EMAIL_USER", "").strip()
        or os.environ.get("E50_SMTP_USER", "").strip()
    )
    pw = (
        os.environ.get("EMAIL_PASS", "").strip()
        or os.environ.get("E50_SMTP_PASS", "").strip()
    )
    return user, pw


def _smtp_host_port() -> tuple[str, int]:
    host = (
        os.environ.get("SMTP_HOST", "").strip()
        or os.environ.get("E50_SMTP_HOST", "").strip()
        or "smtp.gmail.com"
    )
    raw = (
        os.environ.get("SMTP_PORT", "").strip()
        or os.environ.get("E50_SMTP_PORT", "").strip()
    )
    port = 587
    if raw:
        try:
            port = int(raw)
        except ValueError:
            pass
    return host, port


def _remitente() -> str:
    return (
        os.environ.get("REMITENTE", "").strip()
        or os.environ.get("EMAIL_FROM", "").strip()
        or ""
    )


def _recipients() -> list[str]:
    override = os.environ.get("QONTO_COMPLIANCE_EMAIL", "").strip()
    if override:
        return [e.strip() for e in override.split(",") if e.strip()]
    return list(QONTO_DEFAULT_EMAILS)


def _load_letter() -> str:
    if not LETTER_PATH.is_file():
        raise FileNotFoundError(
            f"Lettre introuvable : {LETTER_PATH}\n"
            "Générez-la d'abord (docs/financial/LETTRE_QONTO_JUSTIFICATION_FONDS.md)."
        )
    return LETTER_PATH.read_text(encoding="utf-8")


def _build_body(letter_md: str) -> str:
    return (
        "Madame, Monsieur,\n\n"
        "Veuillez trouver ci-dessous la lettre de justification des fonds "
        "relative au compte EI ESPINAR RODRIGUEZ (SIRET 94361019600017).\n\n"
        "---\n\n"
        f"{letter_md}\n\n"
        "---\n\n"
        "Cordialement,\n"
        "Rubén Espinar Rodríguez\n"
        "Fondateur — TryOnYou / Divineo\n"
        "PCT/EP2025/067317\n"
    )


def _append_log(record: dict) -> None:
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError as e:
        logger.warning("Log write failed: %s", e)


def send_compliance_email(
    *,
    dry_run: bool = False,
) -> bool:
    letter_md = _load_letter()
    body = _build_body(letter_md)
    recipients = _recipients()
    user, password = _smtp_creds()
    from_addr = _remitente() or user
    host, port = _smtp_host_port()

    if not user:
        logger.error(
            "EMAIL_USER (o E50_SMTP_USER) non défini. "
            "Configurez les identifiants SMTP dans .env."
        )
        return False

    if dry_run:
        print(f"[DRY RUN] To: {', '.join(recipients)}")
        print(f"[DRY RUN] Subject: {SUBJECT}")
        print(f"[DRY RUN] From: {from_addr}")
        print(f"[DRY RUN] Body length: {len(body)} chars")
        print("---")
        print(body[:1500] + "…" if len(body) > 1500 else body)
        _append_log({
            "ts": datetime.now(timezone.utc).isoformat(),
            "action": "dry_run",
            "recipients": recipients,
            "subject": SUBJECT,
            "body_length": len(body),
        })
        return True

    if not password:
        logger.error(
            "EMAIL_PASS (o E50_SMTP_PASS) non défini. "
            "Impossible d'envoyer sans mot de passe SMTP."
        )
        return False

    all_ok = True
    for recipient in recipients:
        msg = MIMEMultipart()
        msg["From"] = f"Rubén Espinar Rodríguez <{from_addr}>"
        msg["To"] = recipient
        msg["Subject"] = SUBJECT
        msg["X-TryOnYou-Ref"] = "JUST-QONTO-2026-05-001"
        msg["X-Patent"] = "PCT/EP2025/067317"
        msg.attach(MIMEText(body, "plain", "utf-8"))

        try:
            with smtplib.SMTP(host, port, timeout=30) as server:
                server.starttls()
                server.login(user, password)
                server.sendmail(from_addr, [recipient], msg.as_string())
            logger.info("Email envoyé à %s", recipient)
            _append_log({
                "ts": datetime.now(timezone.utc).isoformat(),
                "action": "sent",
                "recipient": recipient,
                "subject": SUBJECT,
                "status": "ok",
            })
        except smtplib.SMTPAuthenticationError as e:
            code = getattr(e, "smtp_code", "?")
            logger.error(
                "Authentification SMTP refusée (%s). "
                "Vérifiez EMAIL_USER et le mot de passe d'application.",
                code,
            )
            _append_log({
                "ts": datetime.now(timezone.utc).isoformat(),
                "action": "auth_error",
                "recipient": recipient,
                "error": str(e)[:300],
            })
            all_ok = False
        except (OSError, smtplib.SMTPException) as e:
            logger.error("Erreur SMTP pour %s : %s", recipient, e)
            _append_log({
                "ts": datetime.now(timezone.utc).isoformat(),
                "action": "smtp_error",
                "recipient": recipient,
                "error": str(e)[:300],
            })
            all_ok = False

    return all_ok


def main() -> int:
    _merge_dotenv()
    parser = argparse.ArgumentParser(
        description=(
            "Envoie la lettre de justification des fonds à Qonto compliance. "
            "Requiert EMAIL_USER + EMAIL_PASS dans l'environnement."
        )
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Affiche le message sans l'envoyer",
    )
    parser.add_argument(
        "--send",
        action="store_true",
        help="Envoie effectivement l'email",
    )
    args = parser.parse_args()

    if not args.send and not args.dry_run:
        parser.print_help()
        print("\nSpécifiez --send ou --dry-run.")
        return 2

    ok = send_compliance_email(dry_run=args.dry_run)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
