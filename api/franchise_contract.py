"""
FranchiseContract — Contrato de franquicia TryOnYou (LUXURY_CARE tier).

Gestiona la liquidación mensual de cada punto de venta franquiciado:
  - Cuota fija mensual por licencia del espejo digital
  - Entrada única de implementación / algoritmo
  - Comisión variable sobre ventas en espejo

Patente: PCT/EP2025/067317
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""

from __future__ import annotations

from typing import Any


class FranchiseContract:
    """Representa el contrato de franquicia de un punto de venta."""

    def __init__(self, shop_id: str, tier: str = "LUXURY_CARE") -> None:
        self.shop_id = shop_id
        self.tier = tier
        self.license_fee: float = 9900.0       # Fee mensual por punto de venta
        self.entry_fee: float = 100000.0        # Implementación inicial y algoritmo
        self.variable_commission: float = 0.05  # 5 % estándar por venta en espejo

    def calculate_monthly_settlement(self, total_mirror_sales: float) -> dict[str, Any]:
        """Calcula el pago mensual de la franquicia."""
        commission_total = total_mirror_sales * self.variable_commission
        total_due = self.license_fee + commission_total

        return {
            "fixed_fee": self.license_fee,
            "variable_commission": commission_total,
            "total_to_invoice": total_due,
            "currency": "EUR",
            "patent_royalty": "Included (PCT/EP2025/067317)",
        }
