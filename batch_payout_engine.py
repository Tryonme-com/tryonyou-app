"""
Batch Payout Engine — Omega 10 execution guard.

Monitors a target set of Stripe PaymentIntents and executes a payout to the
configured bank destination (Qonto via Stripe) as soon as the banking window
is open and compliance checks are clean.

Safety rules:
- Never hardcode secrets; resolve Stripe key from environment.
- Block execution when compliance anomalies are detected.
- Keep idempotency state on disk to avoid duplicate payouts.

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberania V10 - Founder: Ruben
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
import unicodedata
from zoneinfo import ZoneInfo

from stripe_verify_secret_env import resolve_stripe_secret

_DEFAULT_PI_PREFIX = "pi_3OzL9k"
_DEFAULT_TARGET_COUNT = 5
_DEFAULT_POLL_SECONDS = 60
_DEFAULT_TZ = "Europe/Paris"
_DEFAULT_BANK_OPEN_HOUR = 9
_DEFAULT_BANK_OPEN_MINUTE = 0
_DEFAULT_WEEKDAYS = (0, 1, 2, 3, 4)  # Monday..Friday
_DEFAULT_MAX_INTENT_SCAN = 100
_DEFAULT_DESCRIPTOR = "OMEGA10 BATCH"

_DEFAULT_COMPLIANCE_MARKERS = (
    "anomaly",
    "anomal",
    "compliance_block",
    "blocked",
    "fraud",
    "aml",
    "kyc_fail",
    "sanction",
    "risk_alert",
)

_DEFAULT_COMPLIANCE_PATHS = (
    Path("/workspace/logs/compliance_logs.jsonl"),
    Path("/workspace/logs/compliance_logs.log"),
    Path("/workspace/compliance_logs.jsonl"),
    Path("/workspace/compliance_logs.log"),
    Path("/workspace/logs/sovereignty_access_audit.jsonl"),
)

_STATE_DEFAULT = Path("/tmp/tryonyou_batch_payout_engine_state.json")
_STATUS_WAITING = {
    "waiting_bank_open",
    "waiting_target_count",
    "waiting_intent_status",
    "waiting_balance_available",
    "ready_dry_run",
}
_STATUS_BLOCKED = {
    "blocked_infrastructure_state",
    "blocked_compliance",
    "blocked_config",
    "blocked_stripe_auth",
    "error_payout_create",
}
_STATUS_FINISHED = {"executed", "already_executed"}


@dataclass(frozen=True)
class BatchPayoutConfig:
    payment_intent_ids: tuple[str, ...]
    payment_intent_prefix: str
    target_count: int
    max_intent_scan: int
    poll_seconds: int
    timezone_name: str
    bank_open_hour: int
    bank_open_minute: int
    bank_open_weekdays: tuple[int, ...]
    compliance_log_paths: tuple[Path, ...]
    compliance_markers: tuple[str, ...]
    compliance_strict: bool
    notify_webhook_url: str
    confirm_payout: bool
    state_file: Path
    payout_currency: str
    payout_amount_cents_override: int | None
    payout_descriptor: str
    payout_destination_account: str
    expected_infra_state: str
    expected_souverainete_state: str


def _env_bool(key: str, default: bool = False) -> bool:
    raw = (os.getenv(key) or "").strip().lower()
    if not raw:
        return default
    return raw in {"1", "true", "yes", "on"}


def _env_csv(key: str) -> tuple[str, ...]:
    raw = (os.getenv(key) or "").strip()
    if not raw:
        return ()
    return tuple(item.strip() for item in raw.split(",") if item.strip())


def _env_int(key: str, default: int) -> int:
    raw = (os.getenv(key) or "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _build_config() -> BatchPayoutConfig:
    explicit_ids = _env_csv("BATCH_PAYMENT_INTENT_IDS")
    prefix = (os.getenv("BATCH_PAYMENT_INTENT_PREFIX") or _DEFAULT_PI_PREFIX).strip() or _DEFAULT_PI_PREFIX
    count = max(1, _env_int("BATCH_PAYMENT_INTENT_COUNT", _DEFAULT_TARGET_COUNT))
    poll_seconds = max(5, _env_int("BATCH_PAYOUT_POLL_SECONDS", _DEFAULT_POLL_SECONDS))
    timezone_name = (os.getenv("BATCH_BANK_TIMEZONE") or _DEFAULT_TZ).strip() or _DEFAULT_TZ
    open_hour = max(0, min(23, _env_int("BATCH_BANK_OPEN_HOUR", _DEFAULT_BANK_OPEN_HOUR)))
    open_min = max(0, min(59, _env_int("BATCH_BANK_OPEN_MINUTE", _DEFAULT_BANK_OPEN_MINUTE)))
    custom = _env_csv("BATCH_BANK_OPEN_WEEKDAYS")
    parsed = []
    for item in custom:
        try:
            value = int(item)
        except ValueError:
            continue
        if 0 <= value <= 6:
            parsed.append(value)
    weekdays = tuple(sorted(set(parsed))) if parsed else _DEFAULT_WEEKDAYS

    compliance_paths_env = _env_csv("JULES_COMPLIANCE_LOG_PATHS")
    compliance_paths = tuple(Path(p) for p in compliance_paths_env) if compliance_paths_env else _DEFAULT_COMPLIANCE_PATHS
    compliance_markers = _env_csv("JULES_COMPLIANCE_MARKERS") or _DEFAULT_COMPLIANCE_MARKERS
    compliance_strict = _env_bool("JULES_COMPLIANCE_STRICT", default=False)

    webhook = (
        os.getenv("JULES_SLACK_WEBHOOK_URL")
        or os.getenv("SLACK_WEBHOOK_URL")
        or os.getenv("MAKE_WEBHOOK_URL")
        or ""
    ).strip()
    confirm = _env_bool("BATCH_PAYOUT_CONFIRM", default=False)

    state_file = Path((os.getenv("BATCH_PAYOUT_STATE_FILE") or "").strip() or _STATE_DEFAULT)
    payout_currency = (os.getenv("BATCH_PAYOUT_CURRENCY") or "eur").strip().lower() or "eur"
    payout_descriptor = (os.getenv("BATCH_PAYOUT_DESCRIPTOR") or _DEFAULT_DESCRIPTOR).strip()[:22] or _DEFAULT_DESCRIPTOR
    payout_destination = (os.getenv("QONTO_EXTERNAL_ACCOUNT_ID") or "").strip()

    amount_override_raw = (os.getenv("BATCH_PAYOUT_AMOUNT_CENTS") or "").strip()
    amount_override = None
    if amount_override_raw:
        try:
            parsed_override = int(amount_override_raw)
            if parsed_override > 0:
                amount_override = parsed_override
        except ValueError:
            amount_override = None

    expected_infra = (os.getenv("BATCH_EXPECTED_INFRA_STATE") or "SUPABASE ARMORED").strip()
    expected_souverainete = (os.getenv("BATCH_EXPECTED_SOUVERAINETE_STATE") or "SOUVERAINETE:1").strip()

    return BatchPayoutConfig(
        payment_intent_ids=explicit_ids,
        payment_intent_prefix=prefix,
        target_count=count,
        max_intent_scan=max(5, _env_int("BATCH_MAX_INTENT_SCAN", _DEFAULT_MAX_INTENT_SCAN)),
        poll_seconds=poll_seconds,
        timezone_name=timezone_name,
        bank_open_hour=open_hour,
        bank_open_minute=open_min,
        bank_open_weekdays=weekdays,
        compliance_log_paths=compliance_paths,
        compliance_markers=tuple(marker.lower() for marker in compliance_markers),
        compliance_strict=compliance_strict,
        notify_webhook_url=webhook,
        confirm_payout=confirm,
        state_file=state_file,
        payout_currency=payout_currency,
        payout_amount_cents_override=amount_override,
        payout_descriptor=payout_descriptor,
        payout_destination_account=payout_destination,
        expected_infra_state=expected_infra,
        expected_souverainete_state=expected_souverainete,
    )


def _json_default_state() -> dict[str, Any]:
    return {"executions": {}}


def _load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return _json_default_state()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return _json_default_state()
    if not isinstance(data, dict):
        return _json_default_state()
    data.setdefault("executions", {})
    return data


def _save_state(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _notify(webhook_url: str, payload: dict[str, Any]) -> bool:
    if not webhook_url:
        return False
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=8)
    except Exception:
        return False
    return True


def _norm_state(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", (value or "").strip())
    ascii_state = normalized.encode("ascii", "ignore").decode("ascii")
    return ascii_state.upper().replace(" ", "")


def _scan_compliance(config: BatchPayoutConfig) -> dict[str, Any]:
    anomalies: list[dict[str, Any]] = []
    files_checked: list[str] = []
    files_found = 0

    for path in config.compliance_log_paths:
        files_checked.append(str(path))
        if not path.exists():
            continue
        files_found += 1
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for line_no, line in enumerate(lines, start=1):
            low = line.lower()
            if any(marker in low for marker in config.compliance_markers):
                anomalies.append(
                    {
                        "path": str(path),
                        "line": line_no,
                        "snippet": line.strip()[:280],
                    }
                )

    blocked = bool(anomalies) or (config.compliance_strict and files_found == 0)
    reason = "anomaly_detected" if anomalies else ("no_logs_found_strict_mode" if blocked else "clean")

    return {
        "blocked": blocked,
        "reason": reason,
        "files_found": files_found,
        "files_checked": files_checked,
        "anomalies": anomalies,
    }


def _now_in_tz(config: BatchPayoutConfig, now: datetime | None = None) -> datetime:
    tz = ZoneInfo(config.timezone_name)
    if now is None:
        return datetime.now(tz)
    if now.tzinfo is None:
        return now.replace(tzinfo=tz)
    return now.astimezone(tz)


def _bank_open_state(config: BatchPayoutConfig, now: datetime | None = None) -> dict[str, Any]:
    current = _now_in_tz(config, now)
    open_today = current.replace(
        hour=config.bank_open_hour,
        minute=config.bank_open_minute,
        second=0,
        microsecond=0,
    )
    in_open_weekday = current.weekday() in set(config.bank_open_weekdays)
    is_open = bool(in_open_weekday and current >= open_today)

    if is_open:
        return {
            "is_open": True,
            "now": current.isoformat(),
            "next_open": open_today.isoformat(),
            "seconds_to_open": 0,
        }

    candidate = open_today
    if in_open_weekday and current < open_today:
        next_open = candidate
    else:
        next_open = candidate + timedelta(days=1)
        while next_open.weekday() not in set(config.bank_open_weekdays):
            next_open += timedelta(days=1)
    seconds_to_open = max(1, int((next_open - current).total_seconds()))
    return {
        "is_open": False,
        "now": current.isoformat(),
        "next_open": next_open.isoformat(),
        "seconds_to_open": seconds_to_open,
    }


def _to_dict(obj: Any) -> dict[str, Any]:
    if isinstance(obj, dict):
        return obj
    to_dict = getattr(obj, "to_dict_recursive", None)
    if callable(to_dict):
        return to_dict()
    try:
        return dict(obj)
    except Exception:
        return {}


def _normalize_pi(pi: Any) -> dict[str, Any]:
    data = _to_dict(pi)
    amount_received = data.get("amount_received")
    amount = data.get("amount")
    amount_cents = int(amount_received or amount or 0)
    return {
        "id": str(data.get("id") or ""),
        "status": str(data.get("status") or "").strip().lower(),
        "currency": str(data.get("currency") or "").strip().lower(),
        "amount_cents": amount_cents,
        "created": int(data.get("created") or 0),
    }


def _collect_target_intents(stripe_module: Any, config: BatchPayoutConfig) -> dict[str, Any]:
    intents: list[dict[str, Any]] = []

    if config.payment_intent_ids:
        for intent_id in config.payment_intent_ids:
            pi = stripe_module.PaymentIntent.retrieve(intent_id)
            intents.append(_normalize_pi(pi))
    else:
        listed = stripe_module.PaymentIntent.list(limit=config.max_intent_scan)
        for pi in listed.auto_paging_iter():
            item = _normalize_pi(pi)
            if item["id"].startswith(config.payment_intent_prefix):
                intents.append(item)
            if len(intents) >= config.target_count:
                break

    intents.sort(key=lambda item: item.get("created", 0), reverse=True)
    selected = intents[: config.target_count]

    statuses = [item["status"] for item in selected]
    all_succeeded = len(selected) == config.target_count and all(status == "succeeded" for status in statuses)
    currencies = {item["currency"] for item in selected if item["currency"]}
    currency = next(iter(currencies)) if len(currencies) == 1 else ""
    total_amount_cents = sum(int(item["amount_cents"]) for item in selected)

    return {
        "count": len(selected),
        "target_count": config.target_count,
        "all_succeeded": all_succeeded,
        "statuses": statuses,
        "currency": currency,
        "multiple_currencies": len(currencies) > 1,
        "total_amount_cents": total_amount_cents,
        "intents": selected,
    }


def _resolve_available_balance_cents(stripe_module: Any, currency: str) -> int:
    balance = stripe_module.Balance.retrieve()
    payload = _to_dict(balance)
    available = payload.get("available") or []
    for item in available:
        amount = int(_to_dict(item).get("amount") or 0)
        cur = str(_to_dict(item).get("currency") or "").strip().lower()
        if cur == currency:
            return amount
    return 0


def _intent_fingerprint(intents: list[dict[str, Any]]) -> str:
    ids = sorted(str(item.get("id") or "") for item in intents)
    joined = "|".join(ids).encode("utf-8")
    return hashlib.sha256(joined).hexdigest()


def _register_internal_payout(amount_cents: int, payout_id: str) -> None:
    try:
        from empire_payout_trans import register_payout_transition

        register_payout_transition(
            amount_eur=round(amount_cents / 100.0, 2),
            recipient="QONTO_BATCH_ENGINE",
            concept="omega10_batch_payout",
            flow_token="omega10_batch_engine",
            session_id=payout_id,
            source="batch_payout_engine",
        )
    except Exception:
        # Logging fallback intentionally silent to avoid blocking financial flow.
        return


def run_cycle(config: BatchPayoutConfig, *, now: datetime | None = None) -> dict[str, Any]:
    infra_state = (os.getenv("SUPABASE_INFRA_STATUS") or "SUPABASE ARMORED").strip()
    souverainete_state = (os.getenv("SOUVERAINETE_STATUS") or "SOUVERAINETE:1").strip()
    if (
        _norm_state(infra_state) != _norm_state(config.expected_infra_state)
        or _norm_state(souverainete_state) != _norm_state(config.expected_souverainete_state)
    ):
        result = {
            "status": "blocked_infrastructure_state",
            "infra_state": infra_state,
            "souverainete_state": souverainete_state,
            "expected": {
                "infra_state": config.expected_infra_state,
                "souverainete_state": config.expected_souverainete_state,
            },
        }
        _notify(config.notify_webhook_url, {"event": "batch_payout_blocked", **result})
        return result

    compliance = _scan_compliance(config)
    if compliance["blocked"]:
        result = {"status": "blocked_compliance", "compliance": compliance}
        _notify(config.notify_webhook_url, {"event": "batch_payout_blocked", **result})
        return result

    bank = _bank_open_state(config, now=now)
    if not bank["is_open"]:
        return {"status": "waiting_bank_open", "bank": bank}

    sk = resolve_stripe_secret()
    if not sk.startswith(("sk_live_", "sk_test_")):
        result = {
            "status": "blocked_stripe_auth",
            "error": "missing_or_invalid_stripe_secret",
        }
        _notify(config.notify_webhook_url, {"event": "batch_payout_blocked", **result})
        return result

    try:
        import stripe  # type: ignore
    except ImportError:
        result = {"status": "blocked_config", "error": "stripe_sdk_missing"}
        _notify(config.notify_webhook_url, {"event": "batch_payout_blocked", **result})
        return result

    stripe.api_key = sk
    intents = _collect_target_intents(stripe, config)
    if intents["count"] < config.target_count:
        return {"status": "waiting_target_count", "intents": intents}
    if not intents["all_succeeded"]:
        return {"status": "waiting_intent_status", "intents": intents}
    if intents["multiple_currencies"]:
        result = {
            "status": "blocked_config",
            "error": "multiple_currencies_not_supported",
            "intents": intents,
        }
        _notify(config.notify_webhook_url, {"event": "batch_payout_blocked", **result})
        return result

    payout_currency = intents["currency"] or config.payout_currency
    payout_amount_cents = config.payout_amount_cents_override or intents["total_amount_cents"]
    if payout_amount_cents <= 0:
        result = {"status": "blocked_config", "error": "non_positive_payout_amount", "intents": intents}
        _notify(config.notify_webhook_url, {"event": "batch_payout_blocked", **result})
        return result

    available_cents = _resolve_available_balance_cents(stripe, payout_currency)
    if available_cents < payout_amount_cents:
        return {
            "status": "waiting_balance_available",
            "currency": payout_currency,
            "required_cents": payout_amount_cents,
            "available_cents": available_cents,
        }

    intent_fp = _intent_fingerprint(intents["intents"])
    state = _load_state(config.state_file)
    executions = state.get("executions") or {}
    if intent_fp in executions:
        return {"status": "already_executed", "execution": executions[intent_fp]}

    if not config.confirm_payout:
        return {
            "status": "ready_dry_run",
            "currency": payout_currency,
            "amount_cents": payout_amount_cents,
            "intent_fingerprint": intent_fp,
            "intents": intents,
        }

    create_params: dict[str, Any] = {
        "amount": payout_amount_cents,
        "currency": payout_currency,
        "statement_descriptor": config.payout_descriptor,
        "idempotency_key": f"omega10-{intent_fp[:20]}-{payout_amount_cents}",
    }
    if config.payout_destination_account:
        create_params["destination"] = config.payout_destination_account

    try:
        payout = stripe.Payout.create(**create_params)
    except Exception as exc:
        result = {
            "status": "error_payout_create",
            "error": str(exc),
            "currency": payout_currency,
            "amount_cents": payout_amount_cents,
        }
        _notify(config.notify_webhook_url, {"event": "batch_payout_error", **result})
        return result

    payout_data = _to_dict(payout)
    payout_id = str(payout_data.get("id") or "")
    execution = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "payout_id": payout_id,
        "currency": payout_currency,
        "amount_cents": payout_amount_cents,
        "intent_ids": [item["id"] for item in intents["intents"]],
    }
    executions[intent_fp] = execution
    state["executions"] = executions
    _save_state(config.state_file, state)
    _register_internal_payout(payout_amount_cents, payout_id or "po_unknown")

    result = {"status": "executed", "execution": execution}
    _notify(config.notify_webhook_url, {"event": "batch_payout_executed", **result})
    return result


def run_daemon(config: BatchPayoutConfig, *, max_cycles: int | None = None) -> int:
    cycles = 0
    while True:
        cycles += 1
        result = run_cycle(config)
        print(json.dumps(result, ensure_ascii=False))
        status = str(result.get("status") or "")
        if status in _STATUS_FINISHED:
            return 0
        if status in _STATUS_BLOCKED:
            return 2
        if max_cycles is not None and cycles >= max_cycles:
            return 3
        time.sleep(config.poll_seconds)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Monitoriza PaymentIntents del batch y ejecuta payout a Qonto "
            "cuando la ventana bancaria esta abierta y compliance esta limpio."
        )
    )
    parser.add_argument("--daemon", action="store_true", help="Mantiene monitorizacion en bucle.")
    parser.add_argument("--max-cycles", type=int, default=None, help="Limite de ciclos en modo daemon.")
    parser.add_argument("--once", action="store_true", help="Ejecuta un ciclo (modo por defecto).")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    config = _build_config()
    if args.daemon:
        return run_daemon(config, max_cycles=args.max_cycles)
    result = run_cycle(config)
    print(json.dumps(result, ensure_ascii=False))
    status = str(result.get("status") or "")
    if status in _STATUS_FINISHED or status in _STATUS_WAITING:
        return 0
    if status in _STATUS_BLOCKED:
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
