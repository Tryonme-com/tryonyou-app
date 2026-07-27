"""
Ledger soberano de pagos confirmados — fuente trazable para kill-switch y auditoría.

Canales:
- stripe_webhook → banco Stripe Paris EUR
- csv_bootstrap  → registro Lafayette (sin IBAN en CSV; canal operativo documentado)
- qonto_sync     → reservado

Patente: PCT/EP2025/067317
"""

from __future__ import annotations

import csv
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parent.parent
LEDGER_PATH = ROOT / "logs" / "sovereign_payments.jsonl"
CONTRACT_PATH = ROOT / "contrato_master_v10.json"
DEFAULT_CSV = ROOT / "registro_pagos_hoy.csv"

STRIPE_BANK_LABEL = "Stripe Paris EUR (cuenta FR / STRIPE_SECRET_KEY_FR)"
QONTO_BANK_LABEL = "Qonto (QONTO_API_KEY)"
CSV_BANK_LABEL = "Registro operativo Lafayette — sin IBAN en CSV (canal piloto DIV-*)"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _ledger_dir() -> Path:
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    return LEDGER_PATH.parent


def _read_entries() -> list[dict[str, Any]]:
    if not LEDGER_PATH.is_file():
        return []
    rows: list[dict[str, Any]] = []
    for line in LEDGER_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            rows.append(row)
    return rows


def _write_entry(entry: Mapping[str, Any]) -> dict[str, Any]:
    _ledger_dir()
    payload = dict(entry)
    with LEDGER_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
    return payload


def is_contract_signed() -> bool:
    env = (os.environ.get("CONTRACT_SIGNED") or "").strip().lower()
    if env in {"1", "true", "yes", "on"}:
        return True
    if env in {"0", "false", "no", "off"}:
        return False
    if not CONTRACT_PATH.is_file():
        return False
    try:
        data = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    block = data.get("contrato_master")
    if isinstance(block, dict) and "contrato_firmado" in block:
        return bool(block.get("contrato_firmado"))
    return bool(data.get("contrato_firmado"))


def record_payment(
    *,
    payment_id: str,
    importe_eur: float,
    canal: str,
    banco: str,
    estado: str = "CONFIRMADO",
    meta: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    pid = str(payment_id or "").strip()
    if not pid:
        raise ValueError("payment_id_required")
    amount = round(float(importe_eur) + 1e-9, 2)
    if amount <= 0:
        raise ValueError("importe_eur_must_be_positive")

    for row in _read_entries():
        if str(row.get("payment_id") or "") == pid:
            return row

    entry = {
        "payment_id": pid,
        "importe_eur": amount,
        "estado": estado,
        "canal": canal,
        "banco": banco,
        "contract_signed_at_record": is_contract_signed(),
        "confirmed_at": utc_now_iso(),
        "meta": dict(meta or {}),
    }
    return _write_entry(entry)


def bootstrap_csv_confirmed(csv_path: Path | None = None) -> dict[str, Any]:
    path = csv_path or DEFAULT_CSV
    if not path.is_file():
        return {"imported": 0, "skipped": 0, "source": str(path), "ok": False}

    imported = 0
    skipped = 0
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            estado = str(row.get("estado") or "").strip().upper()
            if estado not in {"CONFIRMADO", "CONFIRMED", "PAID"}:
                skipped += 1
                continue
            pid = str(row.get("id_transaccion") or row.get("payment_id") or "").strip()
            if not pid:
                skipped += 1
                continue
            raw_amount = str(row.get("importe_eur") or row.get("amount") or "0").replace(",", ".")
            try:
                amount = float(raw_amount)
            except ValueError:
                skipped += 1
                continue
            before = len(_read_entries())
            record_payment(
                payment_id=pid,
                importe_eur=amount,
                canal="csv_bootstrap",
                banco=CSV_BANK_LABEL,
                meta={
                    "fecha_hora": row.get("fecha_hora"),
                    "source_file": path.name,
                },
            )
            after = len(_read_entries())
            if after > before:
                imported += 1
            else:
                skipped += 1

    return {"imported": imported, "skipped": skipped, "source": str(path), "ok": True}


def record_stripe_webhook_event(event: Mapping[str, Any]) -> dict[str, Any] | None:
    etype = str(event.get("type") or "")
    data = (event.get("data") or {}).get("object") or {}
    if not isinstance(data, dict):
        return None

    if etype == "checkout.session.completed":
        if str(data.get("payment_status") or "").lower() not in {"paid", "no_payment_required"}:
            return None
        amount_cents = data.get("amount_total")
        if amount_cents is None:
            amount_cents = (data.get("amount_subtotal") or 0)
        amount = round(float(amount_cents or 0) / 100.0, 2)
        pid = str(data.get("id") or data.get("payment_intent") or "")
        return record_payment(
            payment_id=pid,
            importe_eur=amount,
            canal="stripe_webhook",
            banco=STRIPE_BANK_LABEL,
            meta={
                "event_type": etype,
                "payment_status": data.get("payment_status"),
                "metadata": data.get("metadata") or {},
            },
        )

    if etype == "payment_intent.succeeded":
        amount = round(float(data.get("amount_received") or data.get("amount") or 0) / 100.0, 2)
        pid = str(data.get("id") or "")
        return record_payment(
            payment_id=pid,
            importe_eur=amount,
            canal="stripe_webhook",
            banco=STRIPE_BANK_LABEL,
            meta={"event_type": etype, "currency": data.get("currency")},
        )

    return None


def ledger_summary() -> dict[str, Any]:
    bootstrap_csv_confirmed()
    entries = _read_entries()
    confirmed = [e for e in entries if str(e.get("estado") or "").upper() in {"CONFIRMADO", "CONFIRMED", "PAID"}]
    total = round(sum(float(e.get("importe_eur") or 0) for e in confirmed) + 1e-9, 2)

    by_bank: dict[str, float] = {}
    for e in confirmed:
        bank = str(e.get("banco") or "desconocido")
        by_bank[bank] = round(by_bank.get(bank, 0.0) + float(e.get("importe_eur") or 0), 2)

    return {
        "ok": True,
        "confirmed_count": len(confirmed),
        "confirmed_total_eur": total,
        "by_bank": by_bank,
        "contract_signed": is_contract_signed(),
        "ledger_path": str(LEDGER_PATH),
        "entries_sample": confirmed[-5:],
    }


def treasury_status_payload() -> dict[str, Any]:
    summary = ledger_summary()
    return {
        "ok": True,
        "protocol": "sovereign_payment_ledger_v1",
        "contract_signed": summary["contract_signed"],
        "confirmed_total_eur": summary["confirmed_total_eur"],
        "confirmed_count": summary["confirmed_count"],
        "by_bank": summary["by_bank"],
        "note": (
            "Liquidez confirmada en ledger. Stripe/Qonto en /health.validation "
            "reflejan saldo bancario en vivo cuando hay claves."
        ),
    }
