"""
Peacock_Core — integración TryOnYou V10 (sustituye nomenclatura heredada «EDL»).

Reglas:
  - Webhooks HTTP prohibidos hacia abvetos.com (activación de licencia interna / manual).
  - Presupuesto de latencia crítica Zero-Size (API / handshake): ver ZERO_SIZE_LATENCY_BUDGET_MS.
"""

from __future__ import annotations

from urllib.parse import urlparse

ZERO_SIZE_LATENCY_BUDGET_MS = 25

_FORBIDDEN_WEBHOOK_HOST_FRAGMENTS = ("abvetos.com",)


def is_webhook_destination_forbidden(url: str) -> bool:
    """True si la URL apunta a un host no permitido para webhooks salientes."""
    raw = (url or "").strip()
    if not raw:
        return False
    try:
        parsed = urlparse(raw)
        host = (parsed.netloc or "").lower()
        if not host and parsed.path.startswith("//"):
            host = urlparse("https:" + parsed.path).netloc.lower()
    except ValueError:
        return True
    if not host:
        return False
    for frag in _FORBIDDEN_WEBHOOK_HOST_FRAGMENTS:
        if frag in host:
            return True
    return False
