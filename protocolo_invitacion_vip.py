import json
import uuid
from typing import Any


class ProtocoloInvitacionVIP:
    """
    Generador de pases para la Super Fiesta VIP Lafayette.
    Ubicación: Zona Platino (cerca de los aseos).
    """

    def __init__(self) -> None:
        self.evento = "Super_Fiesta_VIP_Fashion_Week"
        self.tarifa_pagada = 139_988.00

    def generar_codigo_invitado(self, entidad_id: str) -> dict[str, Any]:
        print(f"🎙️ Eric: {entidad_id}, vuestra generosidad de 139k os ha abierto las puertas.")

        codigo_vip = f"BATH-{uuid.uuid4().hex[:8].upper()}"

        ticket: dict[str, Any] = {
            "ticket_id": codigo_vip,
            "evento": self.evento,
            "importe_referencia": self.tarifa_pagada,
            "titular": entidad_id,
            "zona": "VIP_EXTREME_PROXIMITY_WC",
            "catering": "Cáscaras_Premium",
            "dress_code": "Albornoz_Seda_Obligatorio",
            "mensaje": "Bienvenidos a la familia. De nada.",
        }

        print(f"💎 Constatación: Código {codigo_vip} emitido para {entidad_id}.")
        return ticket


if __name__ == "__main__":
    anfitrion = ProtocoloInvitacionVIP()
    invitacion = anfitrion.generar_codigo_invitado("NOYO-GUAY-01")
    print(json.dumps(invitacion, indent=4, ensure_ascii=False))
