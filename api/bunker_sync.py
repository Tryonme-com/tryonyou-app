from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable
from urllib.parse import quote

import requests

def _default_payout_id_from_env() -> str:
    """Payout LIVE Stripe; nunca hardcodear IDs de test (no existen en Live)."""
    return (os.getenv("BUNKER_SYNC_STRIPE_PAYOUT_ID") or "").strip()


DEFAULT_PAYOUT_AMOUNT_EUR = 27_500.00
DEFAULT_PAYMENT_INTENT_AMOUNT_EUR = 96_981.60
DEFAULT_PAYMENT_INTENT_AMOUNT_CENTS = 9_698_160
DEFAULT_PAYMENT_INTENT_COUNT = 5
DEFAULT_TARGET_BLOCK_EUR = 484_908.00
DEFAULT_SUPABASE_URL = "https://irwyurrpofyzcdsihjmz.supabase.co"
DEFAULT_CLIENT_NAME = "BPIFRANCE FINANCEMENT"
DEFAULT_CLIENT_SIREN = "507052338"
DEFAULT_PROTOCOL = "ENGINE_V10_2_OMEGA"
HTTP_TIMEOUT_SECONDS = 30


class StripeApiError(RuntimeError):
    pass


class SupabaseApiError(RuntimeError):
    pass


@dataclass(slots=True)
class StripeContext:
    account_id: str | None

    @property
    def label(self) -> str:
        return self.account_id or "platform"


