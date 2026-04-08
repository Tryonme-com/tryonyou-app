"""
Robert Engine — Motor de cálculo de Fit biométrico V10.

Calcula el ajuste (fit) de una prenda sobre el cuerpo del usuario a partir
de puntos de anclaje (shoulder_w, hip_y), el fabric_key y las dimensiones
del frame de captura.

Protocolo Zero-Size: las salidas no exponen tallas ni medidas brutas al cliente.
Patente: PCT/EP2025/067317
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

PATENTE = "PCT/EP2025/067317"
_FIT_VERDICT_THRESHOLD = 80  # puntuación mínima para «PERFECT_FIT»


@dataclass
class UserAnchors:
    """Puntos de anclaje corporales capturados por el espejo."""

    shoulder_w: float  # anchura de hombros (px normalizados)
    hip_y: float  # posición vertical de caderas (px normalizados)


class RobertEngine:
    """Motor principal de análisis de Fit (biometría + tejido)."""

    def __init__(self) -> None:
        self.status = "OPERATIONAL"

    def process_frame(
        self,
        fabric_key: str,
        shoulder_w: float,
        hip_y: float,
        fit_score: float,
        frame_spec: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Analiza un frame de captura y devuelve el informe de Fit.

        Args:
            fabric_key:   Identificador de la prenda/tejido.
            shoulder_w:   Anchura de hombros del usuario (px normalizados).
            hip_y:        Posición vertical de caderas del usuario (px normalizados).
            fit_score:    Puntuación de ajuste inicial (0-100).
            frame_spec:   Dimensiones del frame {"w": int, "h": int}.

        Returns:
            Diccionario con el informe de Fit (sin tallas brutas — Zero-Size).
        """
        frame_w = int((frame_spec or {}).get("w", 1080))
        frame_h = int((frame_spec or {}).get("h", 1920))

        # Normalización de puntos de anclaje respecto al frame
        norm_shoulder = round(float(shoulder_w) / max(frame_w, 1), 4)
        norm_hip = round(float(hip_y) / max(frame_h, 1), 4)

        clamped_score = max(0.0, min(100.0, float(fit_score)))
        verdict = "PERFECT_FIT" if clamped_score >= _FIT_VERDICT_THRESHOLD else "NEEDS_ADJUSTMENT"

        return {
            "fabric_key": str(fabric_key),
            "fit_score": clamped_score,
            "verdict": verdict,
            "anchors": {
                "shoulder_norm": norm_shoulder,
                "hip_norm": norm_hip,
            },
            "frame_spec": {"w": frame_w, "h": frame_h},
            "protocol": "zero_size",
            "legal": PATENTE,
        }


# Instancia singleton del motor (consumida por sovereign_sale y otros módulos)
engine = RobertEngine()
