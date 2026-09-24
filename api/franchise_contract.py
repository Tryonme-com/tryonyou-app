"""
Franchise Contract — Contrato de franquicia Divineo V10.

Gestiona el cálculo de la liquidación mensual de comisiones para los nodos
franquiciados (p.ej. Galeries Lafayette, Balmain Flagship).

Estructura de comisión:
  - variable_commission : % sobre el precio de venta de cada artículo
  - fixed_fee           : cuota fija mensual del franquiciado
  - total_due           : suma total a liquidar

Patente: PCT/EP2025/067317
SIREN: 943 610 196
"""

from __future__ import annotations

from typing import Any

PATENTE = "PCT/EP2025/067317"
SIREN = "943 610 196"

# Tasas por defecto del contrato estándar Divineo V10
DEFAULT_VARIABLE_RATE: float = 0.15  # 15 % sobre el precio de venta
DEFAULT_FIXED_FEE: float = 100.0     # 100 € cuota fija mensual


class FranchiseContract:
    """Contrato de franquicia: cálculo de comisiones y liquidación mensual."""

    def __init__(
        self,
        variable_rate: float = DEFAULT_VARIABLE_RATE,
        fixed_fee: float = DEFAULT_FIXED_FEE,
        franchise_id: str = "DIVINEO-STANDARD",
    ) -> None:
        if not (0.0 <= variable_rate <= 1.0):
            raise ValueError(f"variable_rate must be between 0 and 1, got {variable_rate}")
        if fixed_fee < 0.0:
            raise ValueError(f"fixed_fee must be non-negative, got {fixed_fee}")
        self.variable_rate = variable_rate
        self.fixed_fee = fixed_fee
        self.franchise_id = franchise_id

    def calculate_monthly_settlement(self, item_price: float) -> dict[str, Any]:
        """
        Calcula la liquidación mensual para un artículo vendido.

        Args:
            item_price: Precio de venta del artículo (€).

        Returns:
            Diccionario con desglose de la liquidación:
              - item_price         : precio del artículo
              - variable_commission: comisión variable (rate × precio)
              - fixed_fee          : cuota fija mensual
              - total_due          : total a liquidar (variable + fija)
              - variable_rate      : tasa aplicada
              - franchise_id       : identificador del nodo franquiciado
              - legal              : referencia legal / patente
        """
        price = max(0.0, float(item_price))
        variable_commission = round(price * self.variable_rate, 2)
        total_due = round(variable_commission + self.fixed_fee, 2)

        return {
            "item_price": price,
            "variable_commission": variable_commission,
            "fixed_fee": self.fixed_fee,
            "total_due": total_due,
            "variable_rate": self.variable_rate,
            "franchise_id": self.franchise_id,
            "legal": f"PCT/EP2025/067317 · SIREN {SIREN}",
        }