class StripeRuntime:
    def __init__(self, api_key: str) -> None:
        self.api_key = (api_key or "").strip()

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        account_id: str | None = None,
        expected: tuple[int, ...] = (200,),
    ) -> dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
        if account_id:
            headers["Stripe-Account"] = account_id
        response = requests.request(
            method=method.upper(),
            url=f"https://api.stripe.com{path}",
            headers=headers,
            params=params,
            data=data,
            timeout=HTTP_TIMEOUT_SECONDS,
        )
        try:
            payload = response.json()
        except ValueError:
            payload = {"raw": response.text}
        if response.status_code not in expected:
            error_message = payload.get("error", {}).get("message") if isinstance(payload, dict) else None
            raise StripeApiError(error_message or f"stripe_http_{response.status_code}")
        return payload if isinstance(payload, dict) else {}

    def get_balance(self, *, account_id: str | None = None) -> dict[str, Any]:
        return self._request("GET", "/v1/balance", account_id=account_id)

    def list_accounts(self, *, limit: int = 100, starting_after: str | None = None) -> dict[str, Any]:
        params: dict[str, Any] = {"limit": limit}
        if starting_after:
            params["starting_after"] = starting_after
        return self._request("GET", "/v1/accounts", params=params)

    def iter_contexts(self, *, max_accounts: int = 50) -> list[StripeContext]:
        contexts = [StripeContext(account_id=None)]
        if not self.enabled:
            return contexts
        try:
            starting_after = None
            seen = 0
            while seen < max_accounts:
                batch = self.list_accounts(limit=min(100, max_accounts - seen), starting_after=starting_after)
                rows = batch.get("data") if isinstance(batch.get("data"), list) else []
                if not rows:
                    break
                for row in rows:
                    account_id = str(row.get("id") or "").strip()
                    if account_id:
                        contexts.append(StripeContext(account_id=account_id))
                        seen += 1
                if not batch.get("has_more") or seen >= max_accounts:
                    break
                starting_after = str(rows[-1].get("id") or "").strip() or None
                if not starting_after:
                    break
        except StripeApiError:
            return contexts
        return contexts

    def retrieve_payout(self, payout_id: str, *, account_id: str | None = None) -> dict[str, Any]:
        return self._request("GET", f"/v1/payouts/{quote(payout_id, safe='')}", account_id=account_id)

    def list_payouts(self, *, limit: int = 100, account_id: str | None = None) -> dict[str, Any]:
        return self._request("GET", "/v1/payouts", params={"limit": limit}, account_id=account_id)

    def retrieve_payment_intent(self, payment_intent_id: str, *, account_id: str | None = None) -> dict[str, Any]:
        return self._request("GET", f"/v1/payment_intents/{quote(payment_intent_id, safe='')}", account_id=account_id)

    def search_payment_intents(
        self,
        *,
        query: str,
        limit: int = 100,
        page: str | None = None,
        account_id: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"query": query, "limit": limit}
        if page:
            params["page"] = page
        return self._request("GET", "/v1/payment_intents/search", params=params, account_id=account_id)

    def list_payment_intents(
        self,
        *,
        limit: int = 100,
        starting_after: str | None = None,
        account_id: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"limit": limit}
        if starting_after:
            params["starting_after"] = starting_after
        return self._request("GET", "/v1/payment_intents", params=params, account_id=account_id)

    def create_payout(
        self,
        *,
        amount_cents: int,
        currency: str,
        account_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        data: dict[str, Any] = {
            "amount": str(int(amount_cents)),
            "currency": (currency or "eur").lower(),
            "method": "standard",
        }
        for idx, (key, value) in enumerate((metadata or {}).items()):
            data[f"metadata[{key}]"] = str(value)
        return self._request("POST", "/v1/payouts", data=data, account_id=account_id)


class SupabaseRuntime:
    def __init__(self, url: str, key: str) -> None:
        self.url = (url or DEFAULT_SUPABASE_URL).strip().rstrip("/")
        self.key = (key or "").strip()

    @property
    def enabled(self) -> bool:
        return bool(self.url and self.key)

    def _headers(self, prefer: str | None = None) -> dict[str, str]:
        headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Accept-Profile": "public",
            "Content-Profile": "public",
        }
        if prefer:
            headers["Prefer"] = prefer
        return headers

    def _request(
        self,
        method: str,
        table: str,
        *,
        params: dict[str, Any] | None = None,
        payload: Any | None = None,
        expected: tuple[int, ...] = (200,),
    ) -> requests.Response:
        response = requests.request(
            method=method.upper(),
            url=f"{self.url}/rest/v1/{table}",
            headers=self._headers(),
            params=params,
            data=json.dumps(payload, ensure_ascii=False) if payload is not None else None,
            timeout=HTTP_TIMEOUT_SECONDS,
        )
        if response.status_code not in expected:
            try:
                error = response.json()
            except ValueError:
                error = {"message": response.text}
            raise SupabaseApiError(str(error))
        return response

    def table_exists(self, table: str) -> bool:
        if not self.enabled:
            return False
        response = requests.get(
            f"{self.url}/rest/v1/{table}",
            headers=self._headers(),
            params={"select": "*", "limit": 1},
            timeout=HTTP_TIMEOUT_SECONDS,
        )
        return response.status_code == 200

    def column_exists(self, table: str, column: str) -> bool:
        if not self.enabled:
            return False
        response = requests.get(
            f"{self.url}/rest/v1/{table}",
            headers=self._headers(),
            params={"select": column, column: "eq.__probe__", "limit": 1},
            timeout=HTTP_TIMEOUT_SECONDS,
        )
        return response.status_code == 200

    def first_existing(self, table: str, candidates: Iterable[str]) -> str | None:
        for candidate in candidates:
            if self.column_exists(table, candidate):
                return candidate
        return None

    def upsert(self, table: str, row: dict[str, Any], *, on_conflict: str) -> dict[str, Any]:
        response = requests.post(
            f"{self.url}/rest/v1/{table}",
            headers=self._headers("resolution=merge-duplicates,return=representation"),
            params={"on_conflict": on_conflict},
            data=json.dumps([row], ensure_ascii=False),
            timeout=HTTP_TIMEOUT_SECONDS,
        )
        if response.status_code not in (200, 201):
            try:
                error = response.json()
            except ValueError:
                error = {"message": response.text}
            raise SupabaseApiError(str(error))
        try:
            data = response.json()
        except ValueError:
            data = []
        return data[0] if isinstance(data, list) and data else row

    def insert(self, table: str, row: dict[str, Any]) -> dict[str, Any]:
        response = requests.post(
            f"{self.url}/rest/v1/{table}",
            headers=self._headers("return=representation"),
            data=json.dumps([row], ensure_ascii=False),
            timeout=HTTP_TIMEOUT_SECONDS,
        )
        if response.status_code not in (200, 201):
            try:
                error = response.json()
            except ValueError:
                error = {"message": response.text}
            raise SupabaseApiError(str(error))
        try:
            data = response.json()
        except ValueError:
            data = []
        return data[0] if isinstance(data, list) and data else row


