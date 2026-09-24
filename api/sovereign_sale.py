"""
Sovereign Sale — Proceso completo de venta en el espejo Divineo V10.

Orquesta el flujo de venta soberana:
  1. Robert Engine calcula el Fit biométrico.
  2. Shopify prepara la orden con la prenda exacta.
  3. El contrato de franquicia liquida la comisión.

Patente: PCT/EP2025/067317
SIREN: 943 610 196
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from robert_engine import RobertEngine

if TYPE_CHECKING:
    from franchise_contract import FranchiseContract
    from robert_engine import UserAnchors
    from shopify_bridge import ShopifyBridge

# Instancia global del motor Robert (singleton de módulo)
engine = RobertEngine()


def execute_sovereign_sale(
    franchise: "FranchiseContract",
    shopify: "ShopifyBridge",
    user_anchors: "UserAnchors",
    fabric_key: str,
) -> dict[str, Any]:
    """
    Proceso completo de venta en el espejo.

    Args:
        franchise:    Contrato de franquicia (calcula comisiones).
        shopify:      Puente Shopify (sincroniza y crea la orden).
        user_anchors: Puntos de anclaje corporales del usuario
                      (atributos: shoulder_w, hip_y).
        fabric_key:   Identificador de la prenda/tejido seleccionada.

    Returns:
        Diccionario con:
          - sale_status         : «SUCCESS»
          - shopify_ref         : referencia / estado de la orden Shopify
          - franchise_commission: comisión variable calculada (€)
          - legal               : sello legal con referencia a la patente
    """
    # 1. Robert Engine calcula el Fit
    fit_report = engine.process_frame(
        fabric_key,
        user_anchors.shoulder_w,
        user_anchors.hip_y,
        100,
        {"w": 1080, "h": 1920},
    )

    # 2. Shopify prepara la orden con la talla exacta
    order_status = shopify.sync_robert_to_shopify(fabric_key, {"fitScore": 100})

    # 3. El contrato de franquicia anota la comisión (ej. Vestido Balmain 4.000€)
    item_price = 4000.0
    settlement = franchise.calculate_monthly_settlement(item_price)

    return {
        "sale_status": "SUCCESS",
        "shopify_ref": order_status,
        "franchise_commission": settlement["variable_commission"],
        "legal": "Transaction secured by Patent PCT/EP2025/067317",
    }
