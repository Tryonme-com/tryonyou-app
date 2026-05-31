"""
Disparo soberano «inversores / Jules» — sin secretos en código.

Lee variables de entorno (Slack, Make, Telegram) y notifica si están configuradas.
No ejecuta git ni `git add .`.

Variables típicas (Jules / búnker):
  SLACK_WEBHOOK_URL, MAKE_WEBHOOK_URL, TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID,
  GITHUB_TOKEN (solo comprobación opcional de presencia)

Uso: python3 fatality_investors.py

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import os
import sys


def main() -> int:
    from divineo_slack import slack_post

    bits = [
        "FATALITY_INVESTORS — sello TryOnYou",
        f"SLACK_WEBHOOK_URL: {'ok' if os.getenv('SLACK_WEBHOOK_URL', '').strip() else 'vacío'}",
        f"MAKE_WEBHOOK_URL: {'ok' if os.getenv('MAKE_WEBHOOK_URL', '').strip() else 'vacío'}",
        f"TELEGRAM: {'ok' if (os.getenv('TELEGRAM_BOT_TOKEN') or os.getenv('TELEGRAM_TOKEN', '')).strip() else 'vacío'}",
        f"GITHUB_TOKEN: {'ok' if os.getenv('GITHUB_TOKEN', '').strip() else 'vacío'}",
    ]
    msg = "\n".join(bits)

    if slack_post(msg):
        print("Slack: enviado.")
    else:
        print("Slack: no configurado o fallo; mensaje en stdout:\n", msg)

    print("\nGit y push: manual y acotado (git_protocol_bunker_safe.py).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
