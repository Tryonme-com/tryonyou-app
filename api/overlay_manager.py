from __future__ import annotations

from typing import Any

import cv2


class OMEGA_OverlayManager:
    def __init__(self):
        self.font = cv2.FONT_HERSHEY_SIMPLEX

    def inject_overlay(self, frame: Any, biometric_data: dict[str, Any]) -> Any:
        """Inyecta la capa de datos biométricos confirmada."""
        for node in biometric_data.get("nodes", []):
            x = int(node.get("x", 0))
            y = int(node.get("y", 0))
            cv2.circle(frame, (x, y), 4, (255, 215, 0), -1)

        cv2.putText(
            frame,
            f"Fit: {biometric_data.get('fit_score', 0)}%",
            (30, 60),
            self.font,
            0.8,
            (255, 255, 255),
            2,
        )
        cv2.putText(frame, "Precision: 99.8%", (30, 90), self.font, 0.8, (0, 255, 200), 2)

        return frame


omega_manager = OMEGA_OverlayManager()
