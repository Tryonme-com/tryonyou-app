from __future__ import annotations

import datetime as dt
import hashlib
import json
import unicodedata
from pathlib import Path
from typing import Any


class GestorFallaError(Exception):
    """Error base para el gestor de cobros."""


class ValidacionCobroError(GestorFallaError):
    """Error de validación de entrada."""


class CobroDuplicadoError(GestorFallaError):
    """Se detectó un cobro duplicado y no debe procesarse."""


class MemoryStore:
    """Persistencia local para ledger, saldos y control de duplicados."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"ledger": [], "saldos_pendientes": {}, "dedupe_keys": []}
        with self.path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, dict):
            raise GestorFallaError("El archivo de memoria no tiene formato válido.")
        data.setdefault("ledger", [])
        data.setdefault("saldos_pendientes", {})
        data.setdefault("dedupe_keys", [])
        return data

    def save(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self.path.with_suffix(self.path.suffix + ".tmp")
        with tmp_path.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2, sort_keys=True)
        tmp_path.replace(self.path)


class GestorFallaV9:
    """Gestor financiero para cobros de comisiones de la Falla."""

    CONCEPTOS_VALIDOS = {"cuota", "loteria", "evento"}

    def __init__(
        self,
        comision_pct: float = 0.08,
        cuota_base: float = 50.0,
        memory_store: MemoryStore | None = None,
    ) -> None:
        if comision_pct < 0:
            raise ValueError("comision_pct debe ser >= 0")
        if cuota_base <= 0:
            raise ValueError("cuota_base debe ser > 0")
        self.comision_pct = comision_pct
        self.cuota_base = cuota_base
        self.memory_store = memory_store or MemoryStore("memories/falla_memories.json")

    @staticmethod
    def _normalizar_texto(valor: str) -> str:
        limpio = valor.strip()
        if not limpio:
            return ""
        sin_tildes = unicodedata.normalize("NFKD", limpio)
        return "".join(c for c in sin_tildes if not unicodedata.combining(c)).lower()

    def _validar_nombre(self, nombre: str) -> str:
        if not isinstance(nombre, str) or not nombre.strip():
            raise ValidacionCobroError("El nombre del fallero es obligatorio.")
        return nombre.strip()

    def _validar_concepto(self, concepto: str) -> str:
        if not isinstance(concepto, str):
            raise ValidacionCobroError("El concepto de cobro es obligatorio.")
        concepto_norm = self._normalizar_texto(concepto)
        if concepto_norm not in self.CONCEPTOS_VALIDOS:
            validos = ", ".join(sorted(self.CONCEPTOS_VALIDOS))
            raise ValidacionCobroError(
                f"Concepto inválido '{concepto}'. Valores permitidos: {validos}."
            )
        return concepto_norm

    @staticmethod
    def _validar_bruto(bruto: Any) -> float:
        try:
            bruto_float = float(bruto)
        except (TypeError, ValueError) as exc:
            raise ValidacionCobroError("El importe bruto debe ser numérico.") from exc
        if bruto_float <= 0:
            raise ValidacionCobroError("El importe bruto debe ser mayor que 0.")
        return round(bruto_float, 2)

    @staticmethod
    def _generar_id_fallero(nombre: str) -> str:
        base = "".join(ch if ch.isalnum() else "_" for ch in nombre.upper())
        while "__" in base:
            base = base.replace("__", "_")
        return base.strip("_") or "FALLERO_SIN_ID"

    def _clave_dedupe(
        self,
        fecha: str,
        fallero_id: str,
        concepto: str,
        bruto: float,
        transaccion_id: str | None,
    ) -> str:
        if transaccion_id:
            return f"txn:{transaccion_id.strip()}"
        raw = f"{fecha}:{fallero_id}:{concepto}:{bruto:.2f}"
        digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
        return f"auto:{digest}"

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
        nombre_val = self._validar_nombre(nombre)
        concepto_val = self._validar_concepto(concepto)
        bruto_val = self._validar_bruto(bruto)
        fecha_val = fecha or dt.date.today().isoformat()
        fallero_id_val = (fallero_id or self._generar_id_fallero(nombre_val)).strip().upper()
        clave = self._clave_dedupe(
            fecha=fecha_val,
            fallero_id=fallero_id_val,
            concepto=concepto_val,
            bruto=bruto_val,
            transaccion_id=transaccion_id,
        )

        memoria = self.memory_store.load()
        dedupe_set = set(memoria["dedupe_keys"])
        if clave in dedupe_set:
            raise CobroDuplicadoError(
                f"Cobro duplicado detectado para {fallero_id_val} (clave {clave})."
            )

        comision = round(bruto_val * self.comision_pct, 2)
        neto = round(bruto_val - comision, 2)
        saldos: dict[str, float] = memoria["saldos_pendientes"]
        saldo_previo = round(float(saldos.get(fallero_id_val, 0.0)), 2)

        if bruto_val < self.cuota_base:
            faltante_actual = round(self.cuota_base - bruto_val, 2)
            saldo_pendiente = round(saldo_previo + faltante_actual, 2)
            estado = "Pendiente de regularizar"
        else:
            exceso = round(bruto_val - self.cuota_base, 2)
            saldo_pendiente = round(max(saldo_previo - exceso, 0.0), 2)
            estado = "Pagado"

        saldos[fallero_id_val] = saldo_pendiente

        asiento = {
            "fecha": fecha_val,
            "id_fallero": fallero_id_val,
            "fallero": nombre_val.upper(),
            "concepto": concepto_val,
            "importe_bruto": bruto_val,
            "comision_aplicada": comision,
            "neto_resultante": neto,
            "estado": estado,
            "saldo_pendiente": saldo_pendiente,
            "dedupe_key": clave,
        }

        memoria["ledger"].append(asiento)
        memoria["dedupe_keys"] = sorted(dedupe_set | {clave})
        self.memory_store.save(memoria)
        return asiento

    def procesar_registros(self, registros: list[dict[str, Any]]) -> list[dict[str, Any]]:
        resultados: list[dict[str, Any]] = []
        for registro in registros:
            resultados.append(
                self.ejecutar_cobro(
                    nombre=str(registro.get("nombre", "")),
                    bruto=registro.get("importe_bruto"),
                    concepto=str(registro.get("concepto", "")),
                    fallero_id=registro.get("id_fallero"),
                    transaccion_id=registro.get("transaccion_id"),
                    fecha=registro.get("fecha"),
                )
            )
        return resultados
