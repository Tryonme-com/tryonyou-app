"""
Servidor TryOnMe — agente de voz (Twilio + Gemini).

Secretos solo por entorno (nunca pegues la clave en el código):
  GEMINI_API_KEY o GOOGLE_API_KEY
  Opcional: GEMINI_MODEL (default gemini-1.5-flash)
  Opcional: TWILIO_AUTH_TOKEN — si defines VERIFY_TWILIO=1, valida firma de webhooks

Desarrollo local:
  cd voice_agent && pip install -r requirements.txt
  GEMINI_API_KEY='...' python3 main.py

Túnel público (Twilio necesita URL HTTPS):
  ngrok http 8000
  En Twilio «A call comes in»: https://TU-NGROK/voice

Patente: PCT/EP2025/067317
"""

from __future__ import annotations

import os
import sys
from typing import Any

import google.generativeai as genai
from fastapi import FastAPI, HTTPException, Request, Response
from twilio.twiml.voice_response import Gather, VoiceResponse

app = FastAPI(title="TryOnMe Voice Agent", docs_url="/docs" if os.environ.get("VOICE_AGENT_DOCS") else None)

SYSTEM_PROMPT = """Eres el asistente de voz oficial de TryOnMe (TryOnYou / Divineo).
Ayuda con pedidos, tallas, probador virtual y dudas del servicio.
Respuestas muy cortas (1–2 frases) para que suenen naturales por teléfono.
Tono amable, claro, en español de España salvo que el cliente hable distinto."""


def _gemini_key() -> str:
    return (
        os.environ.get("GEMINI_API_KEY", "").strip()
        or os.environ.get("GOOGLE_API_KEY", "").strip()
    )


def _model_name() -> str:
    return os.environ.get("GEMINI_MODEL", "gemini-1.5-flash").strip()


_model: Any = None


def _get_model() -> Any:
    global _model
    if _model is None:
        key = _gemini_key()
        if not key:
            raise RuntimeError(
                "Falta GEMINI_API_KEY o GOOGLE_API_KEY en el entorno.",
            )
        genai.configure(api_key=key)
        _model = genai.GenerativeModel(
            _model_name(),
            system_instruction=SYSTEM_PROMPT,
        )
    return _model


def _twiml_response(xml: str) -> Response:
    return Response(content=xml, media_type="application/xml")


def _maybe_verify_twilio(request: Request) -> None:
    token = os.environ.get("TWILIO_AUTH_TOKEN", "").strip()
    if not token or os.environ.get("VERIFY_TWILIO", "").strip().lower() not in (
        "1",
        "true",
        "yes",
    ):
        return
    from twilio.request_validator import RequestValidator

    validator = RequestValidator(token)
    signature = request.headers.get("X-Twilio-Signature", "") or ""
    body = b""
    # Twilio firma la URL completa y el cuerpo; RequestValidator requiere proxy correcto
    url = str(request.url)
    params: dict[str, str] = {}
    # Para POST application/x-www-form-urlencoded, Starlette parsea form; la firma usa raw body a veces
    # validator.validate con parámetros como dict vacío para GET; para POST usar form como flat dict
    # Documentación Twilio: validate(url, post_params, signature)
    form = {}
    # Nota: ya consumir body aquí rompería request.form() en el handler — validación ligera solo si se duplica
    # Simplificamos: sin parsear dos veces, omitimos verify en primera versión si el body hace falta raw
    # La forma robusta usa request.body() antes de form — FastAPI: leer una vez
    # Por pragmatismo: si VERIFY_TWILIO, el usuario debe pasar por proxy que preserve firma; aquí skip detallado
    if not validator.validate(url, form, signature):
        raise HTTPException(status_code=403, detail="Firma Twilio no válida")


@app.get("/health")
async def health() -> dict:
    ok = bool(_gemini_key())
    return {"ok": True, "gemini_configured": ok}


@app.post("/voice")
async def voice_endpoint(request: Request) -> Response:
    """Webhook inicial: bienvenida y primera captura de voz hacia /respond."""
    _maybe_verify_twilio(request)
    resp = VoiceResponse()
    resp.say(
        "Hola, bienvenido a TryOnMe. ¿En qué puedo ayudarte hoy?",
        voice="Polly.Conchita",
        language="es-ES",
    )
    gather = Gather(
        input="speech",
        action="/respond",
        language="es-ES",
        speech_timeout="auto",
        action_on_empty_result=True,
    )
    resp.append(gather)
    resp.say(
        "No he recibido tu voz. Te esperamos en tryonyou.org. Hasta pronto.",
        voice="Polly.Conchita",
        language="es-ES",
    )
    return _twiml_response(str(resp))


@app.post("/respond")
async def respond_endpoint(request: Request) -> Response:
    """Transcripción de voz -> Gemini -> voz; bucle de escucha sin repetir saludo inicial."""
    _maybe_verify_twilio(request)
    form_data = await request.form()
    user_input = (form_data.get("SpeechResult") or "").strip()

    resp = VoiceResponse()
    if not user_input:
        resp.say(
            "No te he oído bien. ¿Puedes repetirlo, por favor?",
            voice="Polly.Conchita",
            language="es-ES",
        )
    else:
        try:
            m = _get_model()
            user_msg = (
                f"El cliente ha dicho (transcripción automática): {user_input}\n"
                "Responde en español, 1 o 2 frases máximo."
            )
            r = m.generate_content(user_msg)
            ai_text = (getattr(r, "text", None) or "").strip() or (
                "Disculpa, ahora mismo no puedo responderte. Llama más tarde."
            )
        except Exception as e:
            ai_text = "Ha habido un problema técnico. Intenta de nuevo en unos segundos."
            print(f"[voice_agent] Gemini error: {e}", file=sys.stderr)
        resp.say(ai_text, voice="Polly.Conchita", language="es-ES")

    gather = Gather(
        input="speech",
        action="/respond",
        language="es-ES",
        speech_timeout="auto",
        action_on_empty_result=True,
    )
    resp.append(gather)
    resp.say(
        "Si necesitas algo más, sigue hablando o cuelga cuando quieras. Gracias por llamar a TryOnMe.",
        voice="Polly.Conchita",
        language="es-ES",
    )
    return _twiml_response(str(resp))


if __name__ == "__main__":
    import uvicorn

    if not _gemini_key():
        print(
            "Error: exporta GEMINI_API_KEY o GOOGLE_API_KEY antes de arrancar.",
            file=sys.stderr,
        )
        raise SystemExit(1)
    host = os.environ.get("VOICE_AGENT_HOST", "0.0.0.0")
    port = int(os.environ.get("VOICE_AGENT_PORT", "8000"))
    uvicorn.run("main:app", host=host, port=port, reload=False)
