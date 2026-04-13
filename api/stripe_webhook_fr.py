"""
Webhook Stripe — firma con STRIPE_WEBHOOK_SECRET_FR (Dashboard cuenta Paris).

Configurar en Stripe Dashboard (cuenta verificada FR) la URL del despliegue, p. ej.:
 https://<tu-dominio>/api/stripe_webhook_fr

Eventos útiles: checkout.session.completed, payment_intent.succeeded (grandes importes).
La persistencia en base de datos debe ampliarse según el modelo del proyecto.

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import stripe
from stripe_fr_resolve import resolve_stripe_secret_fr, resolve_stripe_webhook_secret_fr


def process_stripe_webhook_event(event: dict) -> None:
    """Extender aquí: actualizar órdenes / licencias tras pago confirmado."""
    etype = event.get("type") or ""
    data = (event.get("data") or {}).get("object") or {}
    if etype == "checkout.session.completed":
        _ = data.get("id"), data.get("payment_status"), data.get("metadata")
    elif etype == "payment_intent.succeeded":
        _ = data.get("id"), data.get("amount"), data.get("currency")


def handle_stripe_webhook_fr(raw_body: bytes, sig_header: str | None) -> tuple[dict, int]:
    wh = resolve_stripe_webhook_secret_fr()
    if not wh.startswith("whsec_"):
        return {
            "status": "error",
            "message": "stripe_webhook_secret_fr_required",
            "hint": "Define STRIPE_WEBHOOK_SECRET_FR (whsec_…) del endpoint en cuenta Paris.",
        }, 503

    sk = resolve_stripe_secret_fr()
    if sk:
        stripe.api_key = sk

    try:
        event = stripe.Webhook.construct_event(raw_body, sig_header or "", wh)
    except ValueError:
        return {"status": "error", "message": "invalid_payload"}, 400
    except stripe.error.SignatureVerificationError:
        return {"status": "error", "message": "invalid_signature"}, 400

    try:
        process_stripe_webhook_event(event)
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

    return {"status": "ok", "received": True, "type": event.get("type")}, 200
