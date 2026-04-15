"""
Lafayette pilot — crea un PaymentIntent Stripe vinculado al piloto.
La clave secreta se lee de la variable de entorno STRIPE_SECRET_KEY
y debe ser sk_live_… (modo producción).

Every PaymentIntent includes SIREN 943 610 196 in metadata for legal
traceability (Stripe Support / Isabella).
"""

from __future__ import annotations

import os

import stripe
from lafayette_lockdown import sovereign_lock_state

SIREN = "943 610 196"
PATENT = "PCT/EP2025/067317"


def create_lafayette_checkout(session_id: str, amount_eur: float) -> str | None:
    """
    Crea un PaymentIntent vinculado al piloto de Lafayette.

    Args:
        session_id: Identificador único de la sesión (p.ej. "LAF-001").
        amount_eur: Importe en euros (p.ej. 175.50).

    Returns:
        client_secret del PaymentIntent, o None si ocurre un error.
    """
    lock = sovereign_lock_state()
    if lock["blocked"]:
        return None

    sk = (os.getenv("STRIPE_SECRET_KEY") or "").strip()

    if not sk.startswith("sk_live_"):
        return None

    stripe.api_key = sk

    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=int(amount_eur * 100),
            currency="eur",
            payment_method_types=["card"],
            metadata={
                "session_id": session_id,
                "project": "TryOnYou_Lafayette_Pilot",
                "status": "V10_Production",
                "siren": SIREN,
                "patent": PATENT,
                "platform": "TryOnYou_V10",
            },
            description=f"TryOnYou - Mirror Session {session_id}",
        )
        return payment_intent.client_secret
    except stripe.error.StripeError:
        return None
