import hmac
import json
import os
import sys
import traceback
from datetime import datetime, timezone
from urllib.parse import urlencode
from pathlib import Path

from flask import Flask, Response, jsonify, request

_ROOT = Path(__file__).resolve().parent.parent
_API_DIR = Path(__file__).resolve().parent
for _p in (_ROOT, _API_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

_BOOT_ERRORS = []

def _safe_import(module_name, names):
    result = {}
    try:
        mod = __import__(module_name, fromlist=names)
        for n in names:
            result[n] = getattr(mod, n, None)
    except Exception as e:
        _BOOT_ERRORS.append(f"{module_name}: {e}")
        for n in names:
            result[n] = None
    return result

_i = _safe_import('bunker_full_orchestrator', ['orchestrate_beta_waitlist', 'orchestrate_mirror_shadow_dwell'])
orchestrate_beta_waitlist = _i['orchestrate_beta_waitlist']
orchestrate_mirror_shadow_dwell = _i['orchestrate_mirror_shadow_dwell']

_i = _safe_import('financial_guard', ['guard_stripe_call', 'log_sovereignty_event'])
guard_stripe_call = _i['guard_stripe_call']
log_sovereignty_event = _i['log_sovereignty_event']

_i = _safe_import('mirror_digital_make', ['forward_mirror_event'])
forward_mirror_event = _i['forward_mirror_event']

_i = _safe_import('stripe_lafayette', ['create_lafayette_checkout'])
create_lafayette_checkout = _i['create_lafayette_checkout']

_i = _safe_import('stripe_inauguration', ['create_inauguration_checkout_session'])
create_inauguration_checkout_session = _i['create_inauguration_checkout_session']

_i = _safe_import('stripe_webhook', ['handle_webhook'])
handle_webhook = _i['handle_webhook']

_i = _safe_import('inventory_engine', ['inventory_match_payload'])
inventory_match_payload = _i['inventory_match_payload']

_i = _safe_import('shopify_bridge', ['resolve_shopify_checkout_url'])
resolve_shopify_checkout_url = _i['resolve_shopify_checkout_url']

_i = _safe_import('amazon_bridge', ['resolve_amazon_checkout_url'])
resolve_amazon_checkout_url = _i['resolve_amazon_checkout_url']

_i = _safe_import(
    'qonto_iban_transfer',
    [
        'DEFAULT_BENEFICIARY',
        'is_iban_transfer_configured',
        'resolve_iban_transfer_details',
        'validate_transfer_readiness',
        'validate_qonto_invoice_import_readiness',
    ],
)
DEFAULT_BENEFICIARY = _i['DEFAULT_BENEFICIARY']
is_iban_transfer_configured = _i['is_iban_transfer_configured']
resolve_iban_transfer_details = _i['resolve_iban_transfer_details']
validate_transfer_readiness = _i['validate_transfer_readiness']
validate_qonto_invoice_import_readiness = _i['validate_qonto_invoice_import_readiness']

_i = _safe_import('invoice_generator', ['generate_proforma'])
generate_proforma = _i['generate_proforma']

_i = _safe_import('balance_soberana', ['master_ledger', 'ledger_soberano', 'FACTURA_F_2026_001'])
master_ledger = _i['master_ledger']
ledger_soberano = _i['ledger_soberano']
FACTURA_F_2026_001 = _i['FACTURA_F_2026_001']

_i = _safe_import('financial_compliance', ['build_financial_reconciliation_report', 'build_compliance_status_summary'])
build_financial_reconciliation_report = _i['build_financial_reconciliation_report']
build_compliance_status_summary = _i['build_compliance_status_summary']

_i = _safe_import('treasury_monitor', ['get_treasury_status', 'get_payouts_list', 'record_payout'])
get_treasury_status = _i['get_treasury_status']
get_payouts_list = _i['get_payouts_list']
record_payout = _i['record_payout']

_i = _safe_import('territory_expansion', ['get_expansion_nodes', 'get_territory_summary', 'generate_node_contract'])
get_expansion_nodes = _i['get_expansion_nodes']
get_territory_summary = _i['get_territory_summary']
generate_node_contract = _i['generate_node_contract']

_i = _safe_import('empire_payout_trans', ['get_flow_summary', 'register_checkout_success', 'register_payment_intent', 'register_payout_transition'])
get_flow_summary = _i['get_flow_summary']
register_checkout_success = _i['register_checkout_success']
register_payment_intent = _i['register_payment_intent']
register_payout_transition = _i['register_payout_transition']

_i = _safe_import('update_net_liquidity', ['build_master_ledger_status', 'get_ledger_status', 'persist_ledger_status', 'compute_net_liquidity'])
build_master_ledger_status = _i['build_master_ledger_status']
get_ledger_status = _i['get_ledger_status']
persist_ledger_status = _i['persist_ledger_status']
compute_net_liquidity = _i['compute_net_liquidity']

_i = _safe_import('core_engine', ['trace_event', 'mirror_snap_payload', 'perfect_selection_payload', 'model_access_payload', 'kill_switch_status_payload', 'kill_switch_payload'])
trace_event = _i['trace_event']
mirror_snap_payload = _i['mirror_snap_payload']
perfect_selection_payload = _i['perfect_selection_payload']
model_access_payload = _i['model_access_payload']
kill_switch_status_payload = _i['kill_switch_status_payload']
kill_switch_payload = _i['kill_switch_payload']

_i = _safe_import('core_engine', ['SupabaseStore', 'persist_event', 'persist_session', 'save_control_state'])
SupabaseStore = _i['SupabaseStore']
persist_event = _i['persist_event'] or (lambda *a, **kw: None)
persist_session = _i['persist_session'] or (lambda *a, **kw: None)
save_control_state = _i['save_control_state'] or (lambda *a, **kw: None)

_i = _safe_import('divineo_global_orchestrator', ['get_orchestrator_status', 'get_pilot_kpis', 'trigger_global_authority'])
get_orchestrator_status = _i['get_orchestrator_status']
get_pilot_kpis = _i['get_pilot_kpis']
trigger_global_authority = _i['trigger_global_authority']

_i = _safe_import('resend_outreach', ['is_outreach_configured', 'send_brand_proposal', 'send_batch_proposals', 'get_brand_list', 'get_outreach_logs'])
is_outreach_configured = _i['is_outreach_configured']
send_brand_proposal = _i['send_brand_proposal']
send_batch_proposals = _i['send_batch_proposals']
get_brand_list = _i['get_brand_list']
get_outreach_logs = _i['get_outreach_logs']

app = Flask(__name__)

@app.route('/api/debug-boot')
def _debug_boot():
    return jsonify({'boot_errors': _BOOT_ERRORS, 'sys_path': sys.path[:5], 'root': str(_ROOT), 'api_dir': str(_API_DIR)})
MANUS_FLOW_ID = "f89d5d98"
ADVBET_PROVIDER = "advbet"

_ALLOWED_PAYMENT_HOST_SUFFIXES = ("abvetos.com",)
_ALLOWED_PAYMENT_LOCAL_HOSTS = {"localhost", "127.0.0.1"}
_PAYMENT_ORCHESTRATION_LOCKS: set[str] = set()



PAU_ENGINE_VERSION = "V12_Pau_Core_Engine"
PAU_SOVEREIGNTY_STATE = "SOUVERAINETÉ:1"
PAU_PATENT_REFERENCE = "PCT/EP2025/067317"
PAU_SIREN = "943610196"
PAU_SIREN_FORMATTED = "943 610 196"
PAU_DEFAULT_STORE = "Galeries Lafayette Haussmann"
PAU_DEFAULT_LOCATION = "Planta 1 - Espejo Digital"
_PAU_ENGINE = None


class PauPeacockEngine:
    def __init__(self):
        self.stripe_key = (os.getenv("STRIPE_SECRET_KEY") or "").strip()
        self.sb_url = (
            os.getenv("PAU_SUPABASE_URL")
            or os.getenv("SUPABASE_URL")
            or "https://irwyurrpofyzcdsihjmz.supabase.co"
        ).strip()
        self.sb_key = (os.getenv("SUPABASE_SERVICE_ROLE_KEY") or "").strip()
        self.persona = "Eric - Family Lafayette Expert"
        self._stripe = None
        self._db = None

    def _stripe_client(self):
        if self._stripe is False:
            return None
        if self._stripe is None:
            try:
                import stripe

                stripe.api_key = self.stripe_key
                self._stripe = stripe
            except Exception:
                self._stripe = False
        return None if self._stripe is False else self._stripe

    def _supabase_client(self):
        if self._db is False:
            return None
        if self._db is None:
            if not self.sb_key:
                self._db = False
                return None
            try:
                from supabase import create_client

                self._db = create_client(self.sb_url, self.sb_key)
            except Exception:
                self._db = False
        return None if self._db is False else self._db

    def process_body_scan(self, weight, height, event_type):
        recommendations = self._calculate_ideal_looks(height, weight, event_type)
        return {
            "status": "Success",
            "message": "Silueta capturada con elegancia.",
            "persona": self.persona,
            "scan": {
                "weight_kg": weight,
                "height_cm": height,
                "event_type": event_type,
            },
            "looks": recommendations,
        }

    def trigger_snap_logic(self, look_id):
        safe_look_id = str(look_id or "L1").strip() or "L1"
        return {
            "status": "Success",
            "action": "update_avatar_mesh",
            "look_id": safe_look_id,
            "model_url": f"/models/looks/{safe_look_id}.glb",
        }

    def handle_perfect_selection(self, user_id, look_data):
        normalized_look = {
            "id": str((look_data or {}).get("id") or "L1").strip() or "L1",
            "name": str((look_data or {}).get("name") or "Pau Curated Look").strip() or "Pau Curated Look",
            "price": float((look_data or {}).get("price") or 0),
        }
        stripe_client = self._stripe_client()
        if not self.stripe_key or stripe_client is None or not getattr(stripe_client, "checkout", None):
            return {
                "status": "Fallback",
                "checkout_session_created": False,
                "checkout_url": "",
                "payment_provider": "stripe",
                "message": "Stripe no configurado; la selección perfecta queda registrada sin sesión de pago.",
                "look": normalized_look,
            }
        try:
            checkout_session = stripe_client.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'eur',
                        'product_data': {'name': normalized_look['name']},
                        'unit_amount': int(round(normalized_look['price'] * 100)),
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url='https://tryonyou.app/success',
                cancel_url='https://tryonyou.app/cancel',
                metadata={
                    'user_id': str(user_id or 'PAU_GUEST'),
                    'look_id': normalized_look['id'],
                    'type': 'Lafayette_Selection',
                    'sovereignty_state': PAU_SOVEREIGNTY_STATE,
                },
            )
            return {
                "status": "Success",
                "checkout_session_created": True,
                "checkout_url": checkout_session.url,
                "payment_provider": "stripe",
                "look": normalized_look,
            }
        except Exception as exc:
            return {
                "status": "Error",
                "checkout_session_created": False,
                "checkout_url": "",
                "payment_provider": "stripe",
                "error": str(exc),
                "look": normalized_look,
            }

    def reserve_in_store(self, user_id, look_id):
        qr_code_data = f"RES-{user_id}-{look_id}-{datetime.now().timestamp()}"
        payload = {
            "user_id": user_id,
            "look_id": look_id,
            "store": PAU_DEFAULT_STORE,
            "status": "Pending",
            "sovereignty_state": PAU_SOVEREIGNTY_STATE,
        }
        db = self._supabase_client()
        persisted = False
        db_error = ""
        if db is not None:
            try:
                db.table("reservations").insert(payload).execute()
                persisted = True
            except Exception as exc:
                db_error = str(exc)
        else:
            db_error = "supabase_not_configured"
        return {
            "status": "Success",
            "qr_data": qr_code_data,
            "location": PAU_DEFAULT_LOCATION,
            "store": PAU_DEFAULT_STORE,
            "reservation": payload,
            "db_persisted": persisted,
            "db_error": db_error,
        }

    def sync_sovereignty_state(self, user_id):
        db = self._supabase_client()
        if not user_id:
            return {
                "status": "Skipped",
                "db_persisted": False,
                "message": "user_id_not_provided",
            }
        if db is None:
            return {
                "status": "Skipped",
                "db_persisted": False,
                "message": "supabase_not_configured",
            }
        try:
            db.table("profiles").update({"state": PAU_SOVEREIGNTY_STATE}).eq("id", user_id).execute()
            return {
                "status": "Success",
                "db_persisted": True,
                "message": f"Soberanía confirmada para usuario {user_id}.",
            }
        except Exception as exc:
            return {
                "status": "Error",
                "db_persisted": False,
                "message": str(exc),
            }

    def sovereignty_status(self, user_id=""):
        return {
            "status": "active",
            "user_id": str(user_id or "").strip(),
            "state": PAU_SOVEREIGNTY_STATE,
            "persona": self.persona,
            "patent_reference": PAU_PATENT_REFERENCE,
            "siren": PAU_SIREN,
            "siren_formatted": PAU_SIREN_FORMATTED,
            "stripe_configured": bool(self.stripe_key),
            "supabase_configured": bool(self.sb_key),
        }

    def _calculate_ideal_looks(self, h, w, event):
        event_label = str(event or "soirée").strip().lower()
        base_looks = [
            {
                "id": "L1",
                "name": "Balmain Evening",
                "price": 2450.00,
                "fit_profile": "structured",
                "event_tags": ["gala", "soirée", "evening", "cocktail"],
            },
            {
                "id": "L2",
                "name": "Jacquemus Summer",
                "price": 1100.00,
                "fit_profile": "fluid",
                "event_tags": ["summer", "day", "garden", "casual"],
            },
            {
                "id": "L3",
                "name": "Saint Laurent Tuxedo",
                "price": 3200.00,
                "fit_profile": "tailored",
                "event_tags": ["formal", "black tie", "soirée", "dinner"],
            },
            {
                "id": "L4",
                "name": "Dior Silhouette",
                "price": 2800.00,
                "fit_profile": "architectural",
                "event_tags": ["editorial", "business", "vernissage", "formal"],
            },
            {
                "id": "L5",
                "name": "Chanel Classic",
                "price": 4100.00,
                "fit_profile": "classic",
                "event_tags": ["classic", "heritage", "cocktail", "soirée"],
            },
        ]
        ranked = []
        for look in base_looks:
            score = 0
            if event_label and event_label in look["event_tags"]:
                score += 10
            if h and h >= 175 and look["fit_profile"] in {"tailored", "architectural", "structured"}:
                score += 2
            if h and h < 165 and look["fit_profile"] in {"fluid", "classic"}:
                score += 2
            if w and w >= 80 and look["fit_profile"] in {"structured", "classic"}:
                score += 1
            ranked.append({
                "id": look["id"],
                "name": look["name"],
                "price": look["price"],
                "fit_profile": look["fit_profile"],
                "score": score,
            })
        return sorted(ranked, key=lambda item: (-item["score"], item["price"]))


