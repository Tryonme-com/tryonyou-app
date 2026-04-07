"""
Robert Engine — simulation of fabric physical behaviour (TryOnYou V10).

Based on robert-engine.test.ts: models the natural elastic oscillation and the
drape waves (hem fall) of the garment over the user's silhouette.
"""

from __future__ import annotations

import math

# Breathing frequency (human rhythm, rad/ms)
BREATHING_FREQUENCY: float = 0.0015
# Scaling factor: elasticityPct → oscillation amplitude
ELASTICITY_AMPLITUDE_FACTOR: float = 0.0005
# Maximum drape wave amplitude in pixels
MAX_DRAPE_AMPLITUDE_PX: float = 6.0
# Drape wave frequency (rad/ms)
DRAPE_WAVE_FREQUENCY: float = 0.002


def calculate_elasticity_breathing(fabric: dict, timestamp: float) -> float:
    """
    Simulates the natural oscillation of elastic fabric.
    Based on robert-engine.test.ts

    Breathing frequency: 0.0015 (human rhythm)
    Amplitude based on the garment's elasticity percentage
    """
    amplitude = fabric['elasticityPct'] * ELASTICITY_AMPLITUDE_FACTOR
    oscillation = math.sin(timestamp * BREATHING_FREQUENCY) * amplitude
    return 1.0 + oscillation


def calculate_drape_wave(
    fabric: dict,
    timestamp: float,
    garment_w: float,
    num_points: int = 8,
) -> list[float]:
    """
    Generates the drape waves (hem fall) at the bottom of the garment.
    """
    waves: list[float] = []
    amplitude = fabric['drapeCoefficient'] * MAX_DRAPE_AMPLITUDE_PX
    for i in range(num_points):
        # Phase offset so that each wave point moves independently
        offset = i * (math.pi / num_points)
        wave = math.sin(timestamp * DRAPE_WAVE_FREQUENCY + offset) * amplitude
        waves.append(wave)
    return waves
