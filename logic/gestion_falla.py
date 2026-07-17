"""Gestión idempotente de cobros y comisiones para comisiones falleras.

El histórico JSON actúa como la memoria operativa y el libro JSONL se regenera
desde esa fuente de verdad. Esto permite que los reintentos de un webhook no
dupliquen cobros ni asientos contables.

Patente: PCT/EP2025/067317
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import hashlib
import json
import os
import tempfile
import unicodedata
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Iterable, Mapping


COMISION_PCT_PREDETERMINADA = Decimal("0.08")
CUOTA_MINIMA_PREDETERMINADA = Decimal("50.00")
CONCEPTOS_PERMITIDOS = frozenset({"cuota", "loteria", "evento"})
ESTADO_PAGADO = "PAGADO"
ESTADO_PENDIENTE = "PENDIENTE DE REGULARIZAR"
_CENTIMOS = Decimal("0.01")


def _texto_normalizado(value: str) -> str:
    text = unicodedata.normalize("NFKD", value.strip().casefold())
    return "".join(char for char in text if not unicodedata.combining(char))


def _decimal_monetario(value: Any, *, campo: str) -> Decimal:
    if isinstance(value, bool):
        raise ValueError(f"{campo} debe ser un importe numérico")
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError(f"{campo} debe ser un importe numérico") from exc
    if not amount.is_finite():
        raise ValueError(f"{campo} debe ser un importe finito")
    return amount.quantize(_CENTIMOS, rounding=ROUND_HALF_UP)


def _importe_json(value: Decimal) -> float:
    return float(value.quantize(_CENTIMOS, rounding=ROUND_HALF_UP))


class GestorFallaV9:
    """Procesa cobros con comisión configurable y memoria local durable."""

    def __init__(
        self,
        comision_pct: float | Decimal = COMISION_PCT_PREDETERMINADA,
        cuota_base: float | Decimal = CUOTA_MINIMA_PREDETERMINADA,
        *,
        memoria_path: str | os.PathLike[str] | None = None,
        libro_path: str | os.PathLike[str] | None = None,
    ) -> None:
        self.comision_pct = _decimal_monetario(
            comision_pct, campo="comision_pct"
        )
        self.cuota_base = _decimal_monetario(cuota_base, campo="cuota_base")
        if not Decimal("0") <= self.comision_pct <= Decimal("1"):
            raise ValueError("comision_pct debe estar entre 0 y 1")
        if self.cuota_base <= 0:
            raise ValueError("cuota_base debe ser mayor que cero")

        self.memoria_path = Path(
            memoria_path
            or os.getenv("FALLA_MEMORIES_PATH", "data/falla_memories.json")
        )
        self.libro_path = Path(
            libro_path
            or os.getenv("FALLA_LEDGER_PATH", "logs/falla_cobros.jsonl")
        )

    def ejecutar_cobro(
        self,
        nombre: str,
        bruto: Any,
        concepto: str,
        *,
        referencia: str | None = None,
        fallero_id: str | None = None,
        fecha: str | None = None,
    ) -> dict[str, Any]:
        """Valida, calcula, concilia y registra un único cobro."""
        nombre_limpio = self._validar_nombre(nombre)
        concepto_limpio, categoria = self._validar_concepto(concepto)
        importe_bruto = _decimal_monetario(bruto, campo="bruto")
        if importe_bruto <= 0:
            raise ValueError("bruto debe ser mayor que cero")

        fecha_iso = self._validar_fecha(fecha)
        resolved_fallero_id = self._resolver_fallero_id(nombre_limpio, fallero_id)
        resolved_reference = self._resolver_referencia(
            referencia,
            fecha_iso,
            resolved_fallero_id,
            concepto_limpio,
            importe_bruto,
        )

        self.memoria_path.parent.mkdir(parents=True, exist_ok=True)
        lock_path = self.memoria_path.with_suffix(self.memoria_path.suffix + ".lock")
        with lock_path.open("a+", encoding="utf-8") as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            try:
                memoria = self._cargar_memoria()
                existente = memoria["cobros"].get(resolved_reference)
                if existente is not None:
                    self._sincronizar_libro(memoria)
                    return {**existente, "duplicado": True}

                fallero = memoria["falleros"].get(resolved_fallero_id)
                if fallero is None:
                    saldo_inicial = (
                        self.cuota_base if categoria == "cuota" else Decimal("0")
                    )
                    fallero = {
                        "nombre": nombre_limpio,
                        "saldo_pendiente": _importe_json(saldo_inicial),
                    }
                    memoria["falleros"][resolved_fallero_id] = fallero
                elif _texto_normalizado(fallero["nombre"]) != _texto_normalizado(
                    nombre_limpio
                ):
                    raise ValueError(
                        f"fallero_id {resolved_fallero_id!r} pertenece a otro nombre"
                    )

                saldo_anterior = _decimal_monetario(
                    fallero.get("saldo_pendiente", 0),
                    campo="saldo_pendiente",
                )
                saldo_pendiente = max(Decimal("0"), saldo_anterior - importe_bruto)
                comision = (importe_bruto * self.comision_pct).quantize(
                    _CENTIMOS, rounding=ROUND_HALF_UP
                )
                neto = importe_bruto - comision
                estado = (
                    ESTADO_PAGADO
                    if importe_bruto >= self.cuota_base
                    else ESTADO_PENDIENTE
                )

                asiento = {
                    "fecha": fecha_iso,
                    "referencia": resolved_reference,
                    "fallero_id": resolved_fallero_id,
                    "fallero": nombre_limpio.upper(),
                    "concepto": concepto_limpio,
                    "importe_bruto": _importe_json(importe_bruto),
                    "comision_pct": _importe_json(self.comision_pct),
                    "comision_aplicada": _importe_json(comision),
                    "neto_resultante": _importe_json(neto),
                    "saldo_pendiente": _importe_json(saldo_pendiente),
                    "estado": estado,
                }
                fallero["saldo_pendiente"] = asiento["saldo_pendiente"]
                memoria["cobros"][resolved_reference] = asiento
                memoria["actualizado_en"] = dt.datetime.now(dt.timezone.utc).isoformat()

                self._guardar_memoria(memoria)
                self._sincronizar_libro(memoria)
                return {**asiento, "duplicado": False}
            finally:
                fcntl.flock(lock.fileno(), fcntl.LOCK_UN)

    def procesar_pago(
        self,
        fallero_nombre: str,
        importe_bruto: Any,
        concepto: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Alias compatible con el prototipo histórico guardado en Memories."""
        return self.ejecutar_cobro(
            fallero_nombre, importe_bruto, concepto, **kwargs
        )

    def procesar_registros(
        self, registros: Iterable[Mapping[str, Any]]
    ) -> list[dict[str, Any]]:
        """Normaliza payloads previsibles de webhook, Make.com o exportaciones."""
        resultados: list[dict[str, Any]] = []
        for registro in registros:
            nombre = registro.get("nombre", registro.get("fallero"))
            bruto = registro.get(
                "bruto", registro.get("importe", registro.get("monto"))
            )
            concepto = registro.get("concepto", registro.get("tipo"))
            if nombre is None or bruto is None or concepto is None:
                raise ValueError(
                    "cada registro requiere nombre/fallero, bruto/importe/monto "
                    "y concepto/tipo"
                )
            resultados.append(
                self.ejecutar_cobro(
                    str(nombre),
                    bruto,
                    str(concepto),
                    referencia=self._valor_opcional(
                        registro, "referencia", "payment_id", "id"
                    ),
                    fallero_id=self._valor_opcional(registro, "fallero_id"),
                    fecha=self._valor_opcional(registro, "fecha"),
                )
            )
        return resultados

    def obtener_resumen(self) -> list[dict[str, Any]]:
        """Devuelve el histórico contable en orden de inserción."""
        memoria = self._cargar_memoria()
        return list(memoria["cobros"].values())

    @staticmethod
    def _valor_opcional(registro: Mapping[str, Any], *keys: str) -> str | None:
        for key in keys:
            value = registro.get(key)
            if value is not None and str(value).strip():
                return str(value)
        return None

    @staticmethod
    def _validar_nombre(nombre: str) -> str:
        if not isinstance(nombre, str):
            raise ValueError("nombre debe ser texto")
        limpio = " ".join(nombre.strip().split())
        if len(limpio) < 2 or not any(char.isalpha() for char in limpio):
            raise ValueError("nombre de fallero no válido")
        return limpio

    @staticmethod
    def _validar_concepto(concepto: str) -> tuple[str, str]:
        if not isinstance(concepto, str):
            raise ValueError("concepto debe ser texto")
        limpio = " ".join(concepto.strip().split())
        normalizado = _texto_normalizado(limpio)
        categoria = next(
            (
                permitida
                for permitida in CONCEPTOS_PERMITIDOS
                if normalizado == permitida or normalizado.startswith(f"{permitida} ")
            ),
            None,
        )
        if categoria is None:
            permitidos = ", ".join(sorted(CONCEPTOS_PERMITIDOS))
            raise ValueError(f"concepto no válido; categorías permitidas: {permitidos}")
        return limpio, categoria

    @staticmethod
    def _validar_fecha(fecha: str | None) -> str:
        if fecha is None:
            return dt.datetime.now(dt.timezone.utc).date().isoformat()
        try:
            return dt.date.fromisoformat(fecha).isoformat()
        except (TypeError, ValueError) as exc:
            raise ValueError("fecha debe usar el formato ISO AAAA-MM-DD") from exc

    @staticmethod
    def _resolver_fallero_id(nombre: str, fallero_id: str | None) -> str:
        if fallero_id is not None:
            limpio = fallero_id.strip()
            if not limpio or len(limpio) > 80:
                raise ValueError("fallero_id no válido")
            return limpio
        digest = hashlib.sha256(_texto_normalizado(nombre).encode("utf-8")).hexdigest()
        return f"FAL-{digest[:12].upper()}"

    @staticmethod
    def _resolver_referencia(
        referencia: str | None,
        fecha: str,
        fallero_id: str,
        concepto: str,
        bruto: Decimal,
    ) -> str:
        if referencia is not None:
            limpia = referencia.strip()
            if not limpia or len(limpia) > 120:
                raise ValueError("referencia no válida")
            return limpia
        fingerprint = "|".join(
            (fecha, fallero_id, _texto_normalizado(concepto), format(bruto, ".2f"))
        )
        digest = hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()
        return f"AUTO-{digest[:24].upper()}"

    @staticmethod
    def _memoria_vacia() -> dict[str, Any]:
        return {
            "version": 1,
            "falleros": {},
            "cobros": {},
            "actualizado_en": None,
        }

    def _cargar_memoria(self) -> dict[str, Any]:
        if not self.memoria_path.exists():
            return self._memoria_vacia()
        try:
            data = json.loads(self.memoria_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            raise RuntimeError("no se puede leer la memoria de cobros") from exc
        if (
            not isinstance(data, dict)
            or data.get("version") != 1
            or not isinstance(data.get("falleros"), dict)
            or not isinstance(data.get("cobros"), dict)
        ):
            raise RuntimeError("formato de memoria de cobros no compatible")
        return data

    def _guardar_memoria(self, memoria: Mapping[str, Any]) -> None:
        self.memoria_path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporal = tempfile.mkstemp(
            prefix=f".{self.memoria_path.name}.",
            suffix=".tmp",
            dir=self.memoria_path.parent,
        )
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as file:
                json.dump(memoria, file, ensure_ascii=False, indent=2, sort_keys=True)
                file.write("\n")
                file.flush()
                os.fsync(file.fileno())
            os.replace(temporal, self.memoria_path)
        finally:
            if os.path.exists(temporal):
                os.unlink(temporal)

    def _sincronizar_libro(self, memoria: Mapping[str, Any]) -> None:
        self.libro_path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporal = tempfile.mkstemp(
            prefix=f".{self.libro_path.name}.",
            suffix=".tmp",
            dir=self.libro_path.parent,
        )
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as file:
                for asiento in memoria["cobros"].values():
                    file.write(
                        json.dumps(asiento, ensure_ascii=False, sort_keys=True) + "\n"
                    )
                file.flush()
                os.fsync(file.fileno())
            os.replace(temporal, self.libro_path)
        finally:
            if os.path.exists(temporal):
                os.unlink(temporal)


GestionFalla = GestorFallaV9


def _cargar_payload(path: str) -> list[Mapping[str, Any]]:
    if path == "-":
        raw = __import__("sys").stdin.read()
    else:
        raw = Path(path).read_text(encoding="utf-8")
    payload = json.loads(raw)
    if isinstance(payload, Mapping):
        payload = payload.get("registros", [payload])
    if not isinstance(payload, list) or not all(
        isinstance(item, Mapping) for item in payload
    ):
        raise ValueError("el JSON debe ser un registro, una lista o contener registros")
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Procesa cobros de una Falla")
    parser.add_argument(
        "--input",
        default="-",
        help="Archivo JSON de entrada; '-' lee stdin (predeterminado)",
    )
    parser.add_argument("--memory", help="Ruta del histórico Memories")
    parser.add_argument("--ledger", help="Ruta del libro contable JSONL")
    parser.add_argument(
        "--commission",
        default=os.getenv("FALLA_COMISION_PCT", "0.08"),
        help="Comisión decimal; 0.08 equivale al 8%%",
    )
    parser.add_argument(
        "--minimum",
        default=os.getenv("FALLA_CUOTA_MINIMA_EUR", "50.00"),
        help="Cuota mínima en euros",
    )
    args = parser.parse_args(argv)

    try:
        gestor = GestorFallaV9(
            args.commission,
            args.minimum,
            memoria_path=args.memory,
            libro_path=args.ledger,
        )
        resultados = gestor.procesar_registros(_cargar_payload(args.input))
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print(json.dumps({"cobros": resultados}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
