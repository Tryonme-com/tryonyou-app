"""
Reenvío de eventos Espejo Digital → Make.com.

La URL del webhook **solo** se lee del entorno (orden de prioridad en
`resolve_make_webhook_url`). Sin URL configurada se responde 200 `skipped`
para no romper la UX en desarrollo.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

import requests

ALLOWED_EVENTS = frozenset({"balmain_click", "reserve_fitting_click"})


def resolve_make_webhook_url() -> str:
    for key in (
        "MAKE_MIRROR_DIGITAL_WEBHOOK_URL",
        "MAKE_ESPEJO_DIGITAL_WEBHOOK_URL",
        "MAKE_WEBHOOK_URL",
        "TRYONYOU_LEAD_WEBHOOK_URL",
        "MAKE_LEADS_WEBHOOK_URL",
    ):
        u = (os.environ.get(key) or "").strip()
        if u:
            return u
    return ""


def forward_mirror_event(body: dict[str, Any]) -> tuple[dict[str, Any], int]:
    event = str(body.get("event") or "").strip()
    if event not in ALLOWED_EVENTS:
        return {"status": "error", "message": "unknown or missing event"}, 400

    meta = body.get("meta")
    if not isinstance(meta, dict):
        meta = {}

    payload = {
        "event": event,
        "source": str(body.get("source") or "tryonyou_mirror").strip() or "tryonyou_mirror",
        "meta": meta,
        "received_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    url = resolve_make_webhook_url()
    if not url:
        return {
            "status": "skipped",
            "reason": "no_make_webhook_configured",
            "hint_env": "MAKE_MIRROR_DIGITAL_WEBHOOK_URL or MAKE_WEBHOOK_URL",
        }, 200

    try:
        r = requests.post(url, json=payload, timeout=25)
        if not r.ok:
            return {
                "status": "error",
                "message": f"make_http_{r.status_code}",
            }, 502
    except (requests.RequestException, OSError) as e:
        return {"status": "error", "message": str(e)}, 502

    return {"status": "ok", "forwarded": True}, 200
