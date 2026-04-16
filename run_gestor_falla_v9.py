from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from gestor_falla_v9 import (
    CobroDuplicadoError,
    GestorFallaError,
    GestorFallaV9,
    MemoryStore,
)


def _normalizar_registro(raw: dict[str, Any], idx: int) -> dict[str, Any]:
    nombre = raw.get("nombre") or raw.get("fallero") or raw.get("payer_name")
    concepto = raw.get("concepto") or raw.get("tipo") or raw.get("charge_type")
    bruto = (
        raw.get("importe_bruto")
        if raw.get("importe_bruto") is not None
        else raw.get("bruto", raw.get("amount"))
    )
    transaccion_id = (
        raw.get("transaccion_id")
        or raw.get("id_transaccion")
        or raw.get("transaction_id")
    )
    fecha = raw.get("fecha") or raw.get("date")
    fallero_id = raw.get("id_fallero") or raw.get("fallero_id") or raw.get("member_id")

    if not nombre:
        nombre = f"FALLERO_{idx}"
    if not concepto:
        concepto = "cuota"

    return {
        "nombre": nombre,
        "concepto": concepto,
        "importe_bruto": bruto,
        "transaccion_id": transaccion_id,
        "fecha": fecha,
        "id_fallero": fallero_id,
    }


def _cargar_registros(path: Path) -> list[dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict) and "registros" in data:
            data = data["registros"]
        if not isinstance(data, list):
            raise ValueError("El JSON de entrada debe ser una lista o {'registros': [...]} ")
        if not all(isinstance(item, dict) for item in data):
            raise ValueError("Todos los elementos de entrada deben ser objetos JSON.")
        return data

    if suffix == ".csv":
        with path.open("r", encoding="utf-8", newline="") as fh:
            return list(csv.DictReader(fh))

    raise ValueError("Formato no soportado. Usa .json o .csv")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Procesa cobros de falla desde webhook/schedule."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Ruta a archivo de entrada (.json o .csv) con registros.",
    )
    parser.add_argument(
        "--memory-path",
        default="memories/falla_memories.json",
        help="Ruta del storage de memoria para ledger/saldos/dedupe.",
    )
    parser.add_argument(
        "--commission-pct",
        type=float,
        default=0.08,
        help="Porcentaje de comisión fija (por ejemplo 0.08 para 8%).",
    )
    parser.add_argument(
        "--cuota-base",
        type=float,
        default=50.0,
        help="Cuota mínima para marcar un cobro como regularizado.",
    )
    parser.add_argument(
        "--output",
        default="memories/falla_asientos_ultimos.json",
        help="Ruta de salida con asientos procesados del lote actual.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)
    if not input_path.exists():
        print(f"❌ Entrada no encontrada: {input_path}")
        return 1

    try:
        registros_raw = _cargar_registros(input_path)
    except Exception as exc:
        print(f"❌ Error cargando entrada: {exc}")
        return 1

    gestor = GestorFallaV9(
        comision_pct=args.commission_pct,
        cuota_base=args.cuota_base,
        memory_store=MemoryStore(args.memory_path),
    )
    procesados: list[dict[str, Any]] = []
    duplicados = 0
    rechazados = 0

    for idx, raw in enumerate(registros_raw, start=1):
        registro = _normalizar_registro(raw, idx)
        try:
            asiento = gestor.ejecutar_cobro(
                nombre=str(registro["nombre"]),
                bruto=registro["importe_bruto"],
                concepto=str(registro["concepto"]),
                fallero_id=registro.get("id_fallero"),
                transaccion_id=registro.get("transaccion_id"),
                fecha=registro.get("fecha"),
            )
            procesados.append(asiento)
        except CobroDuplicadoError:
            duplicados += 1
        except GestorFallaError:
            rechazados += 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps({"asientos": procesados}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(
        "✅ Procesamiento finalizado | "
        f"procesados={len(procesados)} duplicados={duplicados} rechazados={rechazados}"
    )
    print(f"📒 Asientos guardados en: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
