"""
Decision engine — pure Python, no I/O.

Receives an event dict and a context dict (Redis metadata) and returns a
Decision dataclass describing what the worker should do.

This module has zero side effects.  It can be unit-tested without Redis,
Stripe, or any network calls.
"""
from __future__ import annotations

import logging
from typing import Any

from models.decision import Decision, EventAction

logger = logging.getLogger(__name__)

_MAX_RETRIES = 3

# ── Event → action mapping ────────────────────────────────────────────────────

_ACTION_MAP: dict[str, EventAction] = {
    "payment_intent.succeeded": EventAction.MARK_ORDER_PAID,
    "payment_intent.payment_failed": EventAction.MARK_PAYMENT_FAILED,
    "checkout.session.completed": EventAction.ACTIVATE_SUBSCRIPTION,
    "charge.refunded": EventAction.HANDLE_REFUND,
}

# Event types that benefit from AI enrichment (optional)
_AI_ENRICHMENT_TYPES: set[str] = set()  # e.g. {"payment_intent.payment_failed"}


def decide_event_flow(event: dict[str, Any], context: dict[str, Any]) -> Decision:
    """
    Determine what action the worker should take.

    Args:
        event:   Stripe event dict (validated, from queue)
        context: Redis metadata for this event (retries, status, etc.)

    Returns:
        Decision dataclass with action, priority, retryability, etc.
    """
    event_type: str = event.get("type", "")
    event_id: str = event.get("id", "")
    retries: int = int(context.get("retries", "0"))
    livemode: bool = context.get("livemode", "False") == "True"

    # Exceeded retry budget → manual review
    if retries >= _MAX_RETRIES:
        logger.warning(
            "[decision] max retries reached event_id=%s event_type=%s",
            event_id, event_type,
        )
        return Decision(
            action=EventAction.REQUEST_MANUAL_REVIEW,
            reason="max_retries_exceeded",
            priority=10,
            requires_ai=False,
            provider=None,
            retryable=False,
            metadata={"retries": retries},
        )

    action = _ACTION_MAP.get(event_type, EventAction.IGNORE_EVENT)
    requires_ai = event_type in _AI_ENRICHMENT_TYPES
    priority = 5 if livemode else 1

    logger.debug(
        "[decision] event_id=%s event_type=%s -> action=%s requires_ai=%s",
        event_id, event_type, action, requires_ai,
    )

    return Decision(
        action=action,
        reason=f"matched_rule:{event_type}",
        priority=priority,
        requires_ai=requires_ai,
        provider=None,  # factory.py selects by AI_PROVIDER env var
        retryable=True,
        metadata={"event_type": event_type, "retries": retries},
    )
