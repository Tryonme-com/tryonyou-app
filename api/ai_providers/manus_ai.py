"""
Manus AI provider adapter.

Uses plain HTTP (requests) — no official SDK required.
Replace _build_request_body() and _parse_response() when the real API schema
is confirmed.

Credentials
-----------
    MANUS_API_KEY    required
    MANUS_BASE_URL   optional — defaults to https://api.manus.ai/v1
    MANUS_TIMEOUT_S  optional — per-request timeout in seconds (default 10)

The webhook never imports this module directly.
Only factory.py instantiates this class.
"""
from __future__ import annotations

import logging
import os
from typing import Any

import requests

from .base import AIProvider, AIProviderError
from .circuit_breaker import CircuitBreaker, CircuitBreakerOpenError

logger = logging.getLogger(__name__)

# ── Config (read once at module load) ─────────────────────────────────────────
_API_KEY = os.environ.get("MANUS_API_KEY", "").strip()
_BASE_URL = os.environ.get("MANUS_BASE_URL", "https://api.manus.ai/v1").rstrip("/")
_DEFAULT_TIMEOUT = float(os.environ.get("MANUS_TIMEOUT_S", "10"))

# Headers that must never appear in task payloads
_BLOCKED_PAYLOAD_KEYS = frozenset({"secret", "token", "api_key", "password", "raw"})


class ManusAIProvider(AIProvider):
    """Adapter for Manus AI via HTTP REST."""

    name = "manus_ai"

    def __init__(self) -> None:
        self._circuit = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=60.0,
            name=self.name,
        )
        if not _API_KEY:
            logger.warning(
                "[manus_ai] MANUS_API_KEY not set — provider disabled"
            )
        else:
            logger.info("[manus_ai] provider ready base_url=%s", _BASE_URL)

    # ── AIProvider interface ──────────────────────────────────────────────────

    def run_task(
        self,
        task_type: str,
        payload: dict[str, Any],
        *,
        event_id: str = "",
        timeout: float = _DEFAULT_TIMEOUT,
    ) -> dict[str, Any]:
        if not _API_KEY:
            raise AIProviderError("MANUS_API_KEY not configured")

        body = _build_request_body(task_type, payload, event_id)
        logger.info(
            "[manus_ai] run_task task_type=%s event_id=%s url=%s/tasks",
            task_type, event_id, _BASE_URL,
        )

        try:
            raw = self._circuit.call(self._post, body, timeout)
        except CircuitBreakerOpenError as exc:
            raise AIProviderError(f"Manus AI circuit OPEN: {exc}") from exc
        except requests.Timeout:
            raise AIProviderError(
                f"Manus AI timeout after {timeout}s (task_type={task_type})"
            )
        except requests.HTTPError as exc:
            raise AIProviderError(
                f"Manus AI HTTP {exc.response.status_code}: {exc}"
            ) from exc
        except requests.RequestException as exc:
            raise AIProviderError(f"Manus AI request error: {exc}") from exc

        result = _parse_response(raw)
        logger.info(
            "[manus_ai] completed task_type=%s event_id=%s", task_type, event_id
        )
        return {"ok": True, "provider": self.name, "result": result}

    # ── private ───────────────────────────────────────────────────────────────

    def _post(self, body: dict[str, Any], timeout: float) -> dict[str, Any]:
        resp = requests.post(
            f"{_BASE_URL}/tasks",
            json=body,
            headers={
                "Authorization": "Bearer " + _API_KEY,
                "Content-Type": "application/json",
            },
            timeout=timeout,
        )
        resp.raise_for_status()
        return resp.json()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _build_request_body(
    task_type: str,
    payload: dict[str, Any],
    event_id: str,
) -> dict[str, Any]:
    """
    Build the Manus API request body.
    Strips any blocked keys to prevent leaking secrets.
    Adapt to the real Manus API schema when available.
    """
    safe_payload = {k: v for k, v in payload.items() if k not in _BLOCKED_PAYLOAD_KEYS}
    return {
        "task_type": task_type,
        "context": {
            "event_id": event_id,
            **safe_payload,
        },
    }


def _parse_response(raw: dict[str, Any]) -> Any:
    """
    Extract the meaningful result from the Manus API response.
    Adapt when the real response schema is known.
    """
    return raw.get("result") or raw.get("output") or raw
