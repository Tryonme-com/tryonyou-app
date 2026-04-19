"""
Treasury Monitor — Payout tracking & capital blindaje V11.

Tracks outbound fund movements (payouts) while shielding the sovereign
capital reserve.  All amounts resolved from env or defaults — never
hardcoded IBAN/account data.

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

PAYOUT_LOG_DIR = Path("/tmp/tryonyou_treasury")

DEFAULT_CAPITAL = 398_744.50
DEFAULT_PAYOUT_BUDGET = 1_600.00
DEFAULT_PAYOUT_SLOTS = 4
PAYOUT_AMOUNT_PER_SLOT = 400.00


def _env(key: str, fallback: str = "") -> str:
    return (os.getenv(key) or fallback).strip()


def _read_capital() -> float:
    raw = _env("TREASURY_CAPITAL_EUR", str(DEFAULT_CAPITAL))
    try:
        return float(raw)
    except ValueError:
        return DEFAULT_CAPITAL


def _read_payout_log() -> list[dict]:
    log_path = PAYOUT_LOG_DIR / "payouts.jsonl"
    if not log_path.exists():
        return []
    entries: list[dict] = []
    for line in log_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return entries


def _append_payout(entry: dict) -> None:
    PAYOUT_LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = PAYOUT_LOG_DIR / "payouts.jsonl"
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def get_treasury_status() -> dict:
    """Full treasury snapshot: capital, payouts executed, reserve."""
    capital = _read_capital()
    payouts = _read_payout_log()
    total_out = sum(p.get("amount_eur", 0.0) for p in payouts)
    reserve = round(capital - total_out, 2)
    budget = float(_env("TREASURY_PAYOUT_BUDGET_EUR", str(DEFAULT_PAYOUT_BUDGET)))

    return {
        "entity": ENTITY,
        "siret": SIRET,
        "siren": SIREN,
        "patent": PATENT,
        "capital_eur": capital,
        "total_payouts_eur": round(total_out, 2),
        "reserve_eur": reserve,
        "payout_budget_eur": budget,
        "payout_slots": DEFAULT_PAYOUT_SLOTS,
        "payout_amount_per_slot_eur": PAYOUT_AMOUNT_PER_SLOT,
        "payouts_executed": len(payouts),
        "capital_label": "Capital Social Blindado",
        "bank": "QONTO_BUSINESS",
        "ts": datetime.now(timezone.utc).isoformat(),
    }


def record_payout(
    amount_eur: float,
    recipient: str = "",
    concept: str = "operational",
) -> dict:
    """Record an outbound payout and return the updated entry."""
    entry = {
        "amount_eur": round(amount_eur, 2),
        "recipient": recipient or "operational",
        "concept": concept,
        "ts": datetime.now(timezone.utc).isoformat(),
        "entity": ENTITY,
        "siret": SIRET,
    }
    _append_payout(entry)
    return entry


def get_payouts_list() -> list[dict]:
    """Return all recorded payouts."""
    return _read_payout_log()
