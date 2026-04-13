"""
Live It Engine — Motor de ventas LVT (Live It) para TryOnYou V10.

Cruza el Avatar 3D real del usuario con prendas de la colección Live It
y valida la compra cuando el ajuste supera el umbral de precisión estándar LVT.

Patente: PCT/EP2025/067317
SIREN: 943 610 196
"""

from __future__ import annotations

from typing import Any

# Umbral de ajuste biométrico requerido por el estándar LVT
LVT_PRECISION_THRESHOLD = 0.98


class LiveItSales:
    """Motor de validación y venta de prendas Live It (LVT)."""

    def __init__(self, stock_ref: Any) -> None:
        """
        Args:
            stock_ref: Conexión a las colecciones LVT (inventario de prendas).
        """
        self.stock = stock_ref

    def validate_purchase(self, user_avatar: Any, garment_id: str) -> dict[str, Any]:
        """
        Cruza el Avatar 3D real con la prenda de Live It.

        Si el ajuste biométrico supera el umbral LVT estándar (0.98),
        el pago queda listo para procesarse.

        Args:
            user_avatar: Objeto Avatar 3D del usuario con método ``matches``.
            garment_id:  Identificador de la prenda en el catálogo LVT.

        Returns:
            Diccionario con:
              - status: «READY_FOR_PAYOUT» si el ajuste es perfecto,
                        «FIT_ADJUSTMENT_REQUIRED» en caso contrario.
              - url:    URL de checkout (solo cuando el estado es READY_FOR_PAYOUT).
        """
        if user_avatar.matches(garment_id, precision=LVT_PRECISION_THRESHOLD):
            return {"status": "READY_FOR_PAYOUT", "url": "/checkout"}
        return {"status": "FIT_ADJUSTMENT_REQUIRED"}