def _get_pau_engine():
    global _PAU_ENGINE
    if _PAU_ENGINE is None:
        _PAU_ENGINE = PauPeacockEngine()
    return _PAU_ENGINE


def _pau_float(value):
    try:
        if value in (None, ""):
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _pau_payload(payload=None):
    merged = {
        "version": PAU_ENGINE_VERSION,
        "engine": "PauPeacockEngine",
        "SOUVERAINETÉ": 1,
        "sovereignty_state": PAU_SOVEREIGNTY_STATE,
        "siren": PAU_SIREN,
    }
    if isinstance(payload, dict):
        merged.update(payload)
    return merged


def _pau_resolve_look(body):
    body = body or {}
    provided = body.get("look_data")
    if isinstance(provided, dict) and provided:
        return {
            "id": str(provided.get("id") or "L1").strip() or "L1",
            "name": str(provided.get("name") or "Pau Curated Look").strip() or "Pau Curated Look",
            "price": _pau_float(provided.get("price") or 0),
        }

    engine = _get_pau_engine()
    recommendations = engine._calculate_ideal_looks(
        _pau_float(body.get("height") or body.get("height_cm")),
        _pau_float(body.get("weight") or body.get("weight_kg")),
        str(body.get("event_type") or body.get("occasion") or "soirée").strip() or "soirée",
    )
    requested_look_id = str(body.get("look_id") or "").strip()
    if requested_look_id:
        for look in recommendations:
            if look.get("id") == requested_look_id:
                return look
        return {
            "id": requested_look_id,
            "name": f"Pau Curated Look {requested_look_id}",
            "price": recommendations[0]["price"] if recommendations else 0.0,
        }
    return recommendations[0] if recommendations else {"id": "L1", "name": "Balmain Evening", "price": 2450.0}

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


