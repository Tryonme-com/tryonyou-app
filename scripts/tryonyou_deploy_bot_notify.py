#!/usr/bin/env python3
"""
Notificador oficial de despliegue TryOnYou (Telegram).

Uso:
  python3 scripts/tryonyou_deploy_bot_notify.py --message "✅ Despliegue OK"

Variables de entorno admitidas:
  - TRYONYOU_DEPLOY_BOT_TOKEN (prioritaria)
  - TELEGRAM_BOT_TOKEN / TELEGRAM_TOKEN (fallback)
  - TELEGRAM_CHAT_ID
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


def _resolve_token(cli_token: str | None) -> str:
    token = (cli_token or "").strip()
    if token:
        return "".join(token.split())
    env_token = (
        os.environ.get("TRYONYOU_DEPLOY_BOT_TOKEN", "").strip()
        or os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
        or os.environ.get("TELEGRAM_TOKEN", "").strip()
    )
    return "".join(env_token.split())


def _resolve_chat_id(cli_chat_id: str | None) -> str:
    chat_id = (cli_chat_id or "").strip()
    if chat_id:
        return chat_id
    return os.environ.get("TELEGRAM_CHAT_ID", "").strip() or "7868120279"


def send_message(*, token: str, chat_id: str, message: str) -> bool:
    if not token or not chat_id:
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps(
        {
            "chat_id": chat_id,
            "text": message,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            body = response.read().decode("utf-8", errors="replace")
            return response.status == 200 and '"ok":true' in body.replace(" ", "").lower()
    except (urllib.error.URLError, TimeoutError):
        return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Envía señal de despliegue al bot oficial de Telegram.")
    parser.add_argument("--message", required=True, help="Texto a enviar al chat.")
    parser.add_argument("--bot-token", default="", help="Token Telegram (opcional; fallback a entorno).")
    parser.add_argument("--chat-id", default="", help="Chat ID Telegram (opcional; fallback a entorno).")
    args = parser.parse_args(argv)

    token = _resolve_token(args.bot_token)
    chat_id = _resolve_chat_id(args.chat_id)
    if not token:
        print(
            "❌ Falta token Telegram. Define TRYONYOU_DEPLOY_BOT_TOKEN o TELEGRAM_BOT_TOKEN/TELEGRAM_TOKEN.",
            file=sys.stderr,
        )
        return 2
    if not chat_id:
        print("❌ Falta TELEGRAM_CHAT_ID (o --chat-id).", file=sys.stderr)
        return 2

    if send_message(token=token, chat_id=chat_id, message=args.message):
        print("✅ Notificación enviada al bot de despliegue.")
        return 0

    print("❌ No se pudo entregar la notificación en Telegram.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
