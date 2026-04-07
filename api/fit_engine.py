"""
Fit Engine — Robert Engine physics: probabilidad de devolución por ajuste de prenda.

Calcula el riesgo de devolución a partir de la elasticidad del tejido y las
medidas corporales del usuario (protocolo Zero-Size).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


_SHOULDER_MULTIPLIER: float = 1.2
_TENSION_WEIGHT: float = 0.1
_MAX_RETURN_RISK: float = 0.95
_RISK_THRESHOLD: float = 0.3
_PERCENTAGE_DIVISOR: float = 100.0


@dataclass
class UserAnchors:
    """Puntos de anclaje biométrico del usuario (medidas internas del motor)."""

    shoulder_w: float  # Ancho de hombros en cm


def analyze_fit_return_risk(
    fabric: dict[str, Any],
    user_anchors: UserAnchors,
    garment_id: str,
) -> dict[str, Any]:
    """
    Calcula la probabilidad de devolución basada en la física del Robert Engine.

    Args:
        fabric: Diccionario con claves ``elasticityPct`` (>0–100) y
                ``recoveryPct`` (0–100) del tejido.
        user_anchors: Puntos de anclaje del usuario; requiere ``shoulder_w``
                      (ancho de hombros en cm).
        garment_id: Identificador único de la prenda.

    Returns:
        Diccionario con:
        - ``garment_id``: id de la prenda.
        - ``return_risk_pct``: riesgo de devolución de 0.00 a 95.00.
        - ``recommendation``: "Talla Correcta" o "Sugerir Talla Superior".

    Raises:
        ValueError: Si ``elasticityPct`` es 0 o negativo.
    """
    elasticity = float(fabric["elasticityPct"])
    if elasticity <= 0:
        raise ValueError("elasticityPct must be greater than zero")

    # Si la elasticidad es baja y el torso es ancho -> Riesgo Alto
    tension_factor = (user_anchors.shoulder_w * _SHOULDER_MULTIPLIER) / elasticity

    # Probabilidad de devolución (0.0 a 1.0)
    return_risk = min(
        _MAX_RETURN_RISK,
        (tension_factor * _TENSION_WEIGHT) + (1.0 - fabric["recoveryPct"] / _PERCENTAGE_DIVISOR),
    )

    return {
        "garment_id": garment_id,
        "return_risk_pct": round(return_risk * _PERCENTAGE_DIVISOR, 2),
        "recommendation": "Talla Correcta" if return_risk < _RISK_THRESHOLD else "Sugerir Talla Superior",
    }
