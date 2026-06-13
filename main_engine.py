import hashlib
import hmac
import json
import os
import sqlite3
import time
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager

import requests
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)
executor = ThreadPoolExecutor(max_workers=4)

SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET", "")
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL", "")
DB_PATH = os.environ.get("AUDIT_DB_PATH", "auditoria.db")
MAX_TIMESTAMP_DRIFT_SECONDS = 60 * 5


def init_db() -> None:
    with sqlite3.connect(DB_PATH, timeout=10.0) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS refs (
                ref_id TEXT PRIMARY KEY,
                status TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def _post_to_slack(url: str, text: str) -> None:
    response = requests.post(
        url,
        json={"replace_original": True, "text": text},
        timeout=10,
    )
    response.raise_for_status()


def _save_to_db(ref_id: str, action_id: str) -> None:
    with sqlite3.connect(DB_PATH, timeout=10.0) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute(
            "INSERT OR REPLACE INTO refs (ref_id, status) VALUES (?, ?)",
            (ref_id, action_id),
        )
        conn.commit()


init_db()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    if not SLACK_SIGNING_SECRET:
        raise RuntimeError("SLACK_SIGNING_SECRET no configurado")
    try:
        yield
    finally:
        executor.shutdown(wait=True, cancel_futures=False)


app = FastAPI(lifespan=lifespan)


@app.post("/api/slack/interact")
async def slack_interactive_endpoint(request: Request) -> JSONResponse:
    timestamp = request.headers.get("X-Slack-Request-Timestamp")
    signature = request.headers.get("X-Slack-Signature")
    body = await request.body()

    if not timestamp or not signature:
        raise HTTPException(status_code=400, detail="Headers de Slack incompletos")

    try:
        slack_ts = int(timestamp)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Timestamp inválido") from exc

    if abs(int(time.time()) - slack_ts) > MAX_TIMESTAMP_DRIFT_SECONDS:
        raise HTTPException(status_code=403, detail="Timestamp fuera de ventana permitida")

    sig_basestring = f"v0:{timestamp}:{body.decode()}".encode("utf-8")
    my_signature = "v0=" + hmac.new(
        SLACK_SIGNING_SECRET.encode("utf-8"),
        sig_basestring,
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(my_signature, signature):
        raise HTTPException(status_code=403, detail="Firma inválida")

    form_data = await request.form()
    raw_payload = form_data.get("payload")
    if not raw_payload:
        raise HTTPException(status_code=400, detail="Payload ausente")

    payload = json.loads(raw_payload)
    try:
        action = payload["actions"][0]
        ref_id = action["value"]
        user_name = payload["user"]["name"]
        action_id = action["action_id"]
    except (KeyError, IndexError, TypeError) as exc:
        raise HTTPException(status_code=400, detail="Payload inválido") from exc

    response_url = payload.get("response_url") or SLACK_WEBHOOK_URL

    if not response_url:
        raise HTTPException(status_code=400, detail="response_url ausente")

    new_text = f"*Estado:* Transacción {ref_id} procesada por {user_name}"

    try:
        await asyncio.get_running_loop().run_in_executor(
            executor,
            _post_to_slack,
            response_url,
            new_text,
        )
    except requests.RequestException:
        logger.exception("Error enviando actualización a Slack")
        raise HTTPException(status_code=502, detail="Error notificando a Slack")

    try:
        await asyncio.get_running_loop().run_in_executor(
            executor,
            _save_to_db,
            ref_id,
            action_id,
        )
    except Exception:
        logger.exception("Error guardando en la base de datos")
        raise HTTPException(status_code=500, detail="Error interno")

    return JSONResponse(content={"text": "Procesado"})


if __name__ == "__main__":
    print("🚀 TryOnYou Engine V10.2: En ejecución (Producción Activa)")
    uvicorn.run(app, host="0.0.0.0", port=8000)
