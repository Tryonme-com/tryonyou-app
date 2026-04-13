"""
Live It Engine — Validación de compra para colecciones LVT.

Cruza el Avatar 3D del usuario con la prenda de Live It y,
si el ajuste supera el umbral de precisión estándar LVT (0.98),
habilita el proceso de pago.

Patente: PCT/EP2025/067317
SIREN: 943 610 196
"""

from __future__ import annotations

from typing import Any


class LiveItSales:
    """Motor de ventas Live It — validación de ajuste sobre colecciones LVT."""

    #: Umbral de precisión estándar LVT para aprobar la compra.
    PRECISION_THRESHOLD: float = 0.98

    def __init__(self, stock_ref: Any) -> None:
        """
        Args:
            stock_ref: Conexión a las colecciones LVT (inventario / catálogo).
        """
        self.stock = stock_ref

    def validate_purchase(self, user_avatar: Any, garment_id: str) -> dict[str, str]:
        """
        Cruza el Avatar 3D real con la prenda de Live It.

        Si el ajuste es perfecto (estándar LVT, precisión ≥ 0.98),
        devuelve el estado ``READY_FOR_PAYOUT`` con la URL de checkout;
        en caso contrario solicita un ajuste de talla.

        Args:
            user_avatar: Objeto avatar del usuario con método ``matches``.
            garment_id:  Identificador de la prenda en el catálogo LVT.

        Returns:
            Diccionario con clave ``status`` y, opcionalmente, ``url``.
        """
        if user_avatar.matches(garment_id, precision=self.PRECISION_THRESHOLD):
            return {"status": "READY_FOR_PAYOUT", "url": "/checkout"}
        return {"status": "FIT_ADJUSTMENT_REQUIRED"}
