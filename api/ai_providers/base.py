"""
Base AI provider interface.

All providers must implement AIProvider.run_task().
Nothing in this file imports Flask, Stripe, or any external SDK.
"""
from __future__ import annotations

import abc
from typing import Any


class AIProviderError(Exception):
    """Raised when an AI provider call fails (transient or permanent)."""


class AIProvider(abc.ABC):
    """
    Abstract adapter for an AI provider.

    Implementations live in google_ai.py / manus_ai.py.
    The webhook and Jules worker only ever call run_ai_task() from factory.py;
    they never instantiate a provider directly.
    """

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Short identifier used in logs (e.g. 'google_ai_studio')."""

    @abc.abstractmethod
    def run_task(
        self,
        task_type: str,
        payload: dict[str, Any],
        *,
        event_id: str = "",
        timeout: float = 10.0,
    ) -> dict[str, Any]:
        """
        Execute an AI task and return a structured result.

        Args:
            task_type: Logical task name, e.g. "payment_confirmation".
            payload:   Task-specific data.  Must NOT contain secrets or raw PII.
            event_id:  Stripe event_id — propagated for end-to-end traceability.
            timeout:   Max seconds to wait for the remote provider.

        Returns:
            dict with at least {"ok": True, "provider": str, "result": Any}

        Raises:
            AIProviderError on any failure (circuit-open, HTTP error, timeout…).
        """
