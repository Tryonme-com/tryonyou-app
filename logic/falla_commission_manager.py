from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Any


DEFAULT_COMMISSION_RATE = Decimal("0.08")
DEFAULT_MINIMUM_QUOTA = Decimal("50.00")
VALID_CONCEPT_TYPES = ("cuota", "loteria", "evento")
MONEY_QUANT = Decimal("0.01")


class FallaPaymentError(ValueError):
    """Error de validación para entradas de cobro Falla."""


def _money(value: Any, field_name: str) -> Decimal:
    if isinstance(value, Decimal):
        raw = value
    else:
        normalized = str(value if value is not None else "").strip()
        normalized = normalized.replace("€", "").replace("EUR", "").replace("eur", "").replace(",", ".")
        if not normalized:
            raise FallaPaymentError(f"{field_name}_required")
        try:
            raw = Decimal(normalized)
        except (InvalidOperation, ValueError) as exc:
            raise FallaPaymentError(f"{field_name}_invalid") from exc
    if raw < 0:
        raise FallaPaymentError(f"{field_name}_negative")
    return raw.quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


def _rate(value: Any, field_name: str) -> Decimal:
    normalized = str(value if value is not None else "").strip().replace("%", "").replace(",", ".")
    if not normalized:
        raise FallaPaymentError(f"{field_name}_required")
    try:
        raw = Decimal(normalized)
    except (InvalidOperation, ValueError) as exc:
        raise FallaPaymentError(f"{field_name}_invalid") from exc
    if raw < 0:
        raise FallaPaymentError(f"{field_name}_negative")
    if raw > 1:
        raw = raw / Decimal("100")
    if raw > 1:
        raise FallaPaymentError(f"{field_name}_invalid")
    return raw.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


def _today_iso() -> str:
    return date.today().isoformat()


def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slug(value: str) -> str:
    return "_".join(str(value).strip().upper().split())


def _format_eur(value: Decimal) -> str:
    return f"{value.quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)} EUR"