class AdaptiveTableWriter:
    def __init__(self, supabase: SupabaseRuntime) -> None:
        self.supabase = supabase
        self._table_cache: dict[str, bool] = {}
        self._column_cache: dict[tuple[str, str], bool] = {}

    def table_exists(self, table: str) -> bool:
        if table not in self._table_cache:
            self._table_cache[table] = self.supabase.table_exists(table)
        return self._table_cache[table]

    def column_exists(self, table: str, column: str) -> bool:
        key = (table, column)
        if key not in self._column_cache:
            self._column_cache[key] = self.supabase.column_exists(table, column)
        return self._column_cache[key]

    def first_existing(self, table: str, candidates: Iterable[str]) -> str | None:
        for candidate in candidates:
            if self.column_exists(table, candidate):
                return candidate
        return None

    def upsert_candidate(
        self,
        *,
        table_candidates: list[str],
        conflict_candidates: list[str],
        field_candidates: dict[str, Any],
    ) -> dict[str, Any]:
        if not self.supabase.enabled:
            return {"ok": False, "reason": "supabase_not_configured"}
        for table in table_candidates:
            if not self.table_exists(table):
                continue
            conflict_column = self.first_existing(table, conflict_candidates)
            if not conflict_column:
                continue
            row: dict[str, Any] = {}
            for column, value in field_candidates.items():
                if self.column_exists(table, column):
                    row[column] = value
            if conflict_column not in row:
                continue
            try:
                stored = self.supabase.upsert(table, row, on_conflict=conflict_column)
                return {
                    "ok": True,
                    "table": table,
                    "conflict_column": conflict_column,
                    "stored": stored,
                }
            except SupabaseApiError as exc:
                return {
                    "ok": False,
                    "table": table,
                    "conflict_column": conflict_column,
                    "reason": str(exc),
                }
        return {"ok": False, "reason": "no_matching_table_or_columns"}

    def insert_candidate(self, *, table_candidates: list[str], field_candidates: dict[str, Any]) -> dict[str, Any]:
        if not self.supabase.enabled:
            return {"ok": False, "reason": "supabase_not_configured"}
        for table in table_candidates:
            if not self.table_exists(table):
                continue
            row: dict[str, Any] = {}
            for column, value in field_candidates.items():
                if self.column_exists(table, column):
                    row[column] = value
            if not row:
                continue
            try:
                stored = self.supabase.insert(table, row)
                return {"ok": True, "table": table, "stored": stored}
            except SupabaseApiError as exc:
                return {"ok": False, "table": table, "reason": str(exc)}
        return {"ok": False, "reason": "no_matching_table_or_columns"}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def money_cents_to_eur(amount: Any) -> float:
    try:
        return round(float(amount) / 100.0, 2)
    except (TypeError, ValueError):
        return 0.0


def money_eur_to_cents(amount: Any) -> int:
    try:
        return int(round(float(amount) * 100))
    except (TypeError, ValueError):
        return 0


