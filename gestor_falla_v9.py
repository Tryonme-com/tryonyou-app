"""Gestor financiero para comisiones de festividades Falla.

Este módulo implementa reglas estrictas para:
1) Validar identidad y concepto.
2) Calcular comisión fija.
3) Cruzar y actualizar saldo pendiente en memorias.
4) Registrar asiento contable limpio.
5) Marcar impago como "Pendiente de regularizar".
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any, Optional


ALLOWED_CONCEPT_TOKENS = ("cuota", "loteria", "lotería", "evento")


class GestorFallaV9:
    """Procesador de cobros con memoria persistente y deduplicación."""

    def __init__(
        self,
        comision_pct: float = 0.08,
        cuota_base: float = 50.0,
        memoria_path: Optional[str | Path] = "data/falla_memorias.json",
    ) -> None:
        if comision_pct < 0 or comision_pct > 1:
            raise ValueError("comision_pct debe estar entre 0 y 1.")
        if cuota_base <= 0:
            raise ValueError("cuota_base debe ser mayor que cero.")

        self.comision_pct = comision_pct
        self.cuota_base = cuota_base
        self.memoria_path = Path(memoria_path) if memoria_path else None
        self.registro_memoria: list[dict[str, Any]] = []
        self.saldos_pendientes: dict[str, float] = {}
        self._indices_duplicados: set[str] = set()
        self._cargar_memorias()

    def ejecutar_cobro(
        self,
        nombre: str,
        bruto: float,
        concepto: str,
        *,
        fallero_id: Optional[str] = None,
        referencia_externa: Optional[str] = None,
        fecha: Optional[dt.date] = None,
    ) -> dict[str, Any]:
        """Procesa un cobro individual y devuelve el asiento generado."""
        nombre_limpio = self._validar_nombre(nombre)
        concepto_limpio = self._validar_concepto(concepto)
        bruto_limpio = self._validar_importe(bruto)
        fecha_obj = fecha or dt.date.today()
        fecha_txt = fecha_obj.strftime("%d/%m/%Y")
        id_fallero = self._normalizar_id(fallero_id or nombre_limpio)

        fingerprint = self._generar_fingerprint(
            id_fallero=id_fallero,
            fecha=fecha_txt,
            concepto=concepto_limpio,
            bruto=bruto_limpio,
            referencia_externa=referencia_externa,
        )
        if fingerprint in self._indices_duplicados:
            raise ValueError("Cobro duplicado detectado: transacción ya registrada.")

        comision = round(bruto_limpio * self.comision_pct, 2)
        neto = round(bruto_limpio - comision, 2)
        saldo_anterior = round(self.saldos_pendientes.get(id_fallero, 0.0), 2)
        saldo_nuevo = round(max(0.0, saldo_anterior + self.cuota_base - bruto_limpio), 2)
        estado = "PAGADO" if bruto_limpio >= self.cuota_base else "Pendiente de regularizar"

        asiento = {
            "Fecha": fecha_txt,
            "ID de Fallero": id_fallero,
            "Fallero": nombre_limpio.upper(),
            "Concepto": concepto_limpio,
            "Importe Bruto": bruto_limpio,
            "Comisión Aplicada": comision,
            "Neto Resultante": neto,
            "Saldo Pendiente": saldo_nuevo,
            "Estado": estado,
            "Referencia Externa": referencia_externa or "",
            "Fingerprint": fingerprint,
        }

        self.registro_memoria.append(asiento)
        self.saldos_pendientes[id_fallero] = saldo_nuevo
        self._indices_duplicados.add(fingerprint)
        self._persistir_memorias()
        return asiento

    def procesar_registros(self, registros: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Procesa una lista de cobros sin detenerse en el primer error."""
        resultados: list[dict[str, Any]] = []
        for registro in registros:
            try:
                asiento = self.ejecutar_cobro(
                    nombre=str(registro.get("nombre", "")),
                    bruto=float(registro.get("bruto", 0)),
                    concepto=str(registro.get("concepto", "")),
                    fallero_id=registro.get("fallero_id"),
                    referencia_externa=registro.get("referencia_externa"),
                )
                resultados.append({"ok": True, "asiento": asiento})
            except Exception as exc:  # noqa: BLE001 - devolución estructurada para pipeline
                resultados.append({"ok": False, "error": str(exc), "registro": registro})
        return resultados

    def _validar_nombre(self, nombre: str) -> str:
        limpio = (nombre or "").strip()
        if len(limpio) < 2:
            raise ValueError("Nombre de fallero inválido.")
        return limpio

    def _validar_concepto(self, concepto: str) -> str:
        limpio = (concepto or "").strip()
        if not limpio:
            raise ValueError("Concepto de cobro vacío.")
        concepto_lower = limpio.lower()
        if not any(token in concepto_lower for token in ALLOWED_CONCEPT_TOKENS):
            raise ValueError(
                "Concepto inválido: usa cuota, lotería/loteria o evento."
            )
        return limpio

    def _validar_importe(self, bruto: float) -> float:
        try:
            valor = round(float(bruto), 2)
        except (TypeError, ValueError) as exc:
            raise ValueError("Importe bruto inválido.") from exc
        if valor <= 0:
            raise ValueError("Importe bruto debe ser mayor que cero.")
        return valor

    def _normalizar_id(self, fallero_id: str) -> str:
        return "_".join((fallero_id or "").strip().upper().split())

    def _generar_fingerprint(
        self,
        *,
        id_fallero: str,
        fecha: str,
        concepto: str,
        bruto: float,
        referencia_externa: Optional[str],
    ) -> str:
        base = f"{id_fallero}|{fecha}|{concepto.lower()}|{bruto:.2f}"
        if referencia_externa:
            base = f"{referencia_externa.strip()}|{id_fallero}"
        return hashlib.sha256(base.encode("utf-8")).hexdigest()

    def _cargar_memorias(self) -> None:
        if not self.memoria_path or not self.memoria_path.exists():
            return
        data = json.loads(self.memoria_path.read_text(encoding="utf-8"))
        self.registro_memoria = list(data.get("asientos", []))
        self.saldos_pendientes = {
            str(k): round(float(v), 2) for k, v in data.get("saldos_pendientes", {}).items()
        }
        self._indices_duplicados = {
            str(asiento.get("Fingerprint", ""))
            for asiento in self.registro_memoria
            if asiento.get("Fingerprint")
        }

    def _persistir_memorias(self) -> None:
        if not self.memoria_path:
            return
        self.memoria_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "asientos": self.registro_memoria,
            "saldos_pendientes": self.saldos_pendientes,
        }
        self.memoria_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    gestor = GestorFallaV9(comision_pct=0.08, cuota_base=50.0)
    print("--- PROCESANDO COBROS (COMISIÓN 8%) ---")
    ejemplo = gestor.ejecutar_cobro(
        nombre="Pau",
        bruto=100.0,
        concepto="Cuota Abril",
        referencia_externa="stripe_checkout_001",
    )
    print(ejemplo)
