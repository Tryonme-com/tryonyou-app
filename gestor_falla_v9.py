#!/usr/bin/env python3
"""
Gestor Falla V9 - cobros, comision fija y memoria de deuda.

Uso rapido:
  python3 gestor_falla_v9.py --demo
  python3 gestor_falla_v9.py --input cobros.json --memory data/falla_memorias.json

Variables opcionales:
  FALLA_COMISION_PCT=0.08
  FALLA_CUOTA_BASE=50
  FALLA_MEMORY_PATH=data/falla_memorias.json

Patente: PCT/EP2025/067317 - Bajo Protocolo de Soberania V10 - Founder: Ruben
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
import unicodedata
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Iterable


ALLOWED_CONCEPTS = {"cuota", "loteria", "evento"}
DEFAULT_MEMORY_PATH = Path("data/falla_memorias.json")
MONEY = Decimal("0.01")


class GestorFallaError(ValueError):
    """Error funcional del gestor de cobros Falla."""


class DuplicateCobroError(GestorFallaError):
    """La memoria ya contiene este cobro."""


def _today_iso() -> str:
    return dt.date.today().isoformat()


def _normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.strip().lower())
    without_accents = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", without_accents)


def _slug(value: str) -> str:
    normalized = _normalize_text(value)
    return re.sub(r"[^a-z0-9]+", "-", normalized).strip("-") or "fallero"


def _money(value: Any, *, field: str) -> Decimal:
    if isinstance(value, Decimal):
        amount = value
    else:
        raw = str(value).strip().replace("\u20ac", "").replace(",", ".")
        try:
            amount = Decimal(raw)
        except (InvalidOperation, ValueError) as exc:
            raise GestorFallaError(f"{field} debe ser un numero valido") from exc
    if amount < Decimal("0"):
        raise GestorFallaError(f"{field} no puede ser negativo")
    return amount.quantize(MONEY, rounding=ROUND_HALF_UP)


def _pct(value: Any) -> Decimal:
    raw = str(value).strip().replace("%", "").replace(",", ".")
    try:
        pct = Decimal(raw)
    except (InvalidOperation, ValueError) as exc:
        raise GestorFallaError("comision_pct debe ser un numero valido") from exc
    if pct < Decimal("0"):
        raise GestorFallaError("comision_pct no puede ser negativo")
    if pct > Decimal("1"):
        pct = pct / Decimal("100")
    if pct > Decimal("1"):
        raise GestorFallaError("comision_pct debe estar entre 0 y 1, o entre 0 y 100")
    return pct.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


def _decimal_to_float(value: Decimal) -> float:
    return float(value.quantize(MONEY, rounding=ROUND_HALF_UP))


@dataclass(frozen=True)
class CobroEntrada:
    nombre: str
    bruto: Decimal
    concepto: str
    id_fallero: str
    referencia_externa: str | None = None
    fecha: str | None = None

    @classmethod
    def from_mapping(cls, row: dict[str, Any]) -> "CobroEntrada":
        nombre = str(row.get("nombre") or row.get("fallero") or "").strip()
        concepto = str(row.get("concepto") or row.get("tipo") or "").strip()
        bruto_raw = row.get("bruto", row.get("importe_bruto", row.get("monto")))
        id_fallero = str(row.get("id_fallero") or row.get("fallero_id") or "").strip()
        referencia = row.get("referencia_externa", row.get("external_reference"))
        fecha = row.get("fecha")
        return cls.validated(
            nombre=nombre,
            bruto=bruto_raw,
            concepto=concepto,
            id_fallero=id_fallero or None,
            referencia_externa=str(referencia).strip() if referencia else None,
            fecha=str(fecha).strip() if fecha else None,
        )

    @classmethod
    def validated(
        cls,
        *,
        nombre: str,
        bruto: Any,
        concepto: str,
        id_fallero: str | None = None,
        referencia_externa: str | None = None,
        fecha: str | None = None,
    ) -> "CobroEntrada":
        clean_name = nombre.strip()
        if len(clean_name) < 2:
            raise GestorFallaError("nombre/fallero es obligatorio")

        clean_concept = _normalize_text(concepto)
        if clean_concept not in ALLOWED_CONCEPTS:
            allowed = ", ".join(sorted(ALLOWED_CONCEPTS))
            raise GestorFallaError(f"concepto invalido: {concepto!r}; permitidos: {allowed}")

        amount = _money(bruto, field="importe_bruto")
        clean_id = (id_fallero or _slug(clean_name)).strip()
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{1,63}", clean_id):
            raise GestorFallaError("id_fallero debe tener 2-64 caracteres seguros")

        if fecha:
            try:
                dt.date.fromisoformat(fecha)
            except ValueError as exc:
                raise GestorFallaError("fecha debe usar formato YYYY-MM-DD") from exc

        return cls(
            nombre=clean_name,
            bruto=amount,
            concepto=clean_concept,
            id_fallero=clean_id,
            referencia_externa=referencia_externa or None,
            fecha=fecha or _today_iso(),
        )


class FallaMemoryStore:
    def __init__(self, path: Path | str = DEFAULT_MEMORY_PATH):
        self.path = Path(path)

    def load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"version": 1, "falleros": {}, "transacciones": []}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise GestorFallaError(f"memoria JSON corrupta: {self.path}") from exc
        if not isinstance(data, dict):
            raise GestorFallaError("la memoria debe ser un objeto JSON")
        data.setdefault("version", 1)
        data.setdefault("falleros", {})
        data.setdefault("transacciones", [])
        return data

    def save(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(
            json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        tmp.replace(self.path)


class GestorFallaV9:
    def __init__(
        self,
        comision_pct: Any = None,
        cuota_base: Any = None,
        memory_path: Path | str | None = None,
    ):
        self.comision_pct = _pct(
            comision_pct if comision_pct is not None else os.getenv("FALLA_COMISION_PCT", "0.08")
        )
        self.cuota_base = _money(
            cuota_base if cuota_base is not None else os.getenv("FALLA_CUOTA_BASE", "50"),
            field="cuota_base",
        )
        self.store = FallaMemoryStore(
            memory_path or os.getenv("FALLA_MEMORY_PATH") or DEFAULT_MEMORY_PATH
        )

    def ejecutar_cobro(
        self,
        nombre: str,
        bruto: Any,
        concepto: str,
        *,
        id_fallero: str | None = None,
        referencia_externa: str | None = None,
        fecha: str | None = None,
    ) -> dict[str, Any]:
        entrada = CobroEntrada.validated(
            nombre=nombre,
            bruto=bruto,
            concepto=concepto,
            id_fallero=id_fallero,
            referencia_externa=referencia_externa,
            fecha=fecha,
        )
        memory = self.store.load()
        asiento = self._build_asiento(entrada, memory)
        memory["transacciones"].append(asiento)
        memory["falleros"][entrada.id_fallero] = {
            "id_fallero": entrada.id_fallero,
            "nombre": entrada.nombre.upper(),
            "saldo_pendiente": asiento["saldo_pendiente"],
            "actualizado": asiento["fecha"],
        }
        self.store.save(memory)
        return asiento

    def procesar_lote(self, rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
        accepted: list[dict[str, Any]] = []
        duplicates: list[dict[str, Any]] = []
        errors: list[dict[str, Any]] = []

        for idx, row in enumerate(rows, start=1):
            try:
                entrada = CobroEntrada.from_mapping(row)
                accepted.append(
                    self.ejecutar_cobro(
                        entrada.nombre,
                        entrada.bruto,
                        entrada.concepto,
                        id_fallero=entrada.id_fallero,
                        referencia_externa=entrada.referencia_externa,
                        fecha=entrada.fecha,
                    )
                )
            except DuplicateCobroError as exc:
                duplicates.append({"row": idx, "error": str(exc), "input": row})
            except GestorFallaError as exc:
                errors.append({"row": idx, "error": str(exc), "input": row})

        return {"accepted": accepted, "duplicates": duplicates, "errors": errors}

    def _build_asiento(self, entrada: CobroEntrada, memory: dict[str, Any]) -> dict[str, Any]:
        fingerprint = self._fingerprint(entrada)
        for existing in memory.get("transacciones", []):
            if not isinstance(existing, dict):
                continue
            if existing.get("fingerprint") == fingerprint:
                raise DuplicateCobroError("cobro duplicado por fingerprint")
            if entrada.referencia_externa and existing.get("referencia_externa") == entrada.referencia_externa:
                raise DuplicateCobroError("cobro duplicado por referencia_externa")

        comision = (entrada.bruto * self.comision_pct).quantize(MONEY, rounding=ROUND_HALF_UP)
        neto = (entrada.bruto - comision).quantize(MONEY, rounding=ROUND_HALF_UP)
        previous_debt = self._previous_debt(memory, entrada.id_fallero)
        saldo = self._next_debt(previous_debt, entrada)
        estado = "PAGADO" if entrada.bruto >= self.cuota_base else "Pendiente de regularizar"

        return {
            "fecha": entrada.fecha,
            "id_fallero": entrada.id_fallero,
            "fallero": entrada.nombre.upper(),
            "concepto": entrada.concepto,
            "importe_bruto": _decimal_to_float(entrada.bruto),
            "comision_pct": float(self.comision_pct),
            "comision_aplicada": _decimal_to_float(comision),
            "neto_resultante": _decimal_to_float(neto),
            "saldo_pendiente": _decimal_to_float(saldo),
            "estado": estado,
            "referencia_externa": entrada.referencia_externa,
            "fingerprint": fingerprint,
        }

    def _next_debt(self, previous_debt: Decimal, entrada: CobroEntrada) -> Decimal:
        if entrada.concepto != "cuota":
            return previous_debt
        diff = self.cuota_base - entrada.bruto
        if diff > Decimal("0"):
            return (previous_debt + diff).quantize(MONEY, rounding=ROUND_HALF_UP)
        return max(Decimal("0"), previous_debt + diff).quantize(MONEY, rounding=ROUND_HALF_UP)

    def _previous_debt(self, memory: dict[str, Any], id_fallero: str) -> Decimal:
        fallero = memory.get("falleros", {}).get(id_fallero, {})
        return _money(fallero.get("saldo_pendiente", 0), field="saldo_pendiente")

    def _fingerprint(self, entrada: CobroEntrada) -> str:
        raw = "|".join(
            [
                entrada.fecha or "",
                entrada.id_fallero,
                entrada.concepto,
                str(entrada.bruto),
                entrada.referencia_externa or "",
            ]
        )
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _load_input(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    if text.startswith("["):
        data = json.loads(text)
        if not isinstance(data, list):
            raise GestorFallaError("el JSON de entrada debe ser una lista de cobros")
        return data
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def _demo_rows() -> list[dict[str, Any]]:
    return [
        {
            "id_fallero": "FALLA-PAU",
            "nombre": "Pau",
            "bruto": 100.0,
            "concepto": "cuota",
            "referencia_externa": f"demo-{_today_iso()}-pau",
            "fecha": _today_iso(),
        }
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Procesa cobros Falla con comision y memoria.")
    parser.add_argument("--input", type=Path, help="JSON array o JSONL con cobros de entrada.")
    parser.add_argument("--memory", type=Path, default=None, help="Ruta de memoria JSON.")
    parser.add_argument("--commission", type=str, default=None, help="Comision: 0.08 u 8.")
    parser.add_argument("--cuota", type=str, default=None, help="Cuota minima/base.")
    parser.add_argument("--demo", action="store_true", help="Procesa un cobro de ejemplo.")
    args = parser.parse_args(argv)

    if not args.input and not args.demo:
        parser.error("usa --input o --demo")

    rows = _demo_rows() if args.demo else _load_input(args.input)
    gestor = GestorFallaV9(
        comision_pct=args.commission,
        cuota_base=args.cuota,
        memory_path=args.memory,
    )
    result = gestor.procesar_lote(rows)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
