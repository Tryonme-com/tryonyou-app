#!/usr/bin/env python3
"""
Gestor de cobros Falla V9 con memoria persistente y deduplicación.

Uso rápido:
  python3 gestor_falla_v9.py --input pagos.json --pretty

Formato de entrada (lista JSON):
[
  {
    "id_fallero": "F001",
    "nombre": "Pau",
    "concepto": "cuota",
    "importe_bruto": 100.0,
    "referencia_externa": "stripe_evt_123"
  }
]
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any

MONEY_QUANT = Decimal("0.01")
CONCEPTOS_VALIDOS = {"cuota", "loteria", "evento"}
DEFAULT_MEMORY_PATH = Path("data/falla_memorias.json")


def q_money(value: Decimal) -> Decimal:
    return value.quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


def _to_decimal(value: object) -> Decimal:
    text = str(value).strip().replace(",", ".")
    return Decimal(text)


def _normalize_text(value: object) -> str:
    return str(value or "").strip()


class GestorFallaV9:
    def __init__(
        self,
        comision_pct: Decimal = Decimal("0.08"),
        cuota_base: Decimal = Decimal("50.00"),
        memory_path: Path = DEFAULT_MEMORY_PATH,
    ) -> None:
        self.comision_pct = Decimal(str(comision_pct))
        self.cuota_base = q_money(cuota_base)
        self.memory_path = memory_path
        self._state = self._load_state()

    def _load_state(self) -> dict[str, Any]:
        if not self.memory_path.exists():
            return {
                "schema_version": 1,
                "updated_at": None,
                "processed_fingerprints": [],
                "processed_references": [],
                "saldos_pendientes": {},
                "asientos": [],
            }
        payload = json.loads(self.memory_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("Memoria inválida: se esperaba objeto JSON.")
        payload.setdefault("schema_version", 1)
        payload.setdefault("updated_at", None)
        payload.setdefault("processed_fingerprints", [])
        payload.setdefault("processed_references", [])
        payload.setdefault("saldos_pendientes", {})
        payload.setdefault("asientos", [])
        return payload

    def _save_state(self) -> None:
        self.memory_path.parent.mkdir(parents=True, exist_ok=True)
        self._state["updated_at"] = dt.datetime.now(dt.timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        self.memory_path.write_text(
            json.dumps(self._state, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def _make_fingerprint(
        self,
        id_fallero: str,
        nombre: str,
        concepto: str,
        importe_bruto: Decimal,
        referencia_externa: str,
    ) -> str:
        raw = "|".join(
            [
                id_fallero.upper(),
                nombre.upper(),
                concepto.lower(),
                f"{q_money(importe_bruto)}",
                referencia_externa,
            ]
        )
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _validate_concepto(self, concepto: str) -> None:
        if concepto.lower() not in CONCEPTOS_VALIDOS:
            allowed = ", ".join(sorted(CONCEPTOS_VALIDOS))
            raise ValueError(f"Concepto inválido: '{concepto}'. Permitidos: {allowed}")

    def _validate_nombre(self, nombre: str) -> None:
        if len(nombre.strip()) < 2:
            raise ValueError("Nombre de fallero inválido: mínimo 2 caracteres.")

    def _record_exists(self, fingerprint: str) -> bool:
        return fingerprint in set(self._state["processed_fingerprints"])

    def _reference_exists(self, referencia_externa: str) -> bool:
        if not referencia_externa:
            return False
        return referencia_externa in set(self._state["processed_references"])

    def ejecutar_cobro(self, registro: dict[str, Any]) -> dict[str, Any]:
        fecha = dt.date.today().strftime("%Y-%m-%d")
        id_fallero = _normalize_text(registro.get("id_fallero"))
        nombre = _normalize_text(registro.get("nombre"))
        concepto = _normalize_text(registro.get("concepto")).lower()
        referencia_externa = _normalize_text(registro.get("referencia_externa"))
        bruto = q_money(_to_decimal(registro.get("importe_bruto", "0")))

        if not id_fallero:
            raise ValueError("Falta id_fallero.")
        self._validate_nombre(nombre)
        self._validate_concepto(concepto)
        if bruto <= Decimal("0"):
            raise ValueError("El importe_bruto debe ser mayor que 0.")

        fingerprint = self._make_fingerprint(
            id_fallero=id_fallero,
            nombre=nombre,
            concepto=concepto,
            importe_bruto=bruto,
            referencia_externa=referencia_externa,
        )
        if self._record_exists(fingerprint) or self._reference_exists(referencia_externa):
            return {
                "status": "duplicado",
                "id_fallero": id_fallero,
                "referencia_externa": referencia_externa or None,
                "fingerprint": fingerprint,
            }

        comision = q_money(bruto * self.comision_pct)
        neto = q_money(bruto - comision)
        estado = "PAGADO" if bruto >= self.cuota_base else "Pendiente de regularizar"

        saldo_prev = q_money(_to_decimal(self._state["saldos_pendientes"].get(id_fallero, "0")))
        if bruto < self.cuota_base:
            saldo_nuevo = q_money(saldo_prev + (self.cuota_base - bruto))
        else:
            saldo_nuevo = q_money(max(Decimal("0"), saldo_prev - bruto))

        self._state["saldos_pendientes"][id_fallero] = float(saldo_nuevo)

        asiento = {
            "fecha": fecha,
            "id_fallero": id_fallero,
            "fallero": nombre.upper(),
            "concepto": concepto,
            "importe_bruto_eur": float(bruto),
            "comision_aplicada_eur": float(comision),
            "importe_neto_eur": float(neto),
            "estado": estado,
            "referencia_externa": referencia_externa or None,
            "saldo_pendiente_eur": float(saldo_nuevo),
            "fingerprint": fingerprint,
        }

        self._state["processed_fingerprints"].append(fingerprint)
        if referencia_externa:
            self._state["processed_references"].append(referencia_externa)
        self._state["asientos"].append(asiento)
        self._save_state()
        return {"status": "ok", "asiento": asiento}

    def procesar_lote(self, registros: list[dict[str, Any]]) -> dict[str, Any]:
        resultados: list[dict[str, Any]] = []
        for registro in registros:
            resultados.append(self.ejecutar_cobro(registro))
        procesados = sum(1 for r in resultados if r.get("status") == "ok")
        duplicados = sum(1 for r in resultados if r.get("status") == "duplicado")
        return {
            "procesados": procesados,
            "duplicados": duplicados,
            "total": len(resultados),
            "resultados": resultados,
        }


def _load_input(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        payload = [payload]
    if not isinstance(payload, list):
        raise ValueError("Entrada inválida: se esperaba lista JSON de cobros.")
    out: list[dict[str, Any]] = []
    for row in payload:
        if isinstance(row, dict):
            out.append(row)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Procesador de cobros Falla V9.")
    parser.add_argument(
        "--input",
        required=True,
        help="Ruta al JSON de registros de cobro (objeto o lista).",
    )
    parser.add_argument(
        "--memory",
        default=str(DEFAULT_MEMORY_PATH),
        help="Ruta del fichero de memoria persistente.",
    )
    parser.add_argument(
        "--comision-pct",
        default="0.08",
        help="Comisión fija en decimal (ej: 0.08 para 8%).",
    )
    parser.add_argument(
        "--cuota-base",
        default="50.00",
        help="Cuota mínima para marcar impago parcial.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Imprime salida con indentación legible.",
    )
    args = parser.parse_args()

    source = Path(args.input).resolve()
    if not source.is_file():
        raise SystemExit(f"No existe el archivo de entrada: {source}")

    gestor = GestorFallaV9(
        comision_pct=_to_decimal(args.comision_pct),
        cuota_base=_to_decimal(args.cuota_base),
        memory_path=Path(args.memory),
    )
    registros = _load_input(source)
    result = gestor.procesar_lote(registros)

    if args.pretty:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
