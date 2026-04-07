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

PILOT_COLLECTION: dict[str, dict[str, float]] = {
    "eg0": {  # Silk Haussmann
        "drapeCoefficient": 0.85,
        "weightGSM": 60,
        "elasticityPct": 12,
        "recoveryPct": 95,
        "frictionCoefficient": 0.22,
    },
    "eg1": {  # Business Elite (Cotton/Wool)
        "drapeCoefficient": 0.35,
        "weightGSM": 280,
        "elasticityPct": 4,
        "recoveryPct": 80,
        "frictionCoefficient": 0.65,
    },
    "eg2": {  # Velvet Night
        "drapeCoefficient": 0.55,
        "weightGSM": 320,
        "elasticityPct": 8,
        "recoveryPct": 88,
        "frictionCoefficient": 0.45,
    },
    "eg3": {  # Tech Shell
        "drapeCoefficient": 0.15,
        "weightGSM": 180,
        "elasticityPct": 2,
        "recoveryPct": 98,
        "frictionCoefficient": 0.75,
    },
    "eg4": {  # Cashmere Cloud
        "drapeCoefficient": 0.70,
        "weightGSM": 220,
        "elasticityPct": 15,
        "recoveryPct": 92,
        "frictionCoefficient": 0.30,
    },
}


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
