"""
Simple circuit breaker.

States
------
CLOSED    — normal operation; failures are counted.
OPEN      — calls are rejected immediately for `recovery_timeout` seconds.
HALF_OPEN — one probe call is allowed; success closes, failure re-opens.

Usage
-----
    cb = CircuitBreaker(failure_threshold=3, recovery_timeout=30.0, name="my_api")
    result = cb.call(some_function, arg1, arg2)
"""
from __future__ import annotations

import logging
import time
from enum import Enum
from typing import Any, Callable

logger = logging.getLogger(__name__)


class CBState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreakerOpenError(Exception):
    """Raised when a call is rejected because the circuit is OPEN."""


class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_timeout: float = 30.0,
        name: str = "circuit_breaker",
    ) -> None:
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.name = name
        self._state = CBState.CLOSED
        self._failures = 0
        self._opened_at: float = 0.0

    # ── public ────────────────────────────────────────────────────────────────

    @property
    def state(self) -> CBState:
        """Return current state, auto-transitioning OPEN → HALF_OPEN on timeout."""
        if (
            self._state is CBState.OPEN
            and time.monotonic() - self._opened_at >= self.recovery_timeout
        ):
            self._state = CBState.HALF_OPEN
            logger.info("[circuit_breaker:%s] OPEN → HALF_OPEN (probe allowed)", self.name)
        return self._state

    def call(self, fn: Callable, *args: Any, **kwargs: Any) -> Any:
        """
        Execute fn(*args, **kwargs) under circuit-breaker control.
        Raises CircuitBreakerOpenError if the circuit is OPEN.
        """
        if self.state is CBState.OPEN:
            raise CircuitBreakerOpenError(
                f"Circuit '{self.name}' is OPEN — call rejected"
            )
        try:
            result = fn(*args, **kwargs)
        except Exception:
            self._on_failure()
            raise
        else:
            self._on_success()
            return result

    # ── private ───────────────────────────────────────────────────────────────

    def _on_failure(self) -> None:
        self._failures += 1
        if self._state is CBState.HALF_OPEN or self._failures >= self.failure_threshold:
            self._state = CBState.OPEN
            self._opened_at = time.monotonic()
            logger.warning(
                "[circuit_breaker:%s] → OPEN after %d failure(s)",
                self.name, self._failures,
            )

    def _on_success(self) -> None:
        if self._state is CBState.HALF_OPEN:
            logger.info(
                "[circuit_breaker:%s] HALF_OPEN → CLOSED (recovered)", self.name
            )
        self._state = CBState.CLOSED
        self._failures = 0
