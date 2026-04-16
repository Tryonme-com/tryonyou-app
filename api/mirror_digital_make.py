"""
Reenvío de eventos Espejo Digital → Make.com.

La URL del webhook **solo** se lee del entorno (orden de prioridad en
`resolve_make_webhook_url`). Sin URL configurada se responde 200 `skipped`
para no romper la UX en desarrollo.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

ALLOWED_EVENTS = frozenset({"balmain_click", "reserve_fitting_click"})
AUTONOMY_MODES = frozenset({"primary", "degraded", "sanctuary"})


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _logs_dir() -> Path:
    d = _project_root() / "logs"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _autonomy_queue_path() -> Path:
    return _logs_dir() / "mirror_autonomy_queue.jsonl"


def resolve_autonomy_mode() -> str:
    mode = (os.environ.get("MIRROR_AUTONOMY_MODE") or "primary").strip().lower()
    return mode if mode in AUTONOMY_MODES else "primary"


def _queue_fallback_event(payload: dict[str, Any], reason: str) -> None:
    row = {
        "queued_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "reason": reason[:120],
        "payload": payload,
    }
    with _autonomy_queue_path().open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def _queued_events_count() -> int:
    p = _autonomy_queue_path()
    if not p.is_file():
        return 0
    with p.open(encoding="utf-8") as handle:
        return sum(1 for _ in handle)


def mirror_autonomy_status_payload() -> dict[str, Any]:
    mode = resolve_autonomy_mode()
    webhook = resolve_make_webhook_url()
    return {
        "ok": True,
        "mode": mode,
        "webhook_configured": bool(webhook),
        "queued_events": _queued_events_count(),
        "protocol": "mirror_autonomy_v11",
        "updated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


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

    mode = resolve_autonomy_mode()
    meta = body.get("meta")
    if not isinstance(meta, dict):
        meta = {}

    payload = {
        "event": event,
        "source": str(body.get("source") or "tryonyou_mirror").strip() or "tryonyou_mirror",
        "meta": meta,
        "received_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    if mode in ("degraded", "sanctuary"):
        _queue_fallback_event(payload, reason=f"autonomy_mode_{mode}")
        return {
            "status": "queued_local_fallback",
            "mode": mode,
            "queued": True,
            "reason": "autonomy_mode_active",
        }, 202

    url = resolve_make_webhook_url()
    if not url:
        _queue_fallback_event(payload, reason="no_make_webhook_configured")
        return {
            "status": "queued_local_fallback",
            "mode": mode,
            "queued": True,
            "reason": "no_make_webhook_configured",
            "hint_env": "MAKE_MIRROR_DIGITAL_WEBHOOK_URL or MAKE_WEBHOOK_URL",
        }, 202

    try:
        r = requests.post(url, json=payload, timeout=25)
        if not r.ok:
            _queue_fallback_event(payload, reason=f"make_http_{r.status_code}")
            return {
                "status": "queued_local_fallback",
                "mode": mode,
                "queued": True,
                "reason": f"make_http_{r.status_code}",
            }, 202
    except (requests.RequestException, OSError) as e:
        _queue_fallback_event(payload, reason="make_request_exception")
        return {
            "status": "queued_local_fallback",
            "mode": mode,
            "queued": True,
            "reason": "make_request_exception",
            "detail": str(e),
        }, 202

    return {"status": "ok", "forwarded": True}, 200
