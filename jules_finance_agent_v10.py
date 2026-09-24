"""
Bpifrance / Jules — notificación vía Slack (sin adjuntos binarios por webhook estándar).

Lista rutas de documentos en el mensaje; sube PDFs a tu almacén seguro y pega enlaces si hace falta.

  SLACK_WEBHOOK_URL=...
  python3 jules_finance_agent_v10.py ruta/al/aviso_sirene.pdf
  JULES_FINANCE_DRY_RUN=1 python3 jules_finance_agent_v10.py doc.pdf

Patente: PCT/EP2025/067317 | SIRET: 94361019600017
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from divineo_slack import slack_post

SIRET = "94361019600017"
PATENTE = "PCT/EP2025/067317"
FOUNDER = "Rubén Espinar Rodríguez"


def ejecutar_envio(
    rutas_adjuntos: list[Path],
    *,
    dry_run: bool | None = None,
) -> int:
    if dry_run is None:
        dry_run = os.getenv("JULES_FINANCE_DRY_RUN", "").strip() in (
            "1",
            "true",
            "yes",
        )

    target_ref = os.getenv("BPIFRANCE_TO_EMAIL", "").strip() or "Bpifrance (referencia interna Slack)"

    print(f"🚀 [Jules finance]: protocolo SIRET {SIRET} (Slack)…")

    if not rutas_adjuntos:
        print("❌ Indica al menos un archivo (se nombrará en el mensaje Slack).", file=sys.stderr)
        return 1

    for p in rutas_adjuntos:
        if not p.is_file():
            print(f"❌ No existe: {p}", file=sys.stderr)
            return 1

    cuerpo = f"""À l'attention de Bpifrance (ref. {target_ref}),

Je suis {FOUNDER}, fondateur de TRYONYOU SAS (SIRET {SIRET}).

- PI : {PATENTE}
- Fichiers (chemins locaux listés pour traçabilité interne) :
{chr(10).join(f"  - {p.resolve()}" for p in rutas_adjuntos)}

Cordialement,
{FOUNDER}
"""

    if dry_run:
        print("ℹ️  JULES_FINANCE_DRY_RUN=1 — no Slack.")
        print(cuerpo[:1200])
        return 0

    if not os.environ.get("SLACK_WEBHOOK_URL", "").strip():
        print("❌ Define SLACK_WEBHOOK_URL.", file=sys.stderr)
        return 1

    if slack_post(f"*Jules Finance · Bpifrance*\n```\n{cuerpo[:2800]}\n```"):
        print("✅ Notificación enviada a Slack.")
        return 0
    print("❌ Fallo Slack.", file=sys.stderr)
    return 1


class JulesFinanceAgent:
    def __init__(self) -> None:
        self.siret = SIRET

    def ejecutar_envio_autonomo(self, ruta_documento_sirene: str) -> int:
        return ejecutar_envio([Path(ruta_documento_sirene)])


def main() -> int:
    ap = argparse.ArgumentParser(description="Jules V10 — notificación financière (Slack).")
    ap.add_argument(
        "adjuntos",
        nargs="+",
        type=Path,
        help="Rutas a PDF (solo se listan en Slack)",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Sin envío Slack.",
    )
    args = ap.parse_args()
    return ejecutar_envio(
        list(args.adjuntos),
        dry_run=True if args.dry_run else None,
    )


if __name__ == "__main__":
    raise SystemExit(main())
