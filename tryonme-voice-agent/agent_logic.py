"""
Orquestación Agent 70 — estados de conversación telefónica TryOnMe.

Flujo lógico (no sustituye al LLM; refina tono y métricas de sesión).
"""

from __future__ import annotations

from enum import Enum, auto
import re


class AgentState(Enum):
    SALUDO = auto()
    CONSULTA_STOCK = auto()
    GESTION_PEDIDO = auto()
    CIERRE = auto()


_STOCK_HINTS = re.compile(
    r"\b(stock|unidad|unidades|disponible|talla|probar|proband|chaqueta|vestido|pantal|talla)\b",
    re.I,
)
_PEDIDO_HINTS = re.compile(
    r"\b(pedido|envío|envio|seguimiento|tracking|llega|paquete|repart)\b",
    re.I,
)
_CIERRE_HINTS = re.compile(
    r"\b(adios|adiós|hasta luego|chao|gracias.*colg|cuélga|cuelga|eso es todo|nada más)\b",
    re.I,
)


def infer_next_state(transcript: str, current: AgentState) -> AgentState:
    t = (transcript or "").strip()
    if not t:
        return current
    if _CIERRE_HINTS.search(t):
        return AgentState.CIERRE
    if _STOCK_HINTS.search(t):
        return AgentState.CONSULTA_STOCK
    if _PEDIDO_HINTS.search(t):
        return AgentState.GESTION_PEDIDO
    if current == AgentState.SALUDO:
        return current
    return current


def label_for_logs(state: AgentState) -> str:
    return state.name
