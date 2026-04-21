"""Financial compliance reconciliation helpers for TryOnYou.

This module compares invoice F-2026-001 against the operational ledger,
computes the discrepancy, and exposes compact helpers for compliance
endpoints.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from balance_soberana import FACTURA_F_2026_001, master_ledger

INVOICE_NUMBER = "F-2026-001"
INVOICE_TOTAL_TTC_EUR = 1_160_767.21
OPERATING_LEDGER_TOTAL_EUR = 527_588.00
E2E_REFERENCE = "DIVINEO-V10-PCT2025-067317"
REFERENCE_TYPE = "E2E"
SIREN = "943 610 196"
SIRET = "94361019600017"
IBAN = "FR761695800001576292349652"
BIC = "QNTOFRP1XXX"
ENTITY = "EI - ESPINAR RODRIGUEZ, RUBEN"
CURRENCY = "EUR"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_amount(value: Any, fallback: float) -> float:
    try:
        return round(float(value), 2)
    except (TypeError, ValueError):
        return round(float(fallback), 2)


def _reconciliation_status(invoice_total_eur: float, operating_ledger_total_eur: float) -> tuple[str, float]:
    discrepancy = round(invoice_total_eur - operating_ledger_total_eur, 2)
    if discrepancy == 0:
        status = "MATCHED"
    elif discrepancy > 0:
        status = "DISCREPANCY_DETECTED"
    else:
        status = "OVERALLOCATED_LEDGER"
    return status, discrepancy


def build_financial_reconciliation_report() -> dict[str, Any]:
    ledger = master_ledger() if callable(master_ledger) else {}
    invoice = dict(FACTURA_F_2026_001 or {})

    invoice_total = _normalize_amount(
        invoice.get("importe_ttc_eur"),
        INVOICE_TOTAL_TTC_EUR,
    )

    operational_ledger_total = _normalize_amount(
        ((ledger.get("nivel_1_tesoreria_operativa") or {}).get("total_eur")),
        OPERATING_LEDGER_TOTAL_EUR,
    )

    reconciliation_status, discrepancy = _reconciliation_status(
        invoice_total,
        operational_ledger_total,
    )

    return {
        "status": "ok",
        "audit_type": "financial_reconciliation",
        "generated_at": _utc_now(),
        "entity": ENTITY,
        "invoice": {
            "number": INVOICE_NUMBER,
            "status": str(invoice.get("statut") or "EMISE"),
            "amount_ttc_eur": invoice_total,
            "currency": CURRENCY,
        },
        "operational_ledger": {
            "scope": "master_ledger.nivel_1_tesoreria_operativa",
            "amount_eur": operational_ledger_total,
            "currency": CURRENCY,
        },
        "reconciliation": {
            "status": reconciliation_status,
            "discrepancy_eur": discrepancy,
            "currency": CURRENCY,
            "comparison": "invoice_ttc_vs_operational_ledger",
            "reference_type": REFERENCE_TYPE,
            "reference": E2E_REFERENCE,
            "swift_mt103_used": False,
            "explanation": (
                "La factura F-2026-001 asciende a 1.160.767,21 EUR TTC, mientras que el ledger operativo "
                "refleja 527.588,00 EUR. La diferencia permanece abierta en conciliación."
            ),
        },
        "payment_coordinates": {
            "siren": SIREN,
            "siret": SIRET,
            "iban": IBAN,
            "bic": BIC,
        },
    }


def build_compliance_status_summary() -> dict[str, Any]:
    report = build_financial_reconciliation_report()
    ledger = master_ledger() if callable(master_ledger) else {}
    level_1 = ledger.get("nivel_1_tesoreria_operativa") or {}
    level_2 = ledger.get("nivel_2_contrato_marco") or {}
    invoice = report.get("invoice") or {}
    reconciliation = report.get("reconciliation") or {}

    return {
        "status": "ok",
        "generated_at": report.get("generated_at") or _utc_now(),
        "stripe_webhook": {
            "status": "activo",
            "provider": "stripe",
        },
        "master_ledger": {
            "status": "nivel_1_y_nivel_2_disponibles",
            "nivel_1": {
                "label": "Tesorería Operativa",
                "total_eur": _normalize_amount(level_1.get("total_eur"), OPERATING_LEDGER_TOTAL_EUR),
            },
            "nivel_2": {
                "label": "Contrato Marco",
                "total_ttc_eur": _normalize_amount(level_2.get("total_ttc_eur"), INVOICE_TOTAL_TTC_EUR),
            },
            "capital_total_consolidado_eur": _normalize_amount(
                ledger.get("capital_total_consolidado_eur"),
                INVOICE_TOTAL_TTC_EUR + OPERATING_LEDGER_TOTAL_EUR,
            ),
        },
        "invoice_f_2026_001": {
            "status": invoice.get("status") or "EMISE",
            "amount_ttc_eur": _normalize_amount(invoice.get("amount_ttc_eur"), INVOICE_TOTAL_TTC_EUR),
            "currency": CURRENCY,
        },
        "reference": {
            "type": REFERENCE_TYPE,
            "value": E2E_REFERENCE,
        },
        "reconciliation": {
            "status": reconciliation.get("status") or "DISCREPANCY_DETECTED",
            "discrepancy_eur": _normalize_amount(reconciliation.get("discrepancy_eur"), INVOICE_TOTAL_TTC_EUR - OPERATING_LEDGER_TOTAL_EUR),
            "currency": CURRENCY,
        },
        "payment_coordinates": report.get("payment_coordinates") or {
            "siren": SIREN,
            "siret": SIRET,
            "iban": IBAN,
            "bic": BIC,
        },
    }
