"""
AI provider factory and task runner.

This is the single entry point used by the Jules worker (handle_stripe_event).
The webhook never calls this module.

Usage
-----
    from ai_providers import run_ai_task, AIProviderError

    try:
        result = run_ai_task(
            "payment_confirmation",
            {"amount_display": "$25.00", "currency": "usd"},
            event_id=event_id,
        )
    except AIProviderError as exc:
        logger.warning("AI task failed (non-blocking): %s", exc)

Provider selection
------------------
Priority:
  1. provider_name argument to run_ai_task()
  2. AI_PROVIDER environment variable  ("google" | "manus")
  3. AIProviderError if neither is set

Retry behaviour
---------------
Transient failures (HTTP errors, timeouts) are retried up to `max_retries` times.
CircuitBreakerOpenError and config errors are NOT retried.
"""
from __future__ import annotations

import logging
import os
from typing import Any

from .base import AIProvider, AIProviderError
from .circuit_breaker import CircuitBreakerOpenError

logger = logging.getLogger(__name__)

_AI_PROVIDER_ENV = os.environ.get("AI_PROVIDER", "").strip().lower()

# Singleton provider instances — created once per process.
_providers: dict[str, AIProvider] = {}

# Errors that should not be retried.
_NON_RETRYABLE = (CircuitBreakerOpenError,)


def _get_provider(name: str) -> AIProvider:
    """Return (and cache) a provider instance by name."""
    if name not in _providers:
        if name == "google":
            from .google_ai import GoogleAIStudioProvider
            _providers[name] = GoogleAIStudioProvider()
        elif name == "manus":
            from .manus_ai import ManusAIProvider
            _providers[name] = ManusAIProvider()
        else:
            raise AIProviderError(
                f"Unknown AI provider {name!r}. "
                "Valid values: 'google', 'manus'."
            )
    return _providers[name]


def run_ai_task(
    task_type: str,
    payload: dict[str, Any],
    *,
    event_id: str = "",
    provider_name: str | None = None,
    timeout: float = 10.0,
    max_retries: int = 2,
) -> dict[str, Any]:
    """
    Execute an AI task through the configured provider.

    This function is intentionally decoupled from Flask and Stripe.
    Jules calls it from handle_stripe_event(); the webhook route never calls it.

    Args:
        task_type:     Logical task name, e.g. "payment_confirmation".
        payload:       Task data — must NOT contain secrets or raw PII.
        event_id:      Stripe event_id, forwarded for end-to-end tracing.
        provider_name: Override the env-configured provider for this call.
        timeout:       Per-attempt timeout in seconds.
        max_retries:   Extra attempts on transient failure (0 = try once only).

    Returns:
        dict: {"ok": True, "provider": str, "result": Any}

    Raises:
        AIProviderError: after all retries are exhausted, or on config errors.
    """
    name = (provider_name or _AI_PROVIDER_ENV).lower()
    if not name:
        raise AIProviderError(
            "No AI provider configured. "
            "Set the AI_PROVIDER environment variable or pass provider_name."
        )

    provider = _get_provider(name)
    last_exc: Exception = AIProviderError("no attempts made")
    total_attempts = max_retries + 1

    for attempt in range(1, total_attempts + 1):
        try:
            result = provider.run_task(
                task_type, payload, event_id=event_id, timeout=timeout
            )
            if attempt > 1:
                logger.info(
                    "[ai_factory] task_type=%s event_id=%s recovered on attempt %d/%d",
                    task_type, event_id, attempt, total_attempts,
                )
            return result

        except _NON_RETRYABLE as exc:
            # Circuit open or config error — do not retry.
            logger.warning(
                "[ai_factory] non-retryable task_type=%s event_id=%s provider=%s: %s",
                task_type, event_id, name, exc,
            )
            raise AIProviderError(str(exc)) from exc

        except Exception as exc:
            last_exc = exc
            if attempt < total_attempts:
                logger.warning(
                    "[ai_factory] attempt %d/%d failed task_type=%s event_id=%s: %s — retrying",
                    attempt, total_attempts, task_type, event_id, exc,
                )
            else:
                logger.error(
                    "[ai_factory] all %d attempt(s) exhausted task_type=%s event_id=%s: %s",
                    total_attempts, task_type, event_id, exc,
                )

    raise AIProviderError(
        f"AI task {task_type!r} failed after {total_attempts} attempt(s)"
    ) from last_exc
