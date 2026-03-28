"""
TryOnMe — agente de voz Luna (FastAPI + Twilio + Gemini + tools).

Estructura:
  prompts.py   — personalidad Luna
  tools.py     — consultar_stock, verificar_estado_pedido (conectar a datos reales)

Arranque:
  cd tryonme-voice-agent && pip install -r requirements.txt
  cp .env.example .env   # y pon GEMINI_API_KEY
  python3 main.py

Twilio + ngrok:
  ngrok http 8000
  Webhook «A call comes in» → https://TU-NGROK/voice

Variables: GEMINI_API_KEY (u GOOGLE_API_KEY), GEMINI_MODEL (opcional).

Patente: PCT/EP2025/067317
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response
from twilio.twiml.voice_response import VoiceResponse

import prompts
import tools as tools_mod
from google import genai
from google.genai import types

_ROOT = Path(__file__).resolve().parent
load_dotenv(_ROOT / ".env")

app = FastAPI(title="TryOnMe Voice — Luna")


def _gemini_key() -> str:
    return (
        os.environ.get("GEMINI_API_KEY", "").strip()
        or os.environ.get("GOOGLE_API_KEY", "").strip()
    )


def _model_id() -> str:
    return os.environ.get("GEMINI_MODEL", "gemini-2.0-flash").strip()


def _tool_declarations() -> list[dict]:
    return [
        {
            "name": "consultar_stock",
            "description": (
                "Consulta cuántas unidades hay disponibles para probarse de un producto "
                "en tienda / probador virtual."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "producto": {
                        "type": "string",
                        "description": "Nombre o referencia del producto",
                    },
                },
                "required": ["producto"],
            },
        },
        {
            "name": "verificar_estado_pedido",
            "description": "Consulta el estado de envío de un pedido del cliente.",
            "parameters": {
                "type": "object",
                "properties": {
                    "id_pedido": {
                        "type": "string",
                        "description": "Identificador del pedido",
                    },
                },
                "required": ["id_pedido"],
            },
        },
    ]


def _twiml(xml: str) -> Response:
    return Response(content=xml, media_type="application/xml")


def luna_reply(transcript: str) -> str:
    """Un turno de conversación: Gemini + function calling + tools.py."""
    key = _gemini_key()
    if not key:
        return "El servicio no está configurado. Llama más tarde."

    client = genai.Client(api_key=key)
    tool = types.Tool(function_declarations=_tool_declarations())
    config = types.GenerateContentConfig(
        tools=[tool],
        system_instruction=prompts.SYSTEM_PROMPT,
    )

    contents: list[types.Content] = [
        types.Content(
            role="user",
            parts=[
                types.Part(
                    text=(
                        f"Transcripción del cliente (llamada de voz): {transcript}\n"
                        "Si usas herramientas, incorpora el resultado en una respuesta final "
                        "de una o dos frases muy cortas en español, adecuadas para leer en voz alta."
                    ),
                ),
            ],
        ),
    ]

    for _ in range(6):
        response = client.models.generate_content(
            model=_model_id(),
            contents=contents,
            config=config,
        )
        cands = getattr(response, "candidates", None) or []
        if not cands:
            return "No te he entendido bien. ¿Lo repites, por favor?"
        parts = cands[0].content.parts or []

        fcalls = [p.function_call for p in parts if getattr(p, "function_call", None)]
        texts = [p.text for p in parts if getattr(p, "text", None)]

        if not fcalls:
            reply = "".join(texts).strip()
            return reply or "¿Puedes repetirlo?"

        contents.append(cands[0].content)

        fr_parts: list[types.Part] = []
        for fc in fcalls:
            name = fc.name
            raw_args = fc.args or {}
            args = dict(raw_args) if hasattr(raw_args, "items") else {}
            fn = tools_mod.TOOL_DISPATCH.get(name)
            try:
                out = fn(args) if fn else "Esa consulta no está disponible."
            except Exception as e:
                out = f"No se pudo completar la consulta: {e}"
            fr_parts.append(
                types.Part.from_function_response(
                    name=name,
                    response={"result": out},
                ),
            )
        contents.append(types.Content(role="user", parts=fr_parts))

    return "Demasiadas consultas seguidas. Prueba de nuevo en un instante."


@app.get("/health")
async def health() -> dict:
    return {"ok": True, "gemini_configured": bool(_gemini_key())}


@app.post("/voice")
async def voice_endpoint() -> Response:
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

    resp = VoiceResponse()
    if not transcript:
        resp.say(
            "No te he oído bien. ¿Puedes repetirlo?",
            voice="Polly.Conchita",
            language="es-ES",
        )
    else:
        try:
            text = luna_reply(transcript)
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


if __name__ == "__main__":
    import uvicorn

    if not _gemini_key():
        print("Define GEMINI_API_KEY (o GOOGLE_API_KEY) en .env o el entorno.", file=sys.stderr)
        raise SystemExit(1)
    host = os.environ.get("VOICE_AGENT_HOST", "0.0.0.0")
    port = int(os.environ.get("VOICE_AGENT_PORT", "8000"))
    uvicorn.run(app, host=host, port=port)
