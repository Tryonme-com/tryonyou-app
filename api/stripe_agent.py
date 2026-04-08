"""
StripeAgent — gestión de catálogo y pagos para el proyecto de Espejo Digital.
"""

from __future__ import annotations

import os
from typing import Dict

import stripe


class StripeAgent:
    """
    Agente especializado en la gestión de catálogo y pagos para el
    proyecto de Espejo Digital.
    """

    def __init__(self, api_key: str) -> None:
        stripe.api_key = api_key
        self.version = "2026-04-08"

    def create_product_with_price(
        self, name: str, amount: int, currency: str = "eur"
    ) -> Dict:
        """
        Crea un producto y le asigna un precio unitario.
        amount: int (en céntimos, ej: 1000 = 10.00)
        """
        try:
            product = stripe.Product.create(name=name)
            price = stripe.Price.create(
                product=product.id,
                unit_amount=amount,
                currency=currency,
            )
            return {
                "status": "success",
                "product_id": product.id,
                "price_id": price.id,
                "name": name,
            }
        except stripe.error.StripeError as e:
            return {"status": "error", "message": str(e)}

    def list_recent_activity(self, limit: int = 5):
        """Lista los últimos productos para verificar sincronización."""
        return stripe.Product.list(limit=limit)


if __name__ == "__main__":
    STRIPE_SK = os.getenv("STRIPE_SECRET_KEY", "sk_test_tu_clave_aqui")
    agent = StripeAgent(STRIPE_SK)
    resultado = agent.create_product_with_price(
        name="Blazer Balmain Colección A/W",
        amount=145000,
    )
    print(f"Resultado de la operación: {resultado}")
