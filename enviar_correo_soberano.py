"""
Envío Soberano — SMTP Gmail con credenciales solo en entorno (nunca en el repo).

  export EMAIL_USER='ruben@tryonyou.app'
  export EMAIL_PASS='xxxx xxxx xxxx xxxx'   # App Password de Google
  # o E50_SMTP_USER / E50_SMTP_PASS
  # Opcional (p. ej. bloque Lafayette): SMTP_HOST, SMTP_PORT, REMITENTE

  python3 enviar_correo_soberano.py --dry-run
  python3 enviar_correo_soberano.py --printemps email@printemps.fr
  python3 enviar_correo_soberano.py --bon-marche email@lebonmarche.fr

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import argparse
import os
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def _merge_dotenv() -> None:
    """Carga claves desde .env de la raíz del repo sin sobreescribir variables ya definidas."""
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


def _creds() -> tuple[str, str]:
    user = (
        os.environ.get("EMAIL_USER", "").strip()
        or os.environ.get("E50_SMTP_USER", "").strip()
        or os.environ.get("FOUNDER_EMAIL", "").strip()
    )
    password = (
        os.environ.get("EMAIL_PASS", "").strip()
        or os.environ.get("E50_SMTP_PASS", "").strip()
    )
    return user, password


def _smtp_host_from_env() -> str:
    h = (os.environ.get("SMTP_HOST") or os.environ.get("E50_SMTP_HOST") or "").strip()
    return h or "smtp.gmail.com"


def _smtp_port_from_env() -> int:
    raw = (os.environ.get("SMTP_PORT") or os.environ.get("E50_SMTP_PORT") or "").strip() or "587"
    try:
        p = int(raw, 10)
        return p if p > 0 else 587
    except ValueError:
        return 587


def _remitente_from_env() -> str | None:
    r = (
        os.environ.get("REMITENTE", "").strip()
        or os.environ.get("EMAIL_FROM", "").strip()
        or os.environ.get("SMTP_FROM", "").strip()
    )
    return r or None


def cuerpo_printemps() -> str:
    return """\
Monsieur/Madame,

La technologie est un outil, mais l'honneur est la fondation.

Suite à la libération de l'exclusivité sur le code postal 75009, j'ai pris la décision de proposer notre technologie biométrique Zero-Size prioritairement au Printemps. Notre parole va au-dessus des chiffres, c'est pourquoi nous vous offrons les conditions originales du pilote (16 200 € TTC).

L'élégance commence par l'intégrité. Votre accès exclusif est prêt.

Cordialement,

Rubén Espinar Rodríguez
Chief Sovereign Architect (Google Studio)
"""


def cuerpo_bonmarche() -> str:
    return """\
Monsieur/Madame,

La classe et le luxe marchent main dans la main. De rien ne sert de porter du blanc si l'esprit n'est pas pur.

J'ai réservé pour Le Bon Marché une alliance de noblesse. Contrairement à d'autres, nous privilégions la "Palabra" et la caballerosité. Votre zone est prête au tarif privilège de 16 200 € TTC.

Bienvenue dans le futur de la mode souveraine.

Sincèrement,

Rubén Espinar Rodríguez
Architecte Souverain & Visionnaire
"""


def enviar_correo_soberano(
    destinatario: str,
    asunto: str,
    cuerpo: str,
    *,
    remitente: str | None = None,
    smtp_host: str | None = None,
    smtp_port: int | None = None,
    dry_run: bool = False,
) -> bool:
    user, password = _creds()
    host = (smtp_host if smtp_host is not None else _smtp_host_from_env()).strip()
    port = int(smtp_port) if smtp_port is not None else _smtp_port_from_env()
    from_addr = (remitente or _remitente_from_env() or user).strip()
    # SMTP LOGIN usa la cuenta real; el remitente en cabecera puede venir solo de `remitente`.
    login_user = (user or from_addr).strip()
    if not from_addr or not password or not login_user:
        print(
            "❌ Define EMAIL_USER + EMAIL_PASS (o E50_SMTP_*) (y remitente coherente con esa cuenta).",
            file=sys.stderr,
        )
        return False
    if dry_run:
        print(f"[DRY RUN] To: {destinatario}\nSubject: {asunto}\n---\n{cuerpo[:400]}…")
        return True

    msg = MIMEMultipart()
    msg["From"] = f"Rubén Espinar Rodríguez <{from_addr}>"
    msg["To"] = destinatario.strip()
    msg["Subject"] = asunto
    msg.attach(MIMEText(cuerpo, "plain", "utf-8"))

    try:
        with smtplib.SMTP(host, port, timeout=30) as server:
            server.starttls()
            server.login(login_user, password)
            server.sendmail(from_addr, [destinatario.strip()], msg.as_string())
    except (OSError, smtplib.SMTPException) as e:
        print(f"❌ Erreur technique du Búnker : {e}", file=sys.stderr)
        return False
    print(f"✅ Message de noblesse envoyé à : {destinatario}")
    return True


def main() -> int:
    _merge_dotenv()
    p = argparse.ArgumentParser(description="Envío soberano (Gmail App Password en env).")
    p.add_argument("--dry-run", action="store_true", help="No envía, solo muestra resumen")
    p.add_argument("--printemps", metavar="EMAIL", help="Destinatario Printemps 75009")
    p.add_argument("--bon-marche", metavar="EMAIL", help="Destinatario Le Bon Marché 75007")
    args = p.parse_args()

    if not args.printemps and not args.bon_marche:
        p.print_help()
        return 2

    ok = True
    if args.printemps:
        ok = enviar_correo_soberano(
            args.printemps,
            "Proposition d'Alliance Souveraine : 75009",
            cuerpo_printemps(),
            dry_run=args.dry_run,
        ) and ok
    if args.bon_marche:
        ok = enviar_correo_soberano(
            args.bon_marche,
            "Alliance de Noblesse : Zero-Size Biometrics",
            cuerpo_bonmarche(),
            dry_run=args.dry_run,
        ) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