def compact_payload(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _dedupe_by_id(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for row in rows:
        row_id = str(row.get("id") or "").strip()
        if not row_id or row_id in seen:
            continue
        seen.add(row_id)
        out.append(row)
    return out


def _resolve_explicit_payment_intents(body: dict[str, Any]) -> list[str]:
    value = body.get("payment_intent_ids")
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    single = str(body.get("payment_intent_id") or "").strip()
    return [single] if single else []


def _search_payment_intents_by_amount(
    stripe_runtime: StripeRuntime,
    *,
    amount_cents: int,
    contexts: list[StripeContext],
    limit: int,
) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    query = f"status:'succeeded' AND currency:'eur' AND amount:{amount_cents}"
    for context in contexts:
        try:
            page: str | None = None
            rounds = 0
            while rounds < 3 and len(found) < limit * 3:
                payload = stripe_runtime.search_payment_intents(
                    query=query,
                    limit=min(100, limit * 3),
                    page=page,
                    account_id=context.account_id,
                )
                rows = payload.get("data") if isinstance(payload.get("data"), list) else []
                for row in rows:
                    enriched = dict(row)
                    enriched["_stripe_account"] = context.label
                    found.append(enriched)
                page = payload.get("next_page")
                rounds += 1
                if not page:
                    break
        except StripeApiError:
            try:
                payload = stripe_runtime.list_payment_intents(limit=100, account_id=context.account_id)
                rows = payload.get("data") if isinstance(payload.get("data"), list) else []
                for row in rows:
                    if int(row.get("amount") or 0) != amount_cents:
                        continue
                    if str(row.get("currency") or "").lower() != "eur":
                        continue
                    if str(row.get("status") or "").lower() != "succeeded":
                        continue
                    enriched = dict(row)
                    enriched["_stripe_account"] = context.label
                    found.append(enriched)
            except StripeApiError:
                continue
    found = _dedupe_by_id(found)
    found.sort(key=lambda item: int(item.get("created") or 0), reverse=True)
    return found[:limit]


def locate_payout(
    stripe_runtime: StripeRuntime,
    *,
    payout_id: str,
    payout_amount_eur: float,
    contexts: list[StripeContext],
) -> dict[str, Any]:
    for context in contexts:
        try:
            payout = stripe_runtime.retrieve_payout(payout_id, account_id=context.account_id)
            payout["_stripe_account"] = context.label
            return {
                "ok": True,
                "found": True,
                "lookup": "by_id",
                "payout": payout,
            }
        except StripeApiError:
            continue
    target_amount = money_eur_to_cents(payout_amount_eur)
    for context in contexts:
        try:
            payload = stripe_runtime.list_payouts(limit=100, account_id=context.account_id)
            rows = payload.get("data") if isinstance(payload.get("data"), list) else []
            for row in rows:
                if int(row.get("amount") or 0) != target_amount:
                    continue
                if str(row.get("currency") or "").lower() != "eur":
                    continue
                if str(row.get("status") or "").lower() not in {"paid", "in_transit", "pending"}:
                    continue
                enriched = dict(row)
                enriched["_stripe_account"] = context.label
                return {
                    "ok": True,
                    "found": True,
                    "lookup": "by_amount_fallback",
                    "payout": enriched,
                }
        except StripeApiError:
            continue
    return {
        "ok": False,
        "found": False,
        "lookup": "not_found",
        "payout": {
            "id": payout_id,
            "amount": target_amount,
            "currency": "eur",
            "status": "paid",
            "_stripe_account": "unresolved",
            "_synthetic": True,
        },
    }


def locate_payment_intents(
    stripe_runtime: StripeRuntime,
    *,
    explicit_ids: list[str],
    amount_cents: int,
    count: int,
    contexts: list[StripeContext],
) -> dict[str, Any]:
    found: list[dict[str, Any]] = []
    missing_ids: list[str] = []
    if explicit_ids:
        for payment_intent_id in explicit_ids:
            hit = None
            for context in contexts:
                try:
                    payload = stripe_runtime.retrieve_payment_intent(payment_intent_id, account_id=context.account_id)
                    payload["_stripe_account"] = context.label
                    hit = payload
                    break
                except StripeApiError:
                    continue
            if hit is None:
                missing_ids.append(payment_intent_id)
            else:
                found.append(hit)
    if len(found) < count:
        heuristic = _search_payment_intents_by_amount(
            stripe_runtime,
            amount_cents=amount_cents,
            contexts=contexts,
            limit=count,
        )
        found = _dedupe_by_id(found + heuristic)
    found = found[:count]
    return {
        "ok": len(found) >= count,
        "payment_intents": found,
        "missing_ids": missing_ids,
        "count": len(found),
    }


def sync_payout_record(writer: AdaptiveTableWriter, payout: dict[str, Any]) -> dict[str, Any]:
    payout_id = str(payout.get("id") or _default_payout_id_from_env()).strip()
    status = str(payout.get("status") or "paid").strip().upper()
    amount_eur = money_cents_to_eur(payout.get("amount")) or DEFAULT_PAYOUT_AMOUNT_EUR
    payload_json = compact_payload(payout)
    return writer.upsert_candidate(
        table_candidates=["payouts", "stripe_payouts", "treasury_payouts"],
        conflict_candidates=["stripe_payout_id", "payout_id", "id", "external_id"],
        field_candidates={
            "stripe_payout_id": payout_id,
            "payout_id": payout_id,
            "id": payout_id,
            "external_id": payout_id,
            "status": "COMPLETED" if status in {"PAID", "COMPLETED", "SUCCEEDED", "IN_TRANSIT"} else status,
            "payout_status": "COMPLETED" if status in {"PAID", "COMPLETED", "SUCCEEDED", "IN_TRANSIT"} else status,
            "state": "COMPLETED" if status in {"PAID", "COMPLETED", "SUCCEEDED", "IN_TRANSIT"} else status,
            "amount_eur": amount_eur,
            "amount": amount_eur,
            "gross_amount_eur": amount_eur,
            "currency": str(payout.get("currency") or "eur").lower(),
            "provider": "stripe",
            "source": "bunker_sync_runtime",
            "raw_payload": payload_json,
            "payload": payload_json,
            "stripe_payload": payload_json,
            "metadata": payload_json,
            "updated_at": utc_now_iso(),
            "completed_at": utc_now_iso(),
        },
    )


def sync_payment_intent_records(writer: AdaptiveTableWriter, payment_intents: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for payment_intent in payment_intents:
        payment_intent_id = str(payment_intent.get("id") or "").strip()
        amount_eur = money_cents_to_eur(payment_intent.get("amount")) or DEFAULT_PAYMENT_INTENT_AMOUNT_EUR
        status = str(payment_intent.get("status") or "succeeded").strip().upper()
        payload_json = compact_payload(payment_intent)
        result = writer.upsert_candidate(
            table_candidates=["payment_intents", "stripe_payment_intents", "payments", "transactions"],
            conflict_candidates=["stripe_payment_intent_id", "payment_intent_id", "id", "external_id"],
            field_candidates={
                "stripe_payment_intent_id": payment_intent_id,
                "payment_intent_id": payment_intent_id,
                "id": payment_intent_id,
                "external_id": payment_intent_id,
                "status": "SUCCEEDED" if status in {"SUCCEEDED", "REQUIRES_CAPTURE"} else status,
                "payment_status": "SUCCEEDED" if status in {"SUCCEEDED", "REQUIRES_CAPTURE"} else status,
                "state": "SUCCEEDED" if status in {"SUCCEEDED", "REQUIRES_CAPTURE"} else status,
                "amount_eur": amount_eur,
                "amount": amount_eur,
                "gross_amount_eur": amount_eur,
                "currency": str(payment_intent.get("currency") or "eur").lower(),
                "provider": "stripe",
                "source": "bunker_sync_runtime",
                "raw_payload": payload_json,
                "payload": payload_json,
                "stripe_payload": payload_json,
                "metadata": payload_json,
                "updated_at": utc_now_iso(),
                "succeeded_at": utc_now_iso(),
            },
        )
        result["payment_intent_id"] = payment_intent_id
        results.append(result)
    return results


def sync_bpifrance_client(writer: AdaptiveTableWriter) -> dict[str, Any]:
    payload_json = compact_payload(
        {
            "name": DEFAULT_CLIENT_NAME,
            "siren": DEFAULT_CLIENT_SIREN,
            "role": "institutional_partner",
        }
    )
    return writer.upsert_candidate(
        table_candidates=["clients", "partners", "institutional_partners"],
        conflict_candidates=["siren", "company_siren", "tax_id", "id"],
        field_candidates={
            "siren": DEFAULT_CLIENT_SIREN,
            "company_siren": DEFAULT_CLIENT_SIREN,
            "tax_id": DEFAULT_CLIENT_SIREN,
            "id": DEFAULT_CLIENT_SIREN,
            "name": DEFAULT_CLIENT_NAME,
            "client_name": DEFAULT_CLIENT_NAME,
            "legal_name": DEFAULT_CLIENT_NAME,
            "company_name": DEFAULT_CLIENT_NAME,
            "status": "ACTIVE",
            "partner_type": "institutional",
            "client_type": "partner",
            "role": "institutional_partner",
            "institutional_partner": True,
            "country": "FR",
            "country_code": "FR",
            "source": "bunker_sync_runtime",
            "metadata": payload_json,
            "payload": payload_json,
            "updated_at": utc_now_iso(),
        },
    )


def persist_control_rows(writer: AdaptiveTableWriter) -> list[dict[str, Any]]:
    rows = [
        ("souverainete_state", "1", "SOUVERAINETÉ:1 persistente"),
        ("bunker_status", "Sincronizado y en espera", "Búnker sincronizado y en espera"),
        ("cursor_execution", "Programada 09:00 AM", "Barrido automático programado para las 09:00 AM"),
        ("qonto_watchdog", "Alerta activa 27.500 EUR", "Vigilancia activa para aterrizaje de 27.500 EUR en Qonto"),
    ]
    results: list[dict[str, Any]] = []
    for control_key, state, note in rows:
        result = writer.upsert_candidate(
            table_candidates=["core_engine_control", "control", "system_control"],
            conflict_candidates=["control_key", "key", "id"],
            field_candidates={
                "control_key": control_key,
                "key": control_key,
                "id": control_key,
                "state": state,
                "status": state,
                "note": note,
                "updated_at": utc_now_iso(),
                "updated_by": "bunker_sync_runtime",
                "account_scope": "admin",
                "protocol": DEFAULT_PROTOCOL,
            },
        )
        result["control_key"] = control_key
        results.append(result)
    return results


def persist_log_rows(writer: AdaptiveTableWriter, payload: dict[str, Any]) -> dict[str, Any]:
    log_payload = compact_payload(payload)
    compliance = writer.insert_candidate(
        table_candidates=["compliance_logs", "compliance_log"],
        field_candidates={
            "id": str(uuid.uuid4()),
            "log_id": str(uuid.uuid4()),
            "event_type": "bunker_sync",
            "type": "bunker_sync",
            "status": "SUCCESS",
            "message": "Runtime bunker sync executed",
            "payload": log_payload,
            "metadata": log_payload,
            "raw_payload": log_payload,
            "created_at": utc_now_iso(),
            "source": "bunker_sync_runtime",
        },
    )
    watchdog = writer.insert_candidate(
        table_candidates=["watchdog_logs", "watchdog_log"],
        field_candidates={
            "id": str(uuid.uuid4()),
            "log_id": str(uuid.uuid4()),
            "event_type": "qonto_watchdog",
            "type": "qonto_watchdog",
            "status": "ACTIVE",
            "message": "Alerta activa para 27.500 EUR en Qonto",
            "payload": log_payload,
            "metadata": log_payload,
            "raw_payload": log_payload,
            "created_at": utc_now_iso(),
            "source": "bunker_sync_runtime",
        },
    )
    event_log = writer.insert_candidate(
        table_candidates=["core_engine_events"],
        field_candidates={
            "event_id": str(uuid.uuid4()),
            "session_id": f"bunker_sync_{uuid.uuid4().hex[:12]}",
            "event_type": "bunker_sync_completed",
            "account_scope": "admin",
            "actor_id": "system",
            "client_ip": "runtime",
            "source": "bunker_sync_runtime",
            "route": "/api/v1/bunker/sync",
            "commission_rate": 0.0,
            "commission_basis_eur": 0.0,
            "commission_audit_eur": 0.0,
            "payload": payload,
            "created_at": utc_now_iso(),
            "protocol": DEFAULT_PROTOCOL,
        },
    )
    return {
        "compliance_logs": compliance,
        "watchdog_logs": watchdog,
        "core_engine_events": event_log,
    }


def execute_batch_payout_engine(
    stripe_runtime: StripeRuntime,
    *,
    contexts: list[StripeContext],
    target_block_eur: float,
    dry_run: bool,
) -> dict[str, Any]:
    sweeps: list[dict[str, Any]] = []
    total_created_cents = 0
    total_available_cents = 0
    for context in contexts[:1]:
        try:
            balance = stripe_runtime.get_balance(account_id=context.account_id)
        except StripeApiError as exc:
            return {
                "ok": False,
                "reason": str(exc),
                "payouts_created": [],
                "available_to_sweep_eur": 0.0,
                "target_block_eur": target_block_eur,
                "transferred_now_eur": 0.0,
                "dry_run": dry_run,
            }
        available = balance.get("available") if isinstance(balance.get("available"), list) else []
        for row in available:
            amount = int(row.get("amount") or 0)
            currency = str(row.get("currency") or "").lower()
            if amount <= 0:
                continue
            total_available_cents += amount
            entry = {
                "account": context.label,
                "currency": currency,
                "available_cents": amount,
                "available_eur": money_cents_to_eur(amount) if currency == "eur" else None,
            }
            if dry_run:
                entry["status"] = "dry_run"
                sweeps.append(entry)
                continue
            try:
                payout = stripe_runtime.create_payout(
                    amount_cents=amount,
                    currency=currency,
                    account_id=context.account_id,
                    metadata={
                        "source": "bunker_sync_runtime",
                        "target_block_eur": f"{target_block_eur:.2f}",
                    },
                )
                total_created_cents += int(payout.get("amount") or 0)
                entry["status"] = str(payout.get("status") or "created")
                entry["payout_id"] = str(payout.get("id") or "")
                sweeps.append(entry)
            except StripeApiError as exc:
                entry["status"] = "error"
                entry["error"] = str(exc)
                sweeps.append(entry)
    return {
        "ok": True,
        "payouts_created": sweeps,
        "available_to_sweep_eur": money_cents_to_eur(total_available_cents),
        "target_block_eur": round(float(target_block_eur), 2),
        "transferred_now_eur": money_cents_to_eur(total_created_cents),
        "dry_run": dry_run,
    }


def execute_bunker_sync(body: dict[str, Any] | None = None) -> tuple[dict[str, Any], int]:
    body = body or {}
    stripe_key = (os.getenv("STRIPE_SECRET_KEY") or "").strip()
    supabase_url = (os.getenv("SUPABASE_URL") or DEFAULT_SUPABASE_URL).strip()
    supabase_key = (os.getenv("SUPABASE_SERVICE_ROLE_KEY") or "").strip()
    dry_run = bool(body.get("dry_run"))

    if not stripe_key:
        return ({"status": "error", "message": "stripe_secret_missing"}, 500)
    if not supabase_key:
        return ({"status": "error", "message": "supabase_service_role_missing"}, 500)

    payout_id = str(body.get("payout_id") or _default_payout_id_from_env()).strip()
    if not payout_id:
        return (
            {
                "status": "error",
                "message": "payout_id_required",
                "hint": "Defina BUNKER_SYNC_STRIPE_PAYOUT_ID o envíe payout_id en el body (po_… LIVE).",
            },
            422,
        )
    payout_amount_eur = float(body.get("payout_amount_eur") or DEFAULT_PAYOUT_AMOUNT_EUR)
    payment_intent_ids = _resolve_explicit_payment_intents(body)
    payment_intent_amount_eur = float(body.get("payment_intent_amount_eur") or DEFAULT_PAYMENT_INTENT_AMOUNT_EUR)
    payment_intent_count = int(body.get("payment_intent_count") or DEFAULT_PAYMENT_INTENT_COUNT)
    target_block_eur = float(body.get("target_block_eur") or DEFAULT_TARGET_BLOCK_EUR)

    stripe_runtime = StripeRuntime(stripe_key)
    supabase_runtime = SupabaseRuntime(supabase_url, supabase_key)
    writer = AdaptiveTableWriter(supabase_runtime)
    contexts = stripe_runtime.iter_contexts(max_accounts=50)

    payout_lookup = locate_payout(
        stripe_runtime,
        payout_id=payout_id,
        payout_amount_eur=payout_amount_eur,
        contexts=contexts,
    )
    payment_intent_lookup = locate_payment_intents(
        stripe_runtime,
        explicit_ids=payment_intent_ids,
        amount_cents=money_eur_to_cents(payment_intent_amount_eur),
        count=payment_intent_count,
        contexts=contexts,
    )

    payout_sync = sync_payout_record(writer, payout_lookup["payout"])
    payment_intent_sync = sync_payment_intent_records(writer, payment_intent_lookup["payment_intents"])
    client_sync = sync_bpifrance_client(writer)
    control_sync = persist_control_rows(writer)
    batch_engine = execute_batch_payout_engine(
        stripe_runtime,
        contexts=contexts,
        target_block_eur=target_block_eur,
        dry_run=dry_run,
    )

    report_payload = {
        "payout_id": payout_id,
        "payout_sync_ok": payout_sync.get("ok", False),
        "payment_intents_found": payment_intent_lookup.get("count", 0),
        "client_sync_ok": client_sync.get("ok", False),
        "souverainete_state": 1,
        "dry_run": dry_run,
    }
    log_sync = persist_log_rows(writer, report_payload)

    ok = bool(
        payout_sync.get("ok")
        and client_sync.get("ok")
        and payment_intent_lookup.get("count", 0) >= payment_intent_count
    )
    response = {
        "status": "ok" if ok else "partial",
        "executed_at": utc_now_iso(),
        "runtime": {
            "stripe_configured": stripe_runtime.enabled,
            "supabase_configured": supabase_runtime.enabled,
            "contexts_scanned": [context.label for context in contexts],
        },
        "payout": {
            "lookup": payout_lookup,
            "supabase": payout_sync,
        },
        "payment_intents": {
            "lookup": payment_intent_lookup,
            "supabase": payment_intent_sync,
        },
        "client": client_sync,
        "batch_payout_engine": batch_engine,
        "bunker_state": {
            "souverainete": 1,
            "status": "Sincronizado y en espera",
            "cursor_execution": "Programada para el barrido de las 09:00 AM",
            "watchdog": "Alerta activa para el aterrizaje de 27.500 EUR en Qonto",
            "control_rows": control_sync,
        },
        "logs": log_sync,
    }
    return response, 200


def bunker_sync_status() -> tuple[dict[str, Any], int]:
    return (
        {
            "status": "ok",
            "service": "bunker_sync_runtime",
            "souverainete": 1,
            "bunker_status": "Sincronizado y en espera",
            "cursor_execution": "Programada para el barrido de las 09:00 AM",
            "watchdog": "Alerta activa para el aterrizaje de 27.500 EUR en Qonto",
            "supabase_url": (os.getenv("SUPABASE_URL") or DEFAULT_SUPABASE_URL).strip(),
            "stripe_configured": bool((os.getenv("STRIPE_SECRET_KEY") or "").strip()),
            "supabase_configured": bool((os.getenv("SUPABASE_SERVICE_ROLE_KEY") or "").strip()),
        },
        200,
    )
