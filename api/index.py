import json
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
