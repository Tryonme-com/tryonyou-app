"""
Falla commission manager V9.

Processes Falla payment records with a fixed commission, keeps an auditable
JSONL memory and rejects duplicate charges by transaction id/fingerprint.

Patente: PCT/EP2025/067317
Bajo Protocolo de Soberania V10 - Founder: Ruben
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Iterable

DEFAULT_COMMISSION_RATE = Decimal("0.08")
DEFAULT_MINIMUM_FEE_EUR = Decimal("50.00")
MONEY_QUANT = Decimal("0.01")
VALID_CONCEPTS = {"cuota", "loteria", "evento"}


def _money(value: Decimal) -> Decimal:
    return value.quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


def _money_float(value: Decimal) -> float:
    return float(_money(value))


def _read_decimal_env(key: str, fallback: Decimal) -> Decimal:
    raw = (os.getenv(key) or "").strip().replace(",", ".")
    if not raw:
        return fallback
    try:
        return Decimal(raw)
    except InvalidOperation:
        return fallback


def commission_rate() -> Decimal:
    return _normalize_rate(_read_decimal_env("FALLA_COMMISSION_PCT", DEFAULT_COMMISSION_RATE))


def minimum_fee_eur() -> Decimal:
    return _read_decimal_env("FALLA_CUOTA_BASE_EUR", DEFAULT_MINIMUM_FEE_EUR)


def _normalize_rate(rate: Decimal) -> Decimal:
    if rate > 1:
        return rate / Decimal("100")
    return rate


def memories_path() -> Path:
    raw = (os.getenv("FALLA_MEMORIES_PATH") or "").strip()
    if raw:
        return Path(raw)
    return Path("/tmp/tryonyou_falla/memories.jsonl")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _today_iso() -> str:
    return date.today().isoformat()


def _normalize_name(raw: object) -> str:
    name = str(raw or "").strip()
    if not name:
        raise ValueError("fallero_required")
    return " ".join(name.split()).upper()


def _normalize_concept(raw: object) -> tuple[str, bool]:
    concept = " ".join(str(raw or "").strip().split())
    if not concept:
        raise ValueError("concepto_required")
    token = concept.lower().split()[0]
    return concept, token in VALID_CONCEPTS


def _to_decimal_amount(raw: object) -> Decimal:
    if raw is None:
        raise ValueError("importe_bruto_required")
    text = str(raw).strip().replace("EUR", "").replace("eur", "").replace("€", "")
    text = text.replace(",", ".")
    try:
        amount = Decimal(text)
    except InvalidOperation as exc:
        raise ValueError("importe_bruto_invalid") from exc
    if amount < 0:
        raise ValueError("importe_bruto_negative")
    return _money(amount)


def _stable_transaction_id(
    *,
    provided: object,
    source: str,
    payment_date: str,
    fallero: str,
    concepto: str,
    gross: Decimal,
) -> str:
    explicit = str(provided or "").strip()
    if explicit:
        return explicit
    fingerprint = "|".join(
        [
            source,
            payment_date,
            fallero,
            concepto.lower(),
            str(_money(gross)),
        ]
    )
    return "falla_" + hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()[:24]


def _read_entries(path: Path | None = None) -> list[dict[str, Any]]:
    target = path or memories_path()
    if not target.exists():
        return []
    entries: list[dict[str, Any]] = []
    for line in target.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            entries.append(row)
    return entries


def _append_entry(entry: dict[str, Any], path: Path | None = None) -> None:
    target = path or memories_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")


def _fallero_totals(entries: Iterable[dict[str, Any]], fallero: str) -> dict[str, Decimal]:
    gross = Decimal("0")
    commission = Decimal("0")
    net = Decimal("0")
    for entry in entries:
        if str(entry.get("fallero", "")).strip().upper() != fallero:
            continue
        if entry.get("duplicate") is True:
            continue
        gross += Decimal(str(entry.get("importe_bruto_eur", "0")))
        commission += Decimal(str(entry.get("comision_eur", "0")))
        net += Decimal(str(entry.get("neto_falla_eur", "0")))
    return {
        "importe_bruto_eur": _money(gross),
        "comision_eur": _money(commission),
        "neto_falla_eur": _money(net),
    }


def process_falla_payment(payload: dict[str, Any], path: Path | None = None) -> dict[str, Any]:
    """
    Process one payment and persist the accounting entry unless it is a duplicate.

    Supported input aliases:
      - fallero / nombre / name
      - importe_bruto / bruto / amount_eur / importe_eur
      - concepto / concept
      - transaction_id / id_transaccion / payment_id
      - fecha / payment_date
    """
    if not isinstance(payload, dict):
        raise ValueError("payload_must_be_object")

    source = str(payload.get("source") or payload.get("fuente") or "api").strip() or "api"
    fallero = _normalize_name(payload.get("fallero") or payload.get("nombre") or payload.get("name"))
    concepto, concepto_valido = _normalize_concept(payload.get("concepto") or payload.get("concept"))
    gross = _to_decimal_amount(
        payload.get("importe_bruto")
        if payload.get("importe_bruto") is not None
        else payload.get("bruto")
        if payload.get("bruto") is not None
        else payload.get("amount_eur")
        if payload.get("amount_eur") is not None
        else payload.get("importe_eur")
    )
    payment_date = str(payload.get("fecha") or payload.get("payment_date") or _today_iso()).strip()
    rate = commission_rate()
    minimum = _read_decimal_env("FALLA_CUOTA_BASE_EUR", DEFAULT_MINIMUM_FEE_EUR)
    commission = _money(gross * rate)
    net = _money(gross - commission)
    pending = _money(max(Decimal("0"), minimum - gross))
    status = "PAGADO" if pending == 0 else "PENDIENTE_DE_REGULARIZAR"
    transaction_id = _stable_transaction_id(
        provided=payload.get("transaction_id") or payload.get("id_transaccion") or payload.get("payment_id"),
        source=source,
        payment_date=payment_date,
        fallero=fallero,
        concepto=concepto,
        gross=gross,
    )

    existing = _read_entries(path)
    for entry in existing:
        if str(entry.get("transaction_id", "")).strip() == transaction_id:
            return {
                "status": "duplicate",
                "duplicate": True,
                "transaction_id": transaction_id,
                "asiento": entry,
                "message": "Cobro ya registrado en Memories.",
            }

    totals_before = _fallero_totals(existing, fallero)
    saldo_pendiente = pending
    entry = {
        "event": "falla.payment",
        "fecha": payment_date,
        "processed_at": _utc_now(),
        "transaction_id": transaction_id,
        "source": source,
        "fallero": fallero,
        "fallero_id": str(payload.get("fallero_id") or payload.get("id_fallero") or "").strip(),
        "concepto": concepto,
        "concepto_valido": concepto_valido,
        "importe_bruto_eur": _money_float(gross),
        "commission_rate": float(rate),
        "comision_eur": _money_float(commission),
        "neto_falla_eur": _money_float(net),
        "cuota_minima_eur": _money_float(minimum),
        "saldo_pendiente_eur": _money_float(saldo_pendiente),
        "estado": status,
        "historico_fallero": {
            "importe_bruto_eur": _money_float(totals_before["importe_bruto_eur"] + gross),
            "comision_eur": _money_float(totals_before["comision_eur"] + commission),
            "neto_falla_eur": _money_float(totals_before["neto_falla_eur"] + net),
        },
    }
    _append_entry(entry, path)
    return {
        "status": "ok",
        "duplicate": False,
        "transaction_id": transaction_id,
        "asiento": entry,
    }


def process_falla_batch(payload: dict[str, Any], path: Path | None = None) -> dict[str, Any]:
    records = payload.get("records") if isinstance(payload, dict) else None
    if records is None:
        records = payload.get("cobros") if isinstance(payload, dict) else None
    if records is None:
        records = [payload]
    if not isinstance(records, list):
        raise ValueError("records_must_be_list")

    processed: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for index, record in enumerate(records):
        try:
            processed.append(process_falla_payment(record, path=path))
        except Exception as exc:
            errors.append({"index": index, "error": str(exc)})

    return {
        "status": "ok" if not errors else "partial_error",
        "processed_count": len(processed),
        "duplicates_count": sum(1 for item in processed if item.get("duplicate") is True),
        "errors_count": len(errors),
        "processed": processed,
        "errors": errors,
        "commission_rate": float(commission_rate()),
        "cuota_base_eur": _money_float(minimum_fee_eur()),
        "memory_path": str(path or memories_path()),
    }


def get_falla_memory(path: Path | None = None) -> dict[str, Any]:
    entries = _read_entries(path)
    totals = {
        "importe_bruto_eur": 0.0,
        "comision_eur": 0.0,
        "neto_falla_eur": 0.0,
        "pendiente_regularizar_count": 0,
    }
    falleros: dict[str, dict[str, float]] = {}
    for entry in entries:
        if entry.get("duplicate") is True:
            continue
        totals["importe_bruto_eur"] = round(totals["importe_bruto_eur"] + float(entry.get("importe_bruto_eur", 0)), 2)
        totals["comision_eur"] = round(totals["comision_eur"] + float(entry.get("comision_eur", 0)), 2)
        totals["neto_falla_eur"] = round(totals["neto_falla_eur"] + float(entry.get("neto_falla_eur", 0)), 2)
        if entry.get("estado") == "PENDIENTE_DE_REGULARIZAR":
            totals["pendiente_regularizar_count"] += 1
        fallero = str(entry.get("fallero", "")).strip() or "UNKNOWN"
        bucket = falleros.setdefault(
            fallero,
            {"importe_bruto_eur": 0.0, "comision_eur": 0.0, "neto_falla_eur": 0.0},
        )
        bucket["importe_bruto_eur"] = round(bucket["importe_bruto_eur"] + float(entry.get("importe_bruto_eur", 0)), 2)
        bucket["comision_eur"] = round(bucket["comision_eur"] + float(entry.get("comision_eur", 0)), 2)
        bucket["neto_falla_eur"] = round(bucket["neto_falla_eur"] + float(entry.get("neto_falla_eur", 0)), 2)

    return {
        "status": "ok",
        "entries_count": len(entries),
        "totals": totals,
        "falleros": falleros,
        "entries": entries,
        "memory_path": str(path or memories_path()),
    }
