import os
import time
import uuid

import requests


class GalloChungoCursor:
    def __init__(self):
        self.webhook = os.getenv("MAKE_WEBHOOK_URL", "").strip()
        self.tarifas = {
            "amistosa": 100_000.0,
            "hostil": 124_988.0,
            "suplemento": 15_000.0,
        }

    def disparar_fax(self, id_noyo: str, es_guay: bool = False) -> None:
        if not self.webhook:
            print("❌ Define MAKE_WEBHOOK_URL (webhook Make.com real). No se envía nada.")
            return

        tx_id = f"DIV-{uuid.uuid4().hex[:6].upper()}"
        monto = (
            self.tarifas["hostil"] + self.tarifas["suplemento"]
            if es_guay
            else self.tarifas["amistosa"]
        )

        print(f"🎙️ Eric: {'🚨 MESA BAÑOS' if es_guay else '💎 AMISTOSA'} para {id_noyo}...")

        payload = {
            "tx": tx_id,
            "cliente": id_noyo,
            "monto": monto,
            "countdown": "15:00" if es_guay else "31-Marzo",
            "status": "V10.4_STEALTH_LIVE",
            "org": "5247214",
        }

        try:
            r = requests.post(self.webhook, json=payload, timeout=10)
            if r.status_code == 200:
                print(f"✅ ¡BOOM! Tío Paco ha clavado los {monto}€ de {id_noyo}.")
            else:
                print(f"⚠️ Error {r.status_code} en webhook. Cuerpo: {r.text[:200]}")
        except Exception as e:
            print(f"❌ Fallo de conexión: {e}")


if __name__ == "__main__":
    motor = GalloChungoCursor()
    targets = [f"NOYO-{i:03d}" for i in range(1, 51)]
    targets.append("NOYO-GUAY-PREMIUM")

    if not motor.webhook:
        print(
            "Uso: export MAKE_WEBHOOK_URL='https://hook.eu2.make.com/...'\n"
            "     python3 gallo_omega.py"
        )
    else:
        for t in targets:
            motor.disparar_fax(t, es_guay=("GUAY" in t))
            time.sleep(0.2)