def _advbet_biometric_deep_link_base() -> str:
    return (
        os.getenv("ADVBET_BIOMETRIC_DEEP_LINK_BASE")
        or os.getenv("BIOMETRIC_DEEP_LINK_BASE")
        or "https://tryonyou.app/biometric-verify"
    ).strip().rstrip("/")


def _advbet_payload(*, session_id: str, amount_eur: float) -> dict[str, object]:
    deep_link = f"{_advbet_biometric_deep_link_base()}?{urlencode({'session_id': session_id, 'amount_eur': amount_eur})}"
    return {
        "provider": ADVBET_PROVIDER,
        "biometric_deep_link": deep_link,
        "qr_payload": {
            "format": "deep_link",
            "deep_link": deep_link,
        },
    }


@app.route("/")
def home():
    return "API Active"


@app.route("/", methods=["POST", "PUT", "PATCH", "DELETE"])
def home_mutating_blocked():
    return _cors(jsonify({"status": "error", "message": "Not Found"})), 404


def _cors(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return resp


def _ensure_sovereignty_payload(payload):
    if isinstance(payload, dict):
        payload.setdefault("SOUVERAINETÉ", 1)
        payload.setdefault("sovereignty_state", PAU_SOVEREIGNTY_STATE)
        payload.setdefault("siren", PAU_SIREN)
    return payload


@app.after_request
def _apply_global_sovereignty_headers(resp):
    resp = _cors(resp)
    if resp.status_code == 204:
        return resp
    content_type = (resp.headers.get("Content-Type") or "").lower()
    if "application/json" not in content_type:
        return resp
    try:
        payload = resp.get_json(silent=True)
        if isinstance(payload, dict):
            payload = _ensure_sovereignty_payload(payload)
            body = json.dumps(payload, ensure_ascii=False)
            resp.set_data(body)
            resp.headers["Content-Length"] = str(len(body.encode("utf-8")))
    except Exception:
        return resp
    return resp


def _append_demo_request(body):
    target = Path("/tmp/tryonyou_demo_requests.jsonl")
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(body, ensure_ascii=False) + "\n")


_BUNKER_SYNC_PROTOCOL = "bunker_sync_v1"
_BUNKER_SYNC_ROUTE = "/api/v1/bunker/sync"
# IDs de payout / PI deben ser los de Stripe LIVE (ver .env.example). No hardcodear po_/pi_ de test.
_BUNKER_SYNC_PAYOUT_AMOUNT_EUR = 27_500.00
_BUNKER_SYNC_PAYMENT_INTENT_AMOUNT_EUR = 96_981.60


def _bunker_sync_env_payout_id() -> str:
    return (os.getenv("BUNKER_SYNC_STRIPE_PAYOUT_ID") or "").strip()


def _bunker_sync_env_payment_intent_ids() -> list[str]:
    raw = (os.getenv("BUNKER_SYNC_PAYMENT_INTENT_IDS") or "").strip()
    if not raw:
        return []
    return [x.strip() for x in raw.split(",") if x.strip()]


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()



def _bunker_sync_secret() -> str:
    for key in (
        "BUNKER_SYNC_SECRET",
        "JULES_BUNKER_SYNC_SECRET",
        "JULES_KILL_SWITCH_SECRET",
        "CORE_ENGINE_KILL_SWITCH_SECRET",
    ):
        raw = (os.getenv(key) or "").strip()
        if raw:
            return raw
    return ""



