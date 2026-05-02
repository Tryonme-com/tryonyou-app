"""Gestor de cobros Falla V9.

Procesa cobros de falleros con comision fija, control de cuota minima,
memoria persistente y deduplicacion. Esta pensado para webhook o ejecucion
programada sobre un JSON exportado desde una hoja/base de datos.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import tempfile
import unicodedata
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Mapping


CONCEPTOS_VALIDOS = {"cuota", "loteria", "evento"}
ESTADO_PAGADO = "PAGADO"
ESTADO_PENDIENTE = "Pendiente de regularizar"


class GestorFallaError(ValueError):
    """Error de validacion del gestor Falla."""


class CobroDuplicadoError(GestorFallaError):
    """El cobro ya consta en la memoria."""


ConceptoInvalidoError = GestorFallaError
ValidationError = GestorFallaError


def _decimal(value: Any, field_name: str) -> Decimal:
    try:
        amount = Decimal(str(value).strip().replace(",", "."))
    except (InvalidOperation, AttributeError) as exc:
        raise GestorFallaError(f"{field_name} debe ser un numero valido") from exc

    if amount <= Decimal("0"):
        raise GestorFallaError(f"{field_name} debe ser mayor que cero")
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _money(value: Decimal) -> str:
    return f"{value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)} EUR"


def _normalize_text(value: Any, field_name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise GestorFallaError(f"{field_name} es obligatorio")
    return text


def _normalize_concept(concept: Any) -> str:
    text = _normalize_text(concept, "concepto").lower()
    without_accents = "".join(
        char
        for char in unicodedata.normalize("NFD", text)
        if unicodedata.category(char) != "Mn"
    )
    if without_accents not in CONCEPTOS_VALIDOS:
        valid = ", ".join(sorted(CONCEPTOS_VALIDOS))
        raise GestorFallaError(f"concepto no valido: {text!r}; usa {valid}")
    return without_accents


def _normalize_date(value: str | None = None) -> str:
    if value is None or str(value).strip() == "":
        return _dt.date.today().isoformat()

    raw = str(value).strip()
    if isinstance(value, _dt.date):
        return value.isoformat()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return _dt.datetime.strptime(raw, fmt).date().isoformat()
        except ValueError:
            pass
    raise GestorFallaError("fecha debe usar formato YYYY-MM-DD o DD/MM/YYYY")


def _commission_pct(value: Any) -> Decimal:
    pct = _decimal(value, "comision_pct")
    if pct > Decimal("1"):
        pct = (pct / Decimal("100")).quantize(Decimal("0.0001"))
    if pct >= Decimal("1"):
        raise GestorFallaError("comision_pct debe ser inferior al 100%")
    return pct


def _default_memory_path() -> Path:
    return Path(os.getenv("FALLA_MEMORY_PATH", "data/falla_memorias.json"))


def _load_memory(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"falleros": {}, "transacciones": [], "fingerprints": []}

    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)

    if not isinstance(data, dict):
        raise GestorFallaError("la memoria debe ser un objeto JSON")

    data.setdefault("falleros", {})
    data.setdefault("transacciones", [])
    data.setdefault("fingerprints", [])
    return data


def _save_memory(path: Path, data: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=str(path.parent),
        delete=False,
    ) as tmp:
        json.dump(data, tmp, ensure_ascii=False, indent=2, sort_keys=True)
        tmp.write("\n")
        temp_name = tmp.name
    os.replace(temp_name, path)


@dataclass(frozen=True)
class CobroFalla:
    id_fallero: str
    nombre: str
    bruto: Decimal
    concepto: str
    fecha: str
    referencia_externa: str

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> "CobroFalla":
        id_fallero = _normalize_text(
            payload.get("id_fallero") or payload.get("id") or payload.get("fallero_id"),
            "id_fallero",
        )
        nombre = _normalize_text(payload.get("nombre") or payload.get("fallero"), "nombre")
        bruto = _decimal(
            payload.get("bruto") or payload.get("importe_bruto") or payload.get("importe"),
            "bruto",
        )
        concepto = _normalize_concept(payload.get("concepto"))
        fecha = _normalize_date(payload.get("fecha"))
        referencia = str(
            payload.get("referencia_externa")
            or payload.get("referencia")
            or payload.get("payment_id")
            or ""
        ).strip()
        return cls(
            id_fallero=id_fallero,
            nombre=nombre,
            bruto=bruto,
            concepto=concepto,
            fecha=fecha,
            referencia_externa=referencia,
        )

    @property
    def fingerprint(self) -> str:
        raw = "|".join(
            (
                self.fecha,
                self.id_fallero.strip().lower(),
                self.nombre.strip().lower(),
                self.concepto,
                str(self.bruto),
                self.referencia_externa.strip().lower(),
            )
        )
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class GestorFallaV9:
    """Procesador de cobros con memoria persistente."""

    def __init__(
        self,
        comision_pct: Any | None = None,
        cuota_base: Any | None = None,
        memory_path: str | Path | None = None,
    ) -> None:
        self.comision_pct = _commission_pct(
            comision_pct if comision_pct is not None else os.getenv("FALLA_COMISION_PCT", "0.08")
        )
        self.cuota_base = _decimal(
            cuota_base if cuota_base is not None else os.getenv("FALLA_CUOTA_BASE", "50"),
            "cuota_base",
        )
        self.memory_path = Path(memory_path) if memory_path is not None else _default_memory_path()

    def ejecutar_cobro(
        self,
        nombre: str,
        bruto: Any,
        concepto: str,
        *,
        id_fallero: str | None = None,
        fecha: str | None = None,
        referencia_externa: str = "",
    ) -> dict[str, Any]:
        payload = {
            "id_fallero": id_fallero or nombre,
            "nombre": nombre,
            "bruto": bruto,
            "concepto": concepto,
            "fecha": fecha,
            "referencia_externa": referencia_externa,
        }
        return self.procesar_payload(payload)

    def procesar_payload(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        cobro = CobroFalla.from_payload(payload)
        memoria = _load_memory(self.memory_path)
        self._assert_not_duplicate(memoria, cobro)

        comision = (cobro.bruto * self.comision_pct).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )
        neto = (cobro.bruto - comision).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        estado = ESTADO_PAGADO if cobro.bruto >= self.cuota_base else ESTADO_PENDIENTE

        fallero = self._ensure_fallero(memoria, cobro)
        saldo_previo = Decimal(str(fallero.get("saldo_pendiente", "0")))
        saldo_nuevo = self._saldo_actualizado(saldo_previo, cobro.bruto)
        fallero["saldo_pendiente"] = str(saldo_nuevo)
        fallero["nombre"] = cobro.nombre.upper()

        asiento = {
            "fecha": cobro.fecha,
            "id_fallero": cobro.id_fallero,
            "fallero": cobro.nombre.upper(),
            "concepto": cobro.concepto,
            "importe_bruto": _money(cobro.bruto),
            "comision_pct": str(self.comision_pct),
            "comision_aplicada": _money(comision),
            "neto_resultante": _money(neto),
            "estado": estado,
            "saldo_pendiente": _money(saldo_nuevo),
            "referencia_externa": cobro.referencia_externa,
            "fingerprint": cobro.fingerprint,
        }

        memoria["transacciones"].append(asiento)
        memoria["fingerprints"].append(cobro.fingerprint)
        fallero.setdefault("transacciones", []).append(cobro.fingerprint)
        _save_memory(self.memory_path, memoria)
        return asiento

    def procesar_lote(self, cobros: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
        return [self.procesar_payload(cobro) for cobro in cobros]

    def _assert_not_duplicate(self, memoria: Mapping[str, Any], cobro: CobroFalla) -> None:
        if cobro.fingerprint in set(memoria.get("fingerprints", [])):
            raise CobroDuplicadoError("cobro duplicado por fingerprint")

        if cobro.referencia_externa:
            for tx in memoria.get("transacciones", []):
                if tx.get("referencia_externa") == cobro.referencia_externa:
                    raise CobroDuplicadoError("cobro duplicado por referencia_externa")

    def _ensure_fallero(self, memoria: dict[str, Any], cobro: CobroFalla) -> dict[str, Any]:
        falleros = memoria.setdefault("falleros", {})
        current = falleros.setdefault(
            cobro.id_fallero,
            {"nombre": cobro.nombre.upper(), "saldo_pendiente": "0", "transacciones": []},
        )
        if not isinstance(current, dict):
            raise GestorFallaError(f"memoria corrupta para fallero {cobro.id_fallero}")
        return current

    def _saldo_actualizado(self, saldo_previo: Decimal, bruto: Decimal) -> Decimal:
        diferencia = self.cuota_base - bruto
        return max(Decimal("0.00"), saldo_previo + diferencia).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )


def _extract_cobros(payload: Any) -> list[Mapping[str, Any]]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        if isinstance(payload.get("cobros"), list):
            return payload["cobros"]
        return [payload]
    raise GestorFallaError("el JSON de entrada debe ser un objeto o una lista")


def run_from_file(input_path: Path, memory_path: Path | None = None) -> list[dict[str, Any]]:
    with input_path.open("r", encoding="utf-8") as fh:
        payload = json.load(fh)
    gestor = GestorFallaV9(memory_path=memory_path)
    return gestor.procesar_lote(_extract_cobros(payload))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Procesa cobros Falla V9")
    parser.add_argument("--input", required=True, help="JSON con cobro unico o lista de cobros")
    parser.add_argument("--memory", help="Ruta de memoria JSON persistente")
    args = parser.parse_args(argv)

    results = run_from_file(
        Path(args.input),
        Path(args.memory) if args.memory else None,
    )
    print(json.dumps(results, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
