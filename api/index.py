"""
TRYONYOU — API Flask pour Vercel (entry point: /api/index.py)

Endpoints:
  GET  /api/health          → diagnostic
  POST /api/v1/leads        → capture lead (form de contact)
  GET  /api/v1/leads/count  → compteur (admin/diagnostic)
  POST /api/v1/ops/jules-mail → exécute le traitement des emails comptables
  POST /api/chat-pau        → assistant commercial P.A.U.
  POST /api/pau-habla       → TTS/animation payload pour l'avatar P.A.U.

Stockage: SQLite (/tmp/tryonyou_leads.sqlite, lecture/écriture compatibles
Vercel serverless). En complément, les leads sont également journalisés sur stdout
(récupérables dans les logs Vercel) pour ne perdre aucune demande même si /tmp
est volatil entre invocations.

Sécurité: validation des champs, normalisation email, rate-limit léger
in-memory (best-effort), CORS contrôlé.
"""
from __future__ import annotations

import json
import os
import sqlite3
import sys
import time
from datetime import datetime, timezone
from typing import Any

import stripe
from flask import Flask, jsonify, request, Response

app = Flask(__name__)

DB_PATH = os.environ.get("TRYONYOU_DB_PATH", "/tmp/tryonyou_leads.sqlite")
SIREN = "943 610 196"
PATENT = "PCT/EP2025/067317"
ENDPOINT_SECRET = os.environ.get("STRIPE_ENDPOINT_SECRET", "").strip()

_RATE: dict[str, list[float]] = {}
RATE_WINDOW_S = 60.0
RATE_MAX = 6


# ─── DB ────────────────────────────────────────────────────────────────────
def _db() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH, timeout=5.0)
    con.row_factory = sqlite3.Row
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name   TEXT NOT NULL,
            email       TEXT NOT NULL,
            company     TEXT NOT NULL,
            role        TEXT,
            market      TEXT,
            challenge   TEXT,
            source      TEXT,
            user_agent  TEXT,
            ip          TEXT,
            consent     INTEGER NOT NULL DEFAULT 0,
            submitted_at TEXT NOT NULL,
            created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    con.execute("CREATE INDEX IF NOT EXISTS idx_leads_email ON leads(email)")
    con.execute("CREATE INDEX IF NOT EXISTS idx_leads_company ON leads(company)")
    con.commit()
    return con


# ─── helpers ──────────────────────────────────────────────────────────────
def _client_ip() -> str:
    fwd = request.headers.get("X-Forwarded-For", "")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.remote_addr or "unknown"


def _is_valid_email(value: str) -> bool:
    if not value or " " in value:
        return False
    if value.count("@") != 1:
        return False
    local, domain = value.split("@", 1)
    return bool(local and domain and "." in domain and not domain.startswith(".") and not domain.endswith("."))


def _rate_check(ip: str) -> bool:
    now = time.time()
    bucket = _RATE.setdefault(ip, [])
    bucket[:] = [t for t in bucket if now - t < RATE_WINDOW_S]
    if len(bucket) >= RATE_MAX:
        return False
    bucket.append(now)
    return True


def _cors(resp: Response) -> Response:
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Accept"
    resp.headers["Access-Control-Max-Age"] = "86400"
    return resp


def _json_ok(data: Any, status: int = 200) -> Response:
    return _cors(Response(json.dumps(data, ensure_ascii=False), status=status, mimetype="application/json"))


def _json_err(msg: str, status: int = 400, **extra: Any) -> Response:
    payload = {"ok": False, "error": msg, **extra}
    return _cors(Response(json.dumps(payload, ensure_ascii=False), status=status, mimetype="application/json"))


def _is_authorized_ops_request() -> bool:
    token = os.environ.get("JULES_CRON_TOKEN", "").strip()
    if not token:
        return False

    auth_header = request.headers.get("Authorization", "").strip()
    bearer = auth_header.removeprefix("Bearer ").strip() if auth_header.startswith("Bearer ") else ""
    explicit = request.headers.get("X-Cron-Token", "").strip()
    return bearer == token or explicit == token


# ─── routes ───────────────────────────────────────────────────────────────
@app.route("/api/health", methods=["GET"])
def health() -> Response:
    try:
        con = _db()
        n = con.execute("SELECT COUNT(*) AS n FROM leads").fetchone()["n"]
        con.close()
        db_ok = True
    except Exception as e:
        n = -1
        db_ok = False
        print(f"[tryonyou] db error: {e}", file=sys.stderr)
    return _json_ok({
        "ok": True,
        "service": "tryonyou-api",
        "siren": SIREN,
        "patent": PATENT,
        "db_ok": db_ok,
        "leads_count": n,
        "now": datetime.now(timezone.utc).isoformat(),
    })