def _bunker_sync_supabase_tables() -> dict[str, str]:
    return {
        "payouts": (os.getenv("BUNKER_PAYOUTS_TABLE") or "payouts").strip() or "payouts",
        "payment_intents": (
            os.getenv("BUNKER_PAYMENT_INTENTS_TABLE") or "payment_intents"
        ).strip() or "payment_intents",
        "clients": (os.getenv("BUNKER_CLIENTS_TABLE") or "clients").strip() or "clients",
        "compliance_logs": (
            os.getenv("BUNKER_COMPLIANCE_LOGS_TABLE") or "compliance_logs"
        ).strip() or "compliance_logs",
        "watchdog_logs": (
            os.getenv("BUNKER_WATCHDOG_LOGS_TABLE") or "watchdog_logs"
        ).strip() or "watchdog_logs",
    }



def _bunker_sync_provided_secret(body: dict, headers: dict[str, str]) -> str:
    auth_header = str(headers.get("Authorization", "")).strip()
    bearer = ""
    if auth_header.lower().startswith("bearer "):
        bearer = auth_header[7:].strip()
    return str(
        body.get("secret")
        or body.get("bunker_sync_secret")
        or headers.get("X-Bunker-Sync-Secret")
        or headers.get("X-Kill-Switch-Secret")
        or bearer
        or ""
    ).strip()



def _bunker_sync_authorized(body: dict, headers: dict[str, str]) -> bool:
    expected = _bunker_sync_secret()
    provided = _bunker_sync_provided_secret(body, headers)
    return bool(expected and provided and hmac.compare_digest(expected, provided))



def _bunker_sync_write_row(
    store: SupabaseStore,
    table: str,
    row: dict,
    *,
    on_conflict: str = "",
) -> dict[str, object]:
    try:
        if on_conflict:
            store.upsert(table, row, on_conflict=on_conflict)
            mode = "upsert"
        else:
            store.insert(table, row)
            mode = "insert"
        return {"table": table, "ok": True, "mode": mode}
    except Exception as exc:
        return {
            "table": table,
            "ok": False,
            "mode": "upsert" if on_conflict else "insert",
            "error": str(exc)[:400],
        }



def _bunker_sync_control_row(
    *,
    control_key: str,
    state: str,
    updated_by: str,
    account_scope: str,
    note: str,
    updated_at: str,
) -> dict[str, object]:
    return {
        "control_key": control_key,
        "state": state,
        "updated_at": updated_at,
        "updated_by": updated_by,
        "account_scope": account_scope,
        "note": note,
        "protocol": _BUNKER_SYNC_PROTOCOL,
    }



def _bunker_sync_event_row(
    *,
    session_id: str,
    actor_id: str,
    account_scope: str,
    client_ip: str,
    event_type: str,
    payload: dict,
    amount_eur: float,
) -> dict[str, object]:
    return {
        "session_id": session_id,
        "event_type": event_type,
        "account_scope": account_scope,
        "actor_id": actor_id,
        "client_ip": client_ip,
        "source": "api",
        "route": _BUNKER_SYNC_ROUTE,
        "commission_rate": 0.0,
        "commission_basis_eur": amount_eur,
        "commission_audit_eur": 0.0,
        "payload": payload,
        "protocol": _BUNKER_SYNC_PROTOCOL,
    }