def _first_present(payload: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in payload and payload[key] not in (None, ""):
            return payload[key]
    return None


def resolve_concept_type(concept: Any) -> str:
    raw = str(concept or "").strip().lower()
    if not raw:
        raise FallaPaymentError("concepto_required")
    normalized = raw.replace("í", "i").replace("é", "e").replace("ó", "o")
    for concept_type in VALID_CONCEPT_TYPES:
        if normalized == concept_type or normalized.startswith(f"{concept_type} "):
            return concept_type
    raise FallaPaymentError("concepto_invalid")


@dataclass(frozen=True)
class FallaPaymentInput:
    fallero: str
    importe_bruto: Decimal
    concepto: str
    concepto_tipo: str
    transaction_id: str
    fecha: str
    fallero_id: str


def normalize_payment_input(payload: dict[str, Any]) -> FallaPaymentInput:
    fallero = str(
        payload.get("fallero")
        or payload.get("nombre")
        or payload.get("name")
        or payload.get("customer_name")
        or ""
    ).strip()
    if not fallero:
        raise FallaPaymentError("fallero_required")

    concepto = str(payload.get("concepto") or payload.get("concept") or "").strip()
    concepto_tipo = resolve_concept_type(concepto)
    bruto = _money(_first_present(payload, "importe_bruto", "bruto", "importe", "amount", "amount_eur"), "importe_bruto")
    transaction_id = str(
        payload.get("transaction_id")
        or payload.get("id_transaccion")
        or payload.get("payment_id")
        or payload.get("id")
        or ""
    ).strip()
    if not transaction_id:
        transaction_id = f"FALLA-{_slug(fallero)}-{_slug(concepto)}-{bruto}"

    fecha = str(payload.get("fecha") or payload.get("date") or _today_iso()).strip()
    fallero_id = str(payload.get("fallero_id") or payload.get("id_fallero") or "").strip()
    if not fallero_id:
        fallero_id = f"FALLERO-{_slug(fallero)}"

    return FallaPaymentInput(
        fallero=fallero,
        importe_bruto=bruto,
        concepto=concepto,
        concepto_tipo=concepto_tipo,
        transaction_id=transaction_id,
        fecha=fecha,
        fallero_id=fallero_id,
    )


class JsonFallaMemoryStore:
    def __init__(self, path: str | os.PathLike[str] | None = None):
        default_path = os.getenv("FALLA_MEMORY_PATH", "/tmp/tryonyou_falla_memories.json")
        self.path = Path(path or default_path)

    def load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"fallers": {}, "transactions": []}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise FallaPaymentError("memory_store_invalid_json") from exc
        if not isinstance(data, dict):
            raise FallaPaymentError("memory_store_invalid")
        data.setdefault("fallers", {})
        data.setdefault("transactions", [])
        return data

    def save(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(f"{self.path.suffix}.tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        tmp.replace(self.path)


class GestorFallaV9:
    def __init__(
        self,
        comision_pct: Decimal | float | str | None = None,
        cuota_base: Decimal | float | str | None = None,
        memory_store: JsonFallaMemoryStore | None = None,
    ):
        env_rate = os.getenv("FALLA_COMISION_PCT")
        env_quota = os.getenv("FALLA_CUOTA_BASE")
        self.comision_pct = _rate(comision_pct if comision_pct is not None else env_rate or DEFAULT_COMMISSION_RATE, "comision_pct")
        self.cuota_base = _money(cuota_base if cuota_base is not None else env_quota or DEFAULT_MINIMUM_QUOTA, "cuota_base")
        self.memory_store = memory_store or JsonFallaMemoryStore()

    def ejecutar_cobro(self, payload: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
        raw_payload = dict(payload or {})
        raw_payload.update(kwargs)
        payment = normalize_payment_input(raw_payload)
        memory = self.memory_store.load()

        for existing in memory["transactions"]:
            if existing.get("transaction_id") == payment.transaction_id:
                duplicate = dict(existing)
                duplicate["duplicado"] = True
                duplicate["status"] = "duplicate"
                return duplicate

        comision = (payment.importe_bruto * self.comision_pct).quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)
        neto = (payment.importe_bruto - comision).quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)

        fallers = memory["fallers"]
        faller_state = fallers.setdefault(
            payment.fallero_id,
            {
                "fallero_id": payment.fallero_id,
                "fallero": payment.fallero.upper(),
                "saldo_pendiente_eur": "0.00",
            },
        )
        previous_pending = _money(faller_state.get("saldo_pendiente_eur", "0.00"), "saldo_pendiente_eur")
        due_for_concept = self.cuota_base if payment.concepto_tipo == "cuota" else Decimal("0.00")
        saldo_pendiente = max(previous_pending + due_for_concept - payment.importe_bruto, Decimal("0.00"))
        estado = "PAGADO" if payment.importe_bruto >= self.cuota_base else "PENDIENTE_DE_REGULARIZAR"

        asiento = {
            "fecha": payment.fecha,
            "transaction_id": payment.transaction_id,
            "fallero_id": payment.fallero_id,
            "fallero": payment.fallero.upper(),
            "concepto": payment.concepto,
            "concepto_tipo": payment.concepto_tipo,
            "importe_bruto_eur": _format_eur(payment.importe_bruto),
            "comision_pct": str((self.comision_pct * Decimal("100")).quantize(Decimal("0.01"))),
            "comision_aplicada_eur": _format_eur(comision),
            "neto_falla_eur": _format_eur(neto),
            "saldo_pendiente_eur": _format_eur(saldo_pendiente),
            "estado": estado,
            "duplicado": False,
            "status": "ok",
            "created_at": _now_utc_iso(),
        }

        faller_state.update(
            {
                "fallero": payment.fallero.upper(),
                "saldo_pendiente_eur": str(saldo_pendiente.quantize(MONEY_QUANT)),
                "updated_at": asiento["created_at"],
            }
        )
        memory["transactions"].append(asiento)
        self.memory_store.save(memory)
        return asiento

    def resumen(self) -> dict[str, Any]:
        memory = self.memory_store.load()
        total_bruto = Decimal("0.00")
        total_comision = Decimal("0.00")
        total_neto = Decimal("0.00")
        pendientes = 0
        for tx in memory.get("transactions", []):
            total_bruto += _money(tx.get("importe_bruto_eur", "0"), "importe_bruto_eur")
            total_comision += _money(tx.get("comision_aplicada_eur", "0"), "comision_aplicada_eur")
            total_neto += _money(tx.get("neto_falla_eur", "0"), "neto_falla_eur")
            if tx.get("estado") == "PENDIENTE_DE_REGULARIZAR":
                pendientes += 1
        return {
            "status": "ok",
            "transactions_count": len(memory.get("transactions", [])),
            "fallers_count": len(memory.get("fallers", {})),
            "pendientes_regularizar": pendientes,
            "total_bruto_eur": _format_eur(total_bruto),
            "total_comision_eur": _format_eur(total_comision),
            "total_neto_falla_eur": _format_eur(total_neto),
        }

    def procesar_registros(self, registros: list[dict[str, Any]]) -> dict[str, Any]:
        asientos = [self.ejecutar_cobro(registro) for registro in registros]
        resumen = self.resumen()
        return {
            "status": "ok",
            "processed_count": len(asientos),
            "asientos": asientos,
            "resumen": resumen,
        }
