"""
Distribución soberana de payout (Agente 70) y precio Total Look Divineo.

- Reserva local, inversión BPI, proveedores/servidores y mantenimiento del sistema.
- Descuento Total Look: 30 % sobre el precio de referencia (factor0,70).

Patente PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import datetime
from typing import Any, Final

# Cuotas de execute_empire_distribution (suman 1,0)
_SHARE_LOCAL: Final[float] = 0.40
_SHARE_BPI: Final[float] = 0.25
_SHARE_SERVERS: Final[float] = 0.25
_SHARE_MAINTENANCE: Final[float] = 0.10

# Total Look Divineo: 30 % de descuento
_DIVINEO_TOTAL_LOOK_FACTOR: Final[float] = 0.70

# IVA por defecto (facturación Empire)
_DEFAULT_VAT_RATE: Final[float] = 0.21


def _empire_split_from_total(total_payout: float) -> dict[str, float]:
    if total_payout < 0:
        raise ValueError("total_payout no puede ser negativo")
    return {
        "LOCAL_RESERVE": total_payout * _SHARE_LOCAL,
        "BPI_INVESTMENT": total_payout * _SHARE_BPI,
        "SERVERS_PROVIDERS": total_payout * _SHARE_SERVERS,
        "SYSTEM_MAINTENANCE": total_payout * _SHARE_MAINTENANCE,
    }


def execute_empire_distribution(total_payout: float) -> dict[str, float]:
    """
    Auditoría Agente 70: blindaje del local y deuda de proveedores.

    `total_payout` debe ser >= 0 (misma unidad monetaria que el caller, p. ej. EUR).
    """
    distribution = _empire_split_from_total(total_payout)
    print(f"Fondos distribuidos (soberanía): {distribution}")
    return distribution


def apply_divineo_discount(price: float) -> float:
    """Activa el 30 % de descuento por Total Look (precio final =70 % del de entrada)."""
    if price < 0:
        raise ValueError("price no puede ser negativo")
    return price * _DIVINEO_TOTAL_LOOK_FACTOR


class EmpireBilling:
    """Facturación modo Empire: descuento Divineo Total, IVA y reparto soberano."""

    def __init__(
        self,
        tax_rate: float = _DEFAULT_VAT_RATE,
        *,
        discount_factor: float = _DIVINEO_TOTAL_LOOK_FACTOR,
    ) -> None:
        self.tax_rate = tax_rate
        self.discount_factor = discount_factor

    def generate_invoice(self, user_name: str, look_price: float) -> dict[str, Any]:
        if look_price < 0:
            raise ValueError("look_price no puede ser negativo")
        discounted_price = look_price * self.discount_factor
        total_with_tax = discounted_price * (1 + self.tax_rate)
        invoice_id = f"INV-{datetime.datetime.now().strftime('%Y%m%d%H%M')}"
        raw_splits = _empire_split_from_total(total_with_tax)
        funds_split = {k: round(v, 2) for k, v in raw_splits.items()}
        return {
            "invoice_id": invoice_id,
            "client": user_name,
            "base_price": look_price,
            "final_total": round(total_with_tax, 2),
            "splits": funds_split,
            "status": "PAID_STRIPE_OBK_195",
        }


if __name__ == "__main__":
    billing = EmpireBilling()
    factura_real = billing.generate_invoice("Alta Sociedad París", 2500)
    print(
        f"Factura generada: {factura_real['invoice_id']} - "
        f"Total: {factura_real['final_total']} EUR"
    )
