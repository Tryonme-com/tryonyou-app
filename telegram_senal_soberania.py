"""
Envía un mensaje a Telegram (plantilla TryOnYou V10). Sin secretos en código.

  export TELEGRAM_BOT_TOKEN='123456789:AAH...'   # BotFather (un solo ':'); o TELEGRAM_TOKEN
  export TELEGRAM_CHAT_ID='123456789'            # SOLO dígitos, o -100… grupo, o @canal
  # opcional:
  export TELEGRAM_FORMAT=markdown                # o plain (default)

  python3 telegram_senal_soberania.py

No concatenes nunca el token al chat_id. Si filtraste el token, revócalo en @BotFather.
"""

from __future__ import annotations

import os
import re
import sys
from datetime import datetime

import requests

PATENT = "PCT/EP2025/067317"
SIREN = "94361019600017"


def _credentials() -> tuple[str, str]:
    token = (
        os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
        or os.environ.get("TELEGRAM_TOKEN", "").strip()
    )
    chat = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    return token, chat


def _validate_chat_id(chat: str) -> str | None:
    """Devuelve mensaje de error o None si es válido."""
    if not chat:
        return "TELEGRAM_CHAT_ID vacío."
    if ":" in chat:
        return (
            "TELEGRAM_CHAT_ID no puede contener ':'. "
            "Parece que pegaste el TOKEN del bot junto al id. "
            "Token → TELEGRAM_BOT_TOKEN o TELEGRAM_TOKEN. Id → solo números (ej. "
            "123456789)."
        )
    if chat.startswith("@"):
        if re.fullmatch(r"@[A-Za-z0-9_]{5,}", chat):
            return None
        return "TELEGRAM_CHAT_ID tipo @usuario: formato sospechoso."
    if re.fullmatch(r"-?[0-9]+", chat):
        return None
    return (
        "TELEGRAM_CHAT_ID debe ser solo dígitos (ej. 123456789), "
        "o id de grupo/supergrupo (-100…), o @nombre público del canal."
    )


def _mensaje_plain() -> str:
    return (
        "TRYONYOU V10 — plantilla (verificar datos reales)\n"
        "------------------------------------------\n"
        "Estado: notificación manual\n"
        f"Patente: {PATENT}\n"
        f"Entidad (ref.): SIREN {SIREN}\n\n"
        "Orden de cobro (referencia operativa)\n"
        "• Canon de entrada: 100.000,00 €\n"
        "• Gastos de red: -2.000,00 €\n"
        "• Neto a liquidar (referencia 9 mayo): 98.000,00 €\n\n"
        f"Enviado: {datetime.now().isoformat(timespec='seconds')}"
    )


def _mensaje_markdown() -> str:
    """Modo Markdown clásico de Telegram (menos estricto que MarkdownV2)."""
    return (
        "🏛️ *TRYONYOU V10: PLANTILLA DE MENSAJE*\n"
        "------------------------------------------\n"
        "✅ *Estado:* notificación manual (verificar en sistemas reales)\n"
        f"📑 *Patente:* {PATENT}\n"
        f"🏢 *Entidad (ref.):* SIREN {SIREN}\n\n"
        "💰 *Referencia operativa: Le Bon Marché*\n"
        "• Canon de entrada: 100.000,00 €\n"
        "• Gastos de red: -2.000,00 €\n"
        "• *Neto a liquidar (ref. 9 mayo):* 98.000,00 €\n\n"
        f"_Enviado: {datetime.now().isoformat(timespec='seconds')}_"
    )


def enviar_senal_soberana() -> int:
    print(f"🚀 [{datetime.now().strftime('%H:%M:%S')}] Protocolo Telegram V10…")
    token, chat = _credentials()
    if not token or not chat:
        print(
            "❌ Define TELEGRAM_BOT_TOKEN (o TELEGRAM_TOKEN) y TELEGRAM_CHAT_ID.",
            file=sys.stderr,
        )
        return 1

    err = _validate_chat_id(chat)
    if err:
        print(f"❌ {err}", file=sys.stderr)
        return 1

    fmt = os.environ.get("TELEGRAM_FORMAT", "plain").strip().lower()
    if fmt == "markdown":
        text = _mensaje_markdown()
        parse_mode = "Markdown"
    else:
        text = _mensaje_plain()
        parse_mode = None

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload: dict = {"chat_id": chat, "text": text}
    if parse_mode:
        payload["parse_mode"] = parse_mode

    try:
        r = requests.post(url, json=payload, timeout=30)
        if r.status_code == 200:
            print("✅ Mensaje enviado.")
            return 0
        print(f"❌ HTTP {r.status_code}: {r.text[:400]}", file=sys.stderr)
    except requests.RequestException as e:
        print(f"❌ Red: {e}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(enviar_senal_soberana())
