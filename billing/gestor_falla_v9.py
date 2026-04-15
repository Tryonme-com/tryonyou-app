"""Gestor de cobros para comisiones de Fallas (V9).

Este módulo procesa cobros con comisión fija, mantiene saldos pendientes
por fallero y evita registrar transacciones duplicadas.
"""

from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass
from typing import Dict, List, Optional


CONCEPTOS_VALIDOS = {"cuota", "loteria", "evento"}


@dataclass(frozen=True)
class AsientoCobro:
    fecha: str
    id_fallero: str
    fallero: str
    concepto: str
    importe_bruto: float
    comision_aplicada: float
    neto_resultante: float
    saldo_pendiente: float
    estado: str
    transaccion_id: str


class GestorFallaV9:
    """Motor principal de gestión de cobros con memoria en proceso."""

    def __init__(self, comision_pct: float = 0.08, cuota_base: float = 50.0) -> None:
        if not 0 <= comision_pct < 1:
            raise ValueError("comision_pct debe estar entre 0 y 1.")
        if cuota_base <= 0:
            raise ValueError("cuota_base debe ser mayor que cero.")

        self.comision_pct = comision_pct
        self.cuota_base = cuota_base
        self.registro_memoria: List[AsientoCobro] = []
        self.saldos_pendientes: Dict[str, float] = {}
        self._asientos_por_tx: Dict[str, AsientoCobro] = {}

    @staticmethod
    def _normalizar_concepto(concepto: str) -> str:
        concepto_norm = (concepto or "").strip().lower()
        if concepto_norm == "lotería":
            concepto_norm = "loteria"
        return concepto_norm

    @staticmethod
    def _hoy() -> str:
        return _dt.date.today().strftime("%d/%m/%Y")

    @staticmethod
    def _build_transaccion_id(
        fecha: str,
        id_fallero: str,
        concepto: str,
        bruto: float,
    ) -> str:
        return f"{fecha}|{id_fallero}|{concepto}|{bruto:.2f}"

    def ejecutar_cobro(
        self,
        id_fallero: str,
        nombre: str,
        bruto: float,
        concepto: str,
        transaccion_id: Optional[str] = None,
    ) -> AsientoCobro:
        """Procesa un cobro y actualiza memoria/saldo pendiente.

        Reglas:
        - Valida fallero y concepto.
        - Aplica comisión fija.
        - Actualiza deuda del fallero contra memoria previa.
        - Evita registros duplicados por transacción.
        """

        if not (id_fallero or "").strip():
            raise ValueError("id_fallero es obligatorio.")
        if not (nombre or "").strip():
            raise ValueError("nombre es obligatorio.")
        if bruto <= 0:
            raise ValueError("bruto debe ser mayor que cero.")

        concepto_norm = self._normalizar_concepto(concepto)
        if concepto_norm not in CONCEPTOS_VALIDOS:
            raise ValueError(
                "concepto inválido. Valores permitidos: cuota, loteria, evento."
            )

        fecha = self._hoy()
        tx_id = transaccion_id or self._build_transaccion_id(
            fecha=fecha,
            id_fallero=id_fallero.strip(),
            concepto=concepto_norm,
            bruto=bruto,
        )

        if tx_id in self._asientos_por_tx:
            return self._asientos_por_tx[tx_id]

        comision = round(bruto * self.comision_pct, 2)
        neto = round(bruto - comision, 2)

        deuda_anterior = self.saldos_pendientes.get(id_fallero, 0.0)
        if concepto_norm == "cuota":
            saldo_pendiente = round(max(deuda_anterior + self.cuota_base - bruto, 0.0), 2)
        else:
            saldo_pendiente = round(max(deuda_anterior - bruto, 0.0), 2)
        self.saldos_pendientes[id_fallero] = saldo_pendiente

        estado = "PAGADO"
        if concepto_norm == "cuota" and bruto < self.cuota_base:
            estado = "Pendiente de regularizar"
        elif saldo_pendiente > 0:
            estado = "Pendiente de regularizar"

        asiento = AsientoCobro(
            fecha=fecha,
            id_fallero=id_fallero.strip(),
            fallero=nombre.strip().upper(),
            concepto=concepto_norm,
            importe_bruto=round(bruto, 2),
            comision_aplicada=comision,
            neto_resultante=neto,
            saldo_pendiente=saldo_pendiente,
            estado=estado,
            transaccion_id=tx_id,
        )

        self.registro_memoria.append(asiento)
        self._asientos_por_tx[tx_id] = asiento
        return asiento


if __name__ == "__main__":
    gestor = GestorFallaV9(comision_pct=0.08, cuota_base=50.0)
    print("--- PROCESANDO COBROS (COMISION 8%) ---")
    resultado = gestor.ejecutar_cobro(
        id_fallero="FALLERO-001",
        nombre="Pau",
        bruto=100.0,
        concepto="Cuota",
    )
    print(resultado)
