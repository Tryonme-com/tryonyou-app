"""
Execution engine — dispatches to handlers and optional AI providers.

Receives a Decision and the event/context, calls the correct handler, and
optionally invokes AI enrichment if Decision.requires_ai is True.

AI failures are silently logged so they never block business logic.
"""
from __future__ import annotations

import logging
from typing import Any

from models.decision import Decision, EventAction
from handlers.stripe_handlers import (
    handle_payment_intent_succeeded,
    handle_payment_intent_failed,
    handle_checkout_session_completed,
    handle_charge_refunded,
    handle_unhandled_event,
)

logger = logging.getLogger(__name__)

# ── Handler dispatch ──────────────────────────────────────────────────────────

_HANDLERS = {
    EventAction.MARK_ORDER_PAID: handle_payment_intent_succeeded,
    EventAction.MARK_PAYMENT_FAILED: handle_payment_intent_failed,
    EventAction.ACTIVATE_SUBSCRIPTION: handle_checkout_session_completed,
    EventAction.HANDLE_REFUND: handle_charge_refunded,
    EventAction.IGNORE_EVENT: handle_unhandled_event,
}


def execute_event_flow(
    decision: Decision,
    event: dict[str, Any],
    context: dict[str, Any],
) -> dict[str, Any]:
    """
    Execute the action described by `decision`.

    Returns the handler result dict (at minimum {"ok": bool, "action": str}).
    Raises on unrecoverable failures; let the worker decide retry/DLQ.
    """
    action = decision.action
    event_id = event.get("id", "unknown")

    if action == EventAction.REQUEST_MANUAL_REVIEW:
        logger.error(
            "[execution] manual review required event_id=%s reason=%s",
            event_id, decision.reason,
        )
        return {"ok": False, "action": "request_manual_review", "retryable": False}

    handler = _HANDLERS.get(action, handle_unhandled_event)
    result = handler(event, context)

    if decision.requires_ai:
        _run_ai_optional(decision, event, context)

    return result


# ── AI enrichment (optional, non-blocking) ────────────────────────────────────

def _run_ai_optional(
    decision: Decision,
    event: dict[str, Any],
    context: dict[str, Any],
) -> None:
    """
    Call the AI provider for enrichment.  Errors are swallowed so that a
    failing AI call never prevents the main business action from completing.

    Jules integration point:
    - Set AI_PROVIDER=google or AI_PROVIDER=manus in env
    - run_ai_task() will route to the correct provider
    """
    try:
        from ai_providers.factory import run_ai_task  # noqa: PLC0415

        provider = decision.provider  # None → read from AI_PROVIDER env var
        task_payload = {
            "event_type": event.get("type"),
            "event_id": event.get("id"),
            "action": decision.action.value,
        }
        result = run_ai_task(
            task_type="event_enrichment",
            payload=task_payload,
            provider=provider,
        )
        logger.info(
            "[execution] AI enrichment ok event_id=%s provider=%s",
            event.get("id"), provider,
        )
    except Exception as exc:
        logger.warning(
            "[execution] AI enrichment skipped event_id=%s: %s",
            event.get("id"), exc,
        )
