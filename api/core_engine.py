from __future__ import annotations

import asyncio
import base64
import hashlib
import hmac
import json
import os
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping

import httpx

from inventory_engine import inventory_match_payload, inventory_status_payload
from shopify_bridge import resolve_shopify_checkout_url
from stripe_fr_resolve import resolve_stripe_secret_fr, stripe_api_call_kwargs

CORE_ENGINE_PROTOCOL = "jules_core_engine_v11"
COMMISSION_RATE = 0.08
TARGET_BALANCE_EUR = 27_500.0
DEFAULT_ACCOUNT_SCOPE = "personal"
ACCOUNT_SCOPES = frozenset({"personal", "empresa", "admin"})
SUPABASE_SCHEMA = "public"
DEFAULT_EVENTS_TABLE = "core_engine_events"
DEFAULT_SESSIONS_TABLE = "core_engine_sessions"
DEFAULT_CONTROL_TABLE = "core_engine_control"
DEFAULT_CONTROL_KEY = "mirror_power_state"
DEFAULT_POWER_STATE = "on"
KILL_SWITCH_ALLOWED_ACTIONS = frozenset({"status", "on", "off"})
HTTP_TIMEOUT_SECONDS = 20.0


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def utc_now_iso() -> str:
    return utc_now().strftime("%Y-%m-%dT%H:%M:%SZ")


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _logs_dir() -> Path:
    path = _project_root() / "logs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _fallback_json_path(stem: str) -> Path:
    return _logs_dir() / f"{stem}.jsonl"


