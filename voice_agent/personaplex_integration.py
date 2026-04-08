"""
Puente hacia NVIDIA PersonaPlex (speech-to-speech full-duplex, arquitectura Moshi).

PersonaPlex no sustituye el webhook Twilio half-duplex (Gather → /respond) sin un
gateway de audio en tiempo real: el repo oficial arranca `python -m moshi.server`,
requiere HF_TOKEN (licencia modelo en Hugging Face), Opus/libopus-dev y opcionalmente GPU.

Referencias: https://github.com/NVIDIA/personaplex

Variables de entorno (opcionales, solo si montas el servidor PersonaPlex aparte):
  HF_TOKEN / HUGGINGFACE_HUB_TOKEN — Hugging Face tras aceptar la licencia del modelo
  PERSONAPLEX_BASE_URL — URL interna del servidor Moshi (ej. https://host:8998)
  PERSONAPLEX_BRIDGE_WS_URL — WebSocket del proxy full-duplex (si existe)
  PERSONAPLEX_VOICE_PROMPT — pista de voz / NAT (default sugerido: NATF2.pt)

Este módulo solo expone estado para health checks y documentación operativa.

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import os
from typing import Any


def personaplex_duplex_status() -> dict[str, Any]:
    hf = (
        os.environ.get("HF_TOKEN", "").strip()
        or os.environ.get("HUGGINGFACE_HUB_TOKEN", "").strip()
    )
    base = os.environ.get("PERSONAPLEX_BASE_URL", "").strip().rstrip("/")
    bridge_ws = os.environ.get("PERSONAPLEX_BRIDGE_WS_URL", "").strip()
    voice = (
        os.environ.get("PERSONAPLEX_VOICE_PROMPT", "").strip() or "NATF2.pt"
    )
    return {
        "personaplex_hf_configured": bool(hf),
        "personaplex_server_configured": bool(base),
        "personaplex_base_url": base or None,
        "personaplex_bridge_ws_configured": bool(bridge_ws),
        "voice_prompt_default": voice,
        "twilio_voice_mode": "half_duplex_gather_redirect",
        "full_duplex_note": (
            "Full-duplex: NVIDIA/personaplex + moshi.server; ver README_PERSONAPLEX.md "
            "y .vercel/README.txt (Vercel no aloja GPU). Twilio: Media Streams o cliente Web."
        ),
    }
