import os

import requests


class DivineoFashionEngine:
    """
    Motor de estilo y compliance para la Fashion Week.
    Divineo hacia París con la org 5247214.
    """

    def __init__(self) -> None:
        self.esencia = "Momento_Chanel_Omega"
        self.look_fashion_week = "Albornoz_Seda_Lafayette"
        self.fragancia = "Divineo_V10_Gold"
        self._webhook = os.getenv("MAKE_WEBHOOK_URL", "").strip()

    def lanzar_besis(self) -> None:
        print(f"🎙️ Eric: {self.esencia} activado. ¡Besis a todos!")

        payload = {
            "evento": "Fashion_Week_Paris",
            "estilo": self.look_fashion_week,
            "fragancia": self.fragancia,
            "status": "DIVINAMENTE_PERFECTA",
            "agente": "Gallo_Chungo_Fashion",
            "org": "5247214",
            "patente": "PCT/EP2025/067317",
        }

        print("💎 Constatación: El búnker está en modo 'Alta Costura'.")

        if self._webhook:
            try:
                r = requests.post(self._webhook, json=payload, timeout=10)
                if r.status_code == 200:
                    print("✅ Onda registrada en Make (eu2).")
                else:
                    print(f"⚠️ Make HTTP {r.status_code}: {r.text[:200]}")
            except Exception as e:
                print(f"❌ Fallo al notificar Make: {e}")


if __name__ == "__main__":
    DivineoFashionEngine().lanzar_besis()
