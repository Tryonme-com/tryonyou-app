"""
Referencias canónicas a Google AI Studio (URLs). Override: GOOGLE_AI_STUDIO_PROMPT_URL.
"""

from __future__ import annotations

import os

AI_STUDIO_ORIGIN = "https://aistudio.google.com"

# Prompt compartido (requiere sesión Google); sustituir por variable de entorno si cambia.
DEFAULT_PROMPT_URL = (
    "https://aistudio.google.com/prompts/1rOIfqf14rrodzJqQ37t2PH7yKa17t9tJ"
)


def prompt_url() -> str:
    return os.environ.get("GOOGLE_AI_STUDIO_PROMPT_URL", "").strip() or DEFAULT_PROMPT_URL


def studio_link_fields() -> dict[str, str]:
    """Claves para mezclar en STUDIO_SYNC.json / STUDIO_CONFIG.json."""
    return {
        "google_ai_studio_origin": AI_STUDIO_ORIGIN,
        "google_ai_studio_prompt_url": prompt_url(),
    }