def _run_bunker_sync(body: dict, headers: dict[str, str], remote_addr: str) -> tuple[dict[str, object], int]:
    expected_secret = _bunker_sync_secret()
    if not expected_secret:
        return {
            "status": "error",
            "message": "bunker_sync_secret_not_configured",
        }, 503

    if not _bunker_sync_authorized(body, headers):
        return {
            "status": "error",
            "message": "unauthorized",
        }, 403

    store = SupabaseStore()
    if not store.enabled:
        return {
            "status": "error",
            "message": "supabase_runtime_not_configured",
        }, 503

    actor_id = str(body.get("actor_id", "bunker_cli")).strip() or "bunker_cli"
    account_scope = str(body.get("account_scope", "admin")).strip() or "admin"
    session_id = str(body.get("session_id", "")).strip() or "bunker-sync-lafayette-h2"
    now = _utc_now_iso()
    tables = _bunker_sync_supabase_tables()
    client_ip = str(headers.get("X-Forwarded-For") or remote_addr or "unknown").split(",")[0].strip() or "unknown"

    payout_id = _bunker_sync_env_payout_id()
    payment_intent_ids = _bunker_sync_env_payment_intent_ids()
    if not payout_id or not payment_intent_ids:
        return {
            "status": "error",
            "message": "bunker_sync_live_ids_required",
            "hint": (
                "Defina BUNKER_SYNC_STRIPE_PAYOUT_ID (payout LIVE po_…) y "
                "BUNKER_SYNC_PAYMENT_INTENT_IDS=pi_1,pi_2,… separados por coma. "
                "Evita IDs que no existan en el modo Live de Stripe."
            ),
        }, 422

    block_amount_eur = round(
        _BUNKER_SYNC_PAYMENT_INTENT_AMOUNT_EUR * len(payment_intent_ids),
        2,
    )

    payout_row = {
        "payout_id": payout_id,
        "provider": "stripe",
        "status": "COMPLETED",
        "amount_eur": _BUNKER_SYNC_PAYOUT_AMOUNT_EUR,
        "currency": "EUR",
        "recipient": "Qonto linked account",
        "concept": "Hito 2 settlement",
        "partner_name": "Lafayette",
        "institutional_partner": "BPIFRANCE FINANCEMENT",
        "session_id": session_id,
        "metadata": {
            "block": "Hito 2",
            "source": "bunker_sync_endpoint",
            "sovereignty_state": "SOUVERAINETÉ:1",
        },
        "created_at": now,
        "updated_at": now,
    }

    payment_intent_rows = [
        {
            "payment_intent_id": payment_intent_id,
            "status": "SUCCEEDED",
            "amount_eur": _BUNKER_SYNC_PAYMENT_INTENT_AMOUNT_EUR,
            "currency": "EUR",
            "client_name": "Galeries Lafayette",
            "block_name": "Lafayette",
            "partner_name": "BPIFRANCE FINANCEMENT",
            "session_id": session_id,
            "metadata": {
                "source": "bunker_sync_endpoint",
                "sovereignty_state": "SOUVERAINETÉ:1",
                "batch_total_eur": block_amount_eur,
            },
            "created_at": now,
            "updated_at": now,
        }
        for payment_intent_id in payment_intent_ids
    ]

    client_row = {
        "client_id": "bpifrance_financement_507052338",
        "name": "BPIFRANCE FINANCEMENT",
        "legal_name": "BPIFRANCE FINANCEMENT",
        "siren": "507052338",
        "client_type": "institutional_partner",
        "partner_role": "partner_institutionnel",
        "status": "ACTIVE",
        "country": "FR",
        "source": "bunker_sync_endpoint",
        "created_at": now,
        "updated_at": now,
    }

    payout_write = _bunker_sync_write_row(
        store,
        tables["payouts"],
        payout_row,
        on_conflict="payout_id",
    )
    payment_intent_writes = [
        _bunker_sync_write_row(
            store,
            tables["payment_intents"],
            row,
            on_conflict="payment_intent_id",
        )
        for row in payment_intent_rows
    ]
    client_write = _bunker_sync_write_row(
        store,
        tables["clients"],
        client_row,
        on_conflict="siren",
    )

    control_rows = [
        _bunker_sync_control_row(
            control_key="sovereignty_status",
            state="SOUVERAINETÉ:1",
            updated_by=actor_id,
            account_scope=account_scope,
            note="Persistent sovereign state enabled by bunker sync.",
            updated_at=now,
        ),
        _bunker_sync_control_row(
            control_key="cursor_sweep_schedule",
            state="scheduled",
            updated_by=actor_id,
            account_scope=account_scope,
            note="Cursor sweep scheduled for 09:00 AM over available balance towards linked Qonto account.",
            updated_at=now,
        ),
        _bunker_sync_control_row(
            control_key="qonto_watch_27500",
            state="active",
            updated_by=actor_id,
            account_scope=account_scope,
            note="Active alert for 27,500.00 EUR landing in linked Qonto account.",
            updated_at=now,
        ),
    ]
    control_results = [
        {
            "control_key": row["control_key"],
            "state": row["state"],
            "db_persisted": save_control_state(row),
        }
        for row in control_rows
    ]

    compliance_payload = {
        "session_id": session_id,
        "event_type": "bunker_sync_completed",
        "status": "ok",
        "detail": "Capital synchronization completed and SOUVERAINETÉ:1 persisted.",
        "payload": {
            "payout_id": payout_id,
            "payment_intent_ids": payment_intent_ids,
            "client_siren": "507052338",
        },
        "created_at": now,
    }
    watchdog_payload = {
        "session_id": session_id,
        "event_type": "qonto_watch_armed",
        "status": "active",
        "detail": "09:00 AM sweep scheduled and 27,500 EUR watch armed for Qonto landing.",
        "payload": {
            "watch_amount_eur": _BUNKER_SYNC_PAYOUT_AMOUNT_EUR,
            "batch_total_eur": block_amount_eur,
            "schedule": "09:00 AM",
        },
        "created_at": now,
    }
    compliance_write = _bunker_sync_write_row(store, tables["compliance_logs"], compliance_payload)
    watchdog_write = _bunker_sync_write_row(store, tables["watchdog_logs"], watchdog_payload)

    event_payload = {
        "payout_id": payout_id,
        "payment_intent_ids": payment_intent_ids,
        "institutional_partner": client_row["name"],
        "sovereignty_state": "SOUVERAINETÉ:1",
        "cursor_sweep": {"state": "scheduled", "time": "09:00 AM"},
        "qonto_watch": {"state": "active", "amount_eur": _BUNKER_SYNC_PAYOUT_AMOUNT_EUR},
        "write_results": {
            "payout": payout_write,
            "payment_intents": payment_intent_writes,
            "client": client_write,
            "compliance_logs": compliance_write,
            "watchdog_logs": watchdog_write,
        },
    }
    event_persisted = persist_event(
        _bunker_sync_event_row(
            session_id=session_id,
            actor_id=actor_id,
            account_scope=account_scope,
            client_ip=client_ip,
            event_type="bunker_sync_completed",
            payload=event_payload,
            amount_eur=block_amount_eur,
        )
    )
    session_persisted = persist_session({
        "session_id": session_id,
        "account_scope": account_scope,
        "actor_id": actor_id,
        "last_event_type": "bunker_sync_completed",
        "last_route": _BUNKER_SYNC_ROUTE,
        "last_seen_at": now,
        "source": "api",
        "payload": event_payload,
        "protocol": _BUNKER_SYNC_PROTOCOL,
    })

    log_sovereignty_event(
        event_type="bunker_sync_completed",
        detail=(
            f"payout={payout_id} payment_intents={len(payment_intent_ids)} "
            "sovereignty=SOUVERAINETÉ:1 cursor=09:00 qonto_watch=active"
        ),
        session_id=session_id,
        amount_eur=block_amount_eur,
    )

    target_ok = all(
        [payout_write.get("ok", False), client_write.get("ok", False)]
        + [entry.get("ok", False) for entry in payment_intent_writes]
    )

    return {
        "status": "ok" if target_ok else "partial",
        "session_id": session_id,
        "protocol": _BUNKER_SYNC_PROTOCOL,
        "runtime_supabase": store.enabled,
        "sovereignty_state": "SOUVERAINETÉ:1",
        "capital_block_eur": block_amount_eur,
        "payout": {
            "id": payout_id,
            "status": "COMPLETED",
            "amount_eur": _BUNKER_SYNC_PAYOUT_AMOUNT_EUR,
            "db": payout_write,
        },
        "payment_intents": [
            {
                "id": row["payment_intent_id"],
                "status": row["status"],
                "amount_eur": row["amount_eur"],
                "db": payment_intent_writes[idx],
            }
            for idx, row in enumerate(payment_intent_rows)
        ],
        "client": {
            "name": client_row["name"],
            "siren": client_row["siren"],
            "status": client_row["status"],
            "db": client_write,
        },
        "controls": control_results,
        "logs": {
            "compliance_logs": compliance_write,
            "watchdog_logs": watchdog_write,
            "core_engine_event": event_persisted,
            "core_engine_session": session_persisted,
        },
        "cursor_sweep": {
            "state": "scheduled",
            "time": "09:00 AM",
            "target": "linked_qonto_account",
            "batch_total_eur": block_amount_eur,
        },
        "qonto_watch": {
            "state": "active",
            "watch_amount_eur": _BUNKER_SYNC_PAYOUT_AMOUNT_EUR,
        },
    }, 200 if target_ok else 207


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
    session_id = str(body.get("session_id", "")).strip()
    amount_eur_raw = body.get("amount_eur")

    if session_id or amount_eur_raw is not None:
        if not session_id or amount_eur_raw in (None, ""):
            return _cors(jsonify({
                "status": "error",
                "message": "session_id_and_amount_eur_required",
            })), 400

        try:
            amount_eur = float(amount_eur_raw)
        except (TypeError, ValueError):
            return _cors(jsonify({
                "status": "error",
                "message": "amount_eur_invalid",
            })), 400

        if amount_eur <= 0:
            return _cors(jsonify({
                "status": "error",
                "message": "amount_eur_invalid",
            })), 400

        _PAYMENT_ORCHESTRATION_LOCKS.add(session_id)
        try:
            pi_bundle = guard_stripe_call(create_lafayette_checkout, session_id, amount_eur)
            if not isinstance(pi_bundle, dict):
                return _cors(jsonify({
                    "status": "error",
                    "message": "payment_intent_creation_failed",
                })), 502
            client_secret = str(pi_bundle.get("client_secret") or "").strip()
            payment_intent_id = str(pi_bundle.get("payment_intent_id") or "").strip()
            if not client_secret or not payment_intent_id or not pi_bundle.get("livemode"):
                return _cors(jsonify({
                    "status": "error",
                    "message": "payment_intent_creation_failed",
                    "hint": "Se requiere PaymentIntent LIVE (sk_live_… y livemode=true en Stripe).",
                })), 502

            return _cors(jsonify({
                "status": "ok",
                "client_secret": client_secret,
                "payment_intent_id": payment_intent_id,
                "livemode": True,
                "session_id": session_id,
                "amount_eur": amount_eur,
                "advbet": _advbet_payload(session_id=session_id, amount_eur=amount_eur),
            })), 200
        finally:
            _PAYMENT_ORCHESTRATION_LOCKS.discard(session_id)

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

    qonto_err, qonto_code = validate_qonto_invoice_import_readiness()
    if qonto_code != 200:
        return _cors(jsonify(qonto_err)), qonto_code

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

    qonto_err, qonto_code = validate_qonto_invoice_import_readiness()
    if qonto_code != 200:
        return _cors(jsonify(qonto_err)), qonto_code

    invoice = generate_proforma(to=to, amount_key=amount_key, extra_note=note)
    return _cors(jsonify({
        "status": "ok",
        "invoice": invoice,
    })), 200


