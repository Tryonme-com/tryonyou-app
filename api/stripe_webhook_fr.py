"""
Webhook Stripe — firma con STRIPE_WEBHOOK_SECRET_FR (Dashboard cuenta Paris).

Configurar en Stripe Dashboard (cuenta verificada FR) la URL del despliegue, p. ej.:
 https://<tu-dominio>/api/stripe_webhook_fr

Eventos útiles: checkout.session.completed, payment_intent.succeeded (grandes importes).
Persiste estado SOUVERAINETÉ : 1 tras pago confirmado.

Patente: PCT/EP2025/067317
Protocolo de Soberanía V11 - Founder: Rubén
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import stripe
from financial_guard import log_sovereignty_event
from stripe_fr_resolve import resolve_stripe_secret_fr, resolve_stripe_webhook_secret_fr


def _persist_sovereignty_state(
    session_id: str,
    payment_status: str,
    amount_eur: float,
    metadata: dict,
) -> None:
    """Persist SOUVERAINETÉ : 1 to Supabase after confirmed payment."""
    supabase_url = os.getenv("SUPABASE_URL", "")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    if not supabase_url or not supabase_key:
        log_sovereignty_event(
            event_type="sovereignty_persist_skipped",
            detail="supabase_not_configured",
            session_id=session_id,
        )
        return
    try:
        row = {
            "session_id": session_id,
            "payment_status": payment_status,
            "amount_eur": amount_eur,
            "sovereignty_level": 1,
            "metadata": json.dumps(metadata),
        }
        req = urllib.request.Request(
            f"{supabase_url}/rest/v1/core_engine_events",
            data=json.dumps(row).encode(),
            headers={
                "apikey": supabase_key,
                "Authorization": f"Bearer {supabase_key}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal",
            },
            method="POST",
        )
        urllib.request.urlopen(req, timeout=8)
        log_sovereignty_event(
            event_type="sovereignty_persisted",
            detail=f"level=1 status={payment_status}",
            session_id=session_id,
            amount_eur=amount_eur,
        )
    except Exception as exc:
        log_sovereignty_event(
            event_type="sovereignty_persist_error",
            detail=str(exc)[:300],
            session_id=session_id,
        )


def process_stripe_webhook_event(event: dict) -> None:
    """Process Stripe webhook events. Persists SOUVERAINETÉ state on payment."""
    etype = event.get("type") or ""
    data = (event.get("data") or {}).get("object") or {}

    if etype == "checkout.session.completed":
        session_id = data.get("id", "")
        payment_status = data.get("payment_status", "")
        metadata = data.get("metadata") or {}
        amount_total = data.get("amount_total", 0)

        log_sovereignty_event(
            event_type="checkout_completed",
            detail=f"payment_status={payment_status} amount={amount_total}",
            session_id=session_id,
            amount_eur=amount_total / 100.0 if amount_total else 0.0,
        )

        _persist_sovereignty_state(
            session_id=session_id,
            payment_status=payment_status,
            amount_eur=amount_total / 100.0 if amount_total else 0.0,
            metadata=metadata,
        )

    elif etype == "payment_intent.succeeded":
        intent_id = data.get("id", "")
        amount = data.get("amount", 0)
        currency = data.get("currency", "eur")

        log_sovereignty_event(
            event_type="payment_intent_succeeded",
            detail=f"intent={intent_id} amount={amount} currency={currency}",
            session_id=intent_id,
            amount_eur=amount / 100.0 if amount else 0.0,
        )


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
        log_sovereignty_event(
            event_type="webhook_processing_error",
            detail=str(e)[:300],
        )
        return {"status": "error", "message": str(e)}, 500

    return {"status": "ok", "received": True, "type": event.get("type")}, 200
