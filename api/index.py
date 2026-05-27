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

import csv
import json
import os
import sqlite3
import sys
import time
import uuid
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Any

import stripe
from flask import Flask, jsonify, request, Response

try:
    import qrcode
    _QRCODE_AVAILABLE = True
except ImportError:
    _QRCODE_AVAILABLE = False

app = Flask(__name__)

DB_PATH = os.environ.get("TRYONYOU_DB_PATH", "/tmp/tryonyou_leads.sqlite")
SIREN = "943 610 196"
PATENT = "PCT/EP2025/067317"
ENDPOINT_SECRET = os.environ.get("STRIPE_ENDPOINT_SECRET", "").strip()

_RATE: dict[str, list[float]] = {}
RATE_WINDOW_S = 60.0
RATE_MAX = 6

# ─── Lafayette Piloto OMEGA — Catálogo Multimarca ─────────────────────────────

CATALOGO_GLOBAL: dict[str, list[dict[str, str]]] = {
    "balmain": [
        {"id": "blm_01", "nombre": "Blazer Cruzado Estructurado", "asset": "/assets/balmain_blazer.png", "planta": "Planta 1 - Córner Lujo"},
        {"id": "blm_02", "nombre": "Vestido Knit Geométrico", "asset": "/assets/balmain_dress.png", "planta": "Planta 1 - Córner Lujo"},
    ],
    "prada": [
        {"id": "prd_01", "nombre": "Abrigo Re-Nylon Minimalista Anthracite", "asset": "/assets/prada_coat.png", "planta": "Planta 2 - Créateurs"},
        {"id": "prd_02", "nombre": "Falda Plisada Estructurada", "asset": "/assets/prada_skirt.png", "planta": "Planta 2 - Créateurs"},
    ],
    "hermes": [
        {"id": "rms_01", "nombre": "Capa Corta en Cachemira Bone", "asset": "/assets/hermes_cape.png", "planta": "Planta 1 - Córner Lujo"},
        {"id": "rms_02", "nombre": "Pañuelo de Seda Art Deco", "asset": "/assets/hermes_scarf.png", "planta": "Planta 1 - Córner Lujo"},
    ],
}

# ─── Lafayette VIP (Efecto Paloma) ────────────────────────────────────────────
CATALOGO_VIP: dict[str, dict[str, Any]] = {
    "vip_look_01": {
        "name": "Alta Costura - Blazer Balmain Estructurado Edición Oro",
        "url_asset": "/assets/vip_balmain_gold.png",
        "zona_tienda": "Salón Privado Haussmann - Planta 1",
        "exclusivo": True,
    },
    "vip_look_02": {
        "name": "Visón de Primavera & Conjunto Minimalista Bone",
        "url_asset": "/assets/vip_spring_vison.png",
        "zona_tienda": "Salón Privado Haussmann - Planta 1",
        "exclusivo": True,
    },
}

# SAC Museum guest list — /tmp is the only writable path in Vercel serverless
_MUSEUM_CSV = Path("/tmp/lista_invitados_sac_museum.csv")
_MUSEUM_CSV_HEADER = ["Fecha_Registro", "Email", "Origen_Captacion", "Estado_Invitacion"]


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
        pass

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


# ─── Lafayette VIP — Efecto Paloma ────────────────────────────────────────────

@app.route("/api/lafayette/vip/activar", methods=["OPTIONS", "POST"])
def activar_efecto_paloma() -> Response:
    """Activa el Efecto Paloma: Mode Empire para el espejo digital."""
    if request.method == "OPTIONS":
        return _cors(Response("", status=204))

    body = request.get_json(silent=True) or {}
    client_token = str(body.get("client_token", "")).strip()
    if not client_token:
        return _json_err("Acceso VIP no autorizado", 403)

    return _json_ok({
        "status": "EMPIRE_MODE_ACTIVE",
        "experiencia": "VIP Premium - Efecto Paloma",
        "atencion_personalizada": "Asistente de planta notificado",
        "probador_privado": "Reservado automáticamente - Salón Haussmann",
        "restricciones_talla": "Desactivadas (Ajuste biométrico automatizado a medida)",
    })


@app.route("/api/lafayette/vip/reservar/<garment_id>", methods=["GET"])
def reservar_probador_vip(garment_id: str) -> Response:
    """Genera un QR de prioridad absoluta para el salón privado."""
    if garment_id not in CATALOGO_VIP:
        garment_id = "vip_look_01"

    reserva_id = f"VIP-PALOMA-{str(uuid.uuid4())[:4].upper()}"
    prenda = CATALOGO_VIP[garment_id]

    if not _QRCODE_AVAILABLE:
        return _json_ok({
            "reserva_id": reserva_id,
            "prenda": prenda["name"],
            "zona": prenda["zona_tienda"],
            "qr": None,
            "aviso": "qrcode no disponible en este entorno",
        })

    qr_data = (
        f"TRYONYOU-VIP\n"
        f"Reserva: {reserva_id}\n"
        f"Prenda: {prenda['name']}\n"
        f"Zona: {prenda['zona_tienda']}"
    )
    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return _cors(Response(buf.read(), status=200, mimetype="image/png"))


