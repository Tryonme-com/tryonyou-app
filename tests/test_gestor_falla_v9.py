from __future__ import annotations

import os
import sys
import unittest

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from billing.gestor_falla_v9 import GestorFallaV9


class TestGestorFallaV9(unittest.TestCase):
    def test_calculo_comision_y_neto(self) -> None:
        gestor = GestorFallaV9(comision_pct=0.08, cuota_base=50.0)
        asiento = gestor.ejecutar_cobro(
            id_fallero="F-001",
            nombre="Pau",
            bruto=100.0,
            concepto="cuota",
            transaccion_id="TX-100",
        )
        self.assertEqual(asiento.comision_aplicada, 8.0)
        self.assertEqual(asiento.neto_resultante, 92.0)
        self.assertEqual(asiento.estado, "PAGADO")
        self.assertEqual(asiento.saldo_pendiente, 0.0)

    def test_cuota_inferior_queda_pendiente(self) -> None:
        gestor = GestorFallaV9(comision_pct=0.08, cuota_base=50.0)
        asiento = gestor.ejecutar_cobro(
            id_fallero="F-002",
            nombre="Maria",
            bruto=40.0,
            concepto="Cuota",
            transaccion_id="TX-200",
        )
        self.assertEqual(asiento.estado, "Pendiente de regularizar")
        self.assertEqual(asiento.saldo_pendiente, 10.0)

    def test_deduplicacion_por_transaccion_id(self) -> None:
        gestor = GestorFallaV9(comision_pct=0.08, cuota_base=50.0)
        primero = gestor.ejecutar_cobro(
            id_fallero="F-003",
            nombre="Jose",
            bruto=50.0,
            concepto="cuota",
            transaccion_id="TX-300",
        )
        segundo = gestor.ejecutar_cobro(
            id_fallero="F-003",
            nombre="Jose",
            bruto=50.0,
            concepto="cuota",
            transaccion_id="TX-300",
        )
        self.assertIs(primero, segundo)
        self.assertEqual(len(gestor.registro_memoria), 1)

    def test_cruce_deuda_en_pagos_cuota(self) -> None:
        gestor = GestorFallaV9(comision_pct=0.08, cuota_base=50.0)
        gestor.ejecutar_cobro(
            id_fallero="F-004",
            nombre="Laura",
            bruto=30.0,
            concepto="cuota",
            transaccion_id="TX-401",
        )
        segundo = gestor.ejecutar_cobro(
            id_fallero="F-004",
            nombre="Laura",
            bruto=70.0,
            concepto="cuota",
            transaccion_id="TX-402",
        )
        self.assertEqual(segundo.saldo_pendiente, 0.0)
        self.assertEqual(segundo.estado, "PAGADO")

    def test_concepto_invalido_lanza_error(self) -> None:
        gestor = GestorFallaV9()
        with self.assertRaises(ValueError):
            gestor.ejecutar_cobro(
                id_fallero="F-005",
                nombre="Alex",
                bruto=20.0,
                concepto="donativo",
                transaccion_id="TX-500",
            )


if __name__ == "__main__":
    unittest.main()
