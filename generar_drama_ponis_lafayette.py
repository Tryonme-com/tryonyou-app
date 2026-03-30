"""
TTS vía ElevenLabs — genera drama_ponis_lafayette.mp3 (o nombre vía OUTPUT_FILENAME).

Uso:
  export ELEVENLABS_API_KEY="tu_clave_del_panel_elevenlabs"
  export DRAMA_PONIS_TEXT="Texto largo del drama…"  # opcional
  python3 generar_drama_ponis_lafayette.py

Variables opcionales: ELEVENLABS_VOICE_ID, OUTPUT_FILENAME, ELEVENLABS_MODEL_ID
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import requests

VOICE_ID_DEFAULT = "EXAVITQu4vr4xnSDxMaL"
OUTPUT_FILENAME_DEFAULT = "drama_ponis_lafayette.mp3"
MODEL_DEFAULT = "eleven_multilingual_v2"


def main() -> int:
    api_key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not api_key:
        print(
            "Define ELEVENLABS_API_KEY (clave del panel ElevenLabs, no Google).",
            file=sys.stderr,
        )
        return 1

    voice_id = os.environ.get("ELEVENLABS_VOICE_ID", VOICE_ID_DEFAULT).strip()
    output_name = os.environ.get("OUTPUT_FILENAME", OUTPUT_FILENAME_DEFAULT).strip()
    model_id = os.environ.get("ELEVENLABS_MODEL_ID", MODEL_DEFAULT).strip()
    text = os.environ.get(
        "DRAMA_PONIS_TEXT",
        "Drama Ponis Lafayette — sustituye este texto con DRAMA_PONIS_TEXT o edita aquí.",
    ).strip()
    if not text:
        print("DRAMA_PONIS_TEXT vacío.", file=sys.stderr)
        return 1

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key,
    }
    payload = {"text": text, "model_id": model_id}

    resp = requests.post(url, json=payload, headers=headers, timeout=180)
    if not resp.ok:
        print(resp.status_code, resp.text[:800], file=sys.stderr)
        return 2

    out_path = Path(output_name)
    out_path.write_bytes(resp.content)
    print(f"OK → {out_path.resolve()} ({len(resp.content)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
