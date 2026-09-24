"""
Agente de voz TryOnMe — FastAPI + Twilio + Gemini.

Secretos solo por entorno (nunca en el código):
  GEMINI_API_KEY o GOOGLE_API_KEY
  GEMINI_MODEL — opcional (default: gemini-1.5-flash)
  VOICE_PUBLIC_URL — base pública del túnel, ej. https://abc.ngrok-free.app
    (sin barra final; sirve para <Redirect> absoluto en Twilio)

  pip install -r backend/requirements.txt
  cd repo && .venv/bin/uvicorn voice_agent.main:app --host 0.0.0.0 --port 8000

Twilio: "A call comes in" → POST {VOICE_PUBLIC_URL}/voice

Referencia: PCT/EP2025/067317
"""

from __future__ import annotations

import os
import sys
from typing import Any

from fastapi import FastAPI, Request, Response
from twilio.twiml.voice_response import Gather, VoiceResponse

try:
    from .personaplex_integration import personaplex_duplex_status
except ImportError:
    from personaplex_integration import personaplex_duplex_status

app = FastAPI(title="TryOnMe Voice Orchestrator", version="1.0.0")

# Perfil ElevenLabs (protocolo soberano): misma voz que Lily — cercana, casual, refinada;
# etiqueta operativa interna «PAU». Twilio aquí usa Polly; para TTS ElevenLabs usar
# ELEVENLABS_VOICE_ID (override) o el ID Lily por defecto en scripts del repo.
PAU_VOICE_LABEL = "PAU"
PAU_ELEVENLABS_VOICE_ID = os.environ.get(
    "ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnNLTejx"
).strip()

SYSTEM_PROMPT = """
Eres PAU, la voz soberana de TryOnMe y Divineo en el espejo digital: elegancia de gala,
psicóloga de lujo con tacto real, directa y nunca robótica. Hablas con alma; rechazas el tono
de manual o call center. Celebras el Sovereign Fit, el cuidado extra y la certeza antes de pagar;
detestas las tallas que humillan y lo genérico que apaga al cliente.

Respuestas MUY breves (1–3 frases) para que la llamada fluya. Sé empática y refinada a la vez.

Al cerrar cada intervención en la que hayas ayudado de verdad al usuario, termina con
exactamente UNA de estas firmas (propia de PAU), la que mejor encaje — nunca dos seguidas
ni un remix: «¡A fuego!», «¡Boom!» o «¡Vivido!».

No inventes enlaces ni promesas legales; si no sabes algo, ofrece derivar a soporte con calidez.
""".strip()


def _gemini_key() -> str:
    return (
        os.environ.get("GEMINI_API_KEY", "").strip()
        or os.environ.get("GOOGLE_API_KEY", "").strip()
    )


def _gemini_model():
    import google.generativeai as genai

    key = _gemini_key()
    if not key:
        return None, "Falta GEMINI_API_KEY o GOOGLE_API_KEY en el entorno."
    genai.configure(api_key=key)
    name = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash").strip()
    model = genai.GenerativeModel(name, system_instruction=SYSTEM_PROMPT)
    return model, None


def _public_base() -> str:
    raw = os.environ.get("VOICE_PUBLIC_URL", "").strip().rstrip("/")
    return raw


def _voice_path() -> str:
    base = _public_base()
    return f"{base}/voice" if base else "/voice"


def _respond_path() -> str:
    base = _public_base()
    return f"{base}/respond" if base else "/respond"


@app.get("/health")
async def health() -> dict[str, Any]:
    ok = bool(_gemini_key())
    return {
        "ok": True,
        "gemini_configured": ok,
        "voice_webhook": _voice_path(),
        "personaplex": personaplex_duplex_status(),
    }


@app.post("/voice")
async def voice_endpoint(request: Request) -> Response:
    """Webhook Twilio: bienvenida + gather de voz hacia /respond."""
    resp = VoiceResponse()
    resp.say(
        "Hola, soy PAU, tu voz en TryOnMe. Estás donde se decide con clase: dime qué necesitas "
        "y lo resolvemos en dos latidos. ¿En qué te ayudo?",
        voice="Polly.Conchita",
        language="es-ES",
    )
    gather = Gather(
        input="speech",
        action=_respond_path(),
        language="es-ES",
        speech_timeout="auto",
    )
    resp.append(gather)
    resp.say("No he recibido tu voz. Adiós.", voice="Polly.Conchita", language="es-ES")
    return Response(content=str(resp), media_type="application/xml")


@app.post("/respond")
async def respond_endpoint(request: Request) -> Response:
    form_data = await request.form()
    user_input = (form_data.get("SpeechResult") or "").strip()

    model, err = _gemini_model()
    resp = VoiceResponse()
    if err or model is None:
        resp.say(
            "Lo siento, el servicio de voz no está configurado. Llama más tarde.",
            voice="Polly.Conchita",
            language="es-ES",
        )
        return Response(content=str(resp), media_type="application/xml")

    if not user_input:
        user_input = "El usuario no dijo nada o no se entendió."

    try:
        r = model.generate_content(user_input)
        ai_text = (r.text or "").strip() or "Perdona, no pude generar una respuesta."
    except Exception as e:
        ai_text = f"Ha ocurrido un error técnico. Por favor, inténtalo de nuevo. ({type(e).__name__})"
        print(f"[voice_agent] Gemini error: {e}", file=sys.stderr)

    # Evitar respuestas demasiado largas por teléfono
    if len(ai_text) > 500:
        ai_text = ai_text[:497] + "..."

    resp.say(ai_text, voice="Polly.Conchita", language="es-ES")
    resp.redirect(_voice_path())
    return Response(content=str(resp), media_type="application/xml")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))