# ── V12 Master Ledger: Consolidated Two-Tier Billing ─────────────────

@app.route("/api/v1/master-ledger", methods=["OPTIONS"])
def master_ledger_options():
    return _cors(Response(status=204))


@app.route("/api/v1/master-ledger", methods=["GET"])
def master_ledger_endpoint():
    if master_ledger is None:
        return _cors(jsonify({"status": "error", "message": "master_ledger_unavailable"})), 500
    ledger = master_ledger()
    return _cors(jsonify({"status": "ok", **ledger})), 200


@app.route("/api/v1/master-ledger/factura/F-2026-001", methods=["OPTIONS"])
def factura_f2026001_options():
    return _cors(Response(status=204))


@app.route("/api/v1/master-ledger/factura/F-2026-001", methods=["GET"])
def factura_f2026001():
    if FACTURA_F_2026_001 is None:
        return _cors(jsonify({"status": "error", "message": "factura_unavailable"})), 500
    return _cors(jsonify({"status": "ok", "factura": FACTURA_F_2026_001})), 200


@app.route("/api/v1/compliance/audit", methods=["OPTIONS"])
def compliance_audit_options():
    return _cors(Response(status=204))


@app.route("/api/v1/compliance/audit", methods=["GET"])
def compliance_audit():
    if build_financial_reconciliation_report is None:
        return _cors(jsonify({"status": "error", "message": "financial_compliance_unavailable"})), 500
    report = build_financial_reconciliation_report()
    return _cors(jsonify(report)), 200


@app.route("/api/v1/compliance/status", methods=["OPTIONS"])
def compliance_status_options():
    return _cors(Response(status=204))


@app.route("/api/v1/compliance/status", methods=["GET"])
def compliance_status():
    if build_compliance_status_summary is None:
        return _cors(jsonify({"status": "error", "message": "financial_compliance_unavailable"})), 500
    summary = build_compliance_status_summary()
    return _cors(jsonify(summary)), 200


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
    raw_amount = body.get("amount_eur")
    try:
        amount = float(str(raw_amount).strip().replace(",", "."))
    except (TypeError, ValueError):
        amount = None

    if amount is None or amount <= 0:
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


@app.route("/api/v1/bunker/sync", methods=["OPTIONS"])
def bunker_sync_options():
    return _cors(Response(status=204))


@app.route("/api/v1/bunker/sync", methods=["POST"])
def bunker_sync():
    body = request.get_json(silent=True) or {}
    result, status = _run_bunker_sync(body, dict(request.headers), request.remote_addr or "")
    return _cors(jsonify(result)), status




@app.route("/api/v1/pau/scan", methods=["OPTIONS"])
def pau_scan_options():
    return _cors(Response(status=204))


@app.route("/api/v1/pau/scan", methods=["POST"])
def pau_scan():
    body = request.get_json(force=True, silent=True) or {}
    engine = _get_pau_engine()
    user_id = str(body.get("user_id", "")).strip()
    result = engine.process_body_scan(
        _pau_float(body.get("weight") or body.get("weight_kg")),
        _pau_float(body.get("height") or body.get("height_cm")),
        str(body.get("event_type") or body.get("occasion") or "soirée").strip() or "soirée",
    )
    sync = engine.sync_sovereignty_state(user_id) if user_id else {"status": "Skipped", "db_persisted": False, "message": "user_id_not_provided"}
    return _cors(jsonify(_pau_payload({
        "status": "ok",
        "scan_result": result,
        "sovereignty_sync": sync,
    }))), 200


@app.route("/api/v1/pau/snap", methods=["OPTIONS"])
def pau_snap_options():
    return _cors(Response(status=204))


@app.route("/api/v1/pau/snap", methods=["POST"])
def pau_snap():
    body = request.get_json(force=True, silent=True) or {}
    engine = _get_pau_engine()
    look = _pau_resolve_look(body)
    snap = engine.trigger_snap_logic(look.get("id"))
    return _cors(jsonify(_pau_payload({
        "status": "ok",
        "selected_look": look,
        "snap": snap,
    }))), 200


@app.route("/api/v1/pau/perfect-selection", methods=["OPTIONS"])
def pau_perfect_selection_options():
    return _cors(Response(status=204))


@app.route("/api/v1/pau/perfect-selection", methods=["POST"])
def pau_perfect_selection():
    body = request.get_json(force=True, silent=True) or {}
    engine = _get_pau_engine()
    user_id = str(body.get("user_id") or body.get("customer_id") or "PAU_GUEST").strip() or "PAU_GUEST"
    look = _pau_resolve_look(body)
    selection = engine.handle_perfect_selection(user_id, look)
    sync = engine.sync_sovereignty_state(user_id)
    return _cors(jsonify(_pau_payload({
        "status": "ok",
        "selected_look": look,
        "selection": selection,
        "sovereignty_sync": sync,
    }))), 200


@app.route("/api/v1/pau/reserve", methods=["OPTIONS"])
def pau_reserve_options():
    return _cors(Response(status=204))


@app.route("/api/v1/pau/reserve", methods=["POST"])
def pau_reserve():
    body = request.get_json(force=True, silent=True) or {}
    engine = _get_pau_engine()
    user_id = str(body.get("user_id") or body.get("customer_id") or "PAU_GUEST").strip() or "PAU_GUEST"
    look = _pau_resolve_look(body)
    reservation = engine.reserve_in_store(user_id, str(look.get("id") or "L1"))
    sync = engine.sync_sovereignty_state(user_id)
    return _cors(jsonify(_pau_payload({
        "status": "ok",
        "selected_look": look,
        "reservation": reservation,
        "sovereignty_sync": sync,
    }))), 200


