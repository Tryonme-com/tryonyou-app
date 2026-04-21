"""
Empire payout transition ledger.

Connects successful Stripe checkout intents to treasury payout records while
preserving an auditable chain (button -> checkout -> webhook -> payout).
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from treasury_monitor import record_payout

ALLOWED_CHECKOUT_HOST_SUFFIXES = ("abvetos.com",)
TRACE_FILE_NAME = "events.jsonl"
TRACE_REQUIRED_STEPS = (
    "payment.intent",
    "checkout.session.completed",
    "payout.transition",
)


def _trace_dir() -> Path:
    raw = (os.getenv("TRYONYOU_PAYMENT_TRACE_DIR") or "").strip()
    if raw:
        return Path(raw)
    return Path("/tmp/tryonyou_empire_trace")


def _trace_file() -> Path:
    return _trace_dir() / TRACE_FILE_NAME


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _append_event(entry: dict[str, Any]) -> dict[str, Any]:
    target = _trace_file()
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def _read_events() -> list[dict[str, Any]]:
    target = _trace_file()
    if not target.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in target.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def _is_allowed_checkout_url(raw_url: str) -> bool:
    raw = (raw_url or "").strip()
    if not raw:
        return False
    try:
        parsed = urlparse(raw)
    except Exception:
        return False
    host = (parsed.hostname or "").lower().strip(".")
    if not host:
        return False
    return any(host == suffix or host.endswith(f".{suffix}") for suffix in ALLOWED_CHECKOUT_HOST_SUFFIXES)


def _resolve_flow_token(flow_token: str, session_id: str) -> str:
    token = (flow_token or "").strip()
    if token:
        return token
    sid = (session_id or "").strip()
    if not sid:
        return ""
    for event in reversed(_read_events()):
        if str(event.get("session_id", "")).strip() != sid:
            continue
        prev = str(event.get("flow_token", "")).strip()
        if prev:
            return prev
    return ""


def _normalize_amount_eur(amount_total: int | float | None) -> float:
    if not isinstance(amount_total, (int, float)):
        return 0.0
    if amount_total <= 0:
        return 0.0
    # Stripe webhooks report amount_total in cents.
    return round(float(amount_total) / 100.0, 2)


def register_payment_intent(
    *,
    flow_token: str,
    checkout_url: str,
    button_id: str,
    source: str,
    protocol: str,
    ui_theme: str,
) -> dict[str, Any]:
    event = {
        "event": "payment.intent",
        "ts": _utc_now(),
        "flow_token": (flow_token or "").strip(),
        "checkout_url": (checkout_url or "").strip(),
        "checkout_host_allowed": _is_allowed_checkout_url(checkout_url),
        "button_id": (button_id or "").strip() or "tryonyou-pay-button",
        "source": (source or "").strip() or "index_html_shell",
        "protocol": (protocol or "").strip() or "Pau Emotional Intelligence",
        "ui_theme": (ui_theme or "").strip() or "Sello de Lujo: Antracita",
    }
    return _append_event(event)


def register_checkout_success(
    *,
    session_id: str,
    amount_total: int | float | None,
    currency: str,
    customer_email: str,
    flow_token: str,
    source: str,
) -> dict[str, Any]:
    sid = (session_id or "").strip()
    token = _resolve_flow_token(flow_token, sid)
    amount_eur = _normalize_amount_eur(amount_total)

    success_event = _append_event(
        {
            "event": "checkout.session.completed",
            "ts": _utc_now(),
            "flow_token": token,
            "session_id": sid,
            "amount_total": amount_total if isinstance(amount_total, (int, float)) else None,
            "amount_eur": amount_eur,
            "currency": (currency or "").strip().lower() or "eur",
            "customer_email": (customer_email or "").strip(),
            "source": (source or "").strip() or "stripe_webhook",
            "souverainete_state": 1,
        }
    )

    payout_transition = None
    if amount_eur > 0:
        payout_transition = register_payout_transition(
            amount_eur=amount_eur,
            recipient=(customer_email or "stripe_checkout_success").strip() or "stripe_checkout_success",
            concept="stripe_checkout_success",
            flow_token=token,
            session_id=sid,
            source="stripe_checkout_success",
        )

    return {
        "ok": True,
        "checkout_success": success_event,
        "payout_transition": payout_transition,
    }


def register_payout_transition(
    *,
    amount_eur: float,
    recipient: str,
    concept: str,
    flow_token: str,
    session_id: str,
    source: str,
) -> dict[str, Any]:
    token = _resolve_flow_token(flow_token, session_id)
    payout_entry = record_payout(
        amount_eur=float(amount_eur),
        recipient=(recipient or "").strip() or "operational",
        concept=(concept or "").strip() or "operational",
    )
    transition = {
        "event": "payout.transition",
        "ts": _utc_now(),
        "flow_token": token,
        "session_id": (session_id or "").strip(),
        "amount_eur": round(float(amount_eur), 2),
        "recipient": (recipient or "").strip() or "operational",
        "concept": (concept or "").strip() or "operational",
        "source": (source or "").strip() or "api_v1_treasury_payouts",
        "payout": payout_entry,
    }
    return _append_event(transition)


def get_trace_events() -> list[dict[str, Any]]:
    return _read_events()


def get_flow_summary(*, flow_token: str = "", session_id: str = "") -> dict[str, Any]:
    token = (flow_token or "").strip()
    sid = (session_id or "").strip()
    events = _read_events()

    if token or sid:
        filtered = []
        for event in events:
            event_token = str(event.get("flow_token", "")).strip()
            event_session = str(event.get("session_id", "")).strip()
            if token and event_token == token:
                filtered.append(event)
                continue
            if sid and event_session == sid:
                filtered.append(event)
                continue
        events = filtered

    # If only session_id was provided, infer flow_token for convenience.
    if not token and sid:
        for event in events:
            inferred = str(event.get("flow_token", "")).strip()
            if inferred:
                token = inferred
                break

    event_names = {str(event.get("event", "")).strip() for event in events}
    intent_logged = "payment.intent" in event_names
    checkout_success_logged = "checkout.session.completed" in event_names
    payout_logged = "payout.transition" in event_names

    checkout_host_allowed = True
    for event in events:
        if str(event.get("event", "")).strip() != "payment.intent":
            continue
        checkout_host_allowed = bool(event.get("checkout_host_allowed"))
        break

    missing_steps: list[str] = []
    if not intent_logged:
        missing_steps.append("payment.intent")
    if not checkout_success_logged:
        missing_steps.append("checkout.session.completed")
    if not payout_logged:
        missing_steps.append("payout.transition")
    if intent_logged and not checkout_host_allowed:
        missing_steps.append("checkout_host_not_allowed")

    return {
        "flow_token": token,
        "session_id": sid,
        "intent_logged": intent_logged,
        "checkout_success_logged": checkout_success_logged,
        "payout_logged": payout_logged,
        "checkout_host_allowed": checkout_host_allowed,
        "trace_integrity": len(missing_steps) == 0,
        "missing_steps": missing_steps,
        "events_count": len(events),
        "required_steps": list(TRACE_REQUIRED_STEPS),
    }
