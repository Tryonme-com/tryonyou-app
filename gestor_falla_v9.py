from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any


DEFAULT_COMISION_PCT = Decimal("0.08")
DEFAULT_CUOTA_BASE = Decimal("50.00")
DEFAULT_MEMORY_PATH = Path("data/falla_memorias.json")
ALLOWED_CONCEPTS = ("cuota", "loteria", "evento")


class FallaCobroError(ValueError):
    """Error de validacion para registros de cobro Falla."""


class DuplicateCobroError(FallaCobroError):
    """El cobro ya existe en la memoria persistente."""


def _money(value: Any, field_name: str) -> Decimal:
    if isinstance(value, str):
        normalized = value.strip().replace("€", "").replace(",", ".")
    else:
        normalized = str(value)
    try:
        amount = Decimal(normalized)
    except Exception as exc:  # pragma: no cover - Decimal no expone subtipo estable aqui
        raise FallaCobroError(f"{field_name} debe ser un importe numerico") from exc
    if amount <= 0:
        raise FallaCobroError(f"{field_name} debe ser mayor que cero")
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _rate_from_env(name: str, default: Decimal) -> Decimal:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    return _validate_rate(Decimal(raw.strip().replace(",", ".")), name)


def _validate_rate(rate: Decimal, name: str) -> Decimal:
    if rate < 0 or rate >= 1:
        raise FallaCobroError(f"{name} debe estar entre 0 y 1")
    return rate


def _quota_from_env(name: str, default: Decimal) -> Decimal:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    return _money(raw, name)


def _normalize_id(value: Any, name: str) -> str:
    raw = str(value or "").strip()
    if raw:
        return re.sub(r"[^A-Za-z0-9_-]+", "-", raw).strip("-").upper()
    fallback = re.sub(r"[^A-Za-z0-9]+", "-", name.strip()).strip("-").upper()
    if not fallback:
        raise FallaCobroError("id_fallero o nombre del fallero es obligatorio")
    return fallback


def _normalize_name(value: Any) -> str:
    name = str(value or "").strip()
    if not name:
        raise FallaCobroError("nombre del fallero es obligatorio")
    return re.sub(r"\s+", " ", name).upper()


def _normalize_concept(value: Any) -> tuple[str, str]:
    raw = str(value or "").strip()
    if not raw:
        raise FallaCobroError("concepto es obligatorio")
    normalized = raw.lower().replace("í", "i").replace("é", "e").replace("ó", "o")
    for concept in ALLOWED_CONCEPTS:
        if concept in normalized:
            return concept, raw
    allowed = ", ".join(ALLOWED_CONCEPTS)
    raise FallaCobroError(f"concepto no permitido: {raw!r}. Usa: {allowed}")


def _normalize_date(value: Any | None = None) -> str:
    if value is None or str(value).strip() == "":
        return dt.date.today().isoformat()
    raw = str(value).strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return dt.datetime.strptime(raw, fmt).date().isoformat()
        except ValueError:
            continue
    raise FallaCobroError("fecha debe usar formato YYYY-MM-DD o DD/MM/YYYY")


def _amount_to_json(amount: Decimal) -> float:
    return float(amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


@dataclass(frozen=True)
class CobroFalla:
    id_fallero: str
    nombre: str
    concepto_tipo: str
    concepto: str
    bruto: Decimal
    fecha: str
    referencia_externa: str | None = None

    @classmethod
    def from_record(cls, record: dict[str, Any]) -> "CobroFalla":
        nombre = _normalize_name(
            record.get("nombre")
            or record.get("fallero")
            or record.get("fallero_nombre")
        )
        concepto_tipo, concepto = _normalize_concept(record.get("concepto") or record.get("tipo"))
        bruto = _money(
            record.get("bruto")
            or record.get("importe_bruto")
            or record.get("importe")
            or record.get("monto"),
            "importe_bruto",
        )
        referencia = record.get("referencia_externa") or record.get("payment_id") or record.get("id_pago")
        return cls(
            id_fallero=_normalize_id(record.get("id_fallero"), nombre),
            nombre=nombre,
            concepto_tipo=concepto_tipo,
            concepto=str(concepto).strip(),
            bruto=bruto,
            fecha=_normalize_date(record.get("fecha")),
            referencia_externa=str(referencia).strip() if referencia else None,
        )

    @property
    def fingerprint(self) -> str:
        base = "|".join(
            (
                self.fecha,
                self.id_fallero,
                self.concepto_tipo,
                str(self.bruto),
                self.referencia_externa or "",
            )
        )
        return hashlib.sha256(base.encode("utf-8")).hexdigest()


class FallaMemoryStore:
    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path or os.getenv("FALLA_MEMORY_PATH") or DEFAULT_MEMORY_PATH)

    def load(self) -> dict[str, Any]:
        if not self.path.exists():
            return self._empty()
        with self.path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, dict):
            raise FallaCobroError("la memoria Falla debe ser un objeto JSON")
        data.setdefault("schema_version", 1)
        data.setdefault("configuracion", {})
        data.setdefault("falleros", {})
        data.setdefault("asientos", [])
        data.setdefault("fingerprints", [])
        data.setdefault("referencias_externas", [])
        return data

    def save(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2, sort_keys=True)
            fh.write("\n")

    @staticmethod
    def _empty() -> dict[str, Any]:
        return {
            "schema_version": 1,
            "configuracion": {},
            "falleros": {},
            "asientos": [],
            "fingerprints": [],
            "referencias_externas": [],
        }


