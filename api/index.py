import json
import sys
from pathlib import Path
from typing import Any

from flask import Flask, Response, jsonify, request

_ROOT = Path(__file__).resolve().parent.parent
_API_DIR = Path(__file__).resolve().parent
for _p in (_ROOT, _API_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from bunker_full_orchestrator import (  # noqa: E402
    orchestrate_beta_waitlist,
    orchestrate_mirror_shadow_dwell,
)
from core_engine import (  # noqa: E402
    CORE_ENGINE_PROTOCOL,
    health_payload,
    kill_switch_payload,
    model_access_payload,
    mirror_snap_payload,
    perfect_selection_payload,
    trace_event,
)
from mirror_digital_make import (  # noqa: E402
    forward_mirror_event,
    mirror_autonomy_status_payload,
)
from stripe_inauguration import create_inauguration_checkout_session  # noqa: E402
from stripe_webhook_fr import handle_stripe_webhook_fr  # noqa: E402

app = Flask(__name__)


def _cors(resp: Response) -> Response:
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
    resp.headers[
        "Access-Control-Allow-Headers"
    ] = "Content-Type, Authorization, X-Jules-Session-Id, X-Mirror-Session-Id, X-Jules-Account-Scope, X-Account-Scope, X-Kill-Switch-Secret"
    return resp


def _json_response(payload: dict[str, Any], status: int = 200) -> tuple[Response, int]:
    return _cors(jsonify(payload)), status


def _read_json_body() -> dict[str, Any]:
    if request.content_type and "application/json" not in request.content_type:
        raw = request.get_data(cache=True, as_text=True) or "{}"
        try:
            body = json.loads(raw)
        except json.JSONDecodeError:
            body = {}
        return body if isinstance(body, dict) else {}
    body = request.get_json(force=True, silent=True) or {}
    return body if isinstance(body, dict) else {}


def _handshake_payload() -> dict[str, Any]:
    health = health_payload()
    return {
        "status": "ok",
        "jules_msg": "Jules Core Engine online.",
        "protocolo": CORE_ENGINE_PROTOCOL,
        "next_step": "mirror_ready" if health.get("mirror_enabled") else "mirror_disabled",
        "product_lane": health.get("product_lane"),
        "mirror_enabled": health.get("mirror_enabled"),
    }


@app.route("/")
def home() -> tuple[Response, int]:
    return _json_response(health_payload(), 200)


@app.route("/api", methods=["GET", "POST", "OPTIONS"])
@app.route("/api/", methods=["GET", "POST", "OPTIONS"])
def api_root() -> tuple[Response, int]:
    if request.method == "OPTIONS":
        return _cors(Response(status=204)), 204
    if request.method == "GET":
        return _json_response(health_payload(), 200)
    body = _read_json_body()
    if body.get("ping"):
        return _json_response(_handshake_payload(), 200)
    return _json_response({"status": "error", "message": "Not Found"}, 404)


@app.route("/", methods=["POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
def root_mutations() -> tuple[Response, int]:
    if request.method == "OPTIONS":
        return _cors(Response(status=204)), 204
    body = _read_json_body()
    if body.get("ping"):
        return _json_response(_handshake_payload(), 200)
    return _json_response({"status": "error", "message": "Not Found"}, 404)


@app.route("/api/health", methods=["GET", "OPTIONS"])
@app.route("/health", methods=["GET", "OPTIONS"])
def health() -> tuple[Response, int]:
    if request.method == "OPTIONS":
        return _cors(Response(status=204)), 204
    return _json_response(health_payload(), 200)


@app.route("/api/v1/core/trace", methods=["POST", "OPTIONS"])
@app.route("/v1/core/trace", methods=["POST", "OPTIONS"])
def core_trace() -> tuple[Response, int]:
    if request.method == "OPTIONS":
        return _cors(Response(status=204)), 204
    body = _read_json_body()
    event_type = str(body.get("event_type") or body.get("event") or "custom_event").strip()
    source = str(body.get("source") or "core_trace").strip() or "core_trace"
    trace = trace_event(
        body=body,
        headers=request.headers,
        route="/api/v1/core/trace",
        event_type=event_type,
        source=source,
    )
    return _json_response({"status": "ok", "trace": trace, "protocol": CORE_ENGINE_PROTOCOL}, 200)


@app.route("/api/v1/mirror/snap", methods=["POST", "OPTIONS"])
@app.route("/v1/mirror/snap", methods=["POST", "OPTIONS"])
def mirror_snap() -> tuple[Response, int]:
    if request.method == "OPTIONS":
        return _cors(Response(status=204)), 204
    payload, code = mirror_snap_payload(_read_json_body(), request.headers)
    return _json_response(payload, code)


@app.route("/api/v1/checkout/perfect-selection", methods=["POST", "OPTIONS"])
@app.route("/v1/checkout/perfect-selection", methods=["POST", "OPTIONS"])
def perfect_selection() -> tuple[Response, int]:
    if request.method == "OPTIONS":
        return _cors(Response(status=204)), 204
    payload, code = perfect_selection_payload(_read_json_body(), request.headers)
    return _json_response(payload, code)


@app.route("/api/v1/core/model-access-token", methods=["POST", "OPTIONS"])
@app.route("/v1/core/model-access-token", methods=["POST", "OPTIONS"])
def model_access_token() -> tuple[Response, int]:
    if request.method == "OPTIONS":
        return _cors(Response(status=204)), 204
    payload, code = model_access_payload(_read_json_body(), request.headers)
    return _json_response(payload, code)


@app.route("/api/__jules__/control/kill-switch", methods=["GET", "POST", "OPTIONS"])
@app.route("/__jules__/control/kill-switch", methods=["GET", "POST", "OPTIONS"])
def kill_switch() -> tuple[Response, int]:
    if request.method == "OPTIONS":
        return _cors(Response(status=204)), 204
    body = _read_json_body() if request.method == "POST" else {}
    if request.method == "GET":
        body = {
            "action": request.args.get("action", "status"),
            "secret": request.args.get("secret", ""),
            "note": request.args.get("note", ""),
            "actor_id": request.args.get("actor_id", "mobile"),
            "account_scope": request.args.get("account_scope", "admin"),
        }
    payload, code = kill_switch_payload(body, request.headers)
    return _json_response(payload, code)


@app.route("/api/waitlist_beta", methods=["OPTIONS"])
@app.route("/waitlist_beta", methods=["OPTIONS"])
def waitlist_beta_options() -> tuple[Response, int]:
    return _cors(Response(status=204)), 204


@app.route("/api/waitlist_beta", methods=["POST"])
@app.route("/waitlist_beta", methods=["POST"])
def waitlist_beta() -> tuple[Response, int]:
    body = _read_json_body()
    try:
        result = orchestrate_beta_waitlist(body)
        return _json_response({"status": "ok", **result}, 200)
    except Exception as exc:  # noqa: BLE001
        return _json_response({"status": "error", "message": str(exc)}, 500)


@app.route("/api/mirror_shadow_log", methods=["OPTIONS"])
@app.route("/mirror_shadow_log", methods=["OPTIONS"])
def mirror_shadow_options() -> tuple[Response, int]:
    return _cors(Response(status=204)), 204


@app.route("/api/stripe_inauguration_checkout", methods=["OPTIONS"])
@app.route("/stripe_inauguration_checkout", methods=["OPTIONS"])
def stripe_inauguration_checkout_options() -> tuple[Response, int]:
    return _cors(Response(status=204)), 204


@app.route("/api/stripe_inauguration_checkout", methods=["POST"])
@app.route("/stripe_inauguration_checkout", methods=["POST"])
def stripe_inauguration_checkout() -> tuple[Response, int]:
    origin = request.headers.get("Origin") or ""
    payload, code = create_inauguration_checkout_session(origin or None)
    return _json_response(payload, code)


@app.route("/api/stripe_webhook_fr", methods=["POST"])
@app.route("/stripe_webhook_fr", methods=["POST"])
def stripe_webhook_fr() -> tuple[Response, int]:
    raw = request.get_data(cache=False)
    sig = request.headers.get("Stripe-Signature")
    payload, code = handle_stripe_webhook_fr(raw, sig)
    return jsonify(payload), code


@app.route("/api/mirror_digital_event", methods=["OPTIONS"])
@app.route("/mirror_digital_event", methods=["OPTIONS"])
def mirror_digital_event_options() -> tuple[Response, int]:
    return _cors(Response(status=204)), 204


@app.route("/api/mirror_digital_event", methods=["POST"])
@app.route("/mirror_digital_event", methods=["POST"])
def mirror_digital_event() -> tuple[Response, int]:
    body = _read_json_body()
    trace = trace_event(
        body=body,
        headers=request.headers,
        route="/api/mirror_digital_event",
        event_type=str(body.get("event") or "mirror_digital_event").strip(),
        source=str(body.get("source") or "tryonyou_mirror").strip() or "tryonyou_mirror",
    )
    payload, code = forward_mirror_event(body)
    payload["trace"] = trace
    return _json_response(payload, code)


@app.route("/api/v1/mirror/autonomy/status", methods=["GET", "OPTIONS"])
@app.route("/v1/mirror/autonomy/status", methods=["GET", "OPTIONS"])
def mirror_autonomy_status() -> tuple[Response, int]:
    if request.method == "OPTIONS":
        return _cors(Response(status=204)), 204
    return _json_response(mirror_autonomy_status_payload(), 200)


@app.route("/api/mirror_shadow_log", methods=["POST"])
@app.route("/mirror_shadow_log", methods=["POST"])
def mirror_shadow_log() -> tuple[Response, int]:
    body = _read_json_body()
    try:
        result = orchestrate_mirror_shadow_dwell(body)
        return _json_response({"status": "ok", **result}, 200)
    except Exception as exc:  # noqa: BLE001
        return _json_response({"status": "error", "message": str(exc)}, 500)
