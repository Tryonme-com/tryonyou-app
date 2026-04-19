"""
Lafayette pilot — crea un PaymentIntent Stripe vinculado al piloto.
La clave secreta se lee de STRIPE_SECRET_KEY_FR (Paris) vía stripe_fr_resolve.
Cobro directo Connect: STRIPE_CONNECT_ACCOUNT_ID_FR=acct_…
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import stripe

from financial_guard import guard_stripe_call
from stripe_fr_resolve import resolve_stripe_secret_fr, stripe_api_call_kwargs

SIREN = "943 610 196"
PATENT = "PCT/EP2025/067317"
PLATFORM = "TryOnYou_V10"


def create_lafayette_checkout(session_id: str, amount_eur: float) -> str | None:
    """
    Crea un PaymentIntent vinculado al piloto de Lafayette.

    Args:
        session_id: Identificador único de la sesión (p.ej. "LAF-001").
        amount_eur: Importe en euros (p.ej. 175.50).

    Returns:
        client_secret del PaymentIntent, o None si ocurre un error.
    """
    sk = resolve_stripe_secret_fr()

    if not sk.startswith("sk_live_"):
        return None

    stripe.api_key = sk
    connect_kw = stripe_api_call_kwargs()

    payment_intent = guard_stripe_call(
        stripe.PaymentIntent.create,
        amount=int(amount_eur * 100),
        currency="eur",
        payment_method_types=["card"],
        metadata={
            "session_id": session_id,
            "project": "TryOnYou_Lafayette_Pilot",
            "status": "V10_Production",
            "billing_country_default": "FR",
            "siren": SIREN,
            "patent": PATENT,
            "platform": PLATFORM,
        },
        description=f"TryOnYou - Mirror Session {session_id}",
        **connect_kw,
    )
    return payment_intent.client_secret if payment_intent else None