class GestorFallaV9:
    def __init__(
        self,
        comision_pct: Decimal | float | str | None = None,
        cuota_base: Decimal | float | str | None = None,
        memory_path: str | Path | None = None,
        store: FallaMemoryStore | None = None,
    ) -> None:
        self.comision_pct = (
            _validate_rate(Decimal(str(comision_pct)).quantize(Decimal("0.0001")), "comision_pct")
            if comision_pct is not None
            else _rate_from_env("FALLA_COMISION_PCT", DEFAULT_COMISION_PCT)
        )
        self.cuota_base = (
            _money(cuota_base, "cuota_base")
            if cuota_base is not None
            else _quota_from_env("FALLA_CUOTA_BASE", DEFAULT_CUOTA_BASE)
        )
        self.store = store or FallaMemoryStore(memory_path)

    def ejecutar_cobro(self, nombre: str, bruto: float, concepto: str, **extra: Any) -> dict[str, Any]:
        record = {"nombre": nombre, "bruto": bruto, "concepto": concepto, **extra}
        return self.procesar_registro(record)

    def procesar_registro(self, record: dict[str, Any]) -> dict[str, Any]:
        cobro = CobroFalla.from_record(record)
        memoria = self.store.load()
        fingerprints = set(memoria.get("fingerprints", []))
        referencias = set(memoria.get("referencias_externas", []))

        if cobro.fingerprint in fingerprints:
            raise DuplicateCobroError("cobro duplicado: fingerprint ya registrado")
        if cobro.referencia_externa and cobro.referencia_externa in referencias:
            raise DuplicateCobroError("cobro duplicado: referencia_externa ya registrada")

        comision = (cobro.bruto * self.comision_pct).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        neto = (cobro.bruto - comision).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        falleros = memoria.setdefault("falleros", {})
        fallero = falleros.setdefault(
            cobro.id_fallero,
            {"nombre": cobro.nombre, "saldo_pendiente": _amount_to_json(self.cuota_base)},
        )
        saldo_anterior = Decimal(str(fallero.get("saldo_pendiente", _amount_to_json(self.cuota_base))))
        saldo_pendiente = max(Decimal("0.00"), (saldo_anterior - cobro.bruto)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        if cobro.bruto < self.cuota_base:
            estado = "PENDIENTE_REGULARIZAR"
        elif saldo_pendiente > 0:
            estado = "DEUDA_PENDIENTE"
        else:
            estado = "PAGADO"

        asiento = {
            "fecha": cobro.fecha,
            "id_fallero": cobro.id_fallero,
            "fallero": cobro.nombre,
            "concepto": cobro.concepto,
            "concepto_tipo": cobro.concepto_tipo,
            "importe_bruto": _amount_to_json(cobro.bruto),
            "comision_pct": _amount_to_json(self.comision_pct),
            "comision_aplicada": _amount_to_json(comision),
            "neto_resultante": _amount_to_json(neto),
            "saldo_anterior": _amount_to_json(saldo_anterior),
            "saldo_pendiente": _amount_to_json(saldo_pendiente),
            "estado": estado,
            "referencia_externa": cobro.referencia_externa,
            "fingerprint": cobro.fingerprint,
        }

        memoria["configuracion"] = {
            "comision_pct": _amount_to_json(self.comision_pct),
            "cuota_base": _amount_to_json(self.cuota_base),
        }
        fallero.update(
            {
                "nombre": cobro.nombre,
                "saldo_pendiente": _amount_to_json(saldo_pendiente),
                "actualizado_en": cobro.fecha,
            }
        )
        memoria.setdefault("asientos", []).append(asiento)
        memoria.setdefault("fingerprints", []).append(cobro.fingerprint)
        if cobro.referencia_externa:
            memoria.setdefault("referencias_externas", []).append(cobro.referencia_externa)
        self.store.save(memoria)
        return asiento

    def procesar_lote(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [self.procesar_registro(record) for record in records]


def _read_input(path: str | None) -> Any:
    if not path or path == "-":
        return json.load(os.sys.stdin)
    with Path(path).open("r", encoding="utf-8") as fh:
        return json.load(fh)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Procesa cobros Falla V9 con memoria JSON.")
    parser.add_argument("--input", "-i", help="JSON de cobro unico o lista de cobros. Usa '-' para stdin.")
    parser.add_argument("--memory", "-m", help="Ruta de memoria JSON persistente.")
    parser.add_argument("--commission", type=str, help="Comision fija. Ej: 0.08 para 8%.")
    parser.add_argument("--quota", type=str, help="Cuota minima/base. Ej: 50.00")
    args = parser.parse_args(argv)

    payload = _read_input(args.input)
    records = payload if isinstance(payload, list) else [payload]
    if not all(isinstance(item, dict) for item in records):
        raise FallaCobroError("el input debe ser un objeto JSON o una lista de objetos")

    gestor = GestorFallaV9(comision_pct=args.commission, cuota_base=args.quota, memory_path=args.memory)
    result = gestor.procesar_lote(records)
    json.dump(result if isinstance(payload, list) else result[0], os.sys.stdout, ensure_ascii=False, indent=2)
    os.sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
