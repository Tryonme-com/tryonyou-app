"""
API TryOnYou — FastAPI asíncrono, webhook Make en segundo plano.
Variable: MAKE_WEBHOOK_URL. Objeto app en nivel de módulo para Vercel (ASGI).
Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
import logging
import os

from fastapi import BackgroundTasks, FastAPI, Request
from httpx import AsyncClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

MAKE_WEBHOOK_URL = os.getenv("MAKE_WEBHOOK_URL")


async def notify_make(event_name: str, payload: dict):
    """Envío asíncrono a Make sin retrasar la respuesta al usuario."""
    if not MAKE_WEBHOOK_URL:
        logger.warning("MAKE_WEBHOOK_URL no configurada.")
        return

    async with AsyncClient() as client:
        try:
            response = await client.post(
                MAKE_WEBHOOK_URL,
                json={
                    "event": event_name,
                    "data": payload,
                    "source": "tryonyou-v10-omega",
                },
                timeout=5.0,
            )
            logger.info("Make Notification Success: %s", response.status_code)
        except Exception as e:
            logger.error("Make Notification Failed: %s", str(e))


@app.get("/api/health")
async def health_check():
    return {"status": "online", "bunker": "protected"}


@app.post("/api/mirror/action")
async def handle_action(request: Request, background_tasks: BackgroundTasks):
    """
    Endpoint único para 'Los Listos'. Maneja:
    seleccion, reserva, combinaciones, silueta, compartir, balmain.
    """
    data = await request.json()
    action = data.get("action", "unknown")

    response = {"status": "received", "action": action}

    if action == "balmain":
        response["trigger"] = "snap_avatar_change"

    background_tasks.add_task(notify_make, action, data)

    return response
