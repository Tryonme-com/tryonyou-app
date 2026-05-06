#!/usr/bin/env python3
"""
Gestor Falla V9: comisiones, deuda y memoria contable.

Procesa cobros de falleros desde webhook, CSV o JSON y mantiene un ledger
persistente en JSON para evitar duplicados.

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import tempfile
import unicodedata
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Iterable


MONEY_QUANT = Decimal("0.01")
RATE_QUANT = Decimal("0.0001")
DEFAULT_COMISION_PCT = Decimal("0.08")
DEFAULT_CUOTA_BASE = Decimal("50.00")
VALID_CONCEPTS = {"cuota", "loteria", "evento"}
MEMORY_VERSION = "falla_v9"
ESTADO_PAGADO = "PAGADO"
ESTADO_PENDIENTE = "PENDIENTE DE REGULARIZAR"


class GestorFallaError(ValueError):
    """Error de validacion del gestor de cobros Falla."""


def q_money(value: Decimal) -> Decimal:
    return value.quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


def _decimal_from(raw: object, field_name: str, *, allow_zero: bool = False) -> Decimal:
    text = str(raw).strip().replace("EUR", "").replace("€", "").replace(",", ".")
    if not text:
        raise GestorFallaError(f"{field_name} es obligatorio.")
    try:
        value = Decimal(text)
    except InvalidOperation as exc:
        raise GestorFallaError(f"{field_name} debe ser numerico.") from exc
    if value < 0 or (value == 0 and not allow_zero):
        raise GestorFallaError(f"{field_name} debe ser mayor que cero.")
    return q_money(value)


def _rate_from(raw: object, field_name: str) -> Decimal:
    text = str(raw).strip().replace("%", "").replace(",", ".")
    if not text:
        raise GestorFallaError(f"{field_name} es obligatorio.")
    try:
        value = Decimal(text)
    except InvalidOperation as exc:
        raise GestorFallaError(f"{field_name} debe ser numerico.") from exc
    if value <= 0:
        raise GestorFallaError(f"{field_name} debe ser mayor que cero.")
    if value >= 1:
        value = value / Decimal("100")
    return value.quantize(RATE_QUANT, rounding=ROUND_HALF_UP)


def _money_text(value: Decimal) -> str:
    return f"{q_money(value):.2f}"


def _rate_text(value: Decimal) -> str:
    return f"{value.quantize(RATE_QUANT, rounding=ROUND_HALF_UP):.4f}"


def _strip_accents(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def _normalize_concept(concepto: object) -> str:
    raw = str(concepto or "").strip()
    if not raw:
        raise GestorFallaError("concepto es obligatorio.")
    normalized = _strip_accents(raw).casefold()
    token = normalized.split()[0]
    if token not in VALID_CONCEPTS:
        valid = ", ".join(sorted(VALID_CONCEPTS))
        raise GestorFallaError(f"concepto invalido: {raw!r}. Usa uno de: {valid}.")
    return token


def _fallero_id(nombre: str, explicit_id: object | None = None) -> str:
    if explicit_id is not None and str(explicit_id).strip():
        return str(explicit_id).strip().upper()
    normalized = _strip_accents(nombre).upper()
    safe = "".join(ch if ch.isalnum() else "_" for ch in normalized)
    fallero_id = "_".join(part for part in safe.split("_") if part)
    if not fallero_id:
        raise GestorFallaError("nombre del fallero es obligatorio.")
    return fallero_id


def _empty_memory() -> dict[str, Any]:
    return {
        "version": MEMORY_VERSION,
        "currency": "EUR",
        "transacciones": [],
        "saldos": {},
    }


class GestorFallaV9:
    def __init__(
        self,
        comision_pct: Decimal | float | str = DEFAULT_COMISION_PCT,
        cuota_base: Decimal | float | str = DEFAULT_CUOTA_BASE,
        memoria_path: str | Path | None = None,
    ) -> None:
        self.comision_pct = _rate_from(comision_pct, "comision_pct")
        self.cuota_base = _decimal_from(cuota_base, "cuota_base")
        default_path = os.environ.get("FALLA_MEMORIA_PATH", "falla_memories.json")
        self.memoria_path = Path(memoria_path or default_path)

    def ejecutar_cobro(
        self,
        nombre: str,
        bruto: Decimal | float | str,
        concepto: str,
        *,
        id_transaccion: str | None = None,
        fecha: str | None = None,
        fallero_id: str | None = None,
    ) -> dict[str, Any]:
        nombre_limpio = str(nombre or "").strip()
        if not nombre_limpio:
            raise GestorFallaError("nombre del fallero es obligatorio.")

        fecha_asiento = str(fecha or date.today().isoformat()).strip()
        if not fecha_asiento:
            raise GestorFallaError("fecha es obligatoria.")
        concepto_normalizado = _normalize_concept(concepto)
        bruto_dec = _decimal_from(bruto, "bruto")
        id_fallero = _fallero_id(nombre_limpio, fallero_id)
        tx_id = str(id_transaccion or "").strip() or self._derive_transaction_id(
            fecha_asiento, id_fallero, concepto_normalizado, bruto_dec
        )

        memoria = self._load_memory()
        existing = self._find_transaction(memoria, tx_id)
        if existing is not None:
            duplicate = dict(existing)
            duplicate["duplicado"] = True
            return duplicate

        comision = q_money(bruto_dec * self.comision_pct)
        neto = q_money(bruto_dec - comision)
        deuda_delta = q_money(self.cuota_base - bruto_dec)
        deuda_generada = deuda_delta if deuda_delta > 0 else Decimal("0.00")
        estado = ESTADO_PAGADO if bruto_dec >= self.cuota_base else ESTADO_PENDIENTE

        asiento = {
            "fecha": fecha_asiento,
            "id_transaccion": tx_id,
            "id_fallero": id_fallero,
            "fallero": nombre_limpio.upper(),
            "concepto": concepto_normalizado,
            "importe_bruto_eur": _money_text(bruto_dec),
            "comision_pct": _rate_text(self.comision_pct),
            "comision_eur": _money_text(comision),
            "neto_resultante_eur": _money_text(neto),
            "cuota_base_eur": _money_text(self.cuota_base),
            "deuda_generada_eur": _money_text(deuda_generada),
            "estado": estado,
            "duplicado": False,
        }

        memoria["transacciones"].append(asiento)
        saldo_pendiente = self._update_balance(
            memoria, asiento, bruto_dec, comision, neto, deuda_delta
        )
        asiento["saldo_pendiente_eur"] = _money_text(saldo_pendiente)
        self._save_memory(memoria)
        return asiento

    def procesar_registros(self, registros: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
        return [self.ejecutar_cobro(**_coerce_record(row)) for row in registros]

    def _derive_transaction_id(
        self, fecha: str, id_fallero: str, concepto: str, bruto: Decimal
    ) -> str:
        seed = f"{fecha}|{id_fallero}|{concepto}|{_money_text(bruto)}"
        digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16].upper()
        return f"FALLA-{digest}"

    def _load_memory(self) -> dict[str, Any]:
        if not self.memoria_path.exists():
            return _empty_memory()
        payload = json.loads(self.memoria_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise GestorFallaError("memoria invalida: se esperaba un objeto JSON.")
        payload.setdefault("version", MEMORY_VERSION)
        payload.setdefault("currency", "EUR")
        payload.setdefault("transacciones", [])
        payload.setdefault("saldos", {})
        if not isinstance(payload["transacciones"], list) or not isinstance(
            payload["saldos"], dict
        ):
            raise GestorFallaError("memoria invalida: transacciones/saldos mal formados.")
        return payload

    def _save_memory(self, memoria: dict[str, Any]) -> None:
        self.memoria_path.parent.mkdir(parents=True, exist_ok=True)
        serialized = json.dumps(memoria, ensure_ascii=False, indent=2, sort_keys=True)
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=str(self.memoria_path.parent),
            delete=False,
        ) as handle:
            handle.write(serialized)
            handle.write("\n")
            tmp_name = handle.name
        os.replace(tmp_name, self.memoria_path)

    def _find_transaction(
        self, memoria: dict[str, Any], id_transaccion: str
    ) -> dict[str, Any] | None:
        for row in memoria.get("transacciones", []):
            if isinstance(row, dict) and row.get("id_transaccion") == id_transaccion:
                return row
        return None

    def _update_balance(
        self,
        memoria: dict[str, Any],
        asiento: dict[str, Any],
        bruto: Decimal,
        comision: Decimal,
        neto: Decimal,
        deuda_delta: Decimal,
    ) -> Decimal:
        id_fallero = asiento["id_fallero"]
        saldos = memoria["saldos"]
        current = saldos.get(id_fallero, {})
        saldo_pendiente = _decimal_from(
            current.get("saldo_pendiente_eur", "0.00"),
            "saldo_pendiente_eur",
            allow_zero=True,
        )
        if deuda_delta < 0:
            saldo_pendiente = max(Decimal("0.00"), q_money(saldo_pendiente + deuda_delta))
        else:
            saldo_pendiente = q_money(saldo_pendiente + deuda_delta)

        saldos[id_fallero] = {
            "fallero": asiento["fallero"],
            "saldo_pendiente_eur": _money_text(saldo_pendiente),
            "total_bruto_eur": _money_text(
                _sum_money(current.get("total_bruto_eur", "0.00"), bruto)
            ),
            "total_comisiones_eur": _money_text(
                _sum_money(current.get("total_comisiones_eur", "0.00"), comision)
            ),
            "total_neto_falla_eur": _money_text(
                _sum_money(current.get("total_neto_falla_eur", "0.00"), neto)
            ),
            "ultimo_estado": asiento["estado"],
            "ultima_transaccion": asiento["id_transaccion"],
        }
        return saldo_pendiente


def _sum_money(existing: object, increment: Decimal) -> Decimal:
    current = _decimal_from(existing, "importe acumulado", allow_zero=True)
    return q_money(current + increment)


def _coerce_record(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "nombre": row.get("nombre") or row.get("fallero") or row.get("name"),
        "bruto": (
            row.get("bruto")
            or row.get("importe_bruto")
            or row.get("importe_eur")
            or row.get("amount_eur")
        ),
        "concepto": row.get("concepto") or row.get("tipo_cobro"),
        "id_transaccion": (
            row.get("id_transaccion") or row.get("transaction_id") or row.get("stripe_id")
        ),
        "fecha": row.get("fecha") or row.get("fecha_hora") or row.get("created_at"),
        "fallero_id": row.get("fallero_id") or row.get("id_fallero"),
    }


def load_records(path: Path) -> list[dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        with path.open("r", encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))
    if suffix == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            payload = payload.get("records") or payload.get("cobros") or [payload]
        if not isinstance(payload, list):
            raise GestorFallaError("JSON invalido: se esperaba objeto o lista.")
        return [row for row in payload if isinstance(row, dict)]
    raise GestorFallaError("Formato no soportado. Usa .csv o .json.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Procesa cobros Falla V9.")
    parser.add_argument("--input", help="CSV/JSON con registros de cobro.")
    parser.add_argument("--memoria", help="Ruta de memoria JSON persistente.")
    parser.add_argument("--comision-pct", default=str(DEFAULT_COMISION_PCT))
    parser.add_argument("--cuota-base", default=str(DEFAULT_CUOTA_BASE))
    parser.add_argument("--nombre", help="Nombre del fallero para un cobro directo.")
    parser.add_argument("--bruto", help="Importe bruto para un cobro directo.")
    parser.add_argument("--concepto", help="Concepto: cuota, loteria/loteria o evento.")
    parser.add_argument("--id-transaccion", help="ID externo del cobro.")
    parser.add_argument("--fallero-id", help="ID estable del fallero.")
    parser.add_argument("--fecha", help="Fecha contable; por defecto hoy en ISO.")
    parser.add_argument("--pretty", action="store_true", help="Imprime JSON indentado.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    gestor = GestorFallaV9(
        comision_pct=args.comision_pct,
        cuota_base=args.cuota_base,
        memoria_path=args.memoria,
    )

    try:
        if args.input:
            result: dict[str, Any] | list[dict[str, Any]] = gestor.procesar_registros(
                load_records(Path(args.input))
            )
        else:
            missing = [
                name
                for name in ("nombre", "bruto", "concepto")
                if not getattr(args, name)
            ]
            if missing:
                parser.error(
                    "faltan argumentos para cobro directo: " + ", ".join(missing)
                )
            result = gestor.ejecutar_cobro(
                args.nombre,
                args.bruto,
                args.concepto,
                id_transaccion=args.id_transaccion,
                fecha=args.fecha,
                fallero_id=args.fallero_id,
            )
    except GestorFallaError as exc:
        parser.exit(2, f"Error: {exc}\n")

    print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
