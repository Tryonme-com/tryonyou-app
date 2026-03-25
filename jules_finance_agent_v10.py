"""
Envío SMTP (Gmail) de solicitud Bpifrance con adjunto(s).

  export EMAIL_USER='tu@gmail.com'
  export EMAIL_PASS='contraseña_de_aplicación'   # no la contraseña normal de Gmail
  export BPIFRANCE_TO_EMAIL='correo_verificado@bpifrance.fr'

  # opcional: simular sin enviar
  export JULES_FINANCE_DRY_RUN=1

  python3 jules_finance_agent_v10.py ruta/al/aviso_sirene.pdf
  python3 jules_finance_agent_v10.py doc1.pdf doc2.pdf

Patente: PCT/EP2025/067317 | SIRET: 94361019600017
"""

from __future__ import annotations

import argparse
import mimetypes
import os
import smtplib
import sys
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

SIRET = "94361019600017"
PATENTE = "PCT/EP2025/067317"
FOUNDER = "Rubén Espinar Rodríguez"


def _guess_mime(path: Path) -> tuple[str, str]:
    t, _ = mimetypes.guess_type(str(path))
    if t:
        main, _, sub = t.partition("/")
        if sub:
            return main, sub
    return "application", "octet-stream"


def _adjuntar(msg: MIMEMultipart, path: Path) -> None:
    if not path.is_file():
        raise FileNotFoundError(path)
    main, sub = _guess_mime(path)
    with path.open("rb") as f:
        part = MIMEBase(main, sub)
        part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        "attachment",
        filename=path.name,
    )
    msg.attach(part)


def ejecutar_envio(
    rutas_adjuntos: list[Path],
    *,
    dry_run: bool | None = None,
) -> int:
    email_user = os.getenv("EMAIL_USER", "").strip()
    email_pass = os.getenv("EMAIL_PASS", "").strip()
    target = os.getenv("BPIFRANCE_TO_EMAIL", "").strip()

    if dry_run is None:
        dry_run = os.getenv("JULES_FINANCE_DRY_RUN", "").strip() in (
            "1",
            "true",
            "yes",
        )

    print(f"🚀 [Jules finance]: protocolo envío SIRET {SIRET}…")

    if not email_user or not email_pass:
        print(
            "❌ Define EMAIL_USER y EMAIL_PASS (App Password Gmail).",
            file=sys.stderr,
        )
        return 1
    if not target:
        print(
            "❌ Define BPIFRANCE_TO_EMAIL con un correo oficial verificado con tu gestor.",
            file=sys.stderr,
        )
        return 1
    if not rutas_adjuntos:
        print("❌ Indica al menos un archivo adjunto.", file=sys.stderr)
        return 1

    msg = MIMEMultipart()
    msg["From"] = email_user
    msg["To"] = target
    cc = os.getenv("BPIFRANCE_CC_EMAIL", "").strip()
    if cc:
        msg["Cc"] = cc
    msg["Subject"] = (
        f"Demande d'avance / Bourse French Tech — TRYONYOU — SIRET {SIRET}"
    )

    cuerpo = f"""À l'attention de Bpifrance,

Je suis {FOUNDER}, fondateur de TRYONYOU SAS (SIRET {SIRET}).

Contexte (à adapter selon votre dossier réel) :
- Partenariat / pilote en cours avec Le Bon Marché (LVMH), références contractuelles en pièce jointe si applicable.
- Propriété intellectuelle : {PATENTE}.
- Besoin de trésorerie indicatif : 10 000 € pour continuité opérationnelle (infrastructure) avant l'échéance du 9 mai 2026.

Veuillez trouver ci-joint(s) le(s) document(s).

Cordialement,
{FOUNDER}
TRYONYOU SAS
"""

    msg.attach(MIMEText(cuerpo, "plain", "utf-8"))

    try:
        for p in rutas_adjuntos:
            _adjuntar(msg, p.resolve())
    except Exception as e:
        print(f"⚠️ Adjunto: {e}", file=sys.stderr)
        return 1

    if dry_run:
        print("ℹ️  JULES_FINANCE_DRY_RUN=1 — no se envía correo.")
        print(f"   Para: {target}")
        print(f"   Adjuntos: {[str(p) for p in rutas_adjuntos]}")
        return 0

    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=60) as server:
            server.starttls()
            server.login(email_user, email_pass)
            recipients = [target] + ([cc] if cc else [])
            server.send_message(msg, to_addrs=recipients)
        print("✅ Mensaje enviado.")
        return 0
    except Exception as e:
        print(f"❌ SMTP: {e}", file=sys.stderr)
        return 1


class JulesFinanceAgent:
    """Compatibilidad con el snippet original (usa env + BPIFRANCE_TO_EMAIL)."""

    def __init__(self) -> None:
        self.siret = SIRET

    def ejecutar_envio_autonomo(self, ruta_documento_sirene: str) -> int:
        return ejecutar_envio([Path(ruta_documento_sirene)])


def main() -> int:
    ap = argparse.ArgumentParser(description="Jules V10 — envío financiero (SMTP Gmail).")
    ap.add_argument(
        "adjuntos",
        nargs="+",
        type=Path,
        help="Rutas a PDF/imagen (avis SIRENE, proforma, etc.)",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Montar mensaje sin enviar (ignora JULES_FINANCE_DRY_RUN).",
    )
    args = ap.parse_args()
    return ejecutar_envio(
        list(args.adjuntos),
        dry_run=True if args.dry_run else None,
    )


if __name__ == "__main__":
    raise SystemExit(main())
