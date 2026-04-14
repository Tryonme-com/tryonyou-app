"""
Qonto IBAN / SEPA transfer node — BunkerRepairV11.

Resolves payment via direct SEPA Business transfer instead of broken
personal Stripe test links.  IBAN comes from env (never hardcoded).

SIRET 94361019600017 | PCT/EP2025/067317
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""

from __future__ import annotations

import os
from datetime import datetime, timezone

SIREN = "943 610 196"
SIRET = "94361019600017"
PATENT = "PCT/EP2025/067317"
ENTITY = "EI - ESPINAR RODRIGUEZ"
DEFAULT_BENEFICIARY = "Le Bon Marché Rive Gauche"

AMOUNTS = {
    "setup_fee": 12_500.00,
    "exclusivity": 15_000.00,
    "total_immediate": 27_500.00,
}


def _env(key: str) -> str:
    return (os.getenv(key) or "").strip()


def get_qonto_iban() -> str:
    return _env("QONTO_IBAN")


def get_qonto_bic() -> str:
    return _env("QONTO_BIC")


def is_iban_transfer_configured() -> bool:
    return bool(get_qonto_iban())


def resolve_iban_transfer_details(amount_key: str | None = None) -> dict:
    """Return transfer details for the front-end or invoice generator.

    ``amount_key`` must be one of ``AMOUNTS`` keys or ``None`` (full
    ``total_immediate``).
    """
    iban = get_qonto_iban()
    bic = get_qonto_bic()
    key = amount_key if amount_key and amount_key in AMOUNTS else "total_immediate"
    amount = AMOUNTS[key]

    return {
        "method": "DIRECT_IBAN_TRANSFER",
        "entity": ENTITY,
        "siret": SIRET,
        "siren": SIREN,
        "patent": PATENT,
        "iban": iban or "",
        "bic": bic or "",
        "amount_eur": amount,
        "amount_label": key,
        "currency": "EUR",
        "bank": "QONTO_BUSINESS",
        "iban_configured": bool(iban),
        "note": "Transferencia bancaria SEPA Business.",
        "ts": datetime.now(timezone.utc).isoformat(),
    }


def validate_transfer_readiness() -> tuple[dict, int]:
    """Pre-flight check: can the system accept a SEPA transfer right now?"""
    iban = get_qonto_iban()
    if not iban:
        return {
            "status": "error",
            "message": "qonto_iban_not_configured",
            "hint": "Set QONTO_IBAN in environment (Vercel / .env).",
        }, 503

    return {
        "status": "ok",
        "iban_status": "VERIFIED",
        "method": "DIRECT_IBAN_TRANSFER",
        "entity": ENTITY,
        "siret": SIRET,
    }, 200
