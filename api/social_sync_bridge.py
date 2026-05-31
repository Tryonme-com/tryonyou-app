"""
Puente Social Sync → Make.com (Vercel / FastAPI).

Implementa el Protocolo_Soberania_V10_Social_Sync:
  1. Google Drive: vigilante del Búnker (carpeta PAU_ASSETS_STIRPE)
  2. OpenAI: generación de caption aristocrático (tono Stirpe Lafayette)
  3. Instagram Business: publicación automática del activo

Variable de entorno:
  MAKE_SOCIAL_SYNC_WEBHOOK_URL  (requerida)

Eventos permitidos (campo JSON `event`):
  social_post_pau

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

_MAX_BODY = 64 * 1024
_SOCIAL_SYNC_ALLOWED_EVENTS = frozenset({"social_post_pau"})

# Flow definition for Protocolo_Soberania_V10_Social_Sync (Make.com scenario).
SOCIAL_SYNC_FLOW: dict[str, Any] = {
    "name": "Protocolo_Soberania_V10_Social_Sync",
    "flow": [
        {
            "id": 1,
            "module": "google-drive:watch-files",
            "metadata": {
                "name": "Vigilante del Búnker (Drive)",
                "folder": "PAU_ASSETS_STIRPE",
            },
        },
        {
            "id": 2,
            "module": "openai:create-completion",
            "metadata": {
                "model": "gpt-4-luxury-edition",
                "prompt": (
                    "Actúa como la Stirpe Lafayet. Tono aristocrático, técnico de lujo. "
                    "Describe esta imagen de Pau o la Tía Loki ignorando la mediocridad de "
                    "las tallas y mencionando la Patente PCT/EP2025/067317. Termina con ¡BOOM!"
                ),
            },
        },
        {
            "id": 3,
            "module": "instagram-business:create-photo-post",
            "metadata": {
                "image_url": "{{1.webContentLink}}",
                "caption": "{{2.choices[].text}}",
            },
        },
    ],
    "metadata": {
        "version": "V10_OMEGA",
        "author": "P.A.U. Agent",
    },
}


def _social_sync_webhook_url() -> str:
    return os.environ.get("MAKE_SOCIAL_SYNC_WEBHOOK_URL", "").strip()


async def _social_sync_forward_make_async(url: str, forward: dict) -> None:
    """POST asíncrono al webhook Make.com de Social Sync."""
    import httpx

    async with httpx.AsyncClient() as client:
        try:
            await client.post(
                url,
                json=forward,
                headers={"Content-Type": "application/json"},
                timeout=15.0,
            )
        except (httpx.HTTPError, OSError):
            pass


def register_social_sync_fastapi(app: object) -> None:
    """Registra las rutas de Social Sync en FastAPI."""
    from fastapi import BackgroundTasks, Request
    from fastapi.responses import JSONResponse, Response

    fastapi_app = app

    @fastapi_app.options("/api/social_sync")
    async def social_sync_options() -> Response:
        return Response(status_code=204)

    @fastapi_app.get("/api/social_sync/flow")
    async def get_social_sync_flow() -> dict:
        """Devuelve la configuración del flujo Make.com."""
        return SOCIAL_SYNC_FLOW

    @fastapi_app.post("/api/social_sync")
    async def social_sync_event(
        request: Request,
        background_tasks: BackgroundTasks,
    ) -> JSONResponse | dict:
        url = _social_sync_webhook_url()
        if not url:
            return JSONResponse(
                {
                    "status": "error",
                    "message": "configure MAKE_SOCIAL_SYNC_WEBHOOK_URL",
                },
                status_code=503,
            )

        cl = request.headers.get("content-length")
        if cl is not None:
            try:
                if int(cl) > _MAX_BODY:
                    return JSONResponse(
                        {"status": "error", "message": "payload_too_large"},
                        status_code=413,
                    )
            except ValueError:
                pass

        try:
            body = await request.json()
        except Exception:
            body = None
        if not isinstance(body, dict):
            body = {}

        event = body.get("event")
        if event not in _SOCIAL_SYNC_ALLOWED_EVENTS:
            return JSONResponse(
                {
                    "status": "error",
                    "message": "invalid_or_missing_event",
                    "allowed": sorted(_SOCIAL_SYNC_ALLOWED_EVENTS),
                },
                status_code=400,
            )

        forward: dict = dict(body)
        forward["event"] = event
        forward["received_at_utc"] = datetime.now(timezone.utc).isoformat()
        forward["protocol"] = "Protocolo_Soberania_V10_Social_Sync"
        background_tasks.add_task(_social_sync_forward_make_async, url, forward)
        return {"status": "ok", "accepted": True, "forwarding": True}
