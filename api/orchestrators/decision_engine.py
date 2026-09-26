from __future__ import annotations

from typing import Any

from api.config import settings
from api.models.decision import Decision


def decide_event_flow(event: dict[str, Any], context: dict[str, Any]) -> Decision:
    event_type = event.get("type", "unknown")
    attempts = int(context.get("attempts", 0))
    event_state = context.get("event_state", {})
    obj = event.get("data", {}).get("object", {})

    if event_state.get("status") == "completed":
        return Decision(action="ignore_event", reason="already_completed", priority=0, retryable=False, max_attempts=1)

    if event_type == "payment_intent.succeeded":
        if obj.get("metadata", {}).get("needs_ai") == "true":
            return Decision(
                action="invoke_ai_enrichment",
                reason="payment_success_with_ai_enrichment",
                priority=9,
                requires_ai=True,
                provider=settings.ai_provider,
                retryable=True,
                max_attempts=settings.max_retry_attempts,
            )
        return Decision(action="mark_order_paid", reason="payment_intent_succeeded", priority=8, retryable=True, max_attempts=settings.max_retry_attempts)

    if event_type == "payment_intent.payment_failed":
        return Decision(action="mark_payment_failed", reason="payment_intent_failed", priority=8, retryable=True, max_attempts=settings.max_retry_attempts)

    if event_type == "checkout.session.completed":
        return Decision(action="activate_subscription", reason="checkout_completed", priority=7, retryable=True, max_attempts=settings.max_retry_attempts)

    if event_type == "charge.refunded":
        return Decision(action="handle_refund", reason="charge_refunded", priority=7, retryable=True, max_attempts=settings.max_retry_attempts)

    if attempts >= settings.max_retry_attempts:
        return Decision(action="request_manual_review", reason="max_attempts_exhausted", priority=10, retryable=False, max_attempts=attempts)

    return Decision(action="ignore_event", reason="unsupported_event_type", priority=1, retryable=False, max_attempts=1)
