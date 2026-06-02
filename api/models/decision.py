"""Decision model — the structured output of the decision engine."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class EventAction(str, Enum):
    MARK_ORDER_PAID = "mark_order_paid"
    MARK_PAYMENT_FAILED = "mark_payment_failed"
    ACTIVATE_SUBSCRIPTION = "activate_subscription"
    HANDLE_REFUND = "handle_refund"
    REQUEST_MANUAL_REVIEW = "request_manual_review"
    INVOKE_AI_ENRICHMENT = "invoke_ai_enrichment"
    IGNORE_EVENT = "ignore_event"


@dataclass
class Decision:
    action: EventAction
    reason: str
    priority: int = 5           # 1 (highest) … 10 (lowest)
    requires_ai: bool = False
    provider: str | None = None  # "google" | "manus" | None
    retryable: bool = True
    metadata: dict = field(default_factory=dict)
