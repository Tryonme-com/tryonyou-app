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
from stripe_handler import create_financial_connections_session
from stripe_inauguration import create_inauguration_checkout_session
from stripe_webhook import handle_webhook

app = Flask(__name__)


@app.route("/")
def home():
    return "API Active"


def _cors(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return resp


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


@app.route("/api/stripe_financial_connections_session", methods=["OPTIONS"])
@app.route("/stripe_financial_connections_session", methods=["OPTIONS"])
def stripe_financial_connections_session_options():
    return _cors(Response(status=204))


@app.route("/api/stripe_financial_connections_session", methods=["POST"])
@app.route("/stripe_financial_connections_session", methods=["POST"])
def stripe_financial_connections_session():
    body = request.get_json(force=True, silent=True) or {}
    verified_account = body.get("verified_account") or {}
    return_url = body.get("return_url") or ""
    permissions = body.get("permissions")
    countries = body.get("countries")
    prefetch = body.get("prefetch")

    payload, code = create_financial_connections_session(
        verified_account=verified_account,
        return_url=return_url,
        permissions=permissions,
        countries=countries,
        prefetch=prefetch,
    )
    return _cors(jsonify(payload)), code


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

    return jsonify({
        "status": "ok",
        "version": "V10.4_Lafayette",
        "stripe_configured": bool(stripe_secret),
        "stripe_4_5m_set": bool(stripe_link_4_5m),
        "stripe_98k_set": bool(stripe_link_98k),
        "webhook_secret_set": bool(webhook_secret),
    }), 200