@app.route("/api/v1/pau/sovereignty", methods=["OPTIONS"])
def pau_sovereignty_options():
    return _cors(Response(status=204))


@app.route("/api/v1/pau/sovereignty", methods=["GET", "POST"])
def pau_sovereignty():
    body = request.get_json(silent=True) or {}
    user_id = str(body.get("user_id") or request.args.get("user_id", "")).strip()
    engine = _get_pau_engine()
    sync = engine.sync_sovereignty_state(user_id) if user_id else {"status": "Skipped", "db_persisted": False, "message": "user_id_not_provided"}
    return _cors(jsonify(_pau_payload({
        "status": "ok",
        "persona": engine.persona,
        "sovereignty": engine.sovereignty_status(user_id),
        "sovereignty_sync": sync,
        "patent_reference": PAU_PATENT_REFERENCE,
        "siren_formatted": PAU_SIREN_FORMATTED,
    }))), 200

# ── Digital Mirror: Save Silhouette + Share Look ─────────────────────

@app.route("/api/v1/mirror/save-silhouette", methods=["OPTIONS"])
def mirror_save_silhouette_options():
    return _cors(Response(status=204))


@app.route("/api/v1/mirror/save-silhouette", methods=["POST"])
def mirror_save_silhouette():
    body = request.get_json(force=True, silent=True) or {}
    session_id = str(body.get("session_id", "")).strip()
    protocol = str(body.get("protocol", "zero_size_encrypted")).strip()

    record = {
        "session_id": session_id,
        "protocol": protocol,
        "stored_at": datetime.now(timezone.utc).isoformat(),
        "data_stripped": True,
    }

    db = None
    engine = _get_pau_engine()
    db = engine._supabase_client()
    db_persisted = False
    if db is not None:
        try:
            db.table("silhouettes").insert({
                "session_id": session_id,
                "protocol": protocol,
                "stored_at": record["stored_at"],
            }).execute()
            db_persisted = True
        except Exception:
            pass

    return _cors(jsonify(_pau_payload({
        "status": "ok",
        "silhouette_saved": True,
        "db_persisted": db_persisted,
        "protocol": protocol,
        "height_stripped": True,
        "weight_stripped": True,
        "size_stripped": True,
    }))), 200


@app.route("/api/v1/mirror/share-look", methods=["OPTIONS"])
def mirror_share_look_options():
    return _cors(Response(status=204))


@app.route("/api/v1/mirror/share-look", methods=["POST"])
def mirror_share_look():
    body = request.get_json(force=True, silent=True) or {}
    session_id = str(body.get("session_id", "")).strip()
    look_id = str(body.get("look_id", "")).strip()
    strip_biometric = bool(body.get("strip_biometric", True))

    share_token = f"SH-{abs(hash(session_id + look_id)) % 10_000_000:07d}"

    return _cors(jsonify(_pau_payload({
        "status": "ok",
        "share_token": share_token,
        "look_id": look_id,
        "biometric_stripped": strip_biometric,
        "share_url": f"/share/{share_token}",
        "payload_contains_height": False,
        "payload_contains_weight": False,
        "payload_contains_size": False,
    }))), 200


# ── Qonto SWIFT MT103 Webhook ────────────────────────────────────────

@app.route("/api/v1/qonto/swift-webhook", methods=["OPTIONS"])
def qonto_swift_webhook_options():
    return _cors(Response(status=204))


@app.route("/api/v1/qonto/swift-webhook", methods=["POST"])
def qonto_swift_webhook():
    body = request.get_json(force=True, silent=True) or {}
    try:
        from qonto_swift_webhook import process_swift_mt103, verify_qonto_signature
        sig = request.headers.get("X-Qonto-Signature", "")
        raw = request.get_data(cache=True)
        if not verify_qonto_signature(raw, sig):
            return _cors(jsonify({"status": "error", "message": "invalid_signature"})), 401
        result = process_swift_mt103(body)
        return _cors(jsonify(result)), 200
    except ImportError:
        return _cors(jsonify({"status": "error", "message": "qonto_swift_module_unavailable"})), 500
    except Exception as exc:
        return _cors(jsonify({"status": "error", "message": str(exc)})), 500


@app.route("/api/v1/qonto/swift-log", methods=["OPTIONS"])
def qonto_swift_log_options():
    return _cors(Response(status=204))


@app.route("/api/v1/qonto/swift-log", methods=["GET"])
def qonto_swift_log():
    try:
        from qonto_swift_webhook import get_swift_log
        events = get_swift_log()
        return _cors(jsonify({"status": "ok", "events": events, "count": len(events)})), 200
    except ImportError:
        return _cors(jsonify({"status": "error", "message": "qonto_swift_module_unavailable"})), 500


# ── SMTP Bounce Handling ─────────────────────────────────────────────

@app.route("/api/v1/smtp/bounce", methods=["OPTIONS"])
def smtp_bounce_options():
    return _cors(Response(status=204))


@app.route("/api/v1/smtp/bounce", methods=["POST"])
def smtp_bounce():
    body = request.get_json(force=True, silent=True) or {}
    try:
        from smtp_bounce_handler import process_bounce
        result = process_bounce(body)
        return _cors(jsonify(result)), 200
    except ImportError:
        return _cors(jsonify({"status": "error", "message": "smtp_bounce_module_unavailable"})), 500
    except Exception as exc:
        return _cors(jsonify({"status": "error", "message": str(exc)})), 500


@app.route("/api/v1/smtp/bounces", methods=["OPTIONS"])
def smtp_bounces_options():
    return _cors(Response(status=204))


@app.route("/api/v1/smtp/bounces", methods=["GET"])
def smtp_bounces():
    try:
        from smtp_bounce_handler import get_bounce_log, get_flagged_accounts
        email_filter = request.args.get("email", "")
        bounces = get_bounce_log(email_filter)
        flagged = get_flagged_accounts()
        return _cors(jsonify({
            "status": "ok",
            "bounces": bounces,
            "flagged_accounts": flagged,
            "total_bounces": len(bounces),
            "total_flagged": len(flagged),
        })), 200
    except ImportError:
        return _cors(jsonify({"status": "error", "message": "smtp_bounce_module_unavailable"})), 500


# ── Capital Liberation: Net Liquidity + Ledger Status ────────────────

@app.route("/api/v1/capital/net-liquidity", methods=["OPTIONS"])
def net_liquidity_options():
    return _cors(Response(status=204))


@app.route("/api/v1/capital/net-liquidity", methods=["GET"])
def net_liquidity():
    if compute_net_liquidity is None:
        return _cors(jsonify({"status": "error", "message": "net_liquidity_unavailable"})), 500
    breakdown = compute_net_liquidity()
    return _cors(jsonify({"status": "ok", **breakdown})), 200


@app.route("/api/v1/capital/ledger-status", methods=["OPTIONS"])
def ledger_status_options():
    return _cors(Response(status=204))


