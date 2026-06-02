from __future__ import annotations

from typing import Any

from api.handlers.stripe_handlers import (
    handle_charge_refunded,
    handle_checkout_session_completed,
    handle_payment_intent_failed,
    handle_payment_intent_succeeded,
)
from api.models.decision import Decision
from api.providers.ai.router import run_ai_task


def execute_event_flow(decision: Decision, event: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    action = decision.action

    if action == "mark_order_paid":
        return handle_payment_intent_succeeded(event, context)

    if action == "mark_payment_failed":
        return handle_payment_intent_failed(event, context)

    if action == "activate_subscription":
        return handle_checkout_session_completed(event, context)

    if action == "handle_refund":
        return handle_charge_refunded(event, context)

    if action == "request_manual_review":
        return {
            "result": "manual_review_requested",
            "event_id": event.get("id"),
            "reason": decision.reason,
            "trace_id": context.get("trace_id"),
        }

    if action == "invoke_ai_enrichment":
        safe_payload = {
            "description": f"Event {event.get('id')} type {event.get('type')}",
            "summary_prompt": str(event.get("data", {}).get("object", {}).get("description", ""))[:500],
            "event_id": event.get("id"),
        }
        return run_ai_task("stripe_event_enrichment", safe_payload, provider=decision.provider)

    return {"result": "ignored", "event_id": event.get("id"), "trace_id": context.get("trace_id")}
