"""Notificaciones TryOnYou vía Slack Incoming Webhook (sin SMTP/Gmail)."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request


def slack_post(text: str, *, timeout_s: float = 8.0) -> bool:
    url = os.environ.get("SLACK_WEBHOOK_URL", "").strip()
    if not url:
        return False
    payload = json.dumps({"text": str(text)[:3500]}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as r:
            del r
        return True
    except (urllib.error.URLError, TimeoutError, OSError):
        return False
