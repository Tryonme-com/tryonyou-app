#!/usr/bin/env python3
"""
Auditoría de comisión sobre ventas confirmadas Lafayette.

Entradas soportadas:
1) CSV con columnas: fecha_hora,importe_eur,estado,id_transaccion
2) JSON con lista de objetos y campos equivalentes.

Salida:
- volumen_total_confirmado_eur
- comision_8pct_eur
- total_con_comision_eur
"""

from __future__ import annotations

import argparse
import csv
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Iterable

COMMISSION_RATE = Decimal("0.08")
MONEY_QUANT = Decimal("0.01")


def q_money(value: Decimal) -> Decimal:
    return value.quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


def _to_decimal(raw: object) -> Decimal:
    text = str(raw).strip().replace(",", ".")
    return Decimal(text)


def _is_confirmed(status: object) -> bool:
    return str(status or "").strip().upper() in {"CONFIRMADO", "CONFIRMED", "PAID"}


def _iter_amounts_from_csv(path: Path) -> Iterable[Decimal]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"importe_eur", "estado"}
        missing = required.difference(reader.fieldnames or [])
        if missing:
            joined = ", ".join(sorted(missing))
            raise ValueError(f"CSV inválido: faltan columnas requeridas: {joined}")
        for row in reader:
            if _is_confirmed(row.get("estado")):
                yield _to_decimal(row.get("importe_eur"))


def _iter_amounts_from_json(path: Path) -> Iterable[Decimal]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("JSON inválido: se esperaba una lista de ventas.")
    for row in payload:
        if not isinstance(row, dict):
            continue
        if _is_confirmed(row.get("estado")):
            raw = row.get("importe_eur")
            if raw is None:
                continue
            yield _to_decimal(raw)


def _load_confirmed_amounts(path: Path) -> list[Decimal]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return list(_iter_amounts_from_csv(path))
    if suffix == ".json":
        return list(_iter_amounts_from_json(path))
    raise ValueError("Formato no soportado. Usa .csv o .json")


def run_audit(input_path: Path) -> dict[str, object]:
    amounts = _load_confirmed_amounts(input_path)
    volume = q_money(sum(amounts, Decimal("0")))
    commission = q_money(volume * COMMISSION_RATE)
    total_with_commission = q_money(volume + commission)
    return {
        "source": str(input_path),
        "currency": "EUR",
        "commission_rate": float(COMMISSION_RATE),
        "confirmed_transactions": len(amounts),
        "volumen_total_confirmado_eur": float(volume),
        "comision_8pct_eur": float(commission),
        "total_con_comision_eur": float(total_with_commission),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Auditoría 8% sobre ventas confirmadas.")
    parser.add_argument(
        "--input",
        default="registro_pagos_hoy.csv",
        help="Ruta a CSV/JSON de ventas confirmadas (default: registro_pagos_hoy.csv)",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Imprime JSON con indentación legible.",
    )
    args = parser.parse_args()
    source = Path(args.input).resolve()
    if not source.is_file():
        raise SystemExit(f"No existe el archivo de entrada: {source}")
    result = run_audit(source)
    if args.pretty:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
