"""
PauDisneyGuideV10_2 — Guía experiencial del avatar Pau (TryOnYou V10.2).

Coordina el flujo de experiencia del usuario con las animaciones y acciones
del avatar Pau (referencia: White_Peacock_Natural_r5vr2He).

Etapas de la jornada:
  ENTRADA      — Pau emerge de la moneda y da la bienvenida.
  ESCANEANDO   — Pau camina sobre la interfaz mientras se analiza la silueta.
  LOOK_READY   — Pau valida el look con El Chasquido Maestro.
  SALIDA       — Pau regresa a la moneda y se despide.

Clips de animación: formato .webm con canal alfa (transparencia).
"""

from __future__ import annotations

from typing import Any, Dict, Optional

_JOURNEY: Dict[str, Dict[str, str]] = {
    "ENTRADA": {
        "pau_action": "Emerger_de_Moneda",
        "gesture": "Vuelo_Hacia_Centro",
        "speech": "Bienvenida_Magica",
    },
    "ESCANEANDO": {
        "pau_action": "Caminar_Sobre_Interfaz",
        "gesture": "Curiosidad_Natural",
        "speech": "Analisis_Biometrico_En_Curso",
    },
    "LOOK_READY": {
        "pau_action": "El_Chasquido_Maestro",
        "gesture": "Apertura_Abanico_Total",
        "speech": "Validacion_Divineo",
    },
    "SALIDA": {
        "pau_action": "Regreso_A_Moneda",
        "gesture": "Reverencia_Final",
        "speech": "Despedida_Elegante",
    },
}


class PauDisneyGuideV10_2:
    """Guía de experiencia V10.2 del avatar Pau."""

    def __init__(self) -> None:
        self.guide_state: str = "IDLE_IN_COIN"
        self.user_position: str = "LANDING"
        self.pau_reference: str = "White_Peacock_Natural_r5vr2He"

    def update_experience_flow(self, user_action: str) -> Dict[str, str]:
        """Devuelve el mapeo de acciones de Pau para la etapa indicada.

        Si *user_action* no está reconocida se devuelve el mapeo de ENTRADA.
        """
        return _JOURNEY.get(user_action, _JOURNEY["ENTRADA"])

    def sync_animation_engine(self, state: Optional[Any] = None) -> None:
        """Dispara los clips .webm con canal alfa correspondientes al estado."""
        pass


if __name__ == "__main__":
    guide = PauDisneyGuideV10_2()
    print(f"Guía Pau V10.2 activado. Estado actual: {guide.guide_state}")
