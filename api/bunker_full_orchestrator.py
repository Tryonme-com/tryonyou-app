"""
Bunker Full Orchestrator - Make.com, waitlist local y Supabase opcional.

Payloads JSON estables para escenarios Make.com. Supabase se carga de forma
lazy solo si existen variables y dependencia instalada.

Patente: PCT/EP2025/067317 - @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
VETOS_PRIORITY_BETA = 0.92

_supabase_client: Any | None = None


def _get_supabase_client() -> Any | None:
    """Cliente Supabase lazy; None si falta env o el paquete no esta instalado."""
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client
    url = (os.getenv("SUPABASE_URL") or "").strip()
    key = (os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY") or "").strip()
    if not url or not key:
        return None
    try:
        from supabase import create_client
    except ImportError:
        return None
    _supabase_client = create_client(url, key)
    return _supabase_client


class BunkerOrchestrator:
    """Orquestacion de estado soberano hacia Supabase."""

    def __init__(self) -> None:
        self.status = "SOUVERAINETE:1"

    @property
    def supabase(self) -> Any:
        client = _get_supabase_client()
        if client is None:
            raise RuntimeError(
                "Supabase no configurado: SUPABASE_URL + SUPABASE_KEY "
                "(o SUPABASE_SERVICE_ROLE_KEY) y pip install supabase"
            )
        return client

    def update_sovereignty(self, user_id: str, status: bool = True) -> Any | None:
        if not status:
            return None
        sb = _get_supabase_client()
        if sb is None:
            raise RuntimeError(
                "Supabase no disponible: revisa variables de entorno y dependencia supabase"
            )
        return sb.table("users").update({"status": self.status}).eq("id", user_id).execute()


orchestrator = BunkerOrchestrator()


def _make_post(payload: dict[str, Any]) -> bool:
    url = (os.getenv("MAKE_WEBHOOK_URL") or "").strip()
    if not url:
        return False
    try:
        response = requests.post(url, json=payload, timeout=25)
        return response.status_code == 200
    except OSError:
        return False


def append_waitlist_json(entry: dict[str, Any]) -> tuple[bool, str | None]:
    """Intenta leads_empire/waitlist.json; si no se puede, usa TMPDIR."""
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
    """Webhook Make + append waitlist para beta."""
    payload = {
        "event": "beta_waitlist",
        "channel": "general-tryonyou",
        "message": "NUEVO LEAD - Unete a la beta (TryOnYou)",
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
    """Ruta /api/bunker_full_orchestrator - Make + waitlist con prioridad VetosCore."""
    try:
        priority = float(body.get("priority", body.get("vetos_priority", VETOS_PRIORITY_BETA)))
    except (TypeError, ValueError):
        priority = VETOS_PRIORITY_BETA

    payload = {
        "event": "bunker_full_orchestrator",
        "channel": "general-tryonyou",
        "message": "BUNKER FULL - Beta prioridad VetosCore 0.92",
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
    """Shadow Mirror Test: permanencia en mirror_sanctuary via Make."""
    dwell = body.get("dwell_ms", 0)
    payload = {
        "event": "mirror_shadow_dwell",
        "channel": "general-tryonyou",
        "message": f"Mirror Sanctuary - permanencia {dwell} ms",
        "dwell_ms": dwell,
        "dwell_sec": body.get("dwell_sec"),
        "page": body.get("page", "mirror_sanctuary_v10.html"),
        "reason": body.get("reason"),
        "ts": body.get("ts"),
    }
    ok_make = _make_post(payload)
    return {"make_ok": ok_make}
