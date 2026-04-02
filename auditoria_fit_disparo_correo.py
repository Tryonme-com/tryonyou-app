"""
Envía los borradores de auditoria_fit_borradores/ por SMTP (uno por archivo .txt).

Variables (o entradas equivalentes en .env en la raíz del repo):
  EMAIL_SMTP_HOST   (default: smtp.gmail.com)
  EMAIL_SMTP_PORT   (default: 587)
  EMAIL_USER o E50_SMTP_USER
  EMAIL_PASS o E50_SMTP_PASS
  EMAIL_FROM        (opcional; por defecto EMAIL_USER)

Prueba sin enviar:
  TRYONYOU_EMAIL_DRY_RUN=1 python3 auditoria_fit_disparo_correo.py

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import os
import smtplib
import sys
import time
from email.message import EmailMessage
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BORRADORES = ROOT / "auditoria_fit_borradores"
CTA_URL = "https://hook.eu2.make.com/9tlg80gj8sionvb191g40d7we9bj3ovn"


def _merge_dotenv() -> None:
    env_path = ROOT / ".env"
    if not env_path.is_file():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = val


def _smtp_creds() -> tuple[str, str, str, int, str]:
    host = os.environ.get("EMAIL_SMTP_HOST", "smtp.gmail.com").strip()
    port = int(os.environ.get("EMAIL_SMTP_PORT", "587") or "587")
    user = (
        os.environ.get("EMAIL_USER", "").strip()
        or os.environ.get("E50_SMTP_USER", "").strip()
    )
    password = (
        os.environ.get("EMAIL_PASS", "").strip()
        or os.environ.get("E50_SMTP_PASS", "").strip()
    )
    from_addr = os.environ.get("EMAIL_FROM", "").strip() or user
    return host, user, password, port, from_addr


def _parse_borrador(text: str) -> tuple[str | None, str, str]:
    head, sep, body = text.partition("\n---\n\n")
    if not sep:
        return None, "", text
    to_addr = None
    for line in head.splitlines():
        if line.lower().startswith("para:"):
            to_addr = line.split(":", 1)[1].strip()
            break
    body = body.strip()
    lines = body.split("\n")
    subject = "TryOnYou — Auditoría de Fit · 250 €"
    rest = body
    if lines and lines[0].lower().startswith("objet:"):
        subject = lines[0].split(":", 1)[1].strip()
        rest = "\n".join(lines[1:]).lstrip()

    bloque_cta = (
        "━━━ CTA — Réservation / paiement 250,00 € TTC ━━━\n"
        f"{CTA_URL}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    )
    rest = bloque_cta + rest
    if CTA_URL not in rest:
        rest += f"\n\n{CTA_URL}\n"
    return to_addr, subject, rest


def main() -> int:
    _merge_dotenv()
    dry = os.environ.get("TRYONYOU_EMAIL_DRY_RUN", "").strip() in ("1", "true", "yes")
    host, user, password, port, from_addr = _smtp_creds()

    if not BORRADORES.is_dir():
        print("❌ Falta carpeta auditoria_fit_borradores/", file=sys.stderr)
        return 2

    files = sorted(BORRADORES.glob("*.txt"))
    if not files:
        print("❌ No hay .txt en borradores.", file=sys.stderr)
        return 2

    if not user or not password:
        print(
            "❌ SMTP: define EMAIL_USER + EMAIL_PASS (o E50_SMTP_USER / E50_SMTP_PASS) en entorno o .env.",
            file=sys.stderr,
        )
        return 3

    enviados = 0
    for path in files:
        to_addr, subject, body = _parse_borrador(path.read_text(encoding="utf-8"))
        if not to_addr:
            print(f"⚠️  Sin Para: — {path.name}", file=sys.stderr)
            continue
        if dry:
            print(f"[DRY RUN] → {to_addr} | {subject[:60]}…")
            enviados += 1
            continue

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = from_addr
        msg["To"] = to_addr
        msg.set_content(body)

        with smtplib.SMTP(host, port, timeout=30) as s:
            s.starttls()
            s.login(user, password)
            s.send_message(msg)
        print(f"✅ Enviado → {to_addr}")
        enviados += 1
        time.sleep(2.0)

    print(f"Total procesados: {enviados}/{len(files)}")
    return 0 if enviados == len(files) else 4


if __name__ == "__main__":
    raise SystemExit(main())
