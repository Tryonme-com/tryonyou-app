"""
TRYONYOU — API Flask pour Vercel (entry point: /api/index.py)

Endpoints:
  GET  /api/health          → diagnostic
  POST /api/v1/leads        → capture lead (form de contact)
  GET  /api/v1/leads/count  → compteur (admin/diagnostic)

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

import google.oauth2.credentials
from flask_cors import CORS
from flask import Flask, jsonify, request, Response
from googleapiclient.discovery import build

app = Flask(__name__)
CORS(app)

DB_PATH = os.environ.get("TRYONYOU_DB_PATH", "/tmp/tryonyou_leads.sqlite")
SIREN = "943 610 196"
PATENT = "PCT/EP2025/067317"
GOOGLE_SHEETS_ID = os.environ.get("DIVINEO_LEADS_DB_ID")

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


def _rate_check(ip: str) -> bool:
    now = time.time()
    bucket = _RATE.setdefault(ip, [])
    bucket[:] = [t for t in bucket if now - t < RATE_WINDOW_S]
    if len(bucket) >= RATE_MAX:
        return False
    bucket.append(now)
    return True


def _is_valid_email(email: str) -> bool:
    if not email or len(email) > 254 or " " in email or email.count("@") != 1:
        return False
    local, domain = email.rsplit("@", 1)
    if not local or not domain or "." not in domain:
        return False
    if domain.startswith(".") or domain.endswith("."):
        return False
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


def _google_credentials() -> google.oauth2.credentials.Credentials:
    creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    if not creds_json:
        raise ValueError("Les informations d'identification Google sont manquantes dans l'environnement.")

    info = json.loads(creds_json)
    return google.oauth2.credentials.Credentials.from_authorized_user_info(info)


def get_gmail_service():
    """Inicializa el servicio oficial de la API de Gmail con credenciales reales."""
    return build("gmail", "v1", credentials=_google_credentials())


def get_sheets_service():
    """Inicializa el servicio oficial de la API de Google Sheets."""
    return build("sheets", "v4", credentials=_google_credentials())


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
        return _json_err(f"db error: {e}", 500)


@app.route("/api/jules/process-emails", methods=["POST"])
def process_incoming_emails():
    """
    Escanea la bandeja de entrada, procesa los correos de leads
    y registra los datos de contacto en Divineo_Leads_DB.
    """
    try:
        if not GOOGLE_SHEETS_ID:
            raise ValueError("DIVINEO_LEADS_DB_ID est manquant dans l'environnement.")

        gmail_service = get_gmail_service()
        sheets_service = get_sheets_service()

        # Consultar los mensajes no leídos en la bandeja de entrada real
        results = gmail_service.users().messages().list(userId="me", q="is:unread").execute()
        messages = results.get("messages", [])

        processed_count = 0

        for msg in messages:
            msg_id = msg["id"]
            message = gmail_service.users().messages().get(userId="me", id=msg_id, format="full").execute()

            # Extraer cabeceras (Remitente y Asunto)
            headers = message.get("payload", {}).get("headers", [])
            sender = next((h["value"] for h in headers if h.get("name") == "From"), "Inconnu")
            subject = next((h["value"] for h in headers if h.get("name") == "Subject"), "Sans Objet")

            # Filtrar si el correo pertenece a un lead interesado en el probador
            low_subject = subject.lower()
            if "tryonyou" in low_subject or "pilot" in low_subject or "probador" in low_subject:
                # Registrar lead en Google Sheets
                range_name = "Leads!A:C"
                values = [[sender, subject, "En attente de révision humaine"]]
                body = {"values": values}

                sheets_service.spreadsheets().values().append(
                    spreadsheetId=GOOGLE_SHEETS_ID,
                    range=range_name,
                    valueInputOption="RAW",
                    body=body,
                ).execute()

                # Marcar como leído para evitar duplicados
                gmail_service.users().messages().batchModify(
                    userId="me",
                    body={"ids": [msg_id], "removeLabelIds": ["UNREAD"]},
                ).execute()

                processed_count += 1

        return jsonify(
            {
                "status": "success",
                "message": f"Traitement terminé. {processed_count} leads enregistrés dans Divineo_Leads_DB.",
            }
        ), 200
    except Exception as e:
        print(f"[tryonyou] jules email processing error: {e}", file=sys.stderr)
        return jsonify(
            {
                "status": "error",
                "message": "Erreur lors de l'exécution du service de messagerie.",
            }
        ), 500


# Vercel @vercel/python detects WSGI apps named `app` automatically.
# Do not define a `handler` function here, otherwise the runtime tries to call
# it as a HTTP handler instead of forwarding to the Flask app.

if __name__ == "__main__":  # local dev
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), debug=True)
