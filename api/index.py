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
from qonto_iban_transfer import (
    DEFAULT_BENEFICIARY,
    is_iban_transfer_configured,
    resolve_iban_transfer_details,
    validate_transfer_readiness,
)
from invoice_generator import generate_proforma
from treasury_monitor import (
    get_treasury_status,
    get_payouts_list,
    record_payout,
)
from territory_expansion import (
    get_expansion_nodes,
    get_territory_summary,
    generate_node_contract,
)
from empire_payout_trans import (
    get_flow_summary,
    register_checkout_success,
    register_payment_intent,
    register_payout_transition,
)
from core_engine import (
    trace_event,
    mirror_snap_payload,
    perfect_selection_payload,
    model_access_payload,
    kill_switch_status_payload,
    kill_switch_payload,
)

app = Flask(__name__)
MANUS_FLOW_ID = "f89d5d98"

_ALLOWED_PAYMENT_HOST_SUFFIXES = ("abvetos.com",)
_ALLOWED_PAYMENT_LOCAL_HOSTS = {"localhost", "127.0.0.1"}


def _is_allowed_payment_host(hostname: str) -> bool:
    h = hostname.lower().strip(".")
    if not h:
        return False
    if h in _ALLOWED_PAYMENT_LOCAL_HOSTS:
        return True
    return any(h == suffix or h.endswith(f".{suffix}") for suffix in _ALLOWED_PAYMENT_HOST_SUFFIXES)


def _sanitize_checkout_url(raw_url: str) -> str:
    raw = str(raw_url or "").strip()
    if not raw:
        return ""
    try:
        from urllib.parse import urlparse

        parsed = urlparse(raw)
        if parsed.scheme not in ("http", "https"):
            return ""
        if not _is_allowed_payment_host(parsed.hostname or ""):
            return ""
        return raw
    except Exception:
        return ""


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

    shopify_url = _sanitize_checkout_url(resolve_shopify_checkout_url(lead_id, fabric) or "")
    amazon_url = _sanitize_checkout_url(resolve_amazon_checkout_url(lead_id, fabric) or "")
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
        "payment_guard": {
            "external_checkout_blocked": True,
            "allowed_hosts": list(_ALLOWED_PAYMENT_HOST_SUFFIXES),
        },
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


# ── V11 Empire Final Protocol: Payment Intent + Success Trace ───────

@app.route("/api/v1/empire/payment-intent", methods=["OPTIONS"])
def empire_payment_intent_options():
    return _cors(Response(status=204))


@app.route("/api/v1/empire/payment-intent", methods=["POST"])
def empire_payment_intent():
    body = request.get_json(force=True, silent=True) or {}
    flow_token = str(body.get("flow_token", "")).strip()
    checkout_url = str(body.get("checkout_url", "")).strip()
    button_id = str(body.get("button_id", "tryonyou-pay-button")).strip()
    source = str(body.get("source", "index_html_shell")).strip()
    protocol = str(body.get("protocol", "Pau Emotional Intelligence")).strip()
    ui_theme = str(body.get("ui_theme", "Sello de Lujo: Antracita")).strip()

    if not flow_token or not checkout_url:
        return _cors(jsonify({
            "status": "error",
            "message": "flow_token_and_checkout_url_required",
        })), 400

    event = register_payment_intent(
        flow_token=flow_token,
        checkout_url=checkout_url,
        button_id=button_id,
        source=source,
        protocol=protocol,
        ui_theme=ui_theme,
    )
    return _cors(jsonify({"status": "ok", "intent": event})), 201


@app.route("/api/v1/empire/payment-success", methods=["OPTIONS"])
def empire_payment_success_options():
    return _cors(Response(status=204))


@app.route("/api/v1/empire/payment-success", methods=["POST"])
def empire_payment_success():
    body = request.get_json(force=True, silent=True) or {}
    flow_token = str(body.get("flow_token", "")).strip()
    session_id = str(body.get("session_id", "")).strip()
    source = str(body.get("source", "frontend_success_callback")).strip()
    amount_total = body.get("amount_total")
    currency = str(body.get("currency", "eur")).strip()
    customer_email = str(body.get("customer_email", "")).strip()

    event = register_checkout_success(
        session_id=session_id,
        amount_total=amount_total,
        currency=currency,
        customer_email=customer_email,
        flow_token=flow_token,
        source=source,
    )
    return _cors(jsonify({"status": "ok", "payment_success": event})), 201


