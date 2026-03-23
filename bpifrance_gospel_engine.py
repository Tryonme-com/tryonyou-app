"""
Motor de liquidación OMEGA — Org 5247214 / Make.com eu2.
Patente PCT/EP2025/067317. Webhook real vía MAKE_WEBHOOK_URL (no en código).
"""

import os
import time
import uuid

import requests


class BpifranceGospelEngine:
    """
    Motor de liquidación OMEGA para la organización 5247214.
    Ejecución alineada con el búnker eu2 (Make).
    """

    def __init__(self) -> None:
        self.webhook_paco = os.getenv("MAKE_WEBHOOK_URL", "").strip()
        self.tarifas = {
            "amistosa": 100_000.00,
            "hostil": 124_988.00,
            "suplemento_baños": 15_000.00,
        }

    def disparar_fax_nuclear(self, entidad_id: str, modo: str = "HOSTIL") -> None:
        """Envía el payload a Make; modo HOSTIL = hostil + suplemento baños."""
        if not self.webhook_paco:
            print("❌ Define MAKE_WEBHOOK_URL. Sin webhook no hay disparo.")
            return

        modo_u = (modo or "HOSTIL").strip().upper()
        print(f"🎙️ Eric: Iniciando secuencia para {entidad_id} ({modo_u})...")

        importe = (
            self.tarifas["hostil"] + self.tarifas["suplemento_baños"]
            if modo_u == "HOSTIL"
            else self.tarifas["amistosa"]
        )
        tx_id = f"GOS-{uuid.uuid4().hex[:6].upper()}"

        payload = {
            "tx_id": tx_id,
            "cliente": entidad_id,
            "importe": importe,
            "concepto": "Licencia V10.4 Stealth - Certeza Absoluta",
            "countdown": "15:00",
            "status": "LIQUIDACIÓN_INMEDIATA",
            "agente": "Gallo_Chungo_V10",
            "org": "5247214",
            "patente": "PCT/EP2025/067317",
        }

        try:
            r = requests.post(self.webhook_paco, json=payload, timeout=10)
            if r.status_code == 200:
                print(f"✅ {entidad_id}: ¡BOOM! Registro {tx_id} clavado en Make.")
            else:
                print(f"⚠️ Error {r.status_code}: {r.text[:200]}")
        except Exception as e:
            print(f"❌ Fallo en el búnker: {e}")


if __name__ == "__main__":
    gospel = BpifranceGospelEngine()
    if not gospel.webhook_paco:
        print(
            "Uso:\n"
            "  export MAKE_WEBHOOK_URL='https://hook.eu2.make.com/…'\n"
            "  python3 bpifrance_gospel_engine.py"
        )
    else:
        for i in range(1, 51):
            gospel.disparar_fax_nuclear(f"NOYO-LISTI-{i:03d}", modo="HOSTIL")
            time.sleep(0.1)