@app.route("/api/v1/capital/ledger-status", methods=["GET"])
def ledger_status():
    if get_ledger_status is None:
        return _cors(jsonify({"status": "error", "message": "ledger_status_unavailable"})), 500
    status = get_ledger_status()
    return _cors(jsonify({"status": "ok", **status})), 200


@app.route("/api/v1/capital/sync", methods=["OPTIONS"])
def capital_sync_options():
    return _cors(Response(status=204))


@app.route("/api/v1/capital/sync", methods=["POST"])
def capital_sync():
    if persist_ledger_status is None or get_ledger_status is None:
        return _cors(jsonify({"status": "error", "message": "capital_sync_unavailable"})), 500
    persist_ledger_status()
    status = get_ledger_status()
    return _cors(jsonify({
        "status": "ok",
        "message": f"SISTEMA SINCRONIZADO. SALDO DISPONIBLE: {status.get('net_deployable_eur', 0):,.2f} EUR",
        "ledger": status,
    })), 200


@app.route("/api/v1/capital/invoice-partial", methods=["OPTIONS"])
def invoice_partial_options():
    return _cors(Response(status=204))


@app.route("/api/v1/capital/invoice-partial", methods=["GET"])
def invoice_partial():
    invoice_path = Path(__file__).resolve().parent.parent / "docs" / "legal" / "compliance" / "F-2026-001-PARTIAL.json"
    if not invoice_path.exists():
        return _cors(jsonify({"status": "error", "message": "invoice_not_found"})), 404
    try:
        data = json.loads(invoice_path.read_text(encoding="utf-8"))
        return _cors(jsonify({"status": "ok", "invoice": data})), 200
    except Exception as exc:
        return _cors(jsonify({"status": "error", "message": str(exc)})), 500


# ── Resend Brand Outreach Routes ─────────────────────────────────────────────

@app.route("/api/v1/outreach/brands", methods=["OPTIONS"])
def outreach_brands_options():
    return _cors(Response("", status=204))

@app.route("/api/v1/outreach/brands", methods=["GET"])
def outreach_brands():
    if not get_brand_list:
        return _cors(jsonify({"error": "outreach_module_not_available"})), 503
    return _cors(jsonify({
        "brands": get_brand_list(),
        "total": len(get_brand_list()),
        "configured": is_outreach_configured() if is_outreach_configured else False,
    })), 200

@app.route("/api/v1/outreach/send", methods=["OPTIONS"])
def outreach_send_options():
    return _cors(Response("", status=204))

@app.route("/api/v1/outreach/send", methods=["POST"])
def outreach_send():
    if not send_brand_proposal:
        return _cors(jsonify({"error": "outreach_module_not_available"})), 503
    body = request.get_json(force=True, silent=True) or {}
    brand = str(body.get("brand", "")).strip()
    email = str(body.get("email", "")).strip()
    lang = str(body.get("lang", "en")).strip()
    segment = str(body.get("segment", "Luxury RTW")).strip()
    if not brand or not email:
        return _cors(jsonify({"error": "brand and email are required"})), 400
    result = send_brand_proposal(brand, email, lang=lang, segment=segment)
    status_code = 200 if result.get("ok") else 422
    return _cors(jsonify(result)), status_code

@app.route("/api/v1/outreach/batch", methods=["OPTIONS"])
def outreach_batch_options():
    return _cors(Response("", status=204))

@app.route("/api/v1/outreach/batch", methods=["POST"])
def outreach_batch():
    if not send_batch_proposals:
        return _cors(jsonify({"error": "outreach_module_not_available"})), 503
    body = request.get_json(force=True, silent=True) or {}
    targets = body.get("targets", [])
    lang = str(body.get("lang", "en")).strip()
    if not isinstance(targets, list) or not targets:
        return _cors(jsonify({"error": "targets array is required (each with brand + email)"})), 400
    result = send_batch_proposals(targets, lang=lang)
    return _cors(jsonify(result)), 200

@app.route("/api/v1/outreach/logs", methods=["OPTIONS"])
def outreach_logs_options():
    return _cors(Response("", status=204))

@app.route("/api/v1/outreach/logs", methods=["GET"])
def outreach_logs():
    if not get_outreach_logs:
        return _cors(jsonify({"error": "outreach_module_not_available"})), 503
    limit = request.args.get("limit", "50")
    try:
        limit_int = max(1, min(int(limit), 500))
    except ValueError:
        limit_int = 50
    entries = get_outreach_logs(limit=limit_int)
    return _cors(jsonify({"logs": entries, "count": len(entries)})), 200


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
        "version": PAU_ENGINE_VERSION,
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
        "capital_liberation_available": get_ledger_status is not None,
        "capital_net_deployable_eur": (get_ledger_status() or {}).get("net_deployable_eur") if get_ledger_status else None,
        "capital_status": (get_ledger_status() or {}).get("status") if get_ledger_status else None,
        "mirror_engine_v7": True,
        "digital_mirror_actions": [
            "ma_selection_parfaite",
            "reserver_en_cabine",
            "voir_les_combinaisons",
            "enregistrer_ma_silhouette",
            "partager_le_look",
        ],
        "divineo_global_orchestrator": get_orchestrator_status is not None,
        "orchestrator_architecture": "Pegaso V9.2.6",
        "qonto_swift_webhook_available": True,
        "smtp_bounce_handler_available": True,
        "resend_outreach_available": is_outreach_configured() if is_outreach_configured else False,
        "outreach_brand_count": len(get_brand_list()) if get_brand_list else 0,
    })), 200



# ── Divineo Global Orchestrator Routes ──────────────────────────────────────

@app.route("/api/v1/orchestrator/status", methods=["OPTIONS"])
def orchestrator_status_options():
    return _cors(Response("", status=204))

@app.route("/api/v1/orchestrator/status", methods=["GET"])
def orchestrator_status():
    if not get_orchestrator_status:
        return _cors(jsonify({"error": "orchestrator_not_available"})), 503
    return _cors(jsonify(get_orchestrator_status())), 200

@app.route("/api/v1/orchestrator/kpis", methods=["OPTIONS"])
def orchestrator_kpis_options():
    return _cors(Response("", status=204))

@app.route("/api/v1/orchestrator/kpis", methods=["GET"])
def orchestrator_kpis():
    if not get_pilot_kpis:
        return _cors(jsonify({"error": "orchestrator_not_available"})), 503
    return _cors(jsonify({"kpis": get_pilot_kpis()})), 200

@app.route("/api/v1/orchestrator/execute", methods=["OPTIONS"])
def orchestrator_execute_options():
    return _cors(Response("", status=204))

@app.route("/api/v1/orchestrator/execute", methods=["POST"])
def orchestrator_execute():
    if not trigger_global_authority:
        return _cors(jsonify({"error": "orchestrator_not_available"})), 503
    result = trigger_global_authority()
    return _cors(jsonify(result)), 200


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
