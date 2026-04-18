"""Motor de conversación PAU con control de protocolo soberano (Error 402)."""

from __future__ import annotations

import logging
from typing import Any, Mapping

__all__ = ["PauAgent"]

logger = logging.getLogger(__name__)


class PauAgent:
    """Agente conversacional PAU con personalidad de Eric Lafayette."""

    def __init__(self) -> None:
        self.name = "Pau"
        self.persona = "Eric Lafayette"
        self.status = "ACTIVE"

    def check_sovereign_protocol(self, user_account: Mapping[str, Any]) -> bool:
        """Valida protocolo soberano y actualiza ``status`` a ACTIVE/RESTRICTED."""
        is_restricted = bool(user_account.get("status_402", False))
        if is_restricted:
            self.status = "RESTRICTED"
            logger.info("pau_agent_restricted account_status_402=true")
            return False
        self.status = "ACTIVE"
        return True

    def generate_response(self, user_input: str, user_account: Mapping[str, Any]) -> str:
        """Genera respuesta según estado de protocolo y personalidad configurada."""
        if not self.check_sovereign_protocol(user_account):
            return (
                "Oh, cher, parece que nuestro protocolo soberano ha pausado nuestras "
                "herramientas por un momento. Un ajuste técnico y estaremos creando "
                "magia de nuevo."
            )

        return (
            "Como diría Yves Saint Laurent, el estilo es eterno... sobre tu petición: "
            f"{user_input}. Déjame ver cómo hacerlo impecable."
        )
