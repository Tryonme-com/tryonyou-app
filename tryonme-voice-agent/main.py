"""
TryOnMe — Luna (FastAPI + Twilio + Gemini + Agent 70 + Jules).

Arranque:
  ./run.sh
  # o: python3 main.py

Estándar Agent 70 + Jules:
  from agent_70 import VoiceOrchestrator
  from tools import TryOnMeTools
  import prompts, jules
  luna = VoiceOrchestrator(
      name="Luna",
      brand="TryOnMe",
      llm="gemini-1.5-flash",
      tools=TryOnMeTools.get_all(),
      system_prompt=prompts.SYSTEM_PROMPT,
  )
  jules.run(luna, port=8000, streaming=True)

Patente: PCT/EP2025/067317
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response, WebSocket, WebSocketDisconnect
from twilio.twiml.voice_response import VoiceResponse

import agent_logic
import jules_config
import prompts
import tools as tools_mod
from agent_70 import VoiceOrchestrator

_ROOT = Path(__file__).resolve().parent
load_dotenv(_ROOT / ".env")

app = FastAPI(title="TryOnMe Voice — Luna / Agent 70")

# Sesión por llamada Twilio (CallSid) -> estado orquestador
_sessions: dict[str, agent_logic.AgentState] = {}


def _gemini_key() -> str:
    return (
        os.environ.get("GEMINI_API_KEY", "").strip()
        or os.environ.get("GOOGLE_API_KEY", "").strip()
    )


def _model_id() -> str:
    return os.environ.get("GEMINI_MODEL", "gemini-1.5-flash").strip()


def _get_orchestrator(request: Request) -> VoiceOrchestrator:
    st = getattr(request.app.state, "voice_orchestrator", None)
    if st is not None:
        return st
    orch = VoiceOrchestrator(
        name="Luna",
        brand="TryOnMe",
        llm=_model_id(),
        tools=tools_mod.TryOnMeTools.get_all(),
        system_prompt=prompts.SYSTEM_PROMPT,
    )
    request.app.state.voice_orchestrator = orch
    return orch


def _twiml(xml: str) -> Response:
    return Response(content=xml, media_type="application/xml")


def luna_reply(request: Request, transcript: str) -> str:
    """Un turno de IA (Gemini + function calling)."""
    return _get_orchestrator(request).reply(transcript)


@app.get("/health")
async def health() -> dict[str, Any]:
    return {
        "ok": True,
        "gemini_configured": bool(_gemini_key()),
        "model_default": _model_id(),
        "jules_ws_budget_ms": jules_config.WEBSOCKET_LATENCY_BUDGET_MS,
    }


@app.post("/voice")
async def voice_endpoint() -> Response:
    """Webhook inicial Twilio (<Gather speech>)."""
    resp = VoiceResponse()
    resp.say(
        "Hola, soy Luna de TryOnMe. ¿En qué puedo ayudarte?",
        voice="Polly.Conchita",
        language="es-ES",
    )
    resp.gather(
        input="speech",
        action="/respond",
        language="es-ES",
        speech_timeout="auto",
    )
    resp.say(
        "No he oído nada. Visita tryonyou.org o llama de nuevo. Hasta pronto.",
        voice="Polly.Conchita",
        language="es-ES",
    )
    return _twiml(str(resp))


@app.post("/respond")
async def respond_endpoint(request: Request) -> Response:
    form = await request.form()
    transcript = (form.get("SpeechResult") or form.get("speechResult") or "").strip()
    call_sid = (form.get("CallSid") or "local").strip()

    prev = _sessions.get(call_sid, agent_logic.AgentState.SALUDO)
    nxt = agent_logic.infer_next_state(transcript, prev)
    _sessions[call_sid] = nxt
    print(
        f"[Agent70] CallSid={call_sid} state={agent_logic.label_for_logs(prev)}"
        f" -> {agent_logic.label_for_logs(nxt)}",
        file=sys.stderr,
    )

    resp = VoiceResponse()
    if nxt == agent_logic.AgentState.CIERRE and transcript:
        resp.say(
            "Gracias por llamar a TryOnMe. Hasta pronto.",
            voice="Polly.Conchita",
            language="es-ES",
        )
        return _twiml(str(resp))

    if not transcript:
        resp.say(
            "No te he oído bien. ¿Puedes repetirlo?",
            voice="Polly.Conchita",
            language="es-ES",
        )
    else:
        try:
            text = luna_reply(request, transcript)
        except Exception as e:
            print(f"[Luna] error: {e}", file=sys.stderr)
            text = "Ha ocurrido un problema técnico. Prueba en unos segundos."
        resp.say(text, voice="Polly.Conchita", language="es-ES")

    resp.gather(
        input="speech",
        action="/respond",
        language="es-ES",
        speech_timeout="auto",
    )
    resp.say(
        "Si necesitas algo más, sigue hablando. Gracias por llamar a TryOnMe.",
        voice="Polly.Conchita",
        language="es-ES",
    )
    return _twiml(str(resp))


@app.websocket("/media-stream")
async def media_stream_ws(websocket: WebSocket) -> None:
    """
    Jules: WebSocket para Twilio Media Streams (o pruebas).
    El accept debe completarse dentro del presupuesto de latencia configurado.
    """
    t0 = time.perf_counter()
    await websocket.accept()
    elapsed_ms = (time.perf_counter() - t0) * 1000
    if elapsed_ms > jules_config.WEBSOCKET_LATENCY_BUDGET_MS:
        print(
            f"[Jules] WS accept {elapsed_ms:.0f}ms "
            f"(presupuesto {jules_config.WEBSOCKET_LATENCY_BUDGET_MS}ms)",
            file=sys.stderr,
        )
    try:
        await websocket.send_text('{"event":"connected","protocol":"Call"}')
        while True:
            msg = await websocket.receive_text()
            raw = msg.encode("utf-8")
            if len(raw) > jules_config.MAX_WS_MESSAGE_BYTES:
                break
            t_ack = time.perf_counter()
            await websocket.send_json({"event": "mark", "mark": {"name": "jules_ack"}})
            ack_ms = (time.perf_counter() - t_ack) * 1000
            if ack_ms > jules_config.STREAM_ACK_TARGET_MS:
                print(f"[Jules] ack lento: {ack_ms:.0f}ms", file=sys.stderr)
    except WebSocketDisconnect:
        pass


if __name__ == "__main__":
    import uvicorn

    if not _gemini_key():
        print("Define GEMINI_API_KEY (o GOOGLE_API_KEY) en .env o el entorno.", file=sys.stderr)
        raise SystemExit(1)
    host = os.environ.get("VOICE_AGENT_HOST", "0.0.0.0")
    port = int(os.environ.get("VOICE_AGENT_PORT", "8000"))
    uvicorn.run(app, host=host, port=port)
