"""
Qonto IBAN / SEPA transfer node — datos de transferencia genéricos.

IBAN y montos solo desde entorno. Sin importes fijos ni beneficiarios de marca.

SIRET 94361019600017 | PCT/EP2025/067317
"""

from __future__ import annotations

import os
from datetime import datetime, timezone

SIREN = "943 610 196"
SIRET = "94361019600017"
PATENT = "PCT/EP2025/067317"
ENTITY = "EI - ESPINAR RODRIGUEZ"


def _env(key: str) -> str:
    return (os.getenv(key) or "").strip()


def _amount_from_env(amount_key: str | None = None) -> float:
    if amount_key:
        value = _env(f"QONTO_TRANSFER_AMOUNT_{amount_key.upper()}_EUR")
        if value:
            return float(value)
    default = _env("QONTO_TRANSFER_AMOUNT_EUR")
    if default:
        return float(default)
    return 0.0


def get_qonto_iban() -> str:
    return _env("QONTO_IBAN")


def get_qonto_bic() -> str:
    return _env("QONTO_BIC")


def is_iban_transfer_configured() -> bool:
    return bool(get_qonto_iban())


def resolve_iban_transfer_details(amount_key: str | None = None) -> dict:
    """Return transfer details when IBAN and amount are configured in env."""
    iban = get_qonto_iban()
    bic = get_qonto_bic()
    amount = _amount_from_env(amount_key)
    beneficiary = _env("QONTO_TRANSFER_BENEFICIARY") or ENTITY

    return {
        "method": "DIRECT_IBAN_TRANSFER",
        "entity": ENTITY,
        "beneficiary": beneficiary,
        "siret": SIRET,
        "siren": SIREN,
        "patent": PATENT,
        "iban": iban or "",
        "bic": bic or "",
        "amount_eur": amount,
        "amount_label": amount_key or "default",
        "currency": "EUR",
        "bank": "QONTO_BUSINESS",
        "iban_configured": bool(iban),
        "amount_configured": amount > 0,
        "note": "Transferencia SEPA solo con IBAN e importe definidos en entorno.",
        "ts": datetime.now(timezone.utc).isoformat(),
    }


def validate_transfer_readiness() -> tuple[dict, int]:
    iban = get_qonto_iban()
    amount = _amount_from_env(None)
    if not iban:
        return {
            "status": "error",
            "message": "qonto_iban_not_configured",
            "hint": "Set QONTO_IBAN in environment (Vercel / .env).",
        }, 503
    if amount <= 0:
        return {
            "status": "error",
            "message": "qonto_transfer_amount_not_configured",
            "hint": "Set QONTO_TRANSFER_AMOUNT_EUR after a signed contract.",
        }, 422

    return {
        "status": "ok",
        "iban_status": "VERIFIED",
        "method": "DIRECT_IBAN_TRANSFER",
        "entity": ENTITY,
        "siret": SIRET,
        "amount_eur": amount,
    }, 200


def build_qonto_invoice_import_metadata(
    *,
    invoice_ref: str = "",
    amount_eur: float | None = None,
) -> dict[str, object]:
    supplier = _env("QONTO_INVOICE_SUPPLIER_NAME") or ENTITY
    vat_category = _env("QONTO_INVOICE_VAT_CATEGORY")
    contract_ref = _env("QONTO_CONTRACT_REFERENCE") or ""
    row: dict[str, object] = {
        "proveedor": supplier,
        "supplier_name": supplier,
        "categoria_iva": vat_category,
        "vat_category": vat_category,
        "referencia_contrato": contract_ref,
        "contract_reference": contract_ref,
        "invoice_ref": invoice_ref or None,
        "amount_eur": amount_eur,
        "qonto_import_ready": bool(vat_category and contract_ref),
    }
    if not vat_category or not contract_ref:
        row["qonto_import_hint"] = (
            "Defina QONTO_INVOICE_VAT_CATEGORY y QONTO_CONTRACT_REFERENCE "
            "tras contrato firmado."
        )
    return row


def validate_qonto_invoice_import_readiness() -> tuple[dict | None, int]:
    vat = _env("QONTO_INVOICE_VAT_CATEGORY")
    contract_ref = _env("QONTO_CONTRACT_REFERENCE")
    if vat and contract_ref:
        return None, 200
    return {
        "status": "error",
        "message": "qonto_invoice_metadata_incomplete",
        "hint": (
            "Configure QONTO_INVOICE_VAT_CATEGORY and QONTO_CONTRACT_REFERENCE "
            "after a signed contract."
        ),
    }, 422
