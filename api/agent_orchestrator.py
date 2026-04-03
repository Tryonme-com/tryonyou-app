"""
API — Agente Perfecto Orquestador
Endpoints:
  GET  /api/agents/status   — snapshot del estado de los 61 agentes + mesa
  POST /api/agents/run      — lanza (o re-lanza) la orquestación completa
  GET  /api/mesa/decision   — última decisión de la Mesa de los Listos
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from agente_perfecto_orquestador import (
    AgentePerfectoOrquestador,
    ESTADO_PATH,
)

# Instancia compartida (vida del proceso)
_orquestador: AgentePerfectoOrquestador = AgentePerfectoOrquestador()


def _load_estado() -> dict[str, Any] | None:
    """Carga el último estado persistido en disco, si existe."""
    try:
        if ESTADO_PATH.is_file():
            raw = ESTADO_PATH.read_text(encoding="utf-8")
            return json.loads(raw) if raw.strip() else None
    except (OSError, json.JSONDecodeError):
        pass
    return None


def handle_agents_status() -> dict[str, Any]:
    """GET /api/agents/status — estado actual de los 61 agentes."""
    stored = _load_estado()
    if stored:
        return {"status": "ok", **stored}
    return {"status": "ok", **_orquestador.get_status_snapshot()}


def handle_agents_run() -> dict[str, Any]:
    """POST /api/agents/run — ejecuta la orquestación completa."""
    global _orquestador
    _orquestador = AgentePerfectoOrquestador()
    try:
        resultado = asyncio.run(_orquestador.orquestar_todos())
        completados = sum(
            1 for a in resultado["agents"] if a["status"] == "done"
        )
        return {
            "status": "ok",
            "message": (
                f"Orquestación completada: "
                f"{completados}/{len(resultado['agents'])} agentes listos."
            ),
            "result": resultado,
        }
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


def handle_mesa_decision() -> dict[str, Any]:
    """GET /api/mesa/decision — última decisión de la Mesa de los Listos."""
    stored = _load_estado()
    if stored and "mesa_decision" in stored:
        return {"status": "ok", "mesa_decision": stored["mesa_decision"]}
    snapshot = _orquestador.get_status_snapshot()
    ideas = snapshot.get("mesa_ideas", [])
    return {
        "status": "ok",
        "mesa_decision": {
            "integrantes": ["LISTOS", "GEMINI", "COPILOT", "MANUS", "AGENTE70", "JULES", "TRYONYOUAGENT"],
            "ideas": ideas,
            "message": "Sin orquestación activa. Llama POST /api/agents/run primero.",
        },
    }
