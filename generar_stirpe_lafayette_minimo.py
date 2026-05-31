"""TTS ElevenLabs mínimo (Stirpe Lafayette). Sin claves en disco: ELEVENLABS_API_KEY en el entorno."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import requests

# Lily (Gemela Perfecta) — default Protocolo Soberanía V10 Omega
VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnNLTejx")
OUTPUT_FILENAME = os.environ.get("ELEVENLABS_OUTPUT", "drama_ponis_lafayette.mp3")
MODEL_ID = os.environ.get("ELEVENLABS_MODEL", "eleven_multilingual_v2")

# Protocolo de Soberanía V10 — defaults oficiales (ElevenLabs voice_settings)
V10_VOICE_SETTINGS = {
    "stability": 0.85,
    "similarity_boost": 0.9,
    "style": 0.1,
    "use_speaker_boost": True,
}

TEXTO_STIRPE = (
    "En las Galeries Lafayette, el espejo no miente. "
    "Stirpe Lafayette: ponis de luz, protocolo V10 encendido."
)

URL = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"


def _text_from_argv_or_default() -> str:
    """Si hay argv[1]: lee el fichero si existe; si no, usa el literal (texto en línea)."""
    if len(sys.argv) < 2:
        return TEXTO_STIRPE.strip()
    arg = sys.argv[1].strip()
    if not arg:
        return ""
    p = Path(arg)
    if p.is_file():
        return p.read_text(encoding="utf-8").strip()
    return arg


def main() -> int:
    api_key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not api_key:
        print("Falta ELEVENLABS_API_KEY en el entorno.", file=sys.stderr)
        return 1

    text = _text_from_argv_or_default()
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
        "voice_settings": V10_VOICE_SETTINGS,
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
