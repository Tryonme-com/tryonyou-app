"""
Territory Expansion — Multi-node licensing V11.

Manages the expansion map of TryOnYou deployment nodes beyond the
founding Lafayette Haussmann location.  Each node has a licensing
status, a contract amount (27 500 EUR standard V11 licence) and
a proforma generation hook.

SIRET 94361019600017 | PCT/EP2025/067317
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

SIREN = "943 610 196"
SIRET = "94361019600017"
PATENT = "PCT/EP2025/067317"
ENTITY = "EI - ESPINAR RODRIGUEZ"

LICENCE_FEE_EUR = 27_500.00
SETUP_FEE_EUR = 12_500.00
EXCLUSIVITY_EUR = 15_000.00

TERRITORY_LOG_DIR = Path("/tmp/tryonyou_territory")

EXPANSION_NODES: list[dict] = [
    {
        "id": "lafayette-haussmann",
        "name": "Galeries Lafayette Haussmann",
        "city": "Paris",
        "district": "75009",
        "status": "ACTIVE",
        "licence_eur": LICENCE_FEE_EUR,
        "confirmed": True,
    },
    {
        "id": "bon-marche",
        "name": "Le Bon Marché",
        "city": "Paris",
        "district": "75007",
        "status": "PENDING_LICENCE",
        "licence_eur": LICENCE_FEE_EUR,
        "confirmed": False,
    },
    {
        "id": "le-marais",
        "name": "Le Marais",
        "city": "Paris",
        "district": "75003",
        "status": "PENDING_LICENCE",
        "licence_eur": LICENCE_FEE_EUR,
        "confirmed": False,
    },
    {
        "id": "la-defense",
        "name": "La Défense",
        "city": "Paris",
        "district": "92060",
        "status": "PENDING_LICENCE",
        "licence_eur": LICENCE_FEE_EUR,
        "confirmed": False,
    },
]


def get_expansion_nodes() -> list[dict]:
    """Return all expansion nodes with their licensing status."""
    ts = datetime.now(timezone.utc).isoformat()
    return [
        {**node, "patent": PATENT, "siret": SIRET, "ts": ts}
        for node in EXPANSION_NODES
    ]


def get_territory_summary() -> dict:
    """High-level territory summary for dashboards and health checks."""
    active = [n for n in EXPANSION_NODES if n["status"] == "ACTIVE"]
    pending = [n for n in EXPANSION_NODES if n["status"] == "PENDING_LICENCE"]
    total_confirmed_revenue = sum(n["licence_eur"] for n in active)
    total_pending_revenue = sum(n["licence_eur"] for n in pending)

    return {
        "entity": ENTITY,
        "siret": SIRET,
        "patent": PATENT,
        "total_nodes": len(EXPANSION_NODES),
        "active_nodes": len(active),
        "pending_nodes": len(pending),
        "active_names": [n["name"] for n in active],
        "pending_names": [n["name"] for n in pending],
        "confirmed_revenue_eur": total_confirmed_revenue,
        "pending_revenue_eur": total_pending_revenue,
        "expansion_target_eur": total_confirmed_revenue + total_pending_revenue,
        "licence_fee_eur": LICENCE_FEE_EUR,
        "ts": datetime.now(timezone.utc).isoformat(),
    }


def generate_node_contract(node_id: str) -> dict | None:
    """Generate a proforma contract payload for a specific node."""
    node = next((n for n in EXPANSION_NODES if n["id"] == node_id), None)
    if not node:
        return None

    seq = _next_contract_seq()
    ref = f"CTR-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{seq:03d}"

    contract = {
        "ref": ref,
        "node_id": node["id"],
        "node_name": node["name"],
        "city": node["city"],
        "district": node["district"],
        "entity": ENTITY,
        "siret": SIRET,
        "patent": PATENT,
        "setup_fee_eur": SETUP_FEE_EUR,
        "exclusivity_eur": EXCLUSIVITY_EUR,
        "total_licence_eur": LICENCE_FEE_EUR,
        "currency": "EUR",
        "status": "PROFORMA",
        "ts": datetime.now(timezone.utc).isoformat(),
    }

    try:
        TERRITORY_LOG_DIR.mkdir(parents=True, exist_ok=True)
        target = TERRITORY_LOG_DIR / f"{ref}.json"
        target.write_text(
            json.dumps(contract, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except OSError:
        pass

    return contract


def _next_contract_seq() -> int:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    TERRITORY_LOG_DIR.mkdir(parents=True, exist_ok=True)
    existing = sorted(TERRITORY_LOG_DIR.glob(f"CTR-{stamp}-*.json"))
    return len(existing) + 1
