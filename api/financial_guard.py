"""
Financial Guard — Stripe error resilience layer.
Catches 402 and other payment errors, logs to monetizacion_trace_demo.log,
and retries instead of shutting down the server.

Patente PCT/EP2025/067317
Protocolo de Soberanía V11 - Founder: Rubén
"""
from __future__ import annotations

import logging
import os
import time
from functools import wraps
from typing import Any, Callable

_LOG_FILE = os.getenv(
    "MONETIZATION_LOG_PATH",
    os.path.join(os.path.dirname(__file__), "..", "monetizacion_trace_demo.log"),
)

_logger = logging.getLogger("financial_guard")
_handler = logging.FileHandler(_LOG_FILE, encoding="utf-8")
_handler.setFormatter(
    logging.Formatter("%(asctime)s | %(levelname)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
)
_logger.addHandler(_handler)
_logger.setLevel(logging.INFO)

MAX_RETRIES: int = 3
RETRY_DELAY_S: float = 2.0


def guard_stripe_call(
    fn: Callable[..., Any],
    *args: Any,
    max_retries: int = MAX_RETRIES,
    retry_delay: float = RETRY_DELAY_S,
    **kwargs: Any,
) -> Any:
    """
    Wraps a Stripe API call with retry logic.
    On 402 or other StripeError, logs the failure and retries.
    NEVER calls sys.exit() or shuts down the server.
    """
    last_error: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            result = fn(*args, **kwargs)
            if attempt > 1:
                _logger.info(
                    "stripe_call_recovered | fn=%s | attempt=%d",
                    fn.__name__,
                    attempt,
                )
            return result
        except Exception as exc:
            last_error = exc
            error_code = getattr(exc, "http_status", None) or "unknown"
            _logger.warning(
                "stripe_call_failed | fn=%s | attempt=%d/%d | status=%s | error=%s",
                fn.__name__,
                attempt,
                max_retries,
                error_code,
                str(exc)[:200],
            )
            if attempt < max_retries:
                time.sleep(retry_delay * attempt)

    _logger.error(
        "stripe_call_exhausted | fn=%s | retries=%d | last_error=%s",
        fn.__name__,
        max_retries,
        str(last_error)[:300],
    )
    return None


def resilient_stripe(max_retries: int = MAX_RETRIES, retry_delay: float = RETRY_DELAY_S):
    """
    Decorator version of guard_stripe_call.
    Usage:
        @resilient_stripe()
        def create_payment_intent(...):
            ...
    """

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return guard_stripe_call(
                fn, *args, max_retries=max_retries, retry_delay=retry_delay, **kwargs
            )

        return wrapper

    return decorator


def log_sovereignty_event(
    event_type: str,
    detail: str,
    session_id: str = "",
    amount_eur: float = 0.0,
) -> None:
    """Log a sovereignty/financial event for audit trail."""
    _logger.info(
        "sovereignty_event | type=%s | session=%s | amount=%.2f | detail=%s",
        event_type,
        session_id,
        amount_eur,
        detail[:500],
    )
