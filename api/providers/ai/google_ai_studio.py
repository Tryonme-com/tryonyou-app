from __future__ import annotations

from typing import Any

import requests

from api.config import settings
from api.providers.ai.base import AIProvider


class GoogleAIStudioProvider(AIProvider):
    def run_task(self, task_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        if not settings.google_ai_api_key:
            raise RuntimeError("GOOGLE_AI_API_KEY is missing")

        prompt = payload.get("summary_prompt") or payload.get("description") or "No prompt"
        body = {
            "contents": [{"parts": [{"text": f"Task={task_type}; Context={prompt[:1000]}"}]}],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 300},
        }
        response = requests.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent",
            params={"key": settings.google_ai_api_key},
            json=body,
            timeout=settings.ai_timeout_seconds,
        )
        response.raise_for_status()
        data = response.json()
        text = (
            data.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
        )
        return {"provider": "google", "task_type": task_type, "output": text[:1500]}