@app.route("/api/v1/empire/flow-status", methods=["OPTIONS"])
def empire_flow_status_options():
    return _cors(Response(status=204))


@app.route("/api/v1/empire/flow-status", methods=["GET"])
def empire_flow_status():
    flow_token = str(request.args.get("flow_token", "")).strip()
    session_id = str(request.args.get("session_id", "")).strip()
    summary = get_flow_summary(flow_token=flow_token, session_id=session_id)
    return _cors(jsonify({"status": "ok", "flow": summary})), 200


# ── V11 Repair: Qonto IBAN Transfer + Proforma Invoices ─────────────

@app.route("/api/v1/payment/iban-transfer", methods=["OPTIONS"])
def iban_transfer_options():
    return _cors(Response(status=204))


@app.route("/api/v1/payment/iban-transfer", methods=["GET"])
def iban_transfer_details():
    readiness, code = validate_transfer_readiness()
    if code != 200:
        return _cors(jsonify(readiness)), code

    amount_key = request.args.get("amount", None)
    details = resolve_iban_transfer_details(amount_key)
    return _cors(jsonify({
        "status": "ok",
        **details,
    })), 200


@app.route("/api/v1/payment/iban-transfer", methods=["POST"])
def iban_transfer_initiate():
    body = request.get_json(force=True, silent=True) or {}
    amount_key = str(body.get("amount_key", "")).strip() or None

    readiness, code = validate_transfer_readiness()
    if code != 200:
        return _cors(jsonify(readiness)), code

    details = resolve_iban_transfer_details(amount_key)
    invoice = generate_proforma(
        to=str(body.get("to", DEFAULT_BENEFICIARY)).strip(),
        amount_key=amount_key,
        extra_note=str(body.get("note", "")).strip(),
    )

    return _cors(jsonify({
        "status": "ok",
        "transfer": details,
        "invoice": invoice,
        "message": "Proforma générée. Procédez au virement SEPA Business.",
    })), 200


@app.route("/api/v1/invoice/proforma", methods=["OPTIONS"])
def invoice_proforma_options():
    return _cors(Response(status=204))


@app.route("/api/v1/invoice/proforma", methods=["POST"])
def invoice_proforma():
    body = request.get_json(force=True, silent=True) or {}
    to = str(body.get("to", DEFAULT_BENEFICIARY)).strip()
    amount_key = str(body.get("amount_key", "")).strip() or None
    note = str(body.get("note", "")).strip()

    invoice = generate_proforma(to=to, amount_key=amount_key, extra_note=note)
    return _cors(jsonify({
        "status": "ok",
        "invoice": invoice,
    })), 200


# ── V11 Treasury: Payout Monitoring & Capital Blindaje ───────────────

@app.route("/api/v1/treasury/status", methods=["OPTIONS"])
def treasury_status_options():
    return _cors(Response(status=204))


@app.route("/api/v1/treasury/status", methods=["GET"])
def treasury_status():
    status = get_treasury_status()
    return _cors(jsonify({"status": "ok", **status})), 200


@app.route("/api/v1/treasury/payouts", methods=["OPTIONS"])
def treasury_payouts_options():
    return _cors(Response(status=204))


@app.route("/api/v1/treasury/payouts", methods=["GET"])
def treasury_payouts_list():
    payouts = get_payouts_list()
    return _cors(jsonify({
        "status": "ok",
        "payouts": payouts,
        "count": len(payouts),
    })), 200


@app.route("/api/v1/treasury/payouts", methods=["POST"])
def treasury_record_payout():
    body = request.get_json(force=True, silent=True) or {}
    amount = body.get("amount_eur")
    if not amount or not isinstance(amount, (int, float)) or amount <= 0:
        return _cors(jsonify({
            "status": "error",
            "message": "amount_eur_required_positive",
        })), 400

    entry = record_payout(
        amount_eur=float(amount),
        recipient=str(body.get("recipient", "")).strip(),
        concept=str(body.get("concept", "operational")).strip(),
    )
    flow_token = str(body.get("flow_token", "")).strip()
    session_id = str(body.get("session_id", "")).strip()
    register_payout_transition(
        amount_eur=float(amount),
        recipient=entry.get("recipient", ""),
        concept=entry.get("concept", "operational"),
        flow_token=flow_token,
        session_id=session_id,
        source="api_v1_treasury_payouts",
    )
    return _cors(jsonify({"status": "ok", "payout": entry})), 201


