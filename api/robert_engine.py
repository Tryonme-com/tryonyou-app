"""
Robert Engine — cálculo de pliegues verticales para simulación de tejido.
Basado en la lógica de renderizado de robert-engine.ts (TryOnYou V10).
"""

from __future__ import annotations

import math
from typing import Any


def get_drape_folds(
    fabric: dict[str, Any],
    garment_w: float,
    gravity_h: float,
    now_ms: float,
) -> list[dict[str, float]]:
    """
    Calcula la posición y opacidad de los pliegues verticales.
    Basado en la lógica de renderizado de robert-engine.ts

    Args:
        fabric:     Diccionario de propiedades del tejido.
                    Clave requerida: 'drapeCoefficient' (float, rango 0.0–1.0).
        garment_w:  Ancho de la prenda en píxeles (float).
        gravity_h:  Altura de caída gravitacional en píxeles (float).
        now_ms:     Tiempo actual en milisegundos (float), usado para la
                    animación sinusoidal de los pliegues.

    Returns:
        Lista de diccionarios, uno por pliegue, con las claves:
            - 'x'      (float): posición horizontal del pliegue.
            - 'width'  (float): ancho del pliegue (8 % de garment_w).
            - 'height' (float): alto del pliegue (70 % de gravity_h).
            - 'alpha'  (float): opacidad del pliegue.
    """
    num_folds = 3 if fabric['drapeCoefficient'] < 0.5 else 5
    folds = []

    for i in range(num_folds):
        # Movimiento sinusoidal sutil para simular aire/movimiento
        phase = i * (math.pi / num_folds)
        offset_x = math.sin(now_ms * 0.0015 + phase) * (5 * fabric['drapeCoefficient'])

        fold_x = (-garment_w / 3) + (i * (garment_w / (num_folds - 1))) + offset_x
        # La intensidad del pliegue depende de la caída (drape)
        opacity = 0.05 + (fabric['drapeCoefficient'] * 0.1)

        folds.append({
            "x": fold_x,
            "width": garment_w * 0.08,
            "height": gravity_h * 0.7,
            "alpha": opacity,
        })
    return folds