def _compact_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _append_jsonl(path: Path, payload: Mapping[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(_compact_json(payload) + "\n")


def normalize_account_scope(raw: Any) -> str:
    value = str(raw or "").strip().lower()
    mapping = {
        "business": "empresa",
        "company": "empresa",
        "enterprise": "empresa",
        "corp": "empresa",
        "personal": "personal",
        "user": "personal",
        "client": "personal",
        "member": "personal",
        "admin": "admin",
        "administrator": "admin",
        "root": "admin",
        "owner": "admin",
        "empresa": "empresa",
    }
    normalized = mapping.get(value, value)
    return normalized if normalized in ACCOUNT_SCOPES else DEFAULT_ACCOUNT_SCOPE


def _header_lookup(headers: Mapping[str, Any], name: str) -> str:
    direct = headers.get(name)
    if direct is not None:
        return str(direct).strip()
    alt = headers.get(name.lower())
    if alt is not None:
        return str(alt).strip()
    normalized = name.lower().replace("_", "-")
    for key, value in headers.items():
        key_text = str(key).strip().lower().replace("_", "-")
        if key_text == normalized:
            return str(value).strip()
    return ""


def resolve_account_scope(body: Mapping[str, Any] | None, headers: Mapping[str, Any]) -> str:
    body = body or {}
    meta = body.get("meta") if isinstance(body.get("meta"), Mapping) else {}
    for key in (
        "account_scope",
        "account_environment",
        "account_env",
        "scope",
    ):
        if key in body:
            return normalize_account_scope(body.get(key))
        if key in meta:
            return normalize_account_scope(meta.get(key))
    for header_name in (
        "X-Jules-Account-Scope",
        "X-Account-Scope",
        "X-Account-Environment",
        "X-User-Role",
    ):
        value = _header_lookup(headers, header_name)
        if value:
            return normalize_account_scope(value)
    user = body.get("user") if isinstance(body.get("user"), Mapping) else {}
    for key in ("role", "account_scope", "account_environment"):
        if key in user:
            return normalize_account_scope(user.get(key))
    return DEFAULT_ACCOUNT_SCOPE


def resolve_session_id(body: Mapping[str, Any] | None, headers: Mapping[str, Any]) -> str:
    body = body or {}
    meta = body.get("meta") if isinstance(body.get("meta"), Mapping) else {}
    for key in ("session_id", "mirror_session_id"):
        value = body.get(key) or meta.get(key)
        if value:
            return str(value).strip()[:128]
    for header_name in ("X-Jules-Session-Id", "X-Mirror-Session-Id"):
        value = _header_lookup(headers, header_name)
        if value:
            return value[:128]
    return f"jules_{uuid.uuid4().hex}"


def resolve_actor_id(body: Mapping[str, Any] | None, headers: Mapping[str, Any]) -> str:
    body = body or {}
    meta = body.get("meta") if isinstance(body.get("meta"), Mapping) else {}
    for key in ("actor_id", "user_id", "lead_id", "customer_id"):
        value = body.get(key) or meta.get(key)
        if value:
            return str(value).strip()[:128]
    value = _header_lookup(headers, "X-User-Id")
    return value[:128] if value else "anonymous"


def resolve_client_ip(headers: Mapping[str, Any]) -> str:
    forwarded = _header_lookup(headers, "X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()[:128]
    real_ip = _header_lookup(headers, "X-Real-IP")
    if real_ip:
        return real_ip[:128]
    return "unknown"


def read_json_env(var_name: str, default: Any) -> Any:
    raw = (os.environ.get(var_name) or "").strip()
    if not raw:
        return default
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def round_money(value: float) -> float:
    return round(float(value) + 1e-9, 2)


def resolve_commission_base_eur(payload: Mapping[str, Any] | None) -> float:
    payload = payload or {}
    meta = payload.get("meta") if isinstance(payload.get("meta"), Mapping) else {}
    for key in (
        "gross_amount_eur",
        "amount_eur",
        "checkout_amount_eur",
        "commission_basis_eur",
        "sale_amount_eur",
    ):
        if key in payload:
            return round_money(safe_float(payload.get(key)))
        if key in meta:
            return round_money(safe_float(meta.get(key)))
    return 0.0


class SupabaseStore:
    def __init__(self) -> None:
        self.url = (os.environ.get("SUPABASE_URL") or "").strip().rstrip("/")
        self.key = (
            os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
            or os.environ.get("SUPABASE_ANON_KEY")
            or os.environ.get("SUPABASE_KEY")
            or ""
        ).strip()
        self.schema = (os.environ.get("CORE_ENGINE_SUPABASE_SCHEMA") or SUPABASE_SCHEMA).strip()
        self.events_table = (os.environ.get("CORE_ENGINE_EVENTS_TABLE") or DEFAULT_EVENTS_TABLE).strip()
        self.sessions_table = (os.environ.get("CORE_ENGINE_SESSIONS_TABLE") or DEFAULT_SESSIONS_TABLE).strip()
        self.control_table = (os.environ.get("CORE_ENGINE_CONTROL_TABLE") or DEFAULT_CONTROL_TABLE).strip()

    @property
    def enabled(self) -> bool:
        return bool(self.url and self.key)

    def _headers(self, prefer: str | None = None) -> dict[str, str]:
        headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.schema:
            headers["Accept-Profile"] = self.schema
            headers["Content-Profile"] = self.schema
        if prefer:
            headers["Prefer"] = prefer
        return headers

    def _table_url(self, table: str) -> str:
        return f"{self.url}/rest/v1/{table}"

    def insert(self, table: str, row: Mapping[str, Any]) -> bool:
        if not self.enabled:
            return False
        response = httpx.post(
            self._table_url(table),
            headers=self._headers("return=minimal"),
            content=_compact_json(row),
            timeout=HTTP_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        return True

    def upsert(self, table: str, row: Mapping[str, Any], on_conflict: str) -> bool:
        if not self.enabled:
            return False
        params = {"on_conflict": on_conflict}
        response = httpx.post(
            self._table_url(table),
            params=params,
            headers=self._headers("resolution=merge-duplicates,return=minimal"),
            content=_compact_json(row),
            timeout=HTTP_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        return True

    def select_single(self, table: str, filters: Mapping[str, str]) -> dict[str, Any] | None:
        if not self.enabled:
            return None
        response = httpx.get(
            self._table_url(table),
            params={**filters, "select": "*", "limit": "1"},
            headers=self._headers(),
            timeout=HTTP_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        rows = response.json()
        if isinstance(rows, list) and rows:
            row = rows[0]
            return row if isinstance(row, dict) else None
        return None


_STORE = SupabaseStore()


def _persist_event_fallback(event_row: Mapping[str, Any]) -> None:
    _append_jsonl(_fallback_json_path("core_engine_events"), event_row)


def _persist_session_fallback(session_row: Mapping[str, Any]) -> None:
    _append_jsonl(_fallback_json_path("core_engine_sessions"), session_row)


def persist_event(event_row: Mapping[str, Any]) -> bool:
    try:
        if _STORE.insert(_STORE.events_table, event_row):
            return True
    except httpx.HTTPError:
        pass
    _persist_event_fallback(event_row)
    return False


def persist_session(session_row: Mapping[str, Any]) -> bool:
    try:
        if _STORE.upsert(_STORE.sessions_table, session_row, on_conflict="session_id"):
            return True
    except httpx.HTTPError:
        pass
    _persist_session_fallback(session_row)
    return False


def _control_fallback_path() -> Path:
    return _logs_dir() / "core_engine_control_state.json"


def load_control_state(control_key: str = DEFAULT_CONTROL_KEY) -> dict[str, Any] | None:
    try:
        row = _STORE.select_single(_STORE.control_table, {"control_key": f"eq.{control_key}"})
        if row:
            return row
    except httpx.HTTPError:
        pass
    path = _control_fallback_path()
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if isinstance(data, dict) and data.get("control_key") == control_key:
        return data
    return None


def save_control_state(row: Mapping[str, Any]) -> bool:
    row_payload = dict(row)
    try:
        if _STORE.upsert(_STORE.control_table, row_payload, on_conflict="control_key"):
            return True
    except httpx.HTTPError:
        pass
    _control_fallback_path().write_text(
        _compact_json(row_payload) + "\n",
        encoding="utf-8",
    )
    return False


def is_mirror_powered_on() -> bool:
    row = load_control_state(DEFAULT_CONTROL_KEY)
    if isinstance(row, dict):
        state = str(row.get("state") or DEFAULT_POWER_STATE).strip().lower()
        return state != "off"
    env_state = (os.environ.get("JULES_MIRROR_POWER_STATE") or DEFAULT_POWER_STATE).strip().lower()
    return env_state != "off"


def kill_switch_status_payload() -> dict[str, Any]:
    row = load_control_state(DEFAULT_CONTROL_KEY) or {}
    state = str(row.get("state") or (DEFAULT_POWER_STATE if is_mirror_powered_on() else "off")).strip().lower()
    return {
        "ok": True,
        "control_key": DEFAULT_CONTROL_KEY,
        "state": state,
        "updated_at": row.get("updated_at") or utc_now_iso(),
        "updated_by": row.get("updated_by") or "system",
        "account_scope": row.get("account_scope") or DEFAULT_ACCOUNT_SCOPE,
        "protocol": CORE_ENGINE_PROTOCOL,
    }


def set_kill_switch_state(action: str, actor_id: str, account_scope: str, note: str = "") -> dict[str, Any]:
    normalized_action = str(action or "status").strip().lower()
    if normalized_action not in KILL_SWITCH_ALLOWED_ACTIONS:
        raise ValueError("invalid kill-switch action")
    if normalized_action == "status":
        return kill_switch_status_payload()
    state = "on" if normalized_action == "on" else "off"
    payload = {
        "control_key": DEFAULT_CONTROL_KEY,
        "state": state,
        "updated_at": utc_now_iso(),
        "updated_by": actor_id[:128] or "anonymous",
        "account_scope": normalize_account_scope(account_scope),
        "note": str(note or "").strip()[:500],
        "protocol": CORE_ENGINE_PROTOCOL,
    }
    save_control_state(payload)
    return {
        "ok": True,
        **payload,
    }


def _kill_switch_secret() -> str:
    return (os.environ.get("JULES_KILL_SWITCH_SECRET") or os.environ.get("CORE_ENGINE_KILL_SWITCH_SECRET") or "").strip()


def authorize_kill_switch(body: Mapping[str, Any] | None, headers: Mapping[str, Any]) -> bool:
    secret = _kill_switch_secret()
    if not secret:
        return False
    body = body or {}
    provided = str(
        body.get("secret")
        or body.get("kill_switch_secret")
        or _header_lookup(headers, "X-Kill-Switch-Secret")
        or _header_lookup(headers, "Authorization").removeprefix("Bearer ")
        or ""
    ).strip()
    if not provided:
        return False
    return hmac.compare_digest(provided, secret)


def build_session_row(
    session_id: str,
    account_scope: str,
    actor_id: str,
    body: Mapping[str, Any] | None,
    route: str,
    event_type: str,
) -> dict[str, Any]:
    payload = dict(body or {})
    return {
        "session_id": session_id,
        "account_scope": normalize_account_scope(account_scope),
        "actor_id": actor_id[:128],
        "last_event_type": event_type,
        "last_route": route,
        "last_seen_at": utc_now_iso(),
        "protocol": CORE_ENGINE_PROTOCOL,
        "source": str(payload.get("source") or "tryonyou_mirror").strip()[:128],
        "payload": payload,
    }


def trace_event(
    *,
    body: Mapping[str, Any] | None,
    headers: Mapping[str, Any],
    route: str,
    event_type: str,
    source: str,
) -> dict[str, Any]:
    payload = dict(body or {})
    account_scope = resolve_account_scope(payload, headers)
    session_id = resolve_session_id(payload, headers)
    actor_id = resolve_actor_id(payload, headers)
    client_ip = resolve_client_ip(headers)
    commission_basis_eur = resolve_commission_base_eur(payload)
    event_row = {
        "event_id": str(uuid.uuid4()),
        "session_id": session_id,
        "event_type": event_type,
        "account_scope": account_scope,
        "actor_id": actor_id,
        "client_ip": client_ip,
        "source": str(source).strip()[:128],
        "route": route[:255],
        "commission_rate": COMMISSION_RATE,
        "commission_basis_eur": commission_basis_eur,
        "commission_audit_eur": round_money(commission_basis_eur * COMMISSION_RATE),
        "payload": payload,
        "created_at": utc_now_iso(),
        "protocol": CORE_ENGINE_PROTOCOL,
    }
    db_persisted = persist_event(event_row)
    persist_session(build_session_row(session_id, account_scope, actor_id, payload, route, event_type))
    return {
        "event_id": event_row["event_id"],
        "session_id": session_id,
        "account_scope": account_scope,
        "commission_rate": COMMISSION_RATE,
        "commission_audit_eur": event_row["commission_audit_eur"],
        "db_persisted": db_persisted,
        "created_at": event_row["created_at"],
    }


async def fetch_stripe_balance_async() -> dict[str, Any]:
    secret = resolve_stripe_secret_fr()
    if not secret:
        return {
            "ok": False,
            "provider": "stripe",
            "message": "missing_stripe_secret",
            "balance_eur": 0.0,
        }
    headers = {"Authorization": f"Bearer {secret}"}
    connect_account = stripe_api_call_kwargs().get("stripe_account")
    if isinstance(connect_account, str) and connect_account:
        headers["Stripe-Account"] = connect_account
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT_SECONDS) as client:
        response = await client.get("https://api.stripe.com/v1/balance", headers=headers)
        response.raise_for_status()
        payload = response.json()
    include_pending = (
        os.environ.get("CORE_ENGINE_STRIPE_INCLUDE_PENDING", "true").strip().lower()
        in ("1", "true", "yes", "on")
    )
    total_cents = 0
    for bucket_name in ("available", "pending"):
        if bucket_name == "pending" and not include_pending:
            continue
        bucket = payload.get(bucket_name)
        if not isinstance(bucket, list):
            continue
        for item in bucket:
            if not isinstance(item, Mapping):
                continue
            if str(item.get("currency") or "").strip().lower() != "eur":
                continue
            total_cents += int(item.get("amount") or 0)
    return {
        "ok": True,
        "provider": "stripe",
        "balance_eur": round_money(total_cents / 100.0),
        "currency": "EUR",
        "connect_account": connect_account or None,
        "source_payload": payload,
    }


async def fetch_qonto_balance_async() -> dict[str, Any]:
    api_key = (
        os.environ.get("QONTO_API_KEY")
        or os.environ.get("QONTO_AUTHORIZATION_KEY")
        or ""
    ).strip()
    if not api_key:
        return {
            "ok": False,
            "provider": "qonto",
            "message": "missing_qonto_api_key",
            "balance_eur": 0.0,
        }
    headers = {
        "Authorization": api_key,
        "Accept": "application/json",
    }
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT_SECONDS) as client:
        response = await client.get("https://thirdparty.qonto.com/v2/organization", headers=headers)
        response.raise_for_status()
        payload = response.json()
    balances: list[float] = []
    candidates: list[Any] = []
    organization = payload.get("organization") if isinstance(payload, Mapping) else None
    if isinstance(organization, Mapping):
        bank_accounts = organization.get("bank_accounts")
        if isinstance(bank_accounts, list):
            candidates.extend(bank_accounts)
    if isinstance(payload.get("bank_accounts") if isinstance(payload, Mapping) else None, list):
        candidates.extend(payload.get("bank_accounts"))
    for candidate in candidates:
        if not isinstance(candidate, Mapping):
            continue
        currency = str(candidate.get("currency") or "EUR").strip().upper()
        if currency != "EUR":
            continue
        if candidate.get("authorized_balance_cents") is not None:
            balances.append(safe_float(candidate.get("authorized_balance_cents")) / 100.0)
            continue
        if candidate.get("balance_cents") is not None:
            balances.append(safe_float(candidate.get("balance_cents")) / 100.0)
            continue
        if candidate.get("authorized_balance") is not None:
            balances.append(safe_float(candidate.get("authorized_balance")))
            continue
        if candidate.get("balance") is not None:
            balances.append(safe_float(candidate.get("balance")))
    total_balance = round_money(sum(balances))
    return {
        "ok": True,
        "provider": "qonto",
        "balance_eur": total_balance,
        "currency": "EUR",
        "source_payload": payload,
    }


async def validate_dual_balance_async() -> dict[str, Any]:
    stripe_result, qonto_result = await asyncio.gather(
        fetch_stripe_balance_async(),
        fetch_qonto_balance_async(),
        return_exceptions=True,
    )
    normalized: dict[str, Any] = {"stripe": {}, "qonto": {}}
    for key, result in (("stripe", stripe_result), ("qonto", qonto_result)):
        if isinstance(result, Exception):
            normalized[key] = {
                "ok": False,
                "provider": key,
                "message": str(result),
                "balance_eur": 0.0,
            }
        else:
            normalized[key] = result
    combined_total = round_money(
        safe_float(normalized["stripe"].get("balance_eur"))
        + safe_float(normalized["qonto"].get("balance_eur"))
    )
    threshold_eur = round_money(safe_float(os.environ.get("CORE_ENGINE_TARGET_BALANCE_EUR"), TARGET_BALANCE_EUR))
    return {
        "ok": bool(normalized["stripe"].get("ok")) and bool(normalized["qonto"].get("ok")),
        "threshold_eur": threshold_eur,
        "combined_total_eur": combined_total,
        "qualified": combined_total + 1e-9 >= threshold_eur,
        "stripe": normalized["stripe"],
        "qonto": normalized["qonto"],
        "protocol": CORE_ENGINE_PROTOCOL,
        "validated_at": utc_now_iso(),
    }


def _token_secret() -> str:
    return (
        os.environ.get("JULES_MODEL_ACCESS_TOKEN_SECRET")
        or os.environ.get("CORE_ENGINE_ACCESS_TOKEN_SECRET")
        or os.environ.get("VERCEL_GIT_COMMIT_SHA")
        or "jules-core-engine"
    ).strip()


def build_model_access_token(
    *,
    session_id: str,
    account_scope: str,
    actor_id: str,
    balance_eur: float,
) -> str:
    expires_at = utc_now() + timedelta(minutes=int(os.environ.get("CORE_ENGINE_ACCESS_TOKEN_TTL_MINUTES") or "30"))
    payload = {
        "sid": session_id,
        "scp": normalize_account_scope(account_scope),
        "sub": actor_id[:128],
        "bal": round_money(balance_eur),
        "exp": expires_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "proto": CORE_ENGINE_PROTOCOL,
    }
    serialized = _compact_json(payload).encode("utf-8")
    body = base64.urlsafe_b64encode(serialized).decode("utf-8").rstrip("=")
    signature = hmac.new(_token_secret().encode("utf-8"), body.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"jules.{body}.{signature}"


def model_access_payload(body: Mapping[str, Any] | None, headers: Mapping[str, Any]) -> tuple[dict[str, Any], int]:
    if not is_mirror_powered_on():
        return {
            "ok": False,
            "status": "mirror_off",
            "message": "kill_switch_active",
            "protocol": CORE_ENGINE_PROTOCOL,
        }, 423
    validation = asyncio.run(validate_dual_balance_async())
    session_id = resolve_session_id(body, headers)
    account_scope = resolve_account_scope(body, headers)
    actor_id = resolve_actor_id(body, headers)
    trace = trace_event(
        body={**dict(body or {}), "validation": validation},
        headers=headers,
        route="/api/v1/core/model-access-token",
        event_type="model_access_requested",
        source="jules_core_engine",
    )
    if not validation.get("ok"):
        return {
            "ok": False,
            "status": "validation_unavailable",
            "message": "stripe_or_qonto_unavailable",
            "validation": validation,
            "trace": trace,
            "protocol": CORE_ENGINE_PROTOCOL,
        }, 503
    if not validation.get("qualified"):
        return {
            "ok": False,
            "status": "debt_pending",
            "message": "target_balance_not_reached",
            "validation": validation,
            "trace": trace,
            "protocol": CORE_ENGINE_PROTOCOL,
        }, 402
    token = build_model_access_token(
        session_id=session_id,
        account_scope=account_scope,
        actor_id=actor_id,
        balance_eur=safe_float(validation.get("combined_total_eur")),
    )
    return {
        "ok": True,
        "access_token": token,
        "session_id": session_id,
        "validation": validation,
        "trace": trace,
        "protocol": CORE_ENGINE_PROTOCOL,
    }, 200


def mirror_snap_payload(body: Mapping[str, Any] | None, headers: Mapping[str, Any]) -> tuple[dict[str, Any], int]:
    if not is_mirror_powered_on():
        return {
            "status": "error",
            "message": "mirror_disabled",
            "protocol": CORE_ENGINE_PROTOCOL,
        }, 423
    payload = dict(body or {})
    trace = trace_event(
        body=payload,
        headers=headers,
        route="/api/v1/mirror/snap",
        event_type="silhouette_scan",
        source="mirror_snap",
    )
    match = inventory_match_payload(payload)
    return {
        "status": "ok",
        "session_id": trace["session_id"],
        "jules_msg": "The Snap validé — la silhouette entre dans le protocole Zero-Size.",
        "inventory_match": match,
        "trace": trace,
        "mirror_enabled": True,
        "protocol": CORE_ENGINE_PROTOCOL,
    }, 200


def perfect_selection_payload(body: Mapping[str, Any] | None, headers: Mapping[str, Any]) -> tuple[dict[str, Any], int]:
    if not is_mirror_powered_on():
        return {
            "status": "error",
            "message": "mirror_disabled",
            "protocol": CORE_ENGINE_PROTOCOL,
        }, 423
    payload = dict(body or {})
    lead_id = int(utc_now().timestamp())
    checkout_url = resolve_shopify_checkout_url(lead_id, str(payload.get("fabric_sensation") or ""))
    trace = trace_event(
        body={**payload, "lead_id": lead_id},
        headers=headers,
        route="/api/v1/checkout/perfect-selection",
        event_type="perfect_selection_click",
        source="perfect_selection",
    )
    return {
        "status": "ok",
        "lead_id": lead_id,
        "emotional_seal": "Sélection parfaite enregistrée — audit 8% consolidé hors Stripe.",
        "checkout_primary_url": checkout_url,
        "checkout_shopify_url": checkout_url,
        "trace": trace,
        "protocol": CORE_ENGINE_PROTOCOL,
    }, 200


def health_payload() -> dict[str, Any]:
    status = kill_switch_status_payload()
    return {
        "ok": True,
        "service": "jules-core-engine",
        "product_lane": "tryonyou_v11",
        "protocol": CORE_ENGINE_PROTOCOL,
        "mirror_enabled": status.get("state") != "off",
        "kill_switch": status,
        "inventory": inventory_status_payload(),
    }


def kill_switch_payload(body: Mapping[str, Any] | None, headers: Mapping[str, Any]) -> tuple[dict[str, Any], int]:
    if not authorize_kill_switch(body, headers):
        return {
            "ok": False,
            "message": "unauthorized",
            "protocol": CORE_ENGINE_PROTOCOL,
        }, 401
    payload = dict(body or {})
    action = str(payload.get("action") or payload.get("state") or "status").strip().lower()
    actor_id = resolve_actor_id(payload, headers)
    account_scope = resolve_account_scope(payload, headers)
    note = str(payload.get("note") or "").strip()
    try:
        result = set_kill_switch_state(action, actor_id=actor_id, account_scope=account_scope, note=note)
    except ValueError as exc:
        return {
            "ok": False,
            "message": str(exc),
            "protocol": CORE_ENGINE_PROTOCOL,
        }, 400
    trace_event(
        body={**payload, "result": result},
        headers=headers,
        route="/api/__jules__/control/kill-switch",
        event_type="kill_switch_command",
        source="kill_switch",
    )
    return result, 200
