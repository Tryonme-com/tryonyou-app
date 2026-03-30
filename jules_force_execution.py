"""
Notificación Jules vía Slack (sin Gmail/SMTP).

  SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
  python3 jules_force_execution.py destinatario_ref@interno

Patente: PCT/EP2025/067317
"""
from __future__ import annotations

import argparse
import os
import sys

from divineo_slack import slack_post


class JulesForceExecution:
    def __init__(self) -> None:
        self.patente = "PCT/EP2025/067317"
        self.v10_4 = "V10.4 Stealth Edition"

    def disparar_prueba_real(self, destinatario: str) -> int:
        destinatario = destinatario.strip()
        if not destinatario:
            print("❌ Falta destinatario (referencia interna / canal).", file=sys.stderr)
            return 2
        if not os.environ.get("SLACK_WEBHOOK_URL", "").strip():
            print("❌ Define SLACK_WEBHOOK_URL.", file=sys.stderr)
            return 2

        contenido = (
            f"*Jules Force Execution* — ref. `{destinatario}`\n"
            f"EXPEDIENTE: TYY-2026-001 · VALIDADOR: Nicolas T. (Galeries Lafayette)\n"
            f"Patente: {self.patente} · {self.v10_4}\n"
            f"@CertezaAbsoluta @lo+erestu"
        )
        print(f"🔥 Jules: disparo Slack (ref. {destinatario})...")
        if slack_post(contenido):
            print("✅ Mensaje enviado a Slack.")
            return 0
        print("❌ Fallo webhook Slack.", file=sys.stderr)
        return 1


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Jules Force Execution — Slack únicamente.")
    p.add_argument("destinatario", help="Referencia interna (no SMTP)")
    args = p.parse_args(argv)
    return JulesForceExecution().disparar_prueba_real(args.destinatario)


if __name__ == "__main__":
    raise SystemExit(main())
