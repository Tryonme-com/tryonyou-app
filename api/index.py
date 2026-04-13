import json
import os
import sys
from pathlib import Path

from flask import Flask, Response, jsonify, request

_ROOT = Path(__file__).resolve().parent.parent
_API_DIR = Path(__file__).resolve().parent
for _p in (_ROOT, _API_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from bunker_full_orchestrator import (
    orchestrate_beta_waitlist,
    orchestrate_mirror_shadow_dwell,
)
from mirror_digital_make import forward_mirror_event
from stripe_inauguration import create_inauguration_checkout_session
from stripe_webhook import handle_webhook
from inventory_engine import inventory_match_payload
from shopify_bridge import resolve_shopify_checkout_url
from amazon_bridge import resolve_amazon_checkout_url

app = Flask(__name__)


@app.route("/")
def home():
    return "API Active"


def _cors(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return resp


def _append_demo_request(body):
    target = Path("/tmp/tryonyou_demo_requests.jsonl")
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(body, ensure_ascii=False) + "\n")


@app.route("/api/demo-request", methods=["OPTIONS"])
@app.route("/demo-request", methods=["OPTIONS"])
def demo_request_options():
    return _cors(Response(status=204))


@app.route("/api/demo-request", methods=["POST"])
@app.route("/demo-request", methods=["POST"])
def demo_request():
    body = request.get_json(force=True, silent=True) or {}
    normalized = {
        "name": str(body.get("name", "")).strip(),
        "company": str(body.get("company", "")).strip(),
        "email": str(body.get("email", "")).strip(),
        "role": str(body.get("role", "")).strip(),
        "catalog_size": str(body.get("catalog_size", "")).strip(),
        "message": str(body.get("message", "")).strip(),
        "source": str(body.get("source", "landing_demo_form")).strip() or "landing_demo_form",
        "locale": str(body.get("locale", "fr")).strip() or "fr",
        "ts": str(body.get("ts", "")).strip(),
        "intent": "demo_request",
        "protocol": "zero_size",
        "siret": "94361019600017",
        "patent": "PCT/EP2025/067317",
    }

    required = [normalized["name"], normalized["company"], normalized["email"], normalized["role"]]
    if not all(required):
        return _cors(jsonify({
            "status": "error",
            "message": "missing_required_fields",
        })), 400

    orchestration = False
    orchestration_error = ""

    try:
        _append_demo_request(normalized)
        try:
            orchestrate_beta_waitlist(normalized)
            orchestration = True
        except Exception as exc:
            orchestration_error = str(exc)
        return _cors(jsonify({
            "status": "ok",
            "demo_request_saved": True,
            "orchestration": orchestration,
            "orchestration_error": orchestration_error,
        })), 200
    except Exception as exc:
        return _cors(jsonify({
            "status": "error",
            "message": str(exc),
        })), 500


@app.route("/api/waitlist_beta", methods=["OPTIONS"])
@app.route("/waitlist_beta", methods=["OPTIONS"])
def waitlist_beta_options():
    return _cors(Response(status=204))


@app.route("/api/waitlist_beta", methods=["POST"])
@app.route("/waitlist_beta", methods=["POST"])
def waitlist_beta():
    body = request.get_json(force=True, silent=True) or {}
    try:
        result = orchestrate_beta_waitlist(body)
        return _cors(jsonify({"status": "ok", **result})), 200
    except Exception as e:
        return _cors(jsonify({"status": "error", "message": str(e)})), 500


@app.route("/api/mirror_shadow_log", methods=["OPTIONS"])
@app.route("/mirror_shadow_log", methods=["OPTIONS"])
def mirror_shadow_options():
    return _cors(Response(status=204))


@app.route("/api/stripe_inauguration_checkout", methods=["OPTIONS"])
@app.route("/stripe_inauguration_checkout", methods=["OPTIONS"])
def stripe_inauguration_checkout_options():
    return _cors(Response(status=204))


@app.route("/api/stripe_inauguration_checkout", methods=["POST"])
@app.route("/stripe_inauguration_checkout", methods=["POST"])
def stripe_inauguration_checkout():
    origin = request.headers.get("Origin") or ""
    payload, code = create_inauguration_checkout_session(origin or None)
    return _cors(jsonify(payload)), code


@app.route("/api/mirror_digital_event", methods=["OPTIONS"])
@app.route("/mirror_digital_event", methods=["OPTIONS"])
def mirror_digital_event_options():
    return _cors(Response(status=204))


@app.route("/api/mirror_digital_event", methods=["POST"])
@app.route("/mirror_digital_event", methods=["POST"])
def mirror_digital_event():
    body = request.get_json(force=True, silent=True) or {}
    payload, code = forward_mirror_event(body)
    return _cors(jsonify(payload)), code


@app.route("/api/mirror_shadow_log", methods=["POST"])
@app.route("/mirror_shadow_log", methods=["POST"])
def mirror_shadow_log():
    if request.content_type and "application/json" not in request.content_type:
        raw = request.get_data(cache=True, as_text=True) or "{}"
        try:
            body = json.loads(raw)
        except json.JSONDecodeError:
            body = {}
    else:
        body = request.get_json(force=True, silent=True) or {}
    try:
        result = orchestrate_mirror_shadow_dwell(body)
        return _cors(jsonify({"status": "ok", **result})), 200
    except Exception as e:
        return _cors(jsonify({"status": "error", "message": str(e)})), 500


@app.route("/api/webhook", methods=["POST"])
@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.get_data()
    sig_header = request.headers.get("Stripe-Signature", "")
    result, code = handle_webhook(payload, sig_header)
    return jsonify(result), code


# ── V1 Routes: Perfect Selection + Leads + Mirror Snap ─────────────

@app.route("/api/v1/checkout/perfect-selection", methods=["OPTIONS"])
def perfect_selection_options():
    return _cors(Response(status=204))


@app.route("/api/v1/checkout/perfect-selection", methods=["POST"])
def perfect_selection():
    body = request.get_json(force=True, silent=True) or {}
    fabric = str(body.get("fabric_sensation", "")).strip()
    lead_id = abs(hash(fabric or "anon")) % 10_000_000
    channel = os.environ.get("CHECKOUT_PRIMARY_CHANNEL", "shopify").strip().lower()

    shopify_url = resolve_shopify_checkout_url(lead_id, fabric)
    amazon_url = resolve_amazon_checkout_url(lead_id, fabric)
    primary_url = shopify_url if channel == "shopify" else amazon_url

    seal = (
        "Votre sélection parfaite est prête — "
        "ajustage biométrique validé sous protocole Zero-Size. "
        "Aucune taille classique, uniquement la certitude souveraine."
    )

    return _cors(jsonify({
        "status": "ok",
        "emotional_seal": seal,
        "checkout_primary_url": primary_url or "",
        "checkout_shopify_url": shopify_url or "",
        "checkout_amazon_url": amazon_url or "",
        "protocol": "zero_size",
        "anti_accumulation": True,
    })), 200


@app.route("/api/v1/leads", methods=["OPTIONS"])
def leads_options():
    return _cors(Response(status=204))


@app.route("/api/v1/leads", methods=["POST"])
def leads_capture():
    body = request.get_json(force=True, silent=True) or {}
    intent = str(body.get("intent", "")).strip()
    source = str(body.get("source", "app")).strip()

    try:
        result = orchestrate_beta_waitlist({
            "intent": intent,
            "source": source,
            "protocol": body.get("protocol", "zero_size"),
        })
        return _cors(jsonify({
            "status": "ok",
            "lead_persisted": True,
            **result,
        })), 200
    except Exception as e:
        return _cors(jsonify({
            "status": "ok",
            "lead_persisted": False,
            "message": str(e),
        })), 200


@app.route("/api/v1/mirror/snap", methods=["OPTIONS"])
def mirror_snap_options():
    return _cors(Response(status=204))


@app.route("/api/v1/mirror/snap", methods=["POST"])
def mirror_snap():
    body = request.get_json(force=True, silent=True) or {}
    fabric_sensation = str(body.get("fabric_sensation", "")).strip()
    fabric_fit_verdict = str(body.get("fabric_fit_verdict", "aligned")).strip()

    match = inventory_match_payload({
        "fabric_sensation": fabric_sensation,
        "fabric_fit_verdict": fabric_fit_verdict,
        "snap": True,
    })

    jules_msg = (
        "The Snap — votre ligne trouve son équilibre. "
        f"Référence {match.get('garment_id', 'V10')} ({match.get('brand_line', 'Maison')}) "
        "sous protocole Zero-Size. Le drapé répond avec élégance, sans mesure visible."
    )

    return _cors(jsonify({
        "status": "ok",
        "jules_msg": jules_msg,
        "inventory_match": match,
        "protocolo": "zero_size",
        "siren": "943610196",
        "patente": "PCT/EP2025/067317",
    })), 200


@app.route("/api/health", methods=["GET"])
@app.route("/health", methods=["GET"])
def health():
    stripe_secret = (os.getenv("STRIPE_SECRET_KEY") or "").strip()
    stripe_link_4_5m = (
        os.getenv("STRIPE_LINK_SOVEREIGNTY_4_5M")
        or os.getenv("VITE_STRIPE_LINK_SOVEREIGNTY_4_5M")
        or os.getenv("STRIPE_LINK_4_5M_EUR")
        or ""
    ).strip()
    stripe_link_98k = (
        os.getenv("STRIPE_LINK_SOVEREIGNTY_98K")
        or os.getenv("VITE_STRIPE_LINK_SOVEREIGNTY_98K")
        or os.getenv("STRIPE_LINK_98K_EUR")
        or ""
    ).strip()
    webhook_secret = (os.getenv("STRIPE_WEBHOOK_SECRET") or "").strip()

    return _cors(jsonify({
        "ok": True,
        "status": "ok",
        "version": "V11.0_Lafayette_Sovereign",
        "service": "tryonyou_v11_omega",
        "product_lane": "tryonyou_v11_sovereign",
        "siren": "943610196",
        "patente": "PCT/EP2025/067317",
        "stripe_configured": bool(stripe_secret),
        "stripe_4_5m_set": bool(stripe_link_4_5m),
        "stripe_98k_set": bool(stripe_link_98k),
        "webhook_secret_set": bool(webhook_secret),
    })), 200
