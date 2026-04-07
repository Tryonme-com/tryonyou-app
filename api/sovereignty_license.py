"""
Sovereignty License — verificación de vigencia del nodo emisor del Robert Engine.
"""

from __future__ import annotations

from datetime import datetime, timedelta


def check_sovereignty_license(node_id: str, start_date: str) -> bool:
    """
    Verifica si el nodo debe seguir emitiendo el Robert Engine.

    Returns True if the license is still valid (within 30 days of start_date),
    False if the license has expired (STATUS: LICENSE_EXPIRED -> DISABLE_NODE).
    """
    limit = datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=30)
    if datetime.now() > limit:
        return False  # STATUS: LICENSE_EXPIRED -> DISABLE_NODE
    return True
