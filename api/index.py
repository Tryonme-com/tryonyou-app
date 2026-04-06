"""
API TryOnYou — FastAPI asíncrono, webhook Make en segundo plano.
Variable: MAKE_WEBHOOK_URL. Objeto app en nivel de módulo para Vercel (ASGI).
Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
import logging
import os
import sys
from pathlib import Path

import anyio
from fastapi import BackgroundTasks, FastAPI, Request
from fastapi.responses import JSONResponse
from httpx import AsyncClient

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from bunker_full_orchestrator import orchestrate_beta_waitlist
from social_sync_bridge import register_social_sync_fastapi

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


@app.post("/api/waitlist_beta")
async def waitlist_beta(request: Request):
    """
    Lista beta + hero waitlist (App.tsx). Make.com + waitlist.json vía bunker_full_orchestrator.
    """
    try:
        raw = await request.json()
    except Exception:
        raw = None
    body: dict = raw if isinstance(raw, dict) else {}
    try:
        return await anyio.to_thread.run_sync(orchestrate_beta_waitlist, body)
    except Exception:
        logger.exception("waitlist_beta: orchestrate_beta_waitlist falló")
        return JSONResponse(
            status_code=500,
            content={
                "make_ok": False,
                "waitlist_persisted": False,
                "waitlist_path": None,
                "error": "waitlist_orchestrator_failed",
            },
        )


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


register_social_sync_fastapi(app)
