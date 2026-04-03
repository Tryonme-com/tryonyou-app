"""
Espejo Digital → Make — patrón DivineoAutomation (uso local o scripts).
En producción Vercel, el flujo de clics va a api/make_mirror_bridge.py (mirror_make_event).
"""
import json
import os
from datetime import datetime, timezone

import requests


class DivineoAutomation:
    """
    Orquestador entre Espejo Digital y Make.
    Sincroniza métricas de usuario, selección de looks y alertas técnicas.
    """

    def __init__(self, make_webhook_url: str | None = None):
        self.webhook_url = (make_webhook_url or "").strip() or (
            os.getenv("MAKE_ESPEJO_WEBHOOK_URL", "").strip()
            or os.getenv("MAKE_WEBHOOK_URL", "").strip()
            or os.getenv("MAKE_LEADS_WEBHOOK_URL", "").strip()
        )
        self.headers = {"Content-Type": "application/json"}

    def sync_pilot_metrics(self, user_data: dict, look_data: dict, action_type: str) -> dict:
        """Acciones típicas: seleccion_perfecta, reserva_probador, silueta."""
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_id": user_data.get("id"),
            "action": action_type,
            "look_details": {
                "brand": look_data.get("brand"),
                "garment_id": look_data.get("id"),
                "size_confirmed": look_data.get("size"),
            },
            "metadata": {"source": "digital_mirror_v1"},
        }

        if not self.webhook_url:
            return {"status": "error", "msg": "URL de Make no configurada (env)."}

        try:
            response = requests.post(
                self.webhook_url,
                data=json.dumps(payload),
                headers=self.headers,
                timeout=10,
            )
        except requests.RequestException as e:
            return {"status": "critical_error", "detail": str(e)}

        if response.status_code == 200:
            return {"status": "success", "msg": f"Evento {action_type} sincronizado."}
        return {"status": "error", "code": response.status_code}
