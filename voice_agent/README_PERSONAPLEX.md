# PersonaPlex (NVIDIA) y `voice_agent` — full-duplex

[NVIDIA/personaplex](https://github.com/NVIDIA/personaplex) es un modelo **speech-to-speech** en tiempo real (arquitectura Moshi, licencia NVIDIA + pesos en Hugging Face). Requiere **HF_TOKEN**, GPU adecuada, servidor `moshi`, códec Opus, etc.; no es sustituto directo de **Twilio `<Gather>` + TwiML**, que es **turn-by-turn** (medio dúplex telefónico).

## Alineación con `.vercel/README.txt`

La carpeta `.vercel` solo enlaza el proyecto desplegado en Vercel; **no define** despliegue de voz en GPU. La ruta de voz sigue siendo **servicio aparte** (Railway, VM, Colab con túnel, etc.) con `VOICE_PUBLIC_URL` apuntando al FastAPI de `voice_agent`.

## Integración prevista (puente)

1. **Hoy**: `voice_agent/main.py` — PAU + Gemini + Polly (o ElevenLabs en otros scripts).
2. **Fase puente**: servicio externo que ejecute PersonaPlex y exponga **WebSocket** (audio PCM/Opus). Variables de entorno:
   - `PERSONAPLEX_BRIDGE_WS_URL` — URL del WS del servicio Moshi/PersonaPlex (cuando exista).
   - `HF_TOKEN` — solo en el host que ejecute el modelo (nunca en Vercel static).
3. **Twilio Media Streams** (futuro): bidireccional mic ↔ tu backend ↔ puente PersonaPlex; diseño distinto del webhook actual.

Ver `personaplex_bridge.py` y el campo `personaplex` en `GET /health`.

Patente: PCT/EP2025/067317 — Bajo Protocolo V10 - Founder: Rubén
