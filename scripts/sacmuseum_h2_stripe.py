"""
Batch Payout Engine (SacMuseum/Stripe) con autopayout Lafayette a Qonto.

Modos:
  - SACMUSEUM_PAYOUT_MODE=lafayette_batch:
      escanea transacciones `available`, detecta PaymentIntent `pi_3OzL...`,
      y dispara payout inmediato SIN confirmación manual (crea `po_...`).
  - SACMUSEUM_PAYOUT_MODE=lafayette_watch (default):
      vigila cambios de balance y ejecuta `lafayette_batch` en cada cambio.
  - SACMUSEUM_PAYOUT_MODE=legacy_hito2:
      conserva el flujo histórico de Hito 2 con confirmación explícita.

Trazabilidad soberana:
  - Registra cada payout `po_...` en `logs/sovereignty_payout_log.jsonl`.
  - Evita doble payout del mismo balance transaction con
    `logs/lafayette_batch_payout_state.json`.

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import json
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from stripe_verify_secret_env import resolve_stripe_secret  # noqa: E402

_DEFAULT_PI_PREFIX = "pi_3OzL"
_DEFAULT_DESCRIPTOR = "LAFAYETTE AUTO"
_DEFAULT_CURRENCY = "eur"
_DEFAULT_SCAN_LIMIT = 100
_SOVEREIGN_PAYOUT_LOG = _ROOT / "logs" / "sovereignty_payout_log.jsonl"
_BATCH_STATE_PATH = _ROOT / "logs" / "lafayette_batch_payout_state.json"


@dataclass(frozen=True)
class LafayetteCandidate:
    balance_txn_id: str
    payment_intent_id: str
    charge_id: str | None
    net_cents: int
    currency: str
    available_on: int


def _maybe_load_dotenv() -> None:
    if (os.environ.get("SACMUSEUM_LOAD_DOTENV") or "").strip() != "1":
        return
    try:
        from dotenv import load_dotenv
    except ImportError:
        print(
            "SACMUSEUM_LOAD_DOTENV=1 requiere: pip install python-dotenv",
            file=sys.stderr,
        )
        return
    load_dotenv(_ROOT / ".env")


def _is_true_env(var_name: str) -> bool:
    return (os.environ.get(var_name) or "").strip().lower() in ("1", "true", "yes")


def _req_field(obj: object, *path: str) -> object:
    cur: object = obj
    for p in path:
        if cur is None:
            return None
        if isinstance(cur, dict):
            cur = cur.get(p)
        else:
            cur = getattr(cur, p, None)
    return cur


def _safe_int(value: object, default: int = 0) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return default


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _iter_collection_items(collection: object, *, limit: int) -> list[object]:
    if collection is None:
        return []
    if hasattr(collection, "auto_paging_iter"):
        items: list[object] = []
        for idx, item in enumerate(collection.auto_paging_iter()):
            if idx >= limit:
                break
            items.append(item)
        return items
    if isinstance(collection, list):
        return collection[:limit]
    data = getattr(collection, "data", None)
    if isinstance(data, list):
        return data[:limit]
    return []


def _as_amount_currency(item: object) -> tuple[int, str]:
    if isinstance(item, dict):
        return _safe_int(item.get("amount")), str(item.get("currency", "")).lower()
    return _safe_int(getattr(item, "amount", 0)), str(getattr(item, "currency", "")).lower()


def _available_cents_by_currency(balance: object) -> dict[str, int]:
    available = getattr(balance, "available", None) or _req_field(balance, "available") or []
    totals: dict[str, int] = {}
    for item in available:
        amount, currency = _as_amount_currency(item)
        if not currency:
            continue
        totals[currency] = totals.get(currency, 0) + amount
    return totals


def _build_balance_signature(balance: object) -> str:
    def _normalize(items: object) -> list[dict[str, object]]:
        normalized: list[dict[str, object]] = []
        if not isinstance(items, list):
            return normalized
        for item in items:
            amount, currency = _as_amount_currency(item)
            normalized.append({"amount": amount, "currency": currency})
        normalized.sort(key=lambda x: (str(x["currency"]), int(x["amount"])))
        return normalized

    available = getattr(balance, "available", None) or _req_field(balance, "available") or []
    pending = getattr(balance, "pending", None) or _req_field(balance, "pending") or []
    payload = {"available": _normalize(available), "pending": _normalize(pending)}
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _load_processed_balance_txns(state_path: Path) -> set[str]:
    if not state_path.exists():
        return set()
    try:
        payload = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return set()
    values = payload.get("processed_balance_transactions")
    if not isinstance(values, list):
        return set()
    return {str(v) for v in values if str(v).strip()}


def _save_processed_balance_txns(state_path: Path, values: set[str]) -> None:
    _ensure_parent(state_path)
    payload = {
        "updated_at": _utc_now_iso(),
        "processed_balance_transactions": sorted(values),
    }
    state_path.write_text(
        json.dumps(payload, ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
    )


def _append_sovereignty_payout_log(log_path: Path, payload: dict[str, object]) -> None:
    _ensure_parent(log_path)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=True) + "\n")


def _resolve_payment_intent_id(
    stripe_module: object,
    txn: object,
    acct_id: str,
    charge_cache: dict[str, object],
) -> tuple[str | None, str | None]:
    source_obj = _req_field(txn, "source")
    direct_pi = _req_field(txn, "payment_intent")
    if isinstance(direct_pi, str) and direct_pi.startswith("pi_"):
        return direct_pi, None
    if isinstance(source_obj, dict):
        src_pi = source_obj.get("payment_intent")
        src_id = source_obj.get("id")
        if isinstance(src_pi, str) and src_pi.startswith("pi_"):
            return src_pi, str(src_id) if src_id else None
    if source_obj is not None and not isinstance(source_obj, str):
        src_pi = getattr(source_obj, "payment_intent", None)
        src_id = getattr(source_obj, "id", None)
        if isinstance(src_pi, str) and src_pi.startswith("pi_"):
            return src_pi, str(src_id) if src_id else None

    source_id = str(source_obj or "").strip()
    if source_id.startswith("pi_"):
        return source_id, None
    if not source_id.startswith("ch_"):
        return None, None

    charge_obj = charge_cache.get(source_id)
    if charge_obj is None:
        charge_obj = stripe_module.Charge.retrieve(source_id, stripe_account=acct_id)
        charge_cache[source_id] = charge_obj
    charge_pi = _req_field(charge_obj, "payment_intent")
    if isinstance(charge_pi, str) and charge_pi.startswith("pi_"):
        return charge_pi, source_id
    if isinstance(charge_pi, dict):
        pi_id = str(charge_pi.get("id") or "")
        if pi_id.startswith("pi_"):
            return pi_id, source_id
    return None, source_id


def collect_lafayette_available_candidates(
    stripe_module: object,
    acct_id: str,
    *,
    pi_prefix: str,
    currency: str,
    scan_limit: int,
) -> list[LafayetteCandidate]:
    listed = stripe_module.BalanceTransaction.list(
        stripe_account=acct_id,
        limit=max(1, scan_limit),
    )
    txns = _iter_collection_items(listed, limit=max(1, scan_limit))
    charge_cache: dict[str, object] = {}
    out: list[LafayetteCandidate] = []
    for txn in txns:
        txn_id = str(_req_field(txn, "id") or "").strip()
        status = str(_req_field(txn, "status") or "").lower()
        net = _safe_int(_req_field(txn, "net"))
        cur = str(_req_field(txn, "currency") or "").lower()
        if not txn_id or status != "available" or net <= 0:
            continue
        if cur != currency:
            continue
        pi_id, charge_id = _resolve_payment_intent_id(
            stripe_module, txn, acct_id, charge_cache
        )
        if not pi_id or not pi_id.startswith(pi_prefix):
            continue
        out.append(
            LafayetteCandidate(
                balance_txn_id=txn_id,
                payment_intent_id=pi_id,
                charge_id=charge_id,
                net_cents=net,
                currency=cur,
                available_on=_safe_int(_req_field(txn, "available_on")),
            )
        )
    out.sort(key=lambda c: (c.available_on, c.balance_txn_id))
    return out


def run_lafayette_batch_payout(
    stripe_module: object,
    acct_id: str,
    *,
    pi_prefix: str = _DEFAULT_PI_PREFIX,
    currency: str = _DEFAULT_CURRENCY,
    statement_descriptor: str = _DEFAULT_DESCRIPTOR,
    log_path: Path = _SOVEREIGN_PAYOUT_LOG,
    state_path: Path = _BATCH_STATE_PATH,
    scan_limit: int = _DEFAULT_SCAN_LIMIT,
    dry_run: bool = False,
    balance_snapshot: object | None = None,
) -> dict[str, object]:
    available_balance = balance_snapshot or stripe_module.Balance.retrieve(
        stripe_account=acct_id
    )
    available_by_currency = _available_cents_by_currency(available_balance)
    processed = _load_processed_balance_txns(state_path)
    processed_before = set(processed)
    candidates = collect_lafayette_available_candidates(
        stripe_module,
        acct_id,
        pi_prefix=pi_prefix,
        currency=currency,
        scan_limit=scan_limit,
    )

    summary: dict[str, object] = {
        "mode": "lafayette_batch",
        "scan_limit": scan_limit,
        "currency": currency,
        "pi_prefix": pi_prefix,
        "detected_candidates": len(candidates),
        "created": [],
        "skipped_processed": 0,
        "skipped_insufficient_balance": 0,
        "errors": [],
    }

    for candidate in candidates:
        if candidate.balance_txn_id in processed:
            summary["skipped_processed"] = int(summary["skipped_processed"]) + 1
            continue
        balance_cents = available_by_currency.get(candidate.currency, 0)
        if balance_cents < candidate.net_cents:
            summary["skipped_insufficient_balance"] = (
                int(summary["skipped_insufficient_balance"]) + 1
            )
            continue

        if dry_run:
            print(
                "[DRY-RUN] Lafayette disponible "
                f"{candidate.payment_intent_id} por {candidate.net_cents/100:.2f} "
                f"{candidate.currency.upper()} (sin crear payout)."
            )
            continue

        try:
            payout = stripe_module.Payout.create(
                amount=candidate.net_cents,
                currency=candidate.currency,
                description=f"Lafayette auto payout {candidate.payment_intent_id}",
                statement_descriptor=statement_descriptor[:22],
                stripe_account=acct_id,
                metadata={
                    "flow": "lafayette_batch_available",
                    "payment_intent_id": candidate.payment_intent_id,
                    "balance_transaction_id": candidate.balance_txn_id,
                    "destination_hint": "QONTO",
                    "patent": "PCT/EP2025/067317",
                },
            )
            payout_id = str(getattr(payout, "id", "") or "?")
            available_by_currency[candidate.currency] = (
                available_by_currency.get(candidate.currency, 0) - candidate.net_cents
            )
            processed.add(candidate.balance_txn_id)
            entry = {
                "ts": _utc_now_iso(),
                "engine": "sacmuseum_h2_stripe",
                "mode": "lafayette_batch",
                "stripe_account_id": acct_id,
                "payment_intent_id": candidate.payment_intent_id,
                "balance_transaction_id": candidate.balance_txn_id,
                "charge_id": candidate.charge_id,
                "payout_id": payout_id,
                "amount_cents": candidate.net_cents,
                "amount_eur": round(candidate.net_cents / 100.0, 2),
                "currency": candidate.currency,
                "destination": "QONTO",
                "status": "created",
            }
            _append_sovereignty_payout_log(log_path, entry)
            print(
                f"OK — payout inmediato {payout_id} para {candidate.payment_intent_id} "
                f"→ Qonto ({candidate.net_cents/100:.2f} {candidate.currency.upper()})."
            )
            created = summary["created"]
            if isinstance(created, list):
                created.append(entry)
        except Exception as e:  # StripeError y errores de red/control
            err = (
                f"{candidate.payment_intent_id} / {candidate.balance_txn_id}: "
                f"{getattr(e, 'user_message', None) or e}"
            )
            print(f"Payout Lafayette: error — {err}", file=sys.stderr)
            errors = summary["errors"]
            if isinstance(errors, list):
                errors.append(err)

    if not dry_run and processed != processed_before:
        _save_processed_balance_txns(state_path, processed)
    return summary


def _print_batch_summary(summary: dict[str, object]) -> None:
    created = summary.get("created")
    errors = summary.get("errors")
    created_count = len(created) if isinstance(created, list) else 0
    error_count = len(errors) if isinstance(errors, list) else 0
    print("-" * 70)
    print("BATCH PAYOUT ENGINE — RESUMEN")
    print(f"  mode: {summary.get('mode')}")
    print(f"  detected_candidates: {summary.get('detected_candidates')}")
    print(f"  created_payouts: {created_count}")
    print(f"  skipped_processed: {summary.get('skipped_processed')}")
    print(f"  skipped_insufficient_balance: {summary.get('skipped_insufficient_balance')}")
    print(f"  errors: {error_count}")


def run_lafayette_watch_loop(
    stripe_module: object,
    acct_id: str,
    *,
    pi_prefix: str,
    currency: str,
    statement_descriptor: str,
    poll_interval_sec: float,
    scan_limit: int,
    max_polls: int,
) -> int:
    last_signature: str | None = None
    polls = 0
    print(
        "Lafayette watch activo: payout automático al detectar cambios de balance "
        f"(poll={poll_interval_sec:.1f}s)."
    )
    while True:
        try:
            balance = stripe_module.Balance.retrieve(stripe_account=acct_id)
            signature = _build_balance_signature(balance)
        except Exception as e:
            print(f"Balance watch: error leyendo balance — {e}", file=sys.stderr)
            time.sleep(max(0.5, poll_interval_sec))
            continue

        if signature != last_signature:
            print(f"Cambio de balance detectado ({_utc_now_iso()}). Ejecutando batch...")
            summary = run_lafayette_batch_payout(
                stripe_module,
                acct_id,
                pi_prefix=pi_prefix,
                currency=currency,
                statement_descriptor=statement_descriptor,
                scan_limit=scan_limit,
                dry_run=False,
                balance_snapshot=balance,
            )
            _print_batch_summary(summary)
            last_signature = signature

        polls += 1
        if max_polls > 0 and polls >= max_polls:
            print("Watch finalizado por STRIPE_BALANCE_WATCH_MAX_POLLS.")
            return 0
        time.sleep(max(0.5, poll_interval_sec))


def _print_balance_lines(label: str, items: object) -> None:
    if not items:
        print(f"  {label}: —")
        return
    if not isinstance(items, list):
        print(f"  {label}: {items!r}")
        return
    for x in items:
        amount, currency = _as_amount_currency(x)
        print(f"  {label}: {amount/100.0:.2f} {currency.upper()}")


def _print_final_table(
    acct_id: str,
    verif_summary: str,
    docs_pending: str,
    payout_id: str,
    neto: float,
    stmt_desc: str,
) -> None:
    print("TABLA RESUMEN")
    print(f"{'Campo':<22} | Valor")
    print("-" * 70)
    print(f"{'ID cuenta':<22} | {acct_id}")
    print(f"{'Estado verificación':<22} | {verif_summary[:200]}")
    print(f"{'Documentos pending':<22} | {docs_pending[:200]}")
    print(f"{'Neto objetivo (€)':<22} | {neto:,.2f}")
    print(f"{'Descriptor':<22} | {stmt_desc}")
    print(f"{'Payout ID (po_…)':<22} | {payout_id}")


def _run_legacy_hito2_mode(acct_id: str, stripe_module: object) -> int:
    try:
        bruto = float((os.environ.get("HITO2_BRUTO_EUR") or "27500").replace(",", "."))
    except ValueError:
        bruto = 27500.0
    try:
        tasa = float((os.environ.get("PRIMA_RATE") or "0.15").replace(",", "."))
    except ValueError:
        tasa = 0.15
    prima = bruto * tasa
    neto = bruto - prima
    neto_cents = int(round(neto * 100))

    confirm = _is_true_env("STRIPE_PAYOUT_CONFIRM")
    currency = (os.environ.get("STRIPE_PAYOUT_CURRENCY") or _DEFAULT_CURRENCY).strip().lower()
    stmt_desc = (
        (os.environ.get("STRIPE_PAYOUT_DESCRIPTOR") or "SACT_H2_FINAL").strip()
    )[:22]

    payout_id = "— (no ejecutado)"
    verif_summary = "—"
    docs_pending = "—"

    print(f"SacMuseum / Hito 2 — {datetime.now().isoformat(timespec='seconds')}")
    print("-" * 70)

    try:
        acc = stripe_module.Account.retrieve(acct_id)
    except Exception as e:
        print(f"Cuenta: error Stripe — {getattr(e, 'user_message', None) or e}", file=sys.stderr)
        return 2

    disabled = _req_field(acc, "requirements", "disabled_reason")
    currently_due = _req_field(acc, "requirements", "currently_due") or []
    details_submitted = _req_field(acc, "details_submitted")
    charges_enabled = _req_field(acc, "charges_enabled")
    payouts_enabled = _req_field(acc, "payouts_enabled")

    if not isinstance(currently_due, list):
        currently_due = list(currently_due) if currently_due else []

    verif_summary = (
        f"details_submitted={details_submitted}; charges_enabled={charges_enabled}; "
        f"payouts_enabled={payouts_enabled}; disabled_reason={disabled or '—'}"
    )
    docs_pending = (
        "; ".join(str(x) for x in currently_due) if currently_due else "(ninguno en currently_due)"
    )

    print(f"Cuenta: {acct_id}")
    print(verif_summary)
    print(f"requirements.currently_due: {docs_pending}")

    print("-" * 70)
    print("Liquidación (referencia interna; no asesoría fiscal):")
    print(f"  Bruto:        {bruto:,.2f} €")
    print(f"  Prima ({tasa*100:g}%): {prima:,.2f} €")
    print(f"  Neto a enviar: {neto:,.2f} € ({neto_cents} céntimos)")

    try:
        bal = stripe_module.Balance.retrieve(stripe_account=acct_id)
    except Exception as e:
        print(f"Balance (conectada): error — {getattr(e, 'user_message', None) or e}", file=sys.stderr)
        return 3

    print("-" * 70)
    print("Balance (cuenta conectada):")
    _print_balance_lines("available", getattr(bal, "available", None))
    _print_balance_lines("pending", getattr(bal, "pending", None))

    if not confirm:
        print("-" * 70)
        print("[DRY-RUN] No se creó payout. Para ejecutar: STRIPE_PAYOUT_CONFIRM=1")
        print("-" * 70)
        _print_final_table(
            acct_id,
            verif_summary,
            docs_pending,
            payout_id,
            neto,
            stmt_desc,
        )
        return 0

    available_map = _available_cents_by_currency(bal)
    avail_cents = available_map.get(currency, 0)
    if avail_cents == 0 and available_map:
        currency = next(iter(available_map.keys()))
        avail_cents = available_map[currency]

    if avail_cents < neto_cents:
        print(
            f"No hay fondos available suficientes ({avail_cents/100:.2f} < {neto:.2f} {currency.upper()}).",
            file=sys.stderr,
        )
        print("-" * 70)
        _print_final_table(
            acct_id,
            verif_summary,
            docs_pending,
            "— (saldo available insuficiente)",
            neto,
            stmt_desc,
        )
        return 4

    try:
        payout = stripe_module.Payout.create(
            amount=neto_cents,
            currency=currency,
            description="Liquidación Hito 2 - SacMuseum",
            statement_descriptor=stmt_desc,
            stripe_account=acct_id,
        )
        payout_id = str(getattr(payout, "id", "?"))
        print("-" * 70)
        print(f"Payout creado: {payout_id}")
    except Exception as e:
        print(f"Payout: error — {getattr(e, 'user_message', None) or e}", file=sys.stderr)
        payout_id = f"ERROR: {getattr(e, 'user_message', None) or e}"
        print("-" * 70)
        _print_final_table(
            acct_id,
            verif_summary,
            docs_pending,
            payout_id,
            neto,
            stmt_desc,
        )
        return 5

    print("-" * 70)
    _print_final_table(
        acct_id,
        verif_summary,
        docs_pending,
        payout_id,
        neto,
        stmt_desc,
    )
    return 0


def main() -> int:
    _maybe_load_dotenv()
    sk = resolve_stripe_secret()
    if not sk:
        print(
            "Define STRIPE_SECRET_KEY_FR (u otra clave secreta de la plataforma) en el entorno.",
            file=sys.stderr,
        )
        return 1

    acct_id = (
        (os.environ.get("STRIPE_SACMUSEUM_ACCOUNT_ID") or "").strip()
        or (os.environ.get("STRIPE_CONNECT_ACCOUNT_ID_FR") or "").strip()
        or (os.environ.get("STRIPE_ACCOUNT_ID") or "").strip()
    )
    if not acct_id.startswith("acct_"):
        print(
            "Define STRIPE_SACMUSEUM_ACCOUNT_ID=acct_…, STRIPE_CONNECT_ACCOUNT_ID_FR=acct_… "
            "o STRIPE_ACCOUNT_ID=acct_…",
            file=sys.stderr,
        )
        return 1

    import stripe

    stripe.api_key = sk

    mode = (os.environ.get("SACMUSEUM_PAYOUT_MODE") or "lafayette_watch").strip().lower()
    currency = (os.environ.get("STRIPE_PAYOUT_CURRENCY") or _DEFAULT_CURRENCY).strip().lower()
    statement_descriptor = (
        (os.environ.get("STRIPE_PAYOUT_DESCRIPTOR") or _DEFAULT_DESCRIPTOR).strip()
    )[:22]
    pi_prefix = (os.environ.get("STRIPE_LAFAYETTE_PI_PREFIX") or _DEFAULT_PI_PREFIX).strip()
    scan_limit = _safe_int(os.environ.get("STRIPE_LAFAYETTE_SCAN_LIMIT"), _DEFAULT_SCAN_LIMIT)
    scan_limit = max(1, min(scan_limit, 500))

    if mode == "legacy_hito2":
        return _run_legacy_hito2_mode(acct_id, stripe)

    if not sk.startswith("sk_live_") and not _is_true_env("SACMUSEUM_ALLOW_TEST_KEY"):
        print(
            "Autopayout Lafayette exige sk_live_. Para pruebas controladas usa "
            "SACMUSEUM_ALLOW_TEST_KEY=1.",
            file=sys.stderr,
        )
        return 1

    if mode == "lafayette_watch" or _is_true_env("STRIPE_BALANCE_WATCH"):
        poll_interval = float(os.environ.get("STRIPE_BALANCE_WATCH_POLL_SEC") or "30")
        max_polls = _safe_int(os.environ.get("STRIPE_BALANCE_WATCH_MAX_POLLS"), 0)
        return run_lafayette_watch_loop(
            stripe,
            acct_id,
            pi_prefix=pi_prefix,
            currency=currency,
            statement_descriptor=statement_descriptor,
            poll_interval_sec=poll_interval,
            scan_limit=scan_limit,
            max_polls=max_polls,
        )

    dry_run = _is_true_env("STRIPE_BATCH_DRY_RUN")
    summary = run_lafayette_batch_payout(
        stripe,
        acct_id,
        pi_prefix=pi_prefix,
        currency=currency,
        statement_descriptor=statement_descriptor,
        scan_limit=scan_limit,
        dry_run=dry_run,
    )
    _print_batch_summary(summary)
    errors = summary.get("errors")
    if isinstance(errors, list) and errors:
        return 5
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
