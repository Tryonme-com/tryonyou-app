#!/usr/bin/env python3
"""
Protocolo de Sincronización Financiera TryOnYou (torre de control Qonto → Linear).

- Lee credenciales desde .env (nunca subir .env a git).
- Consulta transacciones Qonto (get_transactions) y detecta un importe objetivo en EUR.
- Si no hay coincidencia, hace polling cada 60 s hasta Ctrl+C o hasta detectar la entrada.
- Tras detección, pasa el ticket Linear indicado a estado completado y añade comentario técnico.

Variables de entorno (ver .env.example):
  LINEAR_API_KEY, QONTO_LOGIN + QONTO_SECRET_KEY o QONTO_API_KEY (formato login:secret)
  Opcionales: LINEAR_TEAM_ID, QONTO_BANK_IBAN, QONTO_BASE_URL, TARGET_AMOUNT_EUR,
              LINEAR_ISSUE_IDENTIFIER, POLL_INTERVAL_SECONDS

Bajo Protocolo de Soberanía V10 — Patente PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from threading import Lock
from typing import Any, Iterator
from zoneinfo import ZoneInfo

import httpx
from dotenv import load_dotenv

# --- Constantes de protocolo (importe de referencia 557.644,20 €; comparación en céntimos) ---
DEFAULT_TARGET_EUR = 557_644.20
DEFAULT_POLL_SECONDS = 60
LINEAR_GQL = "https://api.linear.app/graphql"
QONTO_PROD = "https://thirdparty.qonto.com"
TZ_PARIS = ZoneInfo("Europe/Paris")

LOG = logging.getLogger("master_sync")
# Sincronización mínima entre lecturas (sin lockdown.py ni dependencias de infra)
_lock_qonto = Lock()
_lock_linear = Lock()


@dataclass(frozen=True)
class QontoContext:
    auth_value: str
    base_url: str


@dataclass(frozen=True)
class BankRef:
    bank_account_id: str
    iban: str | None


def _setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)sZ %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )


def _load_env() -> None:
    load_dotenv(override=False)


def _qonto_auth_from_env() -> str:
    single = (os.environ.get("QONTO_API_KEY") or "").strip()
    if single:
        return single
    login = (os.environ.get("QONTO_LOGIN") or "").strip()
    secret = (os.environ.get("QONTO_SECRET_KEY") or "").strip()
    if not login or not secret:
        return ""
    return f"{login}:{secret}"


def _int_env(name: str, default: int) -> int:
    raw = (os.environ.get(name) or "").strip()
    if not raw:
        return default
    try:
        return int(raw, 10)
    except ValueError:
        return default


def _float_env(name: str, default: float) -> float:
    raw = (os.environ.get(name) or "").strip()
    if not raw:
        return default
    s = raw.replace(" ", "")
    try:
        if s.count(",") == 1 and s.count(".") == 0:
            return float(s.replace(",", "."))
        if s.count(".") == 1 and s.count(",") == 0:
            return float(s)
        if s.count(",") == 1 and s.count(".") >= 1 and s.rfind(",") > s.rfind("."):
            return float(s.replace(".", "").replace(",", "."))
        return float(s)
    except ValueError:
        return default


def _euros_to_cents(eur: float) -> int:
    return int(round(eur * 100.0 + 1e-9))


def _now_admin_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _now_admin_paris() -> str:
    return datetime.now(TZ_PARIS).isoformat()


def _qonto_headers(ctx: QontoContext) -> dict[str, str]:
    return {
        "Authorization": ctx.auth_value,
        "Accept": "application/json",
    }


def get_organization(ctx: QontoContext, client: httpx.Client) -> dict[str, Any]:
    """GET /v2/organization. Errores HTTP/ red → excepción; no se registran credenciales."""
    url = f"{ctx.base_url.rstrip('/')}/v2/organization"
    try:
        with _lock_qonto:
            r = client.get(url, headers=_qonto_headers(ctx), timeout=60.0)
        r.raise_for_status()
        return r.json()
    except httpx.HTTPError as e:
        raise RuntimeError(f"Qonto organization: {e}") from e


def _iter_eur_bank_refs(organization_payload: dict[str, Any], preferred_iban: str | None) -> Iterator[BankRef]:
    org = organization_payload.get("organization")
    accounts: list[Any] = []
    if isinstance(org, dict) and isinstance(org.get("bank_accounts"), list):
        accounts.extend(org["bank_accounts"])
    if isinstance(organization_payload.get("bank_accounts"), list):
        accounts.extend(organization_payload["bank_accounts"])
    iban_norm = (preferred_iban or "").replace(" ", "").upper()
    for acc in accounts:
        if not isinstance(acc, dict):
            continue
        if str(acc.get("currency") or "EUR").upper() != "EUR":
            continue
        bid = str(acc.get("id") or "").strip()
        iban = str(acc.get("iban") or "").strip() or None
        if not bid:
            continue
        if iban_norm and (iban or "").replace(" ", "").upper() != iban_norm:
            continue
        yield BankRef(bank_account_id=bid, iban=iban)


def get_transactions_page(
    ctx: QontoContext,
    client: httpx.Client,
    bank: BankRef,
    page: int,
    per_page: int = 100,
) -> dict[str, Any]:
    url = f"{ctx.base_url.rstrip('/')}/v2/transactions"
    params: list[tuple[str, str | int]] = [
        ("bank_account_id", bank.bank_account_id),
        ("per_page", str(per_page)),
        ("page", str(page)),
        ("status[]", "completed"),
        ("side", "credit"),
    ]
    try:
        with _lock_qonto:
            r = client.get(url, headers=_qonto_headers(ctx), params=params, timeout=60.0)
        r.raise_for_status()
        return r.json()
    except httpx.HTTPError as e:
        raise RuntimeError(f"Qonto transactions page {page}: {e}") from e


def get_transactions(
    ctx: QontoContext,
    client: httpx.Client,
    bank: BankRef,
    *,
    max_pages: int = 500,
) -> list[dict[str, Any]]:
    """
    Lista transacciones completadas, lado crédito, en todas las páginas (hasta max_pages).
    Interfaz explícita solicitada por el protocolo; usa internamente get_transactions_page.
    """
    out: list[dict[str, Any]] = []
    page = 1
    while page <= max_pages:
        try:
            payload = get_transactions_page(ctx, client, bank, page=page)
        except RuntimeError as e:
            LOG.warning("%s", e)
            break
        txs = payload.get("transactions")
        if not isinstance(txs, list) or not txs:
            break
        for tx in txs:
            if isinstance(tx, dict):
                out.append(tx)
        nxt = _parse_next_page(payload.get("meta"), current_page=page)
        if nxt is None or nxt <= page:
            break
        page = nxt
    return out


def _parse_next_page(meta: Any, current_page: int) -> int | None:
    if not isinstance(meta, dict):
        return None
    nxt = meta.get("next_page")
    if nxt is not None:
        if isinstance(nxt, int) and nxt > current_page:
            return nxt
        try:
            ip = int(str(nxt), 10)
            if ip > current_page:
                return ip
        except ValueError:
            pass
    cur = meta.get("current_page")
    total = meta.get("total_pages") or meta.get("total_count")
    try:
        c = int(str(cur or current_page), 10)
        t = int(str(total), 10) if total is not None else 0
        if t and c < t:
            return c + 1
    except (TypeError, ValueError):
        pass
    return None


def find_matching_transaction_cents(
    ctx: QontoContext,
    client: httpx.Client,
    org_payload: dict[str, Any],
    target_cents: int,
    preferred_iban: str | None,
) -> dict[str, Any] | None:
    refs = list(_iter_eur_bank_refs(org_payload, preferred_iban))
    if not refs and preferred_iban:
        raise RuntimeError(
            "Ninguna cuenta EUR coincide con QONTO_BANK_IBAN. "
            "Revisa el IBAN o deja QONTO_BANK_IBAN vacío para todas las cuentas EUR."
        )
    if not refs:
        refs = list(_iter_eur_bank_refs(org_payload, None))
    for bank in refs:
        page = 1
        while True:
            try:
                payload = get_transactions_page(ctx, client, bank, page=page)
            except (RuntimeError, httpx.HTTPError) as e:
                LOG.warning("Fallo Qonto al listar transacciones (página %s): %s", page, e)
                break
            txs = payload.get("transactions")
            if not isinstance(txs, list):
                break
            for tx in txs:
                if not isinstance(tx, dict):
                    continue
                c = tx.get("amount_cents")
                if c is None:
                    continue
                try:
                    ic = int(c, 10) if isinstance(c, str) else int(c)
                except (TypeError, ValueError):
                    continue
                if ic == target_cents:
                    return {"bank_account_id": bank.bank_account_id, "transaction": tx}
            nxt = _parse_next_page(payload.get("meta"), current_page=page)
            if nxt is None or nxt <= page:
                break
            page = nxt
    return None


# --- Linear (GraphQL) ---------------------------------------------------------------------------


def _linear_post(api_key: str, query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
    if not api_key:
        return {}
    payload = {"query": query, "variables": variables or {}}
    req = {
        "url": LINEAR_GQL,
        "headers": {
            "Content-Type": "application/json",
            "Authorization": api_key,
        },
        "content": json.dumps(payload),
    }
    try:
        with httpx.Client(timeout=45.0) as client:
            r = client.post(**req)
    except httpx.HTTPError as e:
        raise RuntimeError(f"Linear request failed: {e}") from e
    if r.status_code >= 400:
        raise RuntimeError(f"Linear HTTP {r.status_code}")
    try:
        return r.json()
    except json.JSONDecodeError as e:
        raise RuntimeError("Linear: respuesta no JSON") from e


def parse_issue_identifier(identifier: str) -> tuple[str, int]:
    s = identifier.strip().upper()
    if "-" not in s:
        raise ValueError("LINEAR_ISSUE_IDENTIFIER debe ser tipo PROY-12 (team-number)")
    team, num_s = s.rsplit("-", 1)
    team = team.strip()
    return team, int(num_s, 10)


@dataclass(frozen=True)
class LinearIssue:
    issue_id: str
    team_id: str | None


def linear_find_issue(api_key: str, team_key: str, number: int) -> LinearIssue | None:
    q = """
    query ($team: String!, $n: Int!) {
      issues(
        filter: { and: [ { team: { key: { eq: $team } } }, { number: { eq: $n } } ] }
      ) {
        nodes {
          id
          identifier
          team { id }
        }
      }
    }
    """
    data = _linear_post(api_key, q, {"team": team_key, "n": number})
    err = data.get("errors")
    if err:
        raise RuntimeError(f"Linear GraphQL: {err}")
    nodes = (data.get("data") or {}).get("issues", {}).get("nodes") or []
    if not nodes:
        return None
    n0 = nodes[0] if isinstance(nodes, list) else None
    if not isinstance(n0, dict):
        return None
    iid = str(n0.get("id") or "")
    if not iid:
        return None
    tdata = n0.get("team")
    tid = None
    if isinstance(tdata, dict) and tdata.get("id"):
        tid = str(tdata["id"])
    return LinearIssue(issue_id=iid, team_id=tid)


def linear_completed_state_id(api_key: str, team_id: str) -> str | None:
    q = """
    query ($tid: String!) {
      team(id: $tid) {
        id
        states { nodes { id name type } }
      }
    }
    """
    data = _linear_post(api_key, q, {"tid": team_id})
    err = data.get("errors")
    if err:
        raise RuntimeError(f"Linear GraphQL: {err}")
    team = (data.get("data") or {}).get("team")
    if not isinstance(team, dict):
        return None
    state_nodes = (((team.get("states") or {}) or {}).get("nodes")) or []
    if not isinstance(state_nodes, list):
        return None
    for st in state_nodes:
        if not isinstance(st, dict):
            continue
        if str(st.get("type") or "").lower() == "completed":
            sid = st.get("id")
            if sid:
                return str(sid)
    for st in state_nodes:
        if not isinstance(st, dict):
            continue
        if str(st.get("name") or "").strip().lower() in ("done", "completed", "completado", "completada"):
            sid = st.get("id")
            if sid:
                return str(sid)
    return None


def linear_issue_update_state(api_key: str, issue_id: str, state_id: str) -> None:
    m = """
    mutation ($id: String!, $input: IssueUpdateInput!) {
      issueUpdate(id: $id, input: $input) { success }
    }
    """
    data = _linear_post(api_key, m, {"id": issue_id, "input": {"stateId": state_id}})
    err = data.get("errors")
    if err:
        raise RuntimeError(f"Linear issueUpdate: {err}")


def linear_comment(api_key: str, issue_id: str, body: str) -> None:
    m = """
    mutation ($input: CommentCreateInput!) { commentCreate(input: $input) { success } }
    """
    data = _linear_post(api_key, m, {"input": {"issueId": issue_id, "body": body}})
    err = data.get("errors")
    if err:
        raise RuntimeError(f"Linear commentCreate: {err}")


def run_linear_liquidation_done(issue_identifier: str) -> None:
    api_key = (os.environ.get("LINEAR_API_KEY") or "").strip()
    if not api_key:
        raise RuntimeError("LINEAR_API_KEY no definido")
    if not api_key.startswith("lin_api_"):
        LOG.warning("Se espera LINEAR_API_KEY con prefijo lin_api_ (token Linear)")
    team_key, num = parse_issue_identifier(issue_identifier)
    li = linear_find_issue(api_key, team_key, num)
    if not li:
        raise RuntimeError(f"Linear: no se encontró el issue {issue_identifier}")
    issue_id = li.issue_id
    team_id = (os.environ.get("LINEAR_TEAM_ID") or "").strip() or (li.team_id or "")
    if not team_id:
        raise RuntimeError("Linear: no se pudo resolver el equipo (define LINEAR_TEAM_ID)")
    state_id = (os.environ.get("LINEAR_COMPLETED_STATE_ID") or "").strip() or linear_completed_state_id(
        api_key, team_id
    )
    if not state_id:
        raise RuntimeError("Linear: no se encontró estado de tipo 'completed'")
    with _lock_linear:
        linear_issue_update_state(api_key, issue_id, state_id)
        linear_comment(api_key, issue_id, "Liquidación Confirmada")

    LOG.info("Linear: ticket %s movido a completado y comentado.", issue_identifier)


# --- Flujo principal ---------------------------------------------------------------------------


def _run_once(
    ctx: QontoContext,
    client: httpx.Client,
    org_cache: dict[str, Any] | None,
    target_cents: int,
    bank_iban: str | None,
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    if org_cache is None:
        org_cache = get_organization(ctx, client)
    found = find_matching_transaction_cents(ctx, client, org_cache, target_cents, bank_iban)
    return found, org_cache


def main() -> int:
    _setup_logging()
    _load_env()

    qonto_auth = _qonto_auth_from_env()
    if not qonto_auth:
        LOG.error("Falta autenticación Qonto: define QONTO_API_KEY o QONTO_LOGIN + QONTO_SECRET_KEY")
        return 1

    linear_id = (os.environ.get("LINEAR_ISSUE_IDENTIFIER") or "TRY-12").strip()
    target_eur = _float_env("TARGET_AMOUNT_EUR", DEFAULT_TARGET_EUR)
    target_cents = _euros_to_cents(target_eur)
    cents_raw = (os.environ.get("TARGET_AMOUNT_CENTS") or "").strip()
    if cents_raw.isdigit():
        target_cents = int(cents_raw, 10)
        target_eur = target_cents / 100.0
    poll = max(1, _int_env("POLL_INTERVAL_SECONDS", DEFAULT_POLL_SECONDS))
    qonto_base = (os.environ.get("QONTO_BASE_URL") or QONTO_PROD).strip()
    bank_iban = (os.environ.get("QONTO_BANK_IBAN") or "").strip() or None

    ctx = QontoContext(auth_value=qonto_auth, base_url=qonto_base)
    org_cache: dict[str, Any] | None = None
    match: dict[str, Any] | None = None
    t_start = time.perf_counter()

    LOG.info(
        "Sincro financiera: objetivo %s EUR (%s céntimos); ticket Linear %s; intervalo %ss; Qonto base %s",
        f"{target_eur:,.2f}",
        target_cents,
        linear_id,
        poll,
        qonto_base,
    )

    while match is None:
        try:
            with httpx.Client() as client:
                match, org_cache = _run_once(ctx, client, org_cache, target_cents, bank_iban)
        except (RuntimeError, httpx.HTTPError) as e:
            LOG.warning("Ciclo de comprobación falló (reintento tras %ss): %s", poll, e)
        except OSError as e:
            LOG.warning("Error de red/IO: %s", e)

        if match is not None:
            break
        LOG.info("Sin coincidencia en transacciones Qonto; reintento en %s s (Ctrl+C para detener).", poll)
        try:
            time.sleep(poll)
        except KeyboardInterrupt:
            LOG.info("Interrumpido por usuario.")
            return 2

    ts_confirm = _now_admin_utc()
    ts_paris = _now_admin_paris()
    tx = match.get("transaction") if isinstance(match, dict) else None
    tx = tx if isinstance(tx, dict) else {}
    try:
        run_linear_liquidation_done(linear_id)
    except (RuntimeError, OSError) as e:
        LOG.error("Qonto ok pero Linear falló: %s — vuelve a ejecutar o revisa permisos/ticket.", e)
        return 1

    elapsed = time.perf_counter() - t_start
    report = {
        "protocolo": "Sincronización_Financiera_TryOnYou",
        "marca_temporal_utc": ts_confirm,
        "marca_temporal_europe_paris": ts_paris,
        "importe_objetivo_eur": target_eur,
        "importe_objetivo_cents": target_cents,
        "linear_issue": linear_id,
        "comentario_tecnico": "Liquidación Confirmada",
        "qonto": {
            "bank_account_id": (match or {}).get("bank_account_id"),
            "transaccion": {
                "id": tx.get("transaction_id"),
                "settled_at": tx.get("settled_at"),
                "amount_cents": tx.get("amount_cents"),
            },
        },
        "tiempo_sincro_seg": round(elapsed, 2),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    LOG.info("Informe final emitido (marca %s).", ts_confirm)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        LOG.info("Interrumpido (Ctrl+C).")
        raise SystemExit(2)
