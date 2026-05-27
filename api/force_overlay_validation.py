from __future__ import annotations

from typing import Any

import cv2
import numpy as np


def force_render_overlay(frame: Any) -> Any:
    """Inyección directa de prenda virtual para validación de capa AR."""
    overlay_mask = np.zeros_like(frame)
    cv2.rectangle(overlay_mask, (200, 300), (600, 700), (0, 215, 255), -1)
    alpha = 0.5
    return cv2.addWeighted(frame, 1.0, overlay_mask, alpha, 0)
