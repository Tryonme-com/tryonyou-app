"""Gestor de cobros Falla V9 con memoria persistente.

Este modulo esta pensado para ser usado desde automatizaciones (webhook o cron)
y mantener un historico consistente de cobros sin duplicados.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any


CONCEPTOS_PERMITIDOS = {"cuota", "loteria", "evento"}
CONCEPTOS_ALIAS = {
    "cuota anual": "cuota",
    "cuota mensual": "cuota",
    "rifa": "loteria",
}


class DuplicateTransactionError(ValueError):
    """Error de transaccion ya registrada."""


def _round_money(value: float) -> float:
    return round(float(value), 2)


class GestorFallaV9:
    def __init__(
        self,
        comision_pct: float = 0.08,
        cuota_base: float = 50.0,
        memoria_path: str | Path = "billing/falla_memories.json",
    ) -> None:
        self.comision_pct = float(comision_pct)
        self.cuota_base = float(cuota_base)
        self.memoria_path = Path(memoria_path)
        self._memoria = self._cargar_memoria()

    def _default_memoria(self) -> dict[str, Any]:
        return {
            "version": 1,
            "comision_pct": self.comision_pct,
            "cuota_base": self.cuota_base,
            "saldos_pendientes": {},
            "transaccion_ids": [],
            "asientos": [],
        }

    def _cargar_memoria(self) -> dict[str, Any]:
        if not self.memoria_path.exists():
            return self._default_memoria()
        try:
            contenido = json.loads(self.memoria_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return self._default_memoria()

        memoria = self._default_memoria()
        memoria.update({k: v for k, v in contenido.items() if k in memoria})
        if not isinstance(memoria["saldos_pendientes"], dict):
            memoria["saldos_pendientes"] = {}
        if not isinstance(memoria["transaccion_ids"], list):
            memoria["transaccion_ids"] = []
        if not isinstance(memoria["asientos"], list):
            memoria["asientos"] = []
        return memoria

    def guardar_memoria(self) -> None:
        self.memoria_path.parent.mkdir(parents=True, exist_ok=True)
        self._memoria["comision_pct"] = self.comision_pct
        self._memoria["cuota_base"] = self.cuota_base
        serializado = json.dumps(self._memoria, ensure_ascii=False, indent=2)
        self.memoria_path.write_text(serializado + "\n", encoding="utf-8")

    def _normalizar_nombre(self, nombre: str) -> str:
        limpio = (nombre or "").strip()
        if not limpio:
            raise ValueError("Nombre de fallero vacio")
        return limpio.upper()

    def _normalizar_concepto(self, concepto: str) -> str:
        limpio = (concepto or "").strip().lower()
        if not limpio:
            raise ValueError("Concepto vacio")
        normalizado = CONCEPTOS_ALIAS.get(limpio, limpio)
        if normalizado not in CONCEPTOS_PERMITIDOS:
            raise ValueError(
                "Concepto invalido. Usa uno de: cuota, loteria, evento"
            )
        return normalizado

    def _normalizar_id_fallero(self, fallero_id: str | None, nombre: str) -> str:
        if fallero_id and str(fallero_id).strip():
            return str(fallero_id).strip().upper()
        digest = hashlib.sha256(nombre.encode("utf-8")).hexdigest()[:12]
        return f"FAL-{digest.upper()}"

    def _build_transaccion_id(
        self,
        transaccion_id: str | None,
        *,
        fecha: str,
        fallero_id: str,
        concepto: str,
        bruto: float,
    ) -> str:
        if transaccion_id and str(transaccion_id).strip():
            return str(transaccion_id).strip()
        base = f"{fecha}|{fallero_id}|{concepto}|{_round_money(bruto):.2f}"
        digest = hashlib.sha256(base.encode("utf-8")).hexdigest()[:20]
        return f"TX-{digest.upper()}"

    def ejecutar_cobro(
        self,
        nombre: str,
        bruto: float,
        concepto: str,
        *,
        fallero_id: str | None = None,
        transaccion_id: str | None = None,
        fecha: str | None = None,
    ) -> dict[str, Any]:
        fecha_valor = fecha or dt.date.today().isoformat()
        nombre_valor = self._normalizar_nombre(nombre)
        concepto_valor = self._normalizar_concepto(concepto)
        bruto_valor = _round_money(float(bruto))
        if bruto_valor <= 0:
            raise ValueError("El importe bruto debe ser mayor que 0")

        fallero_id_valor = self._normalizar_id_fallero(fallero_id, nombre_valor)
        tx_id = self._build_transaccion_id(
            transaccion_id,
            fecha=fecha_valor,
            fallero_id=fallero_id_valor,
            concepto=concepto_valor,
            bruto=bruto_valor,
        )
        if tx_id in self._memoria["transaccion_ids"]:
            raise DuplicateTransactionError(f"Transaccion duplicada: {tx_id}")

        comision = _round_money(bruto_valor * self.comision_pct)
        neto = _round_money(bruto_valor - comision)
        estado = (
            "Pendiente de regularizar"
            if bruto_valor < self.cuota_base
            else "Pagado"
        )

        saldo_anterior = _round_money(
            self._memoria["saldos_pendientes"].get(fallero_id_valor, 0.0)
        )
        saldo_actualizado = _round_money(
            max(0.0, saldo_anterior + self.cuota_base - bruto_valor)
        )
        self._memoria["saldos_pendientes"][fallero_id_valor] = saldo_actualizado

        asiento = {
            "fecha": fecha_valor,
            "id_fallero": fallero_id_valor,
            "fallero": nombre_valor,
            "concepto": concepto_valor,
            "importe_bruto": bruto_valor,
            "comision_aplicada": comision,
            "neto_resultante": neto,
            "saldo_pendiente": saldo_actualizado,
            "estado": estado,
            "transaccion_id": tx_id,
        }
        self._memoria["transaccion_ids"].append(tx_id)
        self._memoria["asientos"].append(asiento)
        return asiento

    def procesar_lote(self, registros: list[dict[str, Any]]) -> list[dict[str, Any]]:
        resultados: list[dict[str, Any]] = []
        for registro in registros:
            try:
                asiento = self.ejecutar_cobro(
                    nombre=str(registro.get("fallero_nombre") or registro.get("nombre") or ""),
                    bruto=float(
                        registro.get("importe_bruto")
                        if registro.get("importe_bruto") is not None
                        else registro.get("bruto", 0)
                    ),
                    concepto=str(registro.get("concepto") or ""),
                    fallero_id=registro.get("fallero_id"),
                    transaccion_id=(
                        registro.get("transaccion_id")
                        or registro.get("referencia")
                        or registro.get("id")
                    ),
                    fecha=registro.get("fecha"),
                )
                resultados.append(asiento)
            except DuplicateTransactionError as exc:
                resultados.append(
                    {
                        "estado": "DUPLICADO",
                        "error": str(exc),
                        "transaccion_id": registro.get("transaccion_id")
                        or registro.get("referencia")
                        or registro.get("id"),
                    }
                )
            except (TypeError, ValueError) as exc:
                resultados.append({"estado": "ERROR", "error": str(exc)})

        self.guardar_memoria()
        return resultados

    @property
    def memoria(self) -> dict[str, Any]:
        return self._memoria


def _parse_input_payload(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        if isinstance(data.get("registros"), list):
            return data["registros"]
        return [data]
    raise ValueError("El JSON de entrada debe ser objeto o lista")


def main() -> int:
    parser = argparse.ArgumentParser(description="Procesador de cobros Falla V9")
    parser.add_argument("--input", type=Path, help="Ruta al JSON de registros")
    parser.add_argument(
        "--memoria",
        type=Path,
        default=Path("billing/falla_memories.json"),
        help="Ruta del archivo de memoria persistente",
    )
    parser.add_argument(
        "--comision",
        type=float,
        default=0.08,
        help="Comision fija decimal (0.08 = 8 por ciento)",
    )
    parser.add_argument(
        "--cuota-base",
        type=float,
        default=50.0,
        help="Cuota minima esperada por transaccion",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Imprime salida en JSON con indentacion",
    )
    args = parser.parse_args()

    gestor = GestorFallaV9(
        comision_pct=args.comision,
        cuota_base=args.cuota_base,
        memoria_path=args.memoria,
    )

    if args.input:
        registros = _parse_input_payload(args.input)
    else:
        registros = [{"nombre": "Pau", "importe_bruto": 100.0, "concepto": "cuota"}]

    resultados = gestor.procesar_lote(registros)
    if args.pretty:
        print(json.dumps(resultados, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(resultados, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
