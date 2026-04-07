"""
Espejo Digital → Make — orquestador DivineoAutomation (uso local o scripts).
En Vercel, el flujo de clics va a api/mirror_digital_make.py.

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone

import requests


def _default_make_webhook_url() -> str:
    for key in (
        "MAKE_MIRROR_DIGITAL_WEBHOOK_URL",
        "MAKE_ESPEJO_DIGITAL_WEBHOOK_URL",
        "MAKE_WEBHOOK_URL",
        "MAKE_LEADS_WEBHOOK_URL",
    ):
        u = (os.getenv(key) or "").strip()
        if u:
            return u
    return ""


class DivineoAutomation:
    """
    Orquestador para automatizaciones entre el Espejo Digital y Make.
    Sincroniza métricas de usuario, selección de looks y alertas técnicas.
    """

    def __init__(self, make_webhook_url: str | None = None):
        self.webhook_url = (make_webhook_url or "").strip() or _default_make_webhook_url()
        self.headers = {"Content-Type": "application/json"}

    def sync_pilot_metrics(
        self,
        user_data: dict,
        look_data: dict,
        action_type: str,
    ) -> dict:
        """
        Envía los datos del piloto a Make.
        Acciones: 'seleccion_perfecta', 'reserva_probador', 'silueta'.
        """
        # datetime.now(timezone.utc): aware UTC (evita datetime.utcnow() deprecado en 3.12+).
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_id": user_data.get("id"),
            "action": action_type,
            "look_details": {
                "brand": look_data.get("brand", "Lafayette"),
                "garment_id": look_data.get("id"),
                "size_confirmed": look_data.get("size"),
            },
            "metadata": {
                "source": "digital_mirror_v1",
                "environment": "production",
            },
        }

        try:
            if not self.webhook_url:
                raise ValueError("URL de Webhook de Make no configurada.")

            response = requests.post(
                self.webhook_url,
                data=json.dumps(payload),
                headers=self.headers,
                timeout=10,
            )

            if response.status_code == 200:
                return {"status": "success", "msg": f"Evento {action_type} sincronizado."}
            return {"status": "error", "code": response.status_code}

        except Exception as e:
            return {"status": "critical_error", "detail": str(e)}


if __name__ == "__main__":
    url = _default_make_webhook_url()
    if not url:
        print(
            "Defina MAKE_MIRROR_DIGITAL_WEBHOOK_URL o MAKE_WEBHOOK_URL en el entorno "
            "para ejecutar una prueba; no se enviarán peticiones sin URL."
        )
        raise SystemExit(0)
    tracker = DivineoAutomation(url)
    test_user = {"id": "user_88_pau"}
    test_look = {"brand": "Balmain", "id": "BLM-992", "size": "M"}
    print(tracker.sync_pilot_metrics(test_user, test_look, "seleccion_perfecta"))
