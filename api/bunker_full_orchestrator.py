"""
Bunker Full Orchestrator — Make.com (Slack) + persistencia waitlist en leads_empire/waitlist.json.
Patente: PCT/EP2025/067317 — payloads JSON estables para escenarios Make.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

REPO_ROOT = Path(__file__).resolve().parent

VETOS_PRIORITY_BETA = 0.92


def _make_post(payload: dict[str, Any]) -> bool:
    url = (os.getenv("MAKE_WEBHOOK_URL") or "").strip()
    if not url:
        return False
    try:
        r = requests.post(url, json=payload, timeout=25)
        return r.status_code == 200
    except OSError:
        return False


def append_waitlist_json(entry: dict[str, Any]) -> tuple[bool, str | None]:
    """Intenta `leads_empire/waitlist.json`; si el FS es de solo lectura (p. ej. Vercel), usa TMPDIR."""
    stamped = {
        **entry,
        "stored_at": datetime.now(timezone.utc).isoformat(),
    }
    tmp_base = os.getenv("TMPDIR") or "/tmp"
    candidates = [
        REPO_ROOT / "leads_empire" / "waitlist.json",
        Path(tmp_base) / "leads_empire_waitlist.json",
    ]
    for path in candidates:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            data: list[Any] = []
            if path.is_file():
                raw = path.read_text(encoding="utf-8")
                data = json.loads(raw) if raw.strip() else []
            if not isinstance(data, list):
                data = []
            data.append(stamped)
            path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            return True, str(path)
        except OSError:
            continue
    return False, None


def orchestrate_beta_waitlist(body: dict[str, Any]) -> dict[str, Any]:
    """Webhook Make + append waitlist (sin prioridad fija; rutas legacy)."""
    payload = {
        "event": "beta_waitlist",
        "channel": "general-tryonyou",
        "message": "🚀 NUEVO LEAD — Únete a la beta (TryOnYou)",
        "email": body.get("email"),
        "source": body.get("source", "app_v10"),
        "user_agent": body.get("user_agent"),
        "ts": body.get("ts"),
    }
    ok_make = _make_post(payload)
    ok_file, path = append_waitlist_json(payload)
    return {
        "make_ok": ok_make,
        "waitlist_persisted": ok_file,
        "waitlist_path": path,
    }


def orchestrate_bunker_full_orchestrator(body: dict[str, Any]) -> dict[str, Any]:
    """
    Ruta /api/bunker_full_orchestrator — Make + waitlist con prioridad VetosCore 0.92.
    """
    try:
        priority = float(
            body.get("priority", body.get("vetos_priority", VETOS_PRIORITY_BETA))
        )
    except (TypeError, ValueError):
        priority = VETOS_PRIORITY_BETA

    payload = {
        "event": "bunker_full_orchestrator",
        "channel": "general-tryonyou",
        "message": "🚀 BUNKER FULL — Beta (prioridad VetosCore 0.92)",
        "priority": priority,
        "vetos_priority": priority,
        "score": priority,
        "email": body.get("email"),
        "source": body.get("source", "app_v10_bunker_full"),
        "user_agent": body.get("user_agent"),
        "ts": body.get("ts"),
    }
    ok_make = _make_post(payload)
    ok_file, path = append_waitlist_json(payload)
    return {
        "make_ok": ok_make,
        "waitlist_persisted": ok_file,
        "waitlist_path": path,
        "priority": priority,
    }


def orchestrate_mirror_shadow_dwell(body: dict[str, Any]) -> dict[str, Any]:
    """Shadow Mirror Test: permanencia en mirror_sanctuary → Slack vía Make."""
    dwell = body.get("dwell_ms", 0)
    payload = {
        "event": "mirror_shadow_dwell",
        "channel": "general-tryonyou",
        "message": f"🪞 Mirror Sanctuary — permanencia {dwell} ms",
        "dwell_ms": dwell,
        "dwell_sec": body.get("dwell_sec"),
        "page": body.get("page", "mirror_sanctuary_v10.html"),
        "reason": body.get("reason"),
        "ts": body.get("ts"),
    }
    ok_make = _make_post(payload)
    return {"make_ok": ok_make}