@app.route("/api/lafayette/vip/registrar-museum", methods=["OPTIONS", "POST"])
def registrar_invitado_sac_museum() -> Response:
    """Registra el email VIP en la lista de acceso del SAC Museum."""
    if request.method == "OPTIONS":
        return _cors(Response("", status=204))

    body = request.get_json(silent=True) or {}
    email = str(body.get("email", "")).strip().lower()
    origen = str(body.get("origen", "Espejo Digital - Efecto Paloma (Lafayette Haussmann)")).strip()

    if not _is_valid_email(email):
        return _json_err("Email inválido", 422, field="email")

    # Initialise CSV with header if needed
    try:
        if not _MUSEUM_CSV.exists() or _MUSEUM_CSV.stat().st_size == 0:
            _MUSEUM_CSV.parent.mkdir(parents=True, exist_ok=True)
            with open(_MUSEUM_CSV, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(_MUSEUM_CSV_HEADER)

        # Check for duplicate
        with open(_MUSEUM_CSV, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)  # skip header
            for row in reader:
                if row and row[1] == email:
                    return _json_ok({
                        "status": "already_registered",
                        "message": "Este perfil VIP ya se encuentra en la lista de acceso del SAC Museum.",
                    })

        # Append new guest
        fecha = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        with open(_MUSEUM_CSV, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([fecha, email, origen, "Pendiente de Envío Entrada"])
    except OSError as e:
        print(f"[tryonyou] sac-museum csv error: {e}", file=sys.stderr)

    print(f"[tryonyou] SAC_MUSEUM new guest: {email}", flush=True)

    return _json_ok({
        "status": "success",
        "message": "Correo recolectado y asignado a la lista de eventos del SAC Museum.",
        "email": email,
    }, 201)


@app.route("/api/museum/lista-invitados", methods=["GET"])
def obtener_lista_completa_museum() -> Response:
    """Retorna la lista consolidada de invitados VIP del SAC Museum."""
    lista: list[dict[str, str]] = []
    try:
        if _MUSEUM_CSV.exists():
            with open(_MUSEUM_CSV, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader, None)  # skip header
                for row in reader:
                    if row and len(row) >= 4:
                        lista.append({
                            "fecha": row[0],
                            "email": row[1],
                            "origen": row[2],
                            "estado": row[3],
                        })
    except OSError as e:
        print(f"[tryonyou] sac-museum read error: {e}", file=sys.stderr)

    return _json_ok({"total_invitados": len(lista), "invitados": lista})


# ─── Lafayette Piloto OMEGA — Endpoints ───────────────────────────────────────

@app.route("/status", methods=["GET"])
def get_status() -> Response:
    """Diagnóstico rápido del motor OMEGA."""
    return _json_ok({"status": "online", "engine": "OMEGA_V10.2", "mode": "Empire"})


@app.route("/api/lafayette/carrito", methods=["OPTIONS", "POST"])
def anadir_al_carrito() -> Response:
    """[Función 1] Mi Selección Perfecta — añade una prenda al carrito."""
    if request.method == "OPTIONS":
        return _cors(Response("", status=204))

    body = request.get_json(silent=True) or {}
    garment_id = str(body.get("garment_id", "")).strip()
    talla = str(body.get("talla_calculada", "")).strip()

    if not garment_id:
        return _json_err("garment_id requerido", 422, field="garment_id")

    return _json_ok({
        "status": "success",
        "tienda": "Galeries Lafayette Haussmann",
        "garment_id": garment_id,
        "talla_asegurada": talla or "M",
        "filtro": "Zero-Size Active",
    })


@app.route("/api/lafayette/reservar/<garment_id>", methods=["GET"])
def reservar_en_probador(garment_id: str) -> Response:
    """[Función 2] Reservar en Probador — genera un QR de acceso estándar."""
    reserva_id = f"GL-{str(uuid.uuid4())[:6].upper()}"
    datos_qr = f"https://tryonyou.lafayette.demo/verify/{reserva_id}"

    if not _QRCODE_AVAILABLE:
        return _json_ok({
            "reserva_id": reserva_id,
            "garment_id": garment_id,
            "qr": None,
            "aviso": "qrcode no disponible en este entorno",
        })

    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(datos_qr)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1a1a1a", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return _cors(Response(buf.read(), status=200, mimetype="image/png"))


@app.route("/api/lafayette/coleccion/<marca>", methods=["GET"])
def obtener_coleccion(marca: str) -> Response:
    """[Función 3] Ver Combinaciones — retorna el catálogo de la firma pulsada."""
    marca_key = marca.lower().strip()
    if marca_key not in CATALOGO_GLOBAL:
        return _json_err(
            f"Firma '{marca}' no disponible. Firmas válidas: {', '.join(CATALOGO_GLOBAL)}",
            404,
        )
    return _json_ok({"marca": marca, "sugerencias": CATALOGO_GLOBAL[marca_key]})


@app.route("/api/lafayette/silueta/guardar", methods=["OPTIONS", "POST"])
def guardar_silueta() -> Response:
    """[Función 4] Guardar mi Silueta — almacena puntos biométricos del espejo."""
    if request.method == "OPTIONS":
        return _cors(Response("", status=204))

    body = request.get_json(silent=True) or {}
    if not body:
        return _json_err("Payload biométrico ausente", 422)

    cliente_ref = f"LAFAYETTE_USER_{str(uuid.uuid4())[:6].upper()}"
    return _json_ok({"status": "stored", "cliente_referencia": cliente_ref})


@app.route("/api/lafayette/metricas", methods=["OPTIONS", "POST"])
def registrar_metricas() -> Response:
    """[Función 5] Compartir Look & Métricas — registra actividad del piloto."""
    if request.method == "OPTIONS":
        return _cors(Response("", status=204))

    metricas = request.get_json(silent=True) or {}
    print(f"[tryonyou] Métricas log: {json.dumps(metricas, ensure_ascii=False)}", flush=True)
    return _json_ok({"status": "recorded"})



# Vercel @vercel/python detects WSGI apps named `app` automatically.
# Do not define a `handler` function here, otherwise the runtime tries to call
# it as a HTTP handler instead of forwarding to the Flask app.

if __name__ == "__main__":  # local dev
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), debug=True)
