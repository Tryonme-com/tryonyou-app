from __future__ import annotations

from typing import Any

import cv2


class AR_Engine:
    """Motor de renderizado AR para la capa de visualización OMEGA."""

    def __init__(self, precision: float = 0.998):
        self.precision = precision
        self.color_gold = (0, 215, 255)
        self.color_bone = (245, 245, 245)

    def apply_biometric_overlay(
        self, frame: Any, nodes: list[dict[str, float]], fit_metrics: dict[str, float]
    ) -> Any:
        """Inyecta el overlay con los parámetros del protocolo OMEGA."""
        for node in nodes:
            x = int(node.get("x", 0))
            y = int(node.get("y", 0))
            cv2.circle(frame, (x, y), 4, self.color_gold, -1)

        text_fit = f"FIT SCORE: {fit_metrics.get('fit', 0)}%"
        text_prec = f"PRECISION: {self.precision * 100:.2f}%"

        cv2.putText(frame, text_fit, (50, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, self.color_bone, 2)
        cv2.putText(frame, text_prec, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, self.color_gold, 2)

        return frame


omega_ar = AR_Engine()
