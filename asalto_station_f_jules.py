"""
STATION F — avisos vía Slack (sin SMTP). Por defecto dry-run.

  SLACK_WEBHOOK_URL=...
  E50_SLACK_SEND=1 python3 asalto_station_f_jules.py

Patente ref.: PCT/EP2025/067317
"""

from __future__ import annotations

import os
import sys

from divineo_slack import slack_post


def _on(x: str) -> bool:
    return os.environ.get(x, "").strip().lower() in ("1", "true", "yes", "on")


def asalto_station_f_jules() -> int:
    print("🚀 JULES: Flujo STATION F (Slack, dry-run por defecto)...")

    destinatarios: dict[str, str] = {
        "F/ai Program": "ai@stationf.co",
        "Fighters Program": "fighters@stationf.co",
        "LVMH La Maison": "contact@lamaisondesstartups.lvmh.com",
    }

    mensaje_fr = """
Objet : Candidature TryOnYou - Infrastructure Biométrique "Zéro Retour" (Brevet PCT/EP2025/067317)

À l'attention de l'équipe de STATION F,

Nous soumettons par la présente la candidature de TryOnYou pour intégrer votre écosystème d'innovation.

Cordialement,
Jules Agent - Rubén Espinar Rodríguez
TryOnYou France
"""

    if not _on("E50_SLACK_SEND"):
        print("ℹ️  DRY-RUN: no Slack. Exporta E50_SLACK_SEND=1 para enviar.")
        for programa, addr in destinatarios.items():
            print(f"   → {programa}: {addr}")
        return 0

    if not os.environ.get("SLACK_WEBHOOK_URL", "").strip():
        print("❌ Define SLACK_WEBHOOK_URL.", file=sys.stderr)
        return 1

    bloque = "\n\n".join(
        f"*{programa}* (`{email}`)\n{mensaje_fr}" for programa, email in destinatarios.items()
    )
    if slack_post(bloque[:3500]):
        print("✅ Mensaje agregado a Slack (resumen STATION F).")
        return 0
    print("❌ Fallo Slack.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(asalto_station_f_jules())
