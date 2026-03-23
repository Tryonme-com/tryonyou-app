import os

import requests


class CaballeroGospelEngine:
    """Centro de Mando eu2 — org 5247214. Webhook: MAKE_WEBHOOK_URL."""

    def __init__(self) -> None:
        self.webhook_paco = os.getenv("MAKE_WEBHOOK_URL", "").strip()
        self.tarifa_hostil = 124_988.00
        self.suplemento_baños = 15_000.00
        self.total = self.tarifa_hostil + self.suplemento_baños

    def cobrar_con_divineo(self, entidad_id: str) -> None:
        if not self.webhook_paco:
            print("❌ Define MAKE_WEBHOOK_URL para disparar el webhook.")
            return

        print(f"🎙️ Eric: {entidad_id}, hemos detectado vuestro interés... 'peculiar'.")

        mensaje_divino = (
            "Estimados caballeros, su acceso a la V10.4 ha sido regularizado. "
            "Se han ubicado en la zona de cortesía junto a los servicios. "
            "Gracias por su contribución de 139.988 €. De nada."
        )

        payload = {
            "entidad": entidad_id,
            "importe": self.total,
            "ubicacion": "Mesa_Cerca_Baños",
            "notificacion": mensaje_divino,
            "status": "LIQUIDADO_CON_ESTILO",
            "patente": "PCT/EP2025/067317",
            "org": "5247214",
        }

        try:
            r = requests.post(self.webhook_paco, json=payload, timeout=10)
            if r.status_code == 200:
                print(f"✅ {entidad_id}: Cobrado y notificado. ¡BOOM!")
                print(f"💎 Mensaje: '{mensaje_divino}'")
            else:
                print(f"⚠️ HTTP {r.status_code}: {r.text[:200]}")
        except Exception as e:
            print(f"❌ Error en la seda: {e}")


if __name__ == "__main__":
    CaballeroGospelEngine().cobrar_con_divineo("NOYO-GUAY-01")
