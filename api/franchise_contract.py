"""
FranchiseContract — Contrato de franquicia TryOnYou V10.

Define las condiciones económicas del punto de venta:
  - license_fee:           Fee mensual fijo por punto de venta
  - entry_fee:             Implementación inicial y algoritmo (pago único)
  - variable_commission:   5 % estándar sobre ventas en espejo

Patente: PCT/EP2025/067317
"""
from __future__ import annotations


class FranchiseContract:
    def __init__(self, shop_id: str, tier: str = "LUXURY_CARE") -> None:
        self.shop_id = shop_id
        self.tier = tier
        self.license_fee = 9900.0          # Fee mensual por punto de venta
        self.entry_fee = 100000.0          # Implementación inicial y algoritmo
        self.variable_commission = 0.05    # 5% estándar por venta en espejo

    def calculate_monthly_settlement(self, total_mirror_sales: float) -> dict:
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
