"""
Jules — arranque del runtime de voz (Uvicorn) y modo streaming.

Uso alineado con el estándar de oro:

  from agent_70 import VoiceOrchestrator
  from tools import TryOnMeTools
  import prompts
  import jules

  luna = VoiceOrchestrator(
      name="Luna",
      brand="TryOnMe",
      llm="gemini-1.5-flash",
      tools=TryOnMeTools.get_all(),
      system_prompt=prompts.SYSTEM_PROMPT,
  )
  jules.run(luna, port=8000, streaming=True)
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agent_70 import VoiceOrchestrator


def run(
    orchestrator: VoiceOrchestrator | None = None,
    *,
    port: int = 8000,
    streaming: bool = True,
    host: str = "0.0.0.0",
) -> None:
    import uvicorn

    os.environ["TRYONME_VOICE_STREAMING"] = "1" if streaming else "0"
    if orchestrator is not None:
        import main as voice_main

        voice_main.app.state.voice_orchestrator = orchestrator
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=False,
        ws_ping_interval=float(os.environ.get("JULES_WS_PING_INTERVAL", "20")),
        ws_ping_timeout=float(os.environ.get("JULES_WS_PING_TIMEOUT", "20")),
    )
