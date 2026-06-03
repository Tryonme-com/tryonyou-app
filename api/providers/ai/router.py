from __future__ import annotations

import time
from typing import Any

from api.config import settings
from api.providers.ai.google_ai_studio import GoogleAIStudioProvider
from api.providers.ai.manus_ai import ManusAIProvider


def _get_provider(provider: str):
    if provider == "manus":
        return ManusAIProvider()
    return GoogleAIStudioProvider()


def run_ai_task(task_type: str, payload: dict[str, Any], provider: str | None = None) -> dict[str, Any]:
    selected = (provider or settings.ai_provider or "google").lower()
    runner = _get_provider(selected)
    last_error: Exception | None = None
    for attempt in range(1, 4):
        try:
            result = runner.run_task(task_type, payload)
            result["attempt"] = attempt
            return result
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt >= 3:
                break
            delay = min(
                (2 ** max(attempt - 1, 0)) * settings.retry_backoff_base_seconds,
                settings.retry_max_backoff_seconds,
            )
            time.sleep(delay)
    payload_keys = ",".join(sorted(payload.keys()))
    raise RuntimeError(
        f"ai_task_failed provider={selected} task_type={task_type} payload_keys={payload_keys}: {last_error}"
    ) from last_error
