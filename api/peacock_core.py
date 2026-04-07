"""
Peacock_Core — integración TryOnYou V10 (sustituye nomenclatura heredada «EDL»).

Reglas:
  - Webhooks HTTP prohibidos hacia abvetos.com (activación de licencia interna / manual).
  - Presupuesto de latencia crítica Zero-Size (API / handshake): ver ZERO_SIZE_LATENCY_BUDGET_MS.
"""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

ZERO_SIZE_LATENCY_BUDGET_MS = 25

_FORBIDDEN_WEBHOOK_HOST_FRAGMENTS = ("abvetos.com",)

# Opacidad fija del bolso según robert-engine.ts
_ACCESSORY_ALPHA = 0.88


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


def get_accessory_metrics(
    img_ar: float,
    anchors: dict[str, Any],
    canvas_dim: dict[str, Any],
) -> dict[str, Any]:
    """
    Posicionamiento automático de bolsos basado en la cadera (HipY).
    Opacidad fija del 88% según robert-engine.ts

    Args:
        img_ar: Aspect ratio (height/width) de la imagen del bolso.
        anchors: Diccionario con claves 'cx', 'shoulderW', 'hipY' y 'hasBody'.
        canvas_dim: Diccionario con claves 'w' (ancho) y 'h' (alto) del canvas.

    Returns:
        Diccionario con posición (x, y), tamaño (w, h) y opacidad (alpha) del bolso.
    """
    cx: float = anchors["cx"]
    shoulder_w: float = anchors["shoulderW"]
    hip_y: float = anchors["hipY"]
    has_body: bool = anchors["hasBody"]

    # El bolso escala un 80% respecto al ancho de hombros
    bag_w: float = shoulder_w * 0.8 if has_body else canvas_dim["w"] * 0.18
    bag_h: float = bag_w * img_ar

    # Posicionamiento en el lado derecho de la cadera
    bag_x: float = cx + (shoulder_w * 0.6 if has_body else canvas_dim["w"] * 0.12)
    bag_y: float = hip_y - (bag_h * 0.3)

    return {
        "x": bag_x,
        "y": bag_y,
        "w": bag_w,
        "h": bag_h,
        "alpha": _ACCESSORY_ALPHA,
    }