# ── V11 Territory: Multi-Node Expansion & Licensing ─────────────────

@app.route("/api/v1/territory/nodes", methods=["OPTIONS"])
def territory_nodes_options():
    return _cors(Response(status=204))


@app.route("/api/v1/territory/nodes", methods=["GET"])
def territory_nodes():
    nodes = get_expansion_nodes()
    summary = get_territory_summary()
    return _cors(jsonify({
        "status": "ok",
        "nodes": nodes,
        "summary": summary,
    })), 200


@app.route("/api/v1/territory/contracts", methods=["OPTIONS"])
def territory_contracts_options():
    return _cors(Response(status=204))


@app.route("/api/v1/territory/contracts", methods=["POST"])
def territory_generate_contract():
    body = request.get_json(force=True, silent=True) or {}
    node_id = str(body.get("node_id", "")).strip()
    if not node_id:
        return _cors(jsonify({
            "status": "error",
            "message": "node_id_required",
        })), 400

    contract = generate_node_contract(node_id)
    if not contract:
        return _cors(jsonify({
            "status": "error",
            "message": "node_not_found",
        })), 404

    return _cors(jsonify({"status": "ok", "contract": contract})), 201


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

    territory = get_territory_summary()
    treasury = get_treasury_status()

    return _cors(jsonify({
        "ok": True,
        "status": "ok",
        "version": "V11.2_Rive_Gauche_Manus",
        "service": "tryonyou_v11_omega",
        "product_lane": "tryonyou_v11_sovereign",
        "siren": "943610196",
        "patente": "PCT/EP2025/067317",
        "manus_flow_id": MANUS_FLOW_ID,
        "payment_external_checkout_blocked": True,
        "payment_allowed_hosts": list(_ALLOWED_PAYMENT_HOST_SUFFIXES),
        "stripe_configured": bool(stripe_secret),
        "stripe_4_5m_set": bool(stripe_link_4_5m),
        "stripe_98k_set": bool(stripe_link_98k),
        "webhook_secret_set": bool(webhook_secret),
        "iban_transfer_configured": is_iban_transfer_configured(),
        "payment_method": "DIRECT_IBAN_TRANSFER" if is_iban_transfer_configured() else "STRIPE",
        "territory_active_nodes": territory["active_nodes"],
        "territory_pending_nodes": territory["pending_nodes"],
        "territory_expansion_target_eur": territory["expansion_target_eur"],
        "treasury_reserve_eur": treasury["reserve_eur"],
        "treasury_capital_label": treasury["capital_label"],
    })), 200



# ── Core Engine V11 Routes ──────────────────────────────────────────────────

@app.route("/api/v1/core/trace", methods=["OPTIONS"])
def core_trace_options():
    return _cors(Response("", status=204))

@app.route("/api/v1/core/trace", methods=["POST"])
def core_trace():
    body = request.get_json(silent=True) or {}
    try:
        result = trace_event(
            event_type=body.get("event_type", "unknown"),
            body=body,
            headers=dict(request.headers),
            route="/api/v1/core/trace",
            source=body.get("source", "api"),
        )
        return _cors(jsonify(result)), 200
    except Exception as exc:
        return _cors(jsonify({"status": "ok", "db_persisted": False, "error": str(exc)})), 200



@app.route("/api/v1/core/model-access-token", methods=["OPTIONS"])
def model_access_token_options():
    return _cors(Response("", status=204))

@app.route("/api/v1/core/model-access-token", methods=["POST"])
def model_access_token():
    body = request.get_json(silent=True) or {}
    try:
        result, status = model_access_payload(body, dict(request.headers))
        return _cors(jsonify(result)), status
    except Exception as exc:
        return _cors(jsonify({"status": "error", "message": str(exc)})), 500


@app.route("/api/__jules__/control/kill-switch", methods=["OPTIONS"])
def kill_switch_options():
    return _cors(Response("", status=204))

@app.route("/api/__jules__/control/kill-switch", methods=["GET"])
def kill_switch_get():
    return _cors(jsonify(kill_switch_status_payload())), 200

@app.route("/api/__jules__/control/kill-switch", methods=["POST"])
def kill_switch_post():
    body = request.get_json(silent=True) or {}
    result, status = kill_switch_payload(body, dict(request.headers))
    return _cors(jsonify(result)), status
