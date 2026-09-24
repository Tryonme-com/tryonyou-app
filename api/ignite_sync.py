ignite_sync.py
import os

# 1. Definición de la estructura de archivos
files = {
    "requirements.txt": """fastapi==0.111.0
httpx==0.27.0
redis==5.0.4
pydantic==2.7.1
uvicorn==0.30.1
""",

    "vercel.json": """{
  "rewrites": [
    { "source": "/api/(.*)", "destination": "/api/index.py" }
  ]
}""",

    ".env.example": """APP_URL=https://tu-app.vercel.app
LINEAR_WEBHOOK_SECRET=tu_secreto_linear
GITHUB_WEBHOOK_SECRET=tu_secreto_github
QSTASH_TOKEN=tu_token_qstash
LINEAR_BOT_TOKEN=tu_personal_api_key_linear
GITHUB_BOT_TOKEN=tu_github_token_pat
LINEAR_BOT_ACTOR_ID=id_de_usuario_del_bot_linear
GITHUB_BOT_ACTOR_ID=id_numerico_del_bot_github
UPSTASH_REDIS_HOST=tu_endpoint_redis.upstash.io
UPSTASH_REDIS_PORT=6379
UPSTASH_REDIS_PASSWORD=tu_password_redis
""",

    "api/index.py": """import os
import hmac
import hashlib
import json
from typing import Optional
from fastapi import FastAPI, Request, HTTPException, Header, Response, status
import httpx
from redis import Redis

app = FastAPI()

LINEAR_API_URL = "https://api.linear.app/v1/graphql"
GITHUB_API_URL = "https://api.github.com"
APP_URL = os.getenv("APP_URL", "")

LINEAR_WEBHOOK_SECRET = os.getenv("LINEAR_WEBHOOK_SECRET", "")
GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "")
QSTASH_TOKEN = os.getenv("QSTASH_TOKEN", "")
LINEAR_BOT_TOKEN = os.getenv("LINEAR_BOT_TOKEN", "")
GITHUB_BOT_TOKEN = os.getenv("GITHUB_BOT_TOKEN", "")
LINEAR_BOT_ACTOR_ID = os.getenv("LINEAR_BOT_ACTOR_ID", "")
GITHUB_BOT_ACTOR_ID = os.getenv("GITHUB_BOT_ACTOR_ID", "")

redis_client = Redis(
    host=os.getenv("UPSTASH_REDIS_HOST", ""),
    port=int(os.getenv("UPSTASH_REDIS_PORT", 6379)),
    password=os.getenv("UPSTASH_REDIS_PASSWORD", ""),
    ssl=True,
    decode_responses=True
)

http_client = httpx.AsyncClient()
ALLOWED_LABELS = {"Bug: Critical", "Feature: Core"}

def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    if not secret or not signature: return False
    computed = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(computed, signature.replace("sha256=", ""))

async def enqueue_to_qstash(destination_path: str, payload: dict):
    target_url = f"{APP_URL.rstrip('/')}{destination_path}"
    url = f"https://qstash.upstash.io/v2/publish/{target_url}"
    headers = {
        "Authorization": f"Bearer {QSTASH_TOKEN}",
        "Content-Type": "application/json",
        "Upstash-Max-Retries": "5",
        "Upstash-Backoff-Factor": "2"
    }
    res = await http_client.post(url, headers=headers, json=payload)
    if res.status_code != 201: raise HTTPException(status_code=500, detail="QStash Error")

@app.post("/api/webhooks/linear")
async def linear_webhook(request: Request, x_linear_signature: Optional[str] = Header(None)):
    body_bytes = await request.body()
    if not verify_signature(body_bytes, x_linear_signature, LINEAR_WEBHOOK_SECRET):
        raise HTTPException(status_code=401, detail="Firma inválida")
    payload = json.loads(body_bytes.decode())
    if payload.get("actor", {}).get("id") == LINEAR_BOT_ACTOR_ID: return {"status": "ignored"}
    labels = {l.get("name") for l in payload.get("data", {}).get("labels", []) if isinstance(l, dict)}
    if not labels.intersection(ALLOWED_LABELS): return {"status": "ignored"}
    await enqueue_to_qstash("/api/workers/linear-to-github", payload)
    return Response(status_code=status.HTTP_202_ACCEPTED)

@app.post("/api/webhooks/github")
async def github_webhook(request: Request, x_hub_signature_256: Optional[str] = Header(None), x_github_event: Optional[str] = Header(None)):
    body_bytes = await request.body()
    if not verify_signature(body_bytes, x_hub_signature_256, GITHUB_WEBHOOK_SECRET):
        raise HTTPException(status_code=401, detail="Firma inválida")
    payload = json.loads(body_bytes.decode())
    if str(payload.get("sender", {}).get("id")) == GITHUB_BOT_ACTOR_ID: return {"status": "ignored"}
    if x_github_event != "issues": return {"status": "ignored"}
    await enqueue_to_qstash("/api/workers/github-to-linear", payload)
    return Response(status_code=status.HTTP_202_ACCEPTED)

@app.post("/api/workers/linear-to-github")
async def worker_linear_to_github(request: Request):
    payload = await request.json()
    event_id, issue_data = payload.get("id"), payload.get("data", {})
    linear_issue_id = issue_data.get("id")
    if redis_client.set(f"processed:linear:{event_id}", "1", ex=86400, nx=True) is None: return {"status": "skipped"}
    lock_key = f"lock:entity:{linear_issue_id}"
    if redis_client.set(lock_key, "1", ex=10, nx=True) is None: raise HTTPException(status_code=429, detail="Locked")
    try:
        github_issue_number = redis_client.get(f"mapping:linear:{linear_issue_id}")
        linear_state = issue_data.get("state", {}).get("name", "").lower()
        target_gh_state = "closed" if linear_state in ["done", "canceled", "closed"] else "open"
        repo = "TryOnYou/core-app"
        if payload.get("action") == "create" or not github_issue_number:
            if target_gh_state == "closed": return {"status": "skipped"}
            res = await http_client.post(
                f"{GITHUB_API_URL}/repos/{repo}/issues",
                headers={"Authorization": f"token {GITHUB_BOT_TOKEN}", "Accept": "application/vnd.github.v3+json"},
                json={"title": issue_data.get("title"), "body": f"{issue_data.get('description', '')}\\n\\n---\\n*Sincronizado desde Linear ID: {linear_issue_id}*"}
            )
            if res.status_code == 201:
                gh_num = str(res.json().get("number"))
                redis_client.set(f"mapping:linear:{linear_issue_id}", gh_num)
                redis_client.set(f"mapping:github:{gh_num}", linear_issue_id)
                return {"status": "created", "gh_number": gh_num}
        elif payload.get("action") == "update" and github_issue_number:
            issue_url = f"{GITHUB_API_URL}/repos/{repo}/issues/{github_issue_number}"
            headers = {"Authorization": f"token {GITHUB_BOT_TOKEN}", "Accept": "application/vnd.github.v3+json"}
            curr = await http_client.get(issue_url, headers=headers)
            if curr.status_code == 200 and curr.json().get("state") == target_gh_state: return {"status": "aligned"}
            await http_client.patch(issue_url, headers=headers, json={"state": target_gh_state})
            return {"status": "updated"}
    finally: redis_client.delete(lock_key)

@app.post("/api/workers/github-to-linear")
async def worker_github_to_linear(request: Request):
    payload = await request.json()
    gh_action, issue_data = payload.get("action"), payload.get("issue", {})
    gh_num = str(issue_data.get("number"))
    if redis_client.set(f"processed:github:{gh_num}:{issue_data.get('updated_at', '')}", "1", ex=86400, nx=True) is None: return {"status": "skipped"}
    linear_issue_id = redis_client.get(f"mapping:github:{gh_num}")
    if not linear_issue_id or gh_action not in ["closed", "reopened"]: return {"status": "ignored"}
    target_state = "Done" if gh_action == "closed" else "Todo"
    headers = {"Authorization": LINEAR_BOT_TOKEN, "Content-Type": "application/json"}
    s_res = await http_client.post(LINEAR_API_URL, headers=headers, json={"query": "query { workflowStates { nodes { id name } } }"})\n    state_id = next((s["id"] for s in s_res.json().get("data", {}).get("workflowStates", {}).get("nodes", []) if s["name"].lower() == target_state.lower()), None)
    if state_id:
        await http_client.post(LINEAR_API_URL, headers=headers, json={"query": "mutation Update($id: String!, $sId: String!) { issueUpdate(id: $id, input: { stateId: $sId }) { success } }", "variables": {"id": linear_issue_id, "stateId": state_id}})
        return {"status": "linear_updated"}
"""
}

# 2. Escritura automatizada en disco
os.makedirs("api", exist_ok=True)
for path, content in files.items():
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"📡 [OK] Escrito: {path}")

print("\n🚀 Estructura montada con éxito. Listo para producción.")
