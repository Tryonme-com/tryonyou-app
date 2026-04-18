"""
Conector de aplicación Abvetos — capa estable para peticiones entrantes (Make.com / chat).
"""
from __future__ import annotations

from typing import Any


class AbvetosApp:
    """Fachada mínima; sustituir por webhook HTTP o servicio real cuando exista."""

    def handle_request(self, user_id: str, message: str) -> dict[str, Any]:
        return {
            "ok": True,
            "user_id": user_id,
            "echo": message,
            "channel": "abvetos_connector",
        }