@app.route("/api/v1/leads", methods=["OPTIONS", "POST"])
def post_lead() -> Response:
    if request.method == "OPTIONS":
        return _cors(Response("", status=204))

    ip = _client_ip()
    if not _rate_check(ip):
        return _json_err("Trop de requêtes. Réessayez dans une minute.", 429)

    try:
        body = request.get_json(silent=True) or {}
    except Exception:
        return _json_err("Corps JSON invalide.", 400)

    full_name = str(body.get("full_name", "")).strip()
    email = str(body.get("email", "")).strip().lower()
    company = str(body.get("company", "")).strip()
    role = str(body.get("role", "")).strip()
    market = str(body.get("market", "")).strip()
    challenge = str(body.get("challenge", "")).strip()
    source = str(body.get("source", "")).strip() or "tryonyou.app"
    consent = bool(body.get("consent", False))
    submitted_at = str(body.get("submitted_at", "")).strip() or datetime.now(timezone.utc).isoformat()

    # Validation
    if not full_name or len(full_name) > 200:
        return _json_err("Nom complet manquant ou trop long.", 422, field="full_name")
    if not _is_valid_email(email):
        return _json_err("Email professionnel invalide.", 422, field="email")
    if not company or len(company) > 200:
        return _json_err("Maison / Enseigne manquante.", 422, field="company")
    if not consent:
        return _json_err("Consentement RGPD requis.", 422, field="consent")
    if len(challenge) > 4000:
        return _json_err("Description trop longue.", 422, field="challenge")

    user_agent = request.headers.get("User-Agent", "")[:300]
    payload = {
        "full_name": full_name,
        "email": email,
        "company": company,
        "role": role,
        "market": market,
        "challenge": challenge,
        "source": source,
        "user_agent": user_agent,
        "ip": ip,
        "consent": int(consent),
        "submitted_at": submitted_at,
    }

    # Always log to stdout (Vercel logs) so a record exists even if /tmp is wiped
    print(f"[tryonyou] LEAD {json.dumps(payload, ensure_ascii=False)}", flush=True)

    lead_id: int | None = None
    db_ok = True
    try:
        con = _db()
        cur = con.execute(
            """
            INSERT INTO leads
              (full_name, email, company, role, market, challenge,
               source, user_agent, ip, consent, submitted_at)
            VALUES (:full_name, :email, :company, :role, :market, :challenge,
                    :source, :user_agent, :ip, :consent, :submitted_at)
            """,
            payload,
        )
        lead_id = cur.lastrowid
        con.commit()
        con.close()
    except Exception as e:
        db_ok = False
        print(f"[tryonyou] db insert error: {e}", file=sys.stderr)

    return _json_ok({
        "ok": True,
        "lead_id": lead_id,
        "persisted": db_ok,
        "thank_you": "Merci. Notre équipe parisienne vous recontacte sous 48 h ouvrées.",
    }, 201 if db_ok else 202)


@app.route("/api/v1/leads/count", methods=["GET"])
def leads_count() -> Response:
    try:
        con = _db()
        n = con.execute("SELECT COUNT(*) AS n FROM leads").fetchone()["n"]
        con.close()
        return _json_ok({"ok": True, "count": n})
    except Exception as e:
        print(f"[tryonyou] db count error: {e}", file=sys.stderr)
        return _json_err("db error", 500)


@app.route("/api/v1/ops/jules-mail", methods=["OPTIONS", "POST"])
def run_jules_mail() -> Response:
    if request.method == "OPTIONS":
        return _cors(Response("", status=204))

    if not _is_authorized_ops_request():
        return _json_err("Unauthorized", 401)

    try:
        from jules_mail import jules_mail_agent_execution

        result = jules_mail_agent_execution()
        status = 200 if result.get("ok") else (202 if result.get("status") == "skipped" else 500)
        return _json_ok(result, status)
    except Exception as e:
        print(f"[tryonyou] jules mail execution error: {e}", file=sys.stderr)
        return _json_err("jules mail execution error", 500)


@app.route("/api/webhook", methods=["POST"])
def webhook() -> tuple[Response, int]:
    payload = request.get_data(cache=False, as_text=False)
    sig_header = request.headers.get("Stripe-Signature", "")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, ENDPOINT_SECRET)
    except ValueError:
        return jsonify({"status": "invalid payload"}), 400
    except stripe.error.SignatureVerificationError:
        return jsonify({"status": "invalid signature"}), 400

    event_type = event.get("type")
    if event_type == "payment_intent.succeeded":
        intent = event.get("data", {}).get("object", {})
        _ = intent

    return jsonify({"status": "success"}), 200


@app.route("/api/chat-pau", methods=["POST"])
def chat_pau_endpoint() -> Response:
    data = request.get_json(silent=True) or {}
    mensaje = str(data.get("mensaje", "")).strip()
    es_inversor = bool(data.get("inversor", False))

    if not mensaje:
        return _json_err("Mensaje ausente", 400)

    try:
        from pau_assistant import PauInterfaceAgent

        agente_pau = PauInterfaceAgent()
        respuesta_pau = agente_pau.procesar_consulta_visita(
            mensaje, es_inversor=es_inversor
        )
        return _json_ok({"respuesta": respuesta_pau}, 200)
    except Exception as e:
        print(f"[tryonyou] pau chat error: {e}", file=sys.stderr)
        return _json_err("Error de procesamiento en la interfaz", 500)


@app.route("/api/pau-habla", methods=["POST"])
def pau_habla_endpoint() -> Response:
    data = request.get_json(silent=True) or {}
    texto = str(data.get("texto", "")).strip()
    idioma = str(data.get("idioma", "")).strip() or "fr"
    if not texto:
        return _json_err("Texto ausente", 400)

    try:
        from pau_assistant import generar_audio_habla

        result = generar_audio_habla(texto, idioma)
        status = 200 if result.get("status") == "success" else 503
        return _json_ok(result, status)
    except Exception as e:
        print(f"[tryonyou] pau habla error: {e}", file=sys.stderr)
        return _json_err("Error en generación de audio Pau", 500)


try:
    from manoli import manoli_blueprint
except ModuleNotFoundError as e:
    print(f"[tryonyou] manoli blueprint module not found: {e}", file=sys.stderr)
else:
    try:
        app.register_blueprint(manoli_blueprint)
    except (AssertionError, ValueError) as e:
        print(f"[tryonyou] manoli blueprint not registered: {e}", file=sys.stderr)


# Vercel @vercel/python detects WSGI apps named `app` automatically.
# Do not define a `handler` function here, otherwise the runtime tries to call
# it as a HTTP handler instead of forwarding to the Flask app.

if __name__ == "__main__":  # local dev
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), debug=True)
