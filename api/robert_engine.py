"""
TRYONYOU — Robert Physics Engine (Python Core)
© 2025-2026 Rubén Espinar Rodríguez — All Rights Reserved
Patent: PCT/EP2025/067317 — 22 Claims Protected

Calcula las métricas de renderizado del overlay de prendas sobre el espejo
de Lafayette a partir de la volumetría biométrica detectada (sin solicitar
peso ni altura al usuario).
"""

from __future__ import annotations

import math
import time
from typing import Any

# Tejidos de la colección piloto (Lafayette Stirpe V10)
_PILOT_FABRIC_PHYSICS: dict[str, dict[str, float]] = {
    "silk_haussmann": {
        "drapeCoefficient": 0.85,   # Líquido
        "weightGSM": 60,            # Ligero
        "elasticityPct": 12,
        "frictionCoefficient": 0.22,  # Brillo seda
    },
    "business_elite": {
        "drapeCoefficient": 0.35,   # Rígido
        "weightGSM": 280,           # Pesado
        "elasticityPct": 4,
        "frictionCoefficient": 0.65,
    },
    "velvet_marais": {
        "drapeCoefficient": 0.60,
        "weightGSM": 180,
        "elasticityPct": 7,
        "frictionCoefficient": 0.48,
    },
    "linen_bastille": {
        "drapeCoefficient": 0.45,
        "weightGSM": 150,
        "elasticityPct": 5,
        "frictionCoefficient": 0.55,
    },
    "jersey_opera": {
        "drapeCoefficient": 0.70,
        "weightGSM": 110,
        "elasticityPct": 30,
        "frictionCoefficient": 0.38,
    },
}

PATENT_ID = "PCT/EP2025/067317"
_FIT_PERFECT_THRESHOLD = 95
_ALPHA_PERFECT = 0.95
_ALPHA_BASE = 0.85
_ALPHA_FLOOR = 0.65
_ALPHA_CEIL = 0.95
_GRAVITY_MAX_STRETCH = 0.15   # 15 % máximo según patente
_GSM_MIN = 50
_GSM_RANGE = 350
_LAFAYETTE_BASE = 2.2
_LAFAYETTE_OFFSET = 0.5
_DRAPE_PULL_FACTOR = 0.4
_PULSE_AMPLITUDE = 0.1
_PULSE_OMEGA = 0.002           # rad / ms


class RobertEngine:
    """Motor de física de tejidos para el overlay del Espejo de Lafayette."""

    def __init__(self) -> None:
        self.PILOT_FABRIC_PHYSICS: dict[str, dict[str, float]] = dict(
            _PILOT_FABRIC_PHYSICS
        )

    # ------------------------------------------------------------------
    # Cálculos individuales
    # ------------------------------------------------------------------

    def calculate_lafayette_factor(self, fabric: dict[str, Any]) -> float:
        """Calcula la amplitud de la silueta (Lafayette Factor)."""
        drape_pull = fabric["drapeCoefficient"] * _DRAPE_PULL_FACTOR
        return _LAFAYETTE_BASE + (_LAFAYETTE_OFFSET - drape_pull)

    def calculate_gravity_stretch(
        self, fabric: dict[str, Any], torso_h: float
    ) -> float:
        """Calcula cuánto estira la prenda por su peso (GSM).

        Devuelve la altura ajustada por gravedad en los mismos píxeles que
        *torso_h*.  El estiramiento máximo es del 15 % (patente).
        """
        weight_norm = min(
            1.0, max(0.0, (fabric["weightGSM"] - _GSM_MIN) / _GSM_RANGE)
        )
        return torso_h * (1.0 + (weight_norm * _GRAVITY_MAX_STRETCH))

    def calculate_dynamic_alpha(
        self,
        fit_score: float,
        fabric: dict[str, Any],
        timestamp: float | None = None,
    ) -> float:
        """Gestiona la transparencia y estabilización del tejido.

        Si el ajuste es perfecto (≥ 95 %), la prenda es más sólida.  Para
        ajustes inferiores se aplica un pulso de «respiración».
        """
        if timestamp is None:
            timestamp = time.time() * 1000

        base_alpha = _ALPHA_PERFECT if fit_score >= _FIT_PERFECT_THRESHOLD else _ALPHA_BASE

        pulse = 0.0
        if fit_score < _FIT_PERFECT_THRESHOLD:
            pulse = math.sin(timestamp * _PULSE_OMEGA) * _PULSE_AMPLITUDE

        return max(_ALPHA_FLOOR, min(_ALPHA_CEIL, base_alpha + pulse))

    # ------------------------------------------------------------------
    # API principal
    # ------------------------------------------------------------------

    def get_render_metrics(
        self,
        fabric_key: str,
        shoulder_w: float,
        torso_h: float,
        fit_score: float,
    ) -> dict[str, Any] | None:
        """Genera las métricas de renderizado para el overlay.

        Basado estrictamente en la volumetría detectada; no solicita peso
        ni altura al usuario.

        Returns ``None`` si *fabric_key* no existe en el catálogo.
        """
        fabric = self.PILOT_FABRIC_PHYSICS.get(fabric_key)
        if not fabric:
            return None

        # 1. Ajuste de anchura por caída (Lafayette Factor)
        lafayette_f = self.calculate_lafayette_factor(fabric)
        garment_w = shoulder_w * lafayette_f

        # 2. Ajuste de longitud por gravedad
        gravity_h = self.calculate_gravity_stretch(fabric, torso_h)

        # 3. Estado del escaneo (línea dorada invisible si fit < 95 %)
        is_recalculating = fit_score < _FIT_PERFECT_THRESHOLD

        # 4. Brillo de seda (Silk Highlight)
        is_shiny = fabric["frictionCoefficient"] < 0.35

        return {
            "width": garment_w,
            "height": gravity_h,
            "alpha": self.calculate_dynamic_alpha(fit_score, fabric),
            "is_shiny": is_shiny,
            "is_scanning": is_recalculating,
            "patent_id": PATENT_ID,
        }


# ---------------------------------------------------------------------------
# Ejemplo de uso (Soberanía V10)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    robert = RobertEngine()

    anchura_hombros_px = 450
    altura_torso_px = 800
    ajuste_actual = 88  # % de precisión del escaneo en el segundo 5

    metrics = robert.get_render_metrics(
        "silk_haussmann", anchura_hombros_px, altura_torso_px, ajuste_actual
    )

    print("--- ROBERT ENGINE OUTPUT ---")
    print(f"Anchura Renderizada: {metrics['width']}px")
    print(f"Altura (Gravity Stretch): {metrics['height']}px")
    print(f"Estado Escaneo: {'ACTIVO' if metrics['is_scanning'] else 'COMPLETO'}")
    print(f"Patente Verificada: {metrics['patent_id']}")
