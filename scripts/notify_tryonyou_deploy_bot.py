#!/usr/bin/env python3
"""
Notificador Telegram para @tryonyou_deploy_bot.

Lee credenciales desde entorno y envia un reporte corto de estado:
  TRYONYOU_DEPLOY_BOT_TOKEN (o TELEGRAM_BOT_TOKEN / TELEGRAM_TOKEN)
  TRYONYOU_DEPLOY_CHAT_ID (o TELEGRAM_CHAT_ID)

Si no hay chat id explicito, intenta descubrirlo con getUpdates.
No imprime tokens en consola.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any

import requests


def _token() -> str:
    return (
        os.environ.get("TRYONYOU_DEPLOY_BOT_TOKEN", "").strip()
        or os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
        or os.environ.get("TELEGRAM_TOKEN", "").strip()
    )


def _chat_id_from_env() -> str:
    return (
        os.environ.get("TRYONYOU_DEPLOY_CHAT_ID", "").strip()
        or os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    )


def _discover_chat_id(token: str) -> str:
    """Busca el ultimo chat conocido via getUpdates."""
    try:
        r = requests.get(
            f"https://api.telegram.org/bot{token}/getUpdates",
            params={"limit": 50, "timeout": 0},
            timeout=25,
        )
        r.raise_for_status()
        data = r.json()
    except Exception:
        return ""

    if not data.get("ok"):
        return ""
    result = data.get("result", [])
    for item in reversed(result):
        for key in ("message", "edited_message", "channel_post"):
            payload = item.get(key) or {}
            chat = payload.get("chat") or {}
            chat_id = str(chat.get("id", "")).strip()
            if chat_id:
                return chat_id
    return ""


def _current_branch() -> str:
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return r.stdout.strip() or "unknown-branch"
    except Exception:
        return "unknown-branch"


def _build_text(event: str, status: str, detail: str) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    branch = _current_branch()
    chunks = [
        "TRYONYOU_DEPLOY_BOT",
        f"event={event}",
        f"status={status}",
        f"branch={branch}",
        f"time_utc={now}",
        f"detail={detail}",
        "patent=PCT/EP2025/067317",
    ]
    return "\n".join(chunks)


def _send_message(token: str, chat_id: str, text: str) -> tuple[bool, str]:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        r = requests.post(
            url,
            json={"chat_id": chat_id, "text": text},
            timeout=30,
        )
        if r.status_code == 200:
            return True, "ok"
        body = r.text[:280].replace("\n", " ")
        return False, f"http_{r.status_code}: {body}"
    except Exception as exc:
        return False, f"network_error: {exc}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Notifica estados al bot de despliegue.")
    parser.add_argument("--event", required=True, help="Nombre del evento.")
    parser.add_argument("--status", required=True, help="Estado: success|warning|error.")
    parser.add_argument("--detail", default="", help="Detalle corto del evento.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Muestra payload sin enviar a Telegram.",
    )
    args = parser.parse_args()

    token = _token()
    if not token:
        print("notify_tryonyou_deploy_bot: token ausente en entorno.", file=sys.stderr)
        return 2

    chat_id = _chat_id_from_env() or _discover_chat_id(token)
    if not chat_id:
        print(
            "notify_tryonyou_deploy_bot: chat_id ausente y no descubrible con getUpdates.",
            file=sys.stderr,
        )
        return 3

    text = _build_text(args.event, args.status, args.detail)
    if args.dry_run:
        print(json.dumps({"chat_id": chat_id, "text": text}, ensure_ascii=False, indent=2))
        return 0

    ok, reason = _send_message(token, chat_id, text)
    if not ok:
        print(f"notify_tryonyou_deploy_bot: envio fallido ({reason}).", file=sys.stderr)
        return 1

    print("notify_tryonyou_deploy_bot: enviado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
