"""
Carrito Master Look — complementos validados por Agente 70 → Live It / Divineo.

- Umbral de ítems: LIVEIT_LOOK_MIN_ITEMS (default 6). En staging puedes usar 3.
- Sincronización remota: LIVEIT_CART_SYNC_URL (POST JSON {\"items\": [...]}). Sin URL, no falla
  salvo LIVEIT_CART_SYNC_STRICT=1.

Patente PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


def _min_look_items() -> int:
    raw = (os.getenv("LIVEIT_LOOK_MIN_ITEMS") or "6").strip()
    try:
        n = int(raw)
        return max(1, min(n, 99))
    except ValueError:
        return 6


def _sync_cart_remote(items: list[Any]) -> dict[str, Any]:
    """Delegación a Live It / Make / tienda; contrato JSON estable."""
    url = (os.getenv("LIVEIT_CART_SYNC_URL") or "").strip()
    if not url:
        return {"synced": False, "reason": "LIVEIT_CART_SYNC_URL unset (dry run)"}
    payload = json.dumps({"items": items, "agent": "AGENTE70"}, separators=(",", ":")).encode(
        "utf-8"
    )
    req = urllib.request.Request(
        url,
        data=payload,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return {
                "synced": True,
                "http_status": resp.status,
                "response_preview": body[:4000],
            }
    except urllib.error.HTTPError as e:
        return {"synced": False, "error": str(e), "http_status": getattr(e, "code", None)}
    except OSError as e:
        return {"synced": False, "error": str(e)}


def add_master_look_to_cart(look_data: dict[str, Any]) -> dict[str, Any]:
    """Añade los complementos validados por el Agente 70 al flujo de carrito Live It."""
    items = look_data.get("items")
    if not isinstance(items, list):
        return {"error": "Look incompleto para el estándar del CEO"}
    need = _min_look_items()
    if len(items) < need:
        return {
            "error": "Look incompleto para el estándar del CEO",
            "detail": f"se requieren al menos {need} ítems (actual: {len(items)})",
        }

    sync = _sync_cart_remote(items)
    strict = (os.getenv("LIVEIT_CART_SYNC_STRICT") or "").strip() in ("1", "true", "yes", "on")
    if strict and not sync.get("synced"):
        return {
            "error": "Sincronización carrito Live It no completada",
            "cart_sync": sync,
        }

    out: dict[str, Any] = {
        "status": "DIVINEO_CONFIRMED",
        "total": look_data.get("price"),
        "agent": "AGENTE70",
        "items_count": len(items),
        "cart_sync": sync,
    }
    return out
