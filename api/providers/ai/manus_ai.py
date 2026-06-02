from __future__ import annotations

from typing import Any

import requests

from api.config import settings
from api.providers.ai.base import AIProvider


class ManusAIProvider(AIProvider):
    def run_task(self, task_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        if not settings.manus_api_key:
            raise RuntimeError("MANUS_API_KEY is missing")

        response = requests.post(
            f"{settings.manus_base_url.rstrip('/')}/v1/tasks",
            headers={
                "X-API-Key": settings.manus_api_key,
                "Content-Type": "application/json",
            },
            json={"task_type": task_type, "payload": payload},
            timeout=settings.ai_timeout_seconds,
        )
        response.raise_for_status()
        data = response.json()
        return {
            "provider": "manus",
            "task_type": task_type,
            "output": str(data.get("result") or data.get("status") or "ok")[:1500],
        }
