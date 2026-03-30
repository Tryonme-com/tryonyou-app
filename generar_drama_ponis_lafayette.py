"""Genera audio TTS via ElevenLabs. Requiere: pip install requests, env ELEVENLABS_API_KEY."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import requests

VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL")
OUTPUT_FILENAME = os.environ.get("ELEVENLABS_OUTPUT", "drama_ponis_lafayette.mp3")
MODEL_ID = os.environ.get("ELEVENLABS_MODEL", "eleven_multilingual_v2")

DRAMA_DEFAULT = (
    "En las Galeries Lafayette, el espejo no miente. "
    "Stirpe Lafayette: ponis de luz, protocolo V10 encendido."
)

URL = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"


def main() -> int:
    api_key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not api_key:
        print("Falta ELEVENLABS_API_KEY en el entorno.", file=sys.stderr)
        return 1

    if len(sys.argv) >= 2:
        text = Path(sys.argv[1]).read_text(encoding="utf-8").strip()
    else:
        text = DRAMA_DEFAULT.strip()

    if not text:
        print("El texto esta vacio.", file=sys.stderr)
        return 1

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key,
    }
    payload = {
        "text": text,
        "model_id": MODEL_ID,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.35,
            "use_speaker_boost": True,
        },
    }

    resp = requests.post(URL, headers=headers, data=json.dumps(payload), timeout=120)
    if not resp.ok:
        print(resp.status_code, resp.text[:2000], file=sys.stderr)
        return 1

    out = Path(OUTPUT_FILENAME)
    out.write_bytes(resp.content)
    print(f"OK -> {out.resolve()} ({len(resp.content)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
