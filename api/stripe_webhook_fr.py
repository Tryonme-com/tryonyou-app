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
import urllib.parse
import urllib.request
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import stripe
from financial_guard import log_sovereignty_event
from stripe_fr_resolve import resolve_stripe_secret_fr, resolve_stripe_webhook_secret_fr

SUCCESS_PAYMENT_STATUSES = frozenset({"paid", "success", "succeeded", "payment_success"})


def _is_payment_success(payment_status: str) -> bool:
    return payment_status.strip().lower() in SUCCESS_PAYMENT_STATUSES


def _notify_hito2_blindado(
    session_id: str,
    payment_status: str,
    amount_eur: float,
) -> None:
    webhook_url = (
        os.getenv("JULES_SLACK_WEBHOOK_URL")
        or os.getenv("SLACK_WEBHOOK_URL")
        or os.getenv("MAKE_WEBHOOK_URL")
        or ""
    ).strip()
    if not webhook_url:
        log_sovereignty_event(
            event_type="hito2_notify_skipped",
            detail="no_webhook_configured",
            session_id=session_id,
            amount_eur=amount_eur,
        )
        return
    payload = {
        "event": "hito2_blindado",
        "status": "RESOLVED",
        "session_id": session_id,
        "payment_status": payment_status,
        "amount_eur": amount_eur,
        "message": "Hito 2: Blindado",
    }
    try:
        req = urllib.request.Request(
            webhook_url,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=8)
        log_sovereignty_event(
            event_type="hito2_notified",
            detail="channel=slack_or_make",
            session_id=session_id,
            amount_eur=amount_eur,
        )
    except Exception as exc:
        log_sovereignty_event(
            event_type="hito2_notify_error",
            detail=str(exc)[:300],
            session_id=session_id,
            amount_eur=amount_eur,
        )


def _persist_sovereignty_state(
    session_id: str,
    payment_status: str,
    amount_eur: float,
    metadata: dict,
) -> bool:
    """Persist SOUVERAINETÉ : 1 to Supabase after confirmed payment."""
    supabase_url = os.getenv("SUPABASE_URL", "")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    if not supabase_url or not supabase_key:
        log_sovereignty_event(
            event_type="sovereignty_persist_skipped",
            detail="supabase_not_configured",
            session_id=session_id,
        )
        return False
    users_table = (os.getenv("CORE_ENGINE_USERS_TABLE") or "users").strip() or "users"
    events_table = (os.getenv("CORE_ENGINE_EVENTS_TABLE") or "core_engine_events").strip() or "core_engine_events"
    try:
        status_patch = {"status": "SOUVERAINETÉ:1"}
        session_filter = urllib.parse.quote(session_id, safe="")
        patch_req = urllib.request.Request(
            f"{supabase_url}/rest/v1/{users_table}?session_id=eq.{session_filter}",
            data=json.dumps(status_patch).encode(),
            headers={
                "apikey": supabase_key,
                "Authorization": f"Bearer {supabase_key}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal",
            },
            method="PATCH",
        )
        urllib.request.urlopen(patch_req, timeout=8)
        row = {
            "session_id": session_id,
            "event_type": "payment_success",
            "payment_status": payment_status,
            "amount_eur": amount_eur,
            "sovereignty_level": 1,
            "metadata": json.dumps(metadata),
        }
        event_req = urllib.request.Request(
            f"{supabase_url}/rest/v1/{events_table}",
            data=json.dumps(row).encode(),
            headers={
                "apikey": supabase_key,
                "Authorization": f"Bearer {supabase_key}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal",
            },
            method="POST",
        )
        urllib.request.urlopen(event_req, timeout=8)
        log_sovereignty_event(
            event_type="sovereignty_persisted",
            detail=f"users_status_updated:SOUVERAINETÉ:1 status={payment_status}",
            session_id=session_id,
            amount_eur=amount_eur,
        )
        return True
    except Exception as exc:
        log_sovereignty_event(
            event_type="sovereignty_persist_error",
            detail=str(exc)[:300],
            session_id=session_id,
        )
        return False


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

        if _is_payment_success(payment_status):
            amount_eur = amount_total / 100.0 if amount_total else 0.0
            persisted = _persist_sovereignty_state(
                session_id=session_id,
                payment_status=payment_status,
                amount_eur=amount_eur,
                metadata=metadata,
            )
            if persisted:
                _notify_hito2_blindado(
                    session_id=session_id,
                    payment_status=payment_status,
                    amount_eur=amount_eur,
                )
        else:
            log_sovereignty_event(
                event_type="sovereignty_persist_skipped",
                detail=f"payment_not_success:{payment_status}",
                session_id=session_id,
                amount_eur=amount_total / 100.0 if amount_total else 0.0,
            )

    elif etype == "payment_intent.succeeded":
        intent_id = data.get("id", "")
        amount = data.get("amount", 0)
        currency = data.get("currency", "eur")
        metadata = data.get("metadata") or {}
        session_id = str(metadata.get("session_id") or intent_id or "")
        amount_eur = amount / 100.0 if amount else 0.0

        log_sovereignty_event(
            event_type="payment_intent_succeeded",
            detail=f"intent={intent_id} amount={amount} currency={currency}",
            session_id=session_id,
            amount_eur=amount_eur,
        )
        persisted = _persist_sovereignty_state(
            session_id=session_id,
            payment_status="succeeded",
            amount_eur=amount_eur,
            metadata=metadata,
        )
        if persisted:
            _notify_hito2_blindado(
                session_id=session_id,
                payment_status="succeeded",
                amount_eur=amount_eur,
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
