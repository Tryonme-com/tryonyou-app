"""Registro de Order Commands seguras (Jules / Chambre de Commerce): MP3 Lily + JSON + Telegram opcional.

Entorno: ELEVENLABS_API_KEY, TELEGRAM_BOT_TOKEN (o TELEGRAM_TOKEN), TELEGRAM_CHAT_ID (nunca en código).
Patente: PCT/EP2025/067317
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

from telegram_env import get_telegram_bot_token, get_telegram_chat_id

ROOT = Path(__file__).resolve().parent
LOG_PATH = ROOT / "order_commands_log.json"
AUDIO_DIR = ROOT / "static" / "audio"

VOICE_LILY = os.environ.get("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnNLTejx")
MODEL_ID = os.environ.get("ELEVENLABS_MODEL", "eleven_multilingual_v2")
V10_VOICE = {
    "stability": 0.85,
    "similarity_boost": 0.9,
    "style": 0.1,
    "use_speaker_boost": True,
}

STATUS_DEFAULT = "BAJO PROTOCOLO V10 - SOBERANÍA TOTAL"
RCS_DEFAULT = os.environ.get("ORDER_CLIENT_RCS", "VERIFIED_FR_943610196")


def security_hash(payload_canonical: str) -> str:
    return hashlib.sha256(payload_canonical.encode("utf-8")).hexdigest()


def telegram_send(text: str) -> bool:
    token = get_telegram_bot_token()
    chat = get_telegram_chat_id()
    if not token or not chat:
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    r = requests.post(url, json={"chat_id": chat, "text": text[:4000]}, timeout=30)
    return r.ok


def synthesize_lily(text: str, out_path: Path, api_key: str) -> bool:
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_LILY}"
    headers = {
        "Accept": "audio/mpeg",
        "xi-api-key": api_key,
        "Content-Type": "application/json",
    }
    body = {"text": text, "model_id": MODEL_ID, "voice_settings": V10_VOICE}
    r = requests.post(url, headers=headers, data=json.dumps(body), timeout=120)
    if not r.ok:
        print(r.status_code, r.text[:500], file=sys.stderr)
        return False
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(r.content)
    return True


def load_log() -> dict:
    if not LOG_PATH.is_file():
        return {"entries": []}
    return json.loads(LOG_PATH.read_text(encoding="utf-8"))


def save_log(data: dict) -> None:
    LOG_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def safe_audio_name(order_id: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9_-]+", "_", order_id).strip("_") or "order"
    return f"lily_confirm_{s}.mp3"


def register_order(
    order_id: str,
    order_plaintext: str,
    *,
    client_rcs: str | None = None,
    status: str | None = None,
) -> dict:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rcs = client_rcs or RCS_DEFAULT
    stat = status or STATUS_DEFAULT
    canonical = f"{order_id}|{ts}|{rcs}|{order_plaintext}|{stat}"
    sec_hash = security_hash(canonical)
    rel_audio = f"static/audio/{safe_audio_name(order_id)}"
    abs_audio = ROOT / rel_audio

    entry = {
        "order_id": order_id,
        "timestamp": ts,
        "client_rcs": rcs,
        "audio_validation": rel_audio.replace("\\", "/"),
        "security_hash": sec_hash,
        "status": stat,
    }

    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not key:
        print("Falta ELEVENLABS_API_KEY para MP3.", file=sys.stderr)
        sys.exit(1)

    confirm_msg = (
        f"Orden segura validada. Jules y Chambre de Commerce. "
        f"Código {order_id}. Integridad {sec_hash[:16]}… Certeza absoluta."
    )
    if not synthesize_lily(confirm_msg, abs_audio, key):
        sys.exit(1)

    data = load_log()
    data.setdefault("entries", []).append(entry)
    save_log(data)

    mobile = (
        f"Niña Perfecta: orden sellada.\n{order_id}\nHash: {sec_hash[:12]}…\n{stat}\n@CertezaAbsoluta"
    )
    if telegram_send(mobile):
        entry["telegram_notified"] = True
    else:
        entry["telegram_notified"] = False

    save_log(data)
    return entry


def main() -> int:
    if len(sys.argv) < 3:
        print(
            "Uso: python3 registro_ordenes_seguras.py <order_id> <texto_orden> [--rcs RCS]",
            file=sys.stderr,
        )
        return 1
    oid = sys.argv[1].strip()
    text = sys.argv[2].strip()
    rcs = None
    if "--rcs" in sys.argv:
        i = sys.argv.index("--rcs")
        if i + 1 < len(sys.argv):
            rcs = sys.argv[i + 1].strip()
    if not oid or not text:
        return 1
    e = register_order(oid, text, client_rcs=rcs)
    print(json.dumps(e, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
