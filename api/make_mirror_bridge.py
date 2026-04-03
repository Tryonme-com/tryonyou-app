"""
Puente Espejo Digital → Make.com (Vercel / Flask).

Variables de entorno (al menos una URL de webhook):
  MAKE_ESPEJO_WEBHOOK_URL  (preferida)
  MAKE_WEBHOOK_URL
  MAKE_LEADS_WEBHOOK_URL

Eventos permitidos (campo JSON `event`):
  balmain_brand_click
  reserva_probador

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import TYPE_CHECKING

import requests

if TYPE_CHECKING:
    from flask import Flask, Response

_MAX_BODY = 64 * 1024
_ALLOWED_EVENTS = frozenset({"balmain_brand_click", "reserva_probador"})


def _make_webhook_url() -> str:
    for key in (
        "MAKE_ESPEJO_WEBHOOK_URL",
        "MAKE_WEBHOOK_URL",
        "MAKE_LEADS_WEBHOOK_URL",
    ):
        v = os.environ.get(key, "").strip()
        if v:
            return v
    return ""


def register_make_mirror_routes(app: "Flask") -> None:
    from flask import Response, jsonify, request

    app.config.setdefault("MAX_CONTENT_LENGTH", _MAX_BODY)

    @app.before_request
    def _make_mirror_request_guard() -> Response | None:
        path = (request.path or "").rstrip("/")
        if path != "/api/mirror_make_event":
            return None
        if request.method in ("OPTIONS", "GET", "HEAD"):
            return None
        if request.method != "POST":
            r = jsonify({"status": "error", "message": "method_not_allowed"})
            r.status_code = 405
            return _mirror_cors(r)
        cl = request.content_length
        if cl is not None and cl > _MAX_BODY:
            r = jsonify({"status": "error", "message": "payload_too_large"})
            r.status_code = 413
            return _mirror_cors(r)
        return None

    @app.route("/api/mirror_make_event", methods=["OPTIONS"])
    def mirror_make_event_options() -> Response:
        return _mirror_cors(Response(status=204))

    @app.route("/api/mirror_make_event", methods=["POST"])
    def mirror_make_event() -> tuple[Response, int]:
        url = _make_webhook_url()
        if not url:
            return (
                _mirror_cors(
                    jsonify(
                        {
                            "status": "error",
                            "message": "configure MAKE_ESPEJO_WEBHOOK_URL or MAKE_WEBHOOK_URL",
                        }
                    )
                ),
                503,
            )

        body = request.get_json(force=True, silent=True)
        if not isinstance(body, dict):
            body = {}

        event = body.get("event")
        if event not in _ALLOWED_EVENTS:
            return (
                _mirror_cors(
                    jsonify(
                        {
                            "status": "error",
                            "message": "invalid_or_missing_event",
                            "allowed": sorted(_ALLOWED_EVENTS),
                        }
                    )
                ),
                400,
            )

        forward: dict = {**body}
        forward["event"] = event
        forward["received_at_utc"] = datetime.now(timezone.utc).isoformat()

        try:
            r = requests.post(
                url,
                json=forward,
                headers={"Content-Type": "application/json"},
                timeout=15,
            )
        except requests.RequestException as e:
            return (
                _mirror_cors(
                    jsonify({"status": "error", "message": "upstream_request_failed", "detail": str(e)})
                ),
                502,
            )

        if not (200 <= r.status_code < 300):
            return (
                _mirror_cors(
                    jsonify(
                        {
                            "status": "error",
                            "message": "make_webhook_non_success",
                            "upstream_status": r.status_code,
                        }
                    )
                ),
                502,
            )

        return _mirror_cors(jsonify({"status": "ok", "forwarded": True})), 200


def _mirror_cors(resp: "Response") -> "Response":
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return resp


async def _mirror_forward_make_async(url: str, forward: dict) -> None:
    """POST a Make sin bloquear la respuesta HTTP (FastAPI BackgroundTasks)."""
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


def register_make_mirror_fastapi(app: object) -> None:
    """Rutas Espejo → Make en FastAPI (acepta y reenvía en segundo plano)."""
    from fastapi import BackgroundTasks, Request
    from fastapi.responses import JSONResponse, Response

    fastapi_app = app

    @fastapi_app.options("/api/mirror_make_event")
    async def mirror_make_event_options() -> Response:
        return Response(status_code=204)

    @fastapi_app.post("/api/mirror_make_event")
    async def mirror_make_event(
        request: Request,
        background_tasks: BackgroundTasks,
    ) -> JSONResponse | dict:
        url = _make_webhook_url()
        if not url:
            return JSONResponse(
                {
                    "status": "error",
                    "message": "configure MAKE_ESPEJO_WEBHOOK_URL or MAKE_WEBHOOK_URL",
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
        if event not in _ALLOWED_EVENTS:
            return JSONResponse(
                {
                    "status": "error",
                    "message": "invalid_or_missing_event",
                    "allowed": sorted(_ALLOWED_EVENTS),
                },
                status_code=400,
            )

        forward: dict = dict(body)
        forward["event"] = event
        forward["received_at_utc"] = datetime.now(timezone.utc).isoformat()
        background_tasks.add_task(_mirror_forward_make_async, url, forward)
        return {"status": "ok", "accepted": True, "forwarding": True}
