"""
DivineoPauController — controlador maestro para la interfaz de lujo V10.2.

Gestiona la identidad de Pau (Pavo Real Blanco) y sus estados de experiencia,
asociando cada estado a un activo de vídeo y una frase característica.
"""

from __future__ import annotations

VERSION = "10.2"
PAU_ID = "Real_White_Peacock_Natural"
MOTTO = "El fin de las tallas ha llegado"

_PAU_STATES: dict[str, dict[str, str]] = {
    "welcome": {
        "video": "pau_talking_natural.mp4",
        "phrase": "Lo mejor es que no sabemos de tallas… pero sabemos que vas bien divina.",
    },
    "success": {
        "video": "pau_nodding_natural.mp4",
        "phrase": "Selección perfecta. Te queda impecable.",
    },
    "joy": {
        "video": "pau_laughing_natural.mp4",
        "phrase": "¡Divineo puro! Ese look es para ti.",
    },
}


class DivineoPauController:
    """
    Controlador maestro para la interfaz de lujo V10.2.
    Gestiona la identidad de Pau (Pavo Real Blanco) y sus estados.
    """

    def __init__(self) -> None:
        self.version = VERSION
        self.pau_id = PAU_ID
        self.motto = MOTTO

    def get_pau_state(self, mood: str = "welcome") -> dict[str, str]:
        """
        Retorna el activo de vídeo y el mensaje según el estado de la experiencia.

        :param mood: Estado deseado — «welcome», «success» o «joy».
                     Si no se reconoce, se devuelve el estado «welcome».
        :returns: Diccionario con claves «video» y «phrase».
        """
        return _PAU_STATES.get(mood, _PAU_STATES["welcome"])
