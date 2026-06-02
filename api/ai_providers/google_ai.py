"""
Google AI Studio provider adapter (Gemini models).

SDK
---
    pip install google-generativeai

If the SDK is not installed the provider raises AIProviderError on every call
instead of crashing at import time — keeps the rest of the app working.

Credentials
-----------
    GOOGLE_AI_API_KEY   required — your AI Studio API key
    GOOGLE_AI_MODEL     optional — defaults to "gemini-1.5-flash"

The webhook never imports this module directly.
Only factory.py instantiates this class.
"""
from __future__ import annotations

import logging
import os
from typing import Any

from .base import AIProvider, AIProviderError
from .circuit_breaker import CircuitBreaker, CircuitBreakerOpenError

logger = logging.getLogger(__name__)

# ── Optional SDK import ───────────────────────────────────────────────────────
try:
    import google.generativeai as genai  # type: ignore[import]
    _SDK_AVAILABLE = True
except ImportError:
    genai = None  # type: ignore[assignment]
    _SDK_AVAILABLE = False

# ── Config (read once at module load) ─────────────────────────────────────────
_API_KEY = os.environ.get("GOOGLE_AI_API_KEY", "").strip()
_MODEL = os.environ.get("GOOGLE_AI_MODEL", "gemini-1.5-flash")


class GoogleAIStudioProvider(AIProvider):
    """Adapter for Google AI Studio (Gemini models)."""

    name = "google_ai_studio"

    def __init__(self) -> None:
        self._circuit = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=60.0,
            name=self.name,
        )
        self._ready = False

        if not _SDK_AVAILABLE:
            logger.warning(
                "[google_ai] google-generativeai not installed — "
                "install with: pip install google-generativeai"
            )
            return
        if not _API_KEY:
            logger.warning(
                "[google_ai] GOOGLE_AI_API_KEY not set — provider disabled"
            )
            return

        genai.configure(api_key=_API_KEY)
        self._ready = True
        logger.info("[google_ai] provider ready model=%s", _MODEL)

    # ── AIProvider interface ──────────────────────────────────────────────────

    def run_task(
        self,
        task_type: str,
        payload: dict[str, Any],
        *,
        event_id: str = "",
        timeout: float = 10.0,
    ) -> dict[str, Any]:
        if not _SDK_AVAILABLE:
            raise AIProviderError("google-generativeai SDK not installed")
        if not _API_KEY:
            raise AIProviderError("GOOGLE_AI_API_KEY not configured")

        prompt = _build_prompt(task_type, payload)
        logger.info(
            "[google_ai] run_task task_type=%s event_id=%s model=%s",
            task_type, event_id, _MODEL,
        )

        try:
            text = self._circuit.call(self._generate, prompt)
        except CircuitBreakerOpenError as exc:
            raise AIProviderError(f"Google AI circuit OPEN: {exc}") from exc
        except Exception as exc:
            raise AIProviderError(f"Google AI call failed: {exc}") from exc

        logger.info(
            "[google_ai] completed task_type=%s event_id=%s chars=%d",
            task_type, event_id, len(text),
        )
        return {"ok": True, "provider": self.name, "result": text}

    # ── private ───────────────────────────────────────────────────────────────

    def _generate(self, prompt: str) -> str:
        """
        Direct SDK call — wrapped by circuit breaker.
        Note: google-generativeai does not expose a per-request timeout at the
        generate_content level; add threading.Timer wrapping if strict wall-clock
        enforcement is required.
        """
        model = genai.GenerativeModel(_MODEL)
        response = model.generate_content(prompt)
        return response.text


# ── Prompt templates ──────────────────────────────────────────────────────────
# Keep prompts minimal — do NOT embed raw PII or secrets.

def _build_prompt(task_type: str, payload: dict[str, Any]) -> str:
    if task_type == "payment_confirmation":
        return (
            "Write a short, friendly payment confirmation (2 sentences). "
            f"Amount: {payload.get('amount_display', 'N/A')}  "
            f"Currency: {str(payload.get('currency', '')).upper()}."
        )
    if task_type == "payment_failure_analysis":
        return (
            "Summarise why a payment might fail and suggest one corrective action "
            f"for the customer. Decline reason: {payload.get('error', 'unknown')}."
        )
    if task_type == "checkout_followup":
        return (
            "Write a brief post-checkout welcome message (2 sentences). "
            f"Payment status: {payload.get('payment_status', 'N/A')}."
        )
    if task_type == "refund_notification":
        return (
            "Write a short, empathetic refund notification (2 sentences). "
            f"Refunded amount: {payload.get('amount_display', 'N/A')}."
        )
    # Generic fallback — never log the full payload
    return f"Process the following task: {task_type}. Context keys: {list(payload.keys())}."
