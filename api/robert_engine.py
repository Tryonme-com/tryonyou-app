"""
TRYONYOU — Robert Physics Engine (Python Core)
© 2025-2026 Rubén Espinar Rodríguez — All Rights Reserved
Patent: PCT/EP2025/067317 — 22 Claims Protected

Motor de física de tejidos para el overlay de renderizado de prendas.
Calcula métricas de ancho, alto, alfa y brillo basándose estrictamente
en la volumetría detectada (sin solicitar peso ni talla al usuario).
"""

from __future__ import annotations

import math
import time

PATENT_ID = "PCT/EP2025/067317"

# Límites de normalización de peso (GSM)
_GSM_MIN = 50
_GSM_MAX = 400  # rango total: max - min = 350

# Estiramiento máximo por gravedad (según patente)
_MAX_GRAVITY_STRETCH = 0.15

# Umbrales de ajuste
_FIT_PERFECT_THRESHOLD = 95

# Coeficiente de fricción por debajo del cual se considera tejido brillante
_SHINY_FRICTION_THRESHOLD = 0.35

# Tejidos predefinidos de la colección piloto Lafayette
PILOT_FABRIC_PHYSICS: dict[str, dict] = {
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
        "weightGSM": 320,
        "elasticityPct": 6,
        "frictionCoefficient": 0.78,
    },
    "linen_rivoli": {
        "drapeCoefficient": 0.45,
        "weightGSM": 180,
        "elasticityPct": 8,
        "frictionCoefficient": 0.55,
    },
    "chiffon_opera": {
        "drapeCoefficient": 0.90,
        "weightGSM": 45,
        "elasticityPct": 15,
        "frictionCoefficient": 0.18,
    },
}


class RobertEngine:
    """Motor de física de tejidos del sistema TryOnYou V10.

    Calcula las métricas de renderizado del overlay (ancho, alto, alpha,
    brillo) a partir de la volumetría detectada por biometría, sin
    solicitar datos al usuario (peso/talla).
    """

    def __init__(self, fabric_physics: dict[str, dict] | None = None) -> None:
        self.PILOT_FABRIC_PHYSICS: dict[str, dict] = (
            fabric_physics if fabric_physics is not None else PILOT_FABRIC_PHYSICS
        )

    # ------------------------------------------------------------------
    # Cálculos de física
    # ------------------------------------------------------------------

    def calculate_lafayette_factor(self, fabric: dict) -> float:
        """Amplitud de silueta (Lafayette Factor).

        Devuelve un multiplicador de anchura basado en el coeficiente de
        caída del tejido.  Un tejido líquido (drape alto) produce una
        silueta más ceñida; uno rígido, más voluminosa.
        """
        drape_pull = fabric["drapeCoefficient"] * 0.4
        return 2.2 + (0.5 - drape_pull)

    def calculate_gravity_stretch(self, fabric: dict, torso_h: float) -> float:
        """Estiramiento longitudinal por gravedad según el peso del tejido (GSM).

        Normaliza el GSM en el rango [_GSM_MIN, _GSM_MIN + 350] y aplica
        un máximo del 15 % de estiramiento adicional (según patente).
        """
        weight_norm = min(
            1.0,
            max(0.0, (fabric["weightGSM"] - _GSM_MIN) / (_GSM_MAX - _GSM_MIN)),
        )
        return torso_h * (1.0 + weight_norm * _MAX_GRAVITY_STRETCH)

    def calculate_dynamic_alpha(
        self,
        fit_score: float,
        fabric: dict,
        timestamp: float | None = None,
    ) -> float:
        """Transparencia dinámica del tejido con efecto de «respiración».

        Si el ajuste es perfecto (≥ 95 %), la prenda aparece más sólida
        (alpha 0.95).  Por debajo de ese umbral se añade un pulso sinusoidal
        que simula el estado de recalibración del escaneo.
        """
        if timestamp is None:
            timestamp = time.time() * 1000

        base_alpha = 0.95 if fit_score >= _FIT_PERFECT_THRESHOLD else 0.85

        pulse = 0.0
        if fit_score < _FIT_PERFECT_THRESHOLD:
            pulse = math.sin(timestamp * 0.002) * 0.1

        return max(0.65, min(0.95, base_alpha + pulse))

    # ------------------------------------------------------------------
    # API principal
    # ------------------------------------------------------------------

    def get_render_metrics(
        self,
        fabric_key: str,
        shoulder_w: float,
        torso_h: float,
        fit_score: float,
    ) -> dict | None:
        """Genera las métricas de renderizado para el overlay.

        Parámetros
        ----------
        fabric_key:
            Clave del tejido en ``PILOT_FABRIC_PHYSICS``.
        shoulder_w:
            Anchura de hombros detectada por biometría (píxeles).
        torso_h:
            Altura del torso detectada por biometría (píxeles).
        fit_score:
            Porcentaje de precisión del escaneo actual (0–100).

        Devuelve un diccionario con las métricas de renderizado, o
        ``None`` si el tejido no existe.
        """
        fabric = self.PILOT_FABRIC_PHYSICS.get(fabric_key)
        if not fabric:
            return None

        # 1. Ajuste de anchura por caída (Lafayette Factor)
        lafayette_f = self.calculate_lafayette_factor(fabric)
        garment_w = shoulder_w * lafayette_f

        # 2. Ajuste de longitud por gravedad
        gravity_h = self.calculate_gravity_stretch(fabric, torso_h)

        # 3. Estado del escaneo (recalibrando si fit < 95 %)
        is_recalculating = fit_score < _FIT_PERFECT_THRESHOLD

        # 4. Brillo de seda (Silk Highlight)
        is_shiny = fabric["frictionCoefficient"] < _SHINY_FRICTION_THRESHOLD

        return {
            "width": garment_w,
            "height": gravity_h,
            "alpha": self.calculate_dynamic_alpha(fit_score, fabric),
            "is_shiny": is_shiny,
            "is_scanning": is_recalculating,
            "patent_id": PATENT_ID,
        }


# ---------------------------------------------------------------------------
# Demostración (espejo Lafayette — Soberanía V10)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    robert = RobertEngine()

    # Datos detectados por biometría (no preguntados al usuario)
    anchura_hombros_px = 450
    altura_torso_px = 800
    ajuste_actual = 88  # % de precisión en el segundo 5

    metrics = robert.get_render_metrics(
        "silk_haussmann", anchura_hombros_px, altura_torso_px, ajuste_actual
    )

    print("--- ROBERT ENGINE OUTPUT ---")
    print(f"Anchura Renderizada: {metrics['width']}px")
    print(f"Altura (Gravity Stretch): {metrics['height']}px")
    print(f"Estado Escaneo: {'ACTIVO' if metrics['is_scanning'] else 'COMPLETO'}")
    print(f"Patente Verificada: {metrics['patent_id']}")
