"""Divineo Standard — validación de calidad de imagen para el CEO."""

from __future__ import annotations

from enum import IntEnum


class ImageQuality(IntEnum):
    """Niveles de calidad de imagen ordenados de menor a mayor."""

    LOW = 1
    STANDARD = 2
    HIGH = 3
    PREMIUM = 4
    MASTERPIECE = 5


class ImageAsset:
    """Representa un recurso de imagen con un nivel de calidad asignado."""

    def __init__(self, quality: ImageQuality) -> None:
        self.quality = quality


def validate_divineo_standard(image_asset: ImageAsset) -> str:
    """Valida que el recurso de imagen alcance el nivel MASTERPIECE.

    Args:
        image_asset: El recurso de imagen a evaluar.

    Returns:
        Mensaje de aprobación si la calidad es MASTERPIECE.

    Raises:
        Exception: Si la calidad es inferior a MASTERPIECE.
    """
    if image_asset.quality < ImageQuality.MASTERPIECE:
        raise Exception("🚫 CALIDAD INSUFICIENTE PARA EL CEO. PURGANDO.")
    return "✅ Aprobado para el Búnker V11"
