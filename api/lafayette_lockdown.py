"""
Lafayette Sovereign Lockdown guard.

Centraliza el bloqueo operativo para cualquier flujo dirigido a
Galeries Lafayette Haussmann / Vega mientras el pago no esté recibido
o el contrato anual no esté validado.
"""

from __future__ import annotations

import os

TARGET = "Galeries Lafayette Haussmann"
CONTRACT_REQUIRED = "ANNUAL_FIXED_RATE"
PAYMENT_REQUIRED = "RECEIVED"
DEFAULT_PAYMENT_STATUS = "AWAITING_210_3K"
DEFAULT_CONTRACT_MODE = CONTRACT_REQUIRED
ULTIMATUM = "BLACK_SCREEN_ULTIMATUM"

_CONTEXT_TOKENS = ("lafayette", "haussmann", "vega", "75009")


def _env(key: str, default: str) -> str:
    return (os.getenv(key) or default).strip()


def _is_truthy(raw: str) -> bool:
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def is_lafayette_context(raw: str | None) -> bool:
    value = str(raw or "").strip().lower()
    return any(token in value for token in _CONTEXT_TOKENS)


def sovereign_lock_state() -> dict:
    payment_status = _env("LAFAYETTE_PAYMENT_STATUS", DEFAULT_PAYMENT_STATUS).upper()
    contract_mode = _env("LAFAYETTE_CONTRACT_MODE", DEFAULT_CONTRACT_MODE).upper()
    lock_enabled = _is_truthy(_env("LAFAYETTE_LOCK_ENABLED", "1"))

    reasons: list[str] = []
    if payment_status != PAYMENT_REQUIRED:
        reasons.append("payment_pending")
    if contract_mode != CONTRACT_REQUIRED:
        reasons.append("annual_contract_required")

    blocked = lock_enabled and bool(reasons)
    return {
        "target": TARGET,
        "lock_enabled": lock_enabled,
        "payment_status": payment_status,
        "contract_required": CONTRACT_REQUIRED,
        "contract_mode": contract_mode,
        "blocked": blocked,
        "motive": "Deuda pendiente + Exigencia de Contrato Anual." if blocked else "",
        "ultimatum": ULTIMATUM if blocked else "",
        "reasons": reasons,
    }


def lafayette_lock_response(context_hint: str | None) -> tuple[dict, int] | None:
    if not is_lafayette_context(context_hint):
        return None

    state = sovereign_lock_state()
    if not state["blocked"]:
        return None

    payload = {
        "status": "blocked",
        "message": "lafayette_lockdown_active",
        "target": state["target"],
        "motive": state["motive"],
        "ultimatum": state["ultimatum"],
        "reasons": state["reasons"],
        "payment_status": state["payment_status"],
        "contract_required": state["contract_required"],
    }
    return payload, 423
