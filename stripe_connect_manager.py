"""
Stripe Connect Platform Manager — TryOnYou / Espejo Digital Soberano.

Gestiona cuentas Connect V2, onboarding y Destination Charges
para vendedores de la plataforma.

Bajo Protocolo de Soberanía V10 — Founder: Rubén Espinar Rodríguez
@CertezaAbsoluta @lo+erestu | Patente PCT/EP2025/067317
"""

from __future__ import annotations

import os
from typing import Optional

import stripe

STRIPE_API_KEY = os.getenv("STRIPE_SECRET_KEY", "")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

_test_mode = STRIPE_API_KEY.startswith("sk_test_")

stripe_client: Optional[stripe.StripeClient] = None
if STRIPE_API_KEY:
    stripe_client = stripe.StripeClient(STRIPE_API_KEY)


def _require_client() -> stripe.StripeClient:
    if stripe_client is None:
        raise RuntimeError(
            "STRIPE_SECRET_KEY no configurada. "
            "Define la variable de entorno antes de usar el manager."
        )
    return stripe_client


class TryOnYouManager:
    """Gestor de operaciones Stripe Connect para la plataforma TryOnYou."""

    def __init__(self, platform_fee_cents: int = 500):
        self.platform_fee_cents = platform_fee_cents

    def create_connected_account(self, email: str, name: str) -> str:
        """Crea una cuenta Stripe Connect V2 para un nuevo vendedor."""
        client = _require_client()
        try:
            account = client.v2.core.accounts.create(
                display_name=name,
                contact_email=email,
                identity={"country": "us"},
                dashboard="express",
                defaults={
                    "responsibilities": {
                        "fees_collector": "application",
                        "losses_collector": "application",
                    },
                },
                configuration={
                    "recipient": {
                        "capabilities": {
                            "stripe_balance": {
                                "stripe_transfers": {"requested": True},
                            },
                        },
                    },
                },
            )
            return account.id
        except Exception as e:
            raise RuntimeError(f"Error al crear cuenta Connect: {e}") from e

    def get_onboarding_link(self, account_id: str, return_url: str) -> str:
        """Genera el link de onboarding para que el vendedor complete su perfil."""
        client = _require_client()
        link = client.v2.core.account_links.create(
            account=account_id,
            use_case={
                "type": "account_onboarding",
                "account_onboarding": {
                    "configurations": ["recipient"],
                    "refresh_url": return_url,
                    "return_url": return_url,
                },
            },
        )
        return link.url

    def check_account_status(self, account_id: str) -> dict:
        """Verifica si la cuenta está lista para recibir transferencias."""
        client = _require_client()
        acc = client.v2.core.accounts.retrieve(
            account_id,
            params={"include": ["configuration.recipient", "requirements"]},
        )
        is_active = (
            acc.configuration.recipient.capabilities.stripe_balance.stripe_transfers.status
            == "active"
        )
        req_status = acc.requirements.summary.minimum_deadline.status
        is_onboarded = req_status not in ("currently_due", "past_due")

        return {
            "ready": is_active and is_onboarded,
            "transfers_active": is_active,
            "onboarded": is_onboarded,
            "status": "OPERATIVO" if is_active else "PENDIENTE",
        }

    def create_checkout_session(
        self,
        price_id: str,
        destination_account: str,
        success_url: str = "https://tryonyou.com/success",
        cancel_url: Optional[str] = None,
    ) -> str:
        """Crea una Checkout Session con Destination Charge y comisión de plataforma."""
        client = _require_client()
        params: dict = {
            "line_items": [{"price": price_id, "quantity": 1}],
            "payment_intent_data": {
                "application_fee_amount": self.platform_fee_cents,
                "transfer_data": {"destination": destination_account},
            },
            "mode": "payment",
            "success_url": success_url,
        }
        if cancel_url:
            params["cancel_url"] = cancel_url
        session = client.checkout.sessions.create(**params)
        return session.url


if __name__ == "__main__":
    if _test_mode:
        print("OPERANDO EN MODO TEST")

    manager = TryOnYouManager()
    print("Stripe Connect Manager listo para procesar pagos.")
