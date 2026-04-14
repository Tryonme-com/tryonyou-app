"""
Proforma invoice generator — BunkerRepairV11.

Generates structured invoice payloads for Galeries Lafayette / SEPA
Business transfers through Qonto.  No PDF rendering here — just the
data contract for the front-end and downstream billing pipelines.

SIRET 94361019600017 | PCT/EP2025/067317
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from qonto_iban_transfer import (
    AMOUNTS,
    ENTITY,
    PATENT,
    SIREN,
    SIRET,
    get_qonto_bic,
    get_qonto_iban,
)

_INVOICES_DIR = Path("/tmp/tryonyou_invoices")


def _next_ref() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    _INVOICES_DIR.mkdir(parents=True, exist_ok=True)
    existing = sorted(_INVOICES_DIR.glob(f"INV-{stamp}-*.json"))
    seq = len(existing) + 1
    return f"INV-{stamp}-{seq:03d}"


def generate_proforma(
    to: str = "Galeries Lafayette Haussmann",
    amount_key: str | None = None,
    extra_note: str = "",
) -> dict:
    """Build a proforma invoice payload.

    Returns the invoice dict (also persisted to /tmp for local audit).
    """
    key = amount_key if amount_key and amount_key in AMOUNTS else "total_immediate"
    amount = AMOUNTS[key]
    ref = _next_ref()

    invoice = {
        "ref": ref,
        "from": ENTITY,
        "siret": SIRET,
        "siren": SIREN,
        "patent": PATENT,
        "to": to,
        "iban": get_qonto_iban() or "",
        "bic": get_qonto_bic() or "",
        "bank": "QONTO_BUSINESS",
        "currency": "EUR",
        "amount_eur": amount,
        "amount_label": key,
        "note": extra_note or "Paiement par virement bancaire SEPA Business.",
        "ts": datetime.now(timezone.utc).isoformat(),
        "status": "PROFORMA",
    }

    try:
        _INVOICES_DIR.mkdir(parents=True, exist_ok=True)
        target = _INVOICES_DIR / f"{ref}.json"
        target.write_text(json.dumps(invoice, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        pass

    return invoice
