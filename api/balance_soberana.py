"""
Balance Soberana — metadatos legales TryOnYou + ledger operativo vacío por defecto.

No incluye deudas, facturas ni importes objetivo hacia terceros sin contrato.
Los importes reales deben cargarse vía entorno tras acuerdo firmado.

Patente: PCT/EP2025/067317
SIREN: 943 610 196
SIRET: 94361019600017
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone

PATENTE = "PCT/EP2025/067317"
SIREN = "943 610 196"
SIRET = "94361019600017"
ENTITY = "EI - ESPINAR RODRIGUEZ, RUBEN"
IBAN = "FR761695800001576292349652"
BIC = "QNTOFRP1XXX"
LEDGER_NOTE = (
    "Ledger operativo vacío por defecto. "
    "Define TREASURY_LINE_ITEMS_JSON tras contrato firmado."
)


def _line_items_from_env() -> list[dict[str, object]]:
    raw = (os.getenv("TREASURY_LINE_ITEMS_JSON") or "").strip()
    if not raw:
        return []
    data = json.loads(raw)
    if not isinstance(data, list):
        raise ValueError("TREASURY_LINE_ITEMS_JSON debe ser una lista JSON.")
    return data


def _line_items_total(items: list[dict[str, object]]) -> float:
    total = 0.0
    for item in items:
        try:
            total += float(item.get("amount_eur") or 0)
        except (TypeError, ValueError):
            continue
    return round(total, 2)


def master_ledger() -> dict:
    """Ledger consolidado genérico (sin clientes ficticios)."""
    items = _line_items_from_env()
    total = _line_items_total(items)
    return {
        "entity": ENTITY,
        "siren": SIREN,
        "siret": SIRET,
        "patente": PATENTE,
        "iban": IBAN,
        "bic": BIC,
        "ts": datetime.now(timezone.utc).isoformat(),
        "note": LEDGER_NOTE,
        "line_items": items,
        "total_eur": total,
        "SOUVERAINETÉ": 1,
    }


def ledger_soberano() -> dict[str, object]:
    """Ledger resumido para integraciones externas."""
    items = _line_items_from_env()
    return {
        "patente": PATENTE,
        "siren": SIREN,
        "note": LEDGER_NOTE,
        "line_items_count": len(items),
        "capital_total_eur": _line_items_total(items),
    }


def balance_total_soberano() -> float:
    """Imprime estado de tesorería genérico (sin reclamar deudas de terceros)."""
    items = _line_items_from_env()
    total = _line_items_total(items)
    print("--- [ESTADO FINANCIERO: TRYONYOU — TESORERÍA GENÉRICA] ---")
    print(f"TOTAL CONFIGURADO: {total:,.2f} €")
    print(f"NOTA: {LEDGER_NOTE}")
    return total
