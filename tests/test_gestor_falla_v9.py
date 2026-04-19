"""Tests para billing.gestor_falla_v9."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from billing.gestor_falla_v9 import DuplicateTransactionError, GestorFallaV9


class TestGestorFallaV9(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.memoria_path = Path(self.tmp.name) / "falla_memories.json"

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_ejecutar_cobro_pagado(self) -> None:
        gestor = GestorFallaV9(
            comision_pct=0.08,
            cuota_base=50.0,
            memoria_path=self.memoria_path,
        )
        asiento = gestor.ejecutar_cobro(
            nombre="Pau",
            bruto=100.0,
            concepto="cuota",
            fallero_id="F-001",
            transaccion_id="TX-001",
            fecha="2026-04-19",
        )
        self.assertEqual(asiento["fallero"], "PAU")
        self.assertEqual(asiento["comision_aplicada"], 8.0)
        self.assertEqual(asiento["neto_resultante"], 92.0)
        self.assertEqual(asiento["estado"], "Pagado")

    def test_ejecutar_cobro_pendiente_regularizar(self) -> None:
        gestor = GestorFallaV9(
            comision_pct=0.08,
            cuota_base=50.0,
            memoria_path=self.memoria_path,
        )
        asiento = gestor.ejecutar_cobro(
            nombre="Maria",
            bruto=40.0,
            concepto="cuota",
            fallero_id="F-002",
            transaccion_id="TX-002",
            fecha="2026-04-19",
        )
        self.assertEqual(asiento["estado"], "Pendiente de regularizar")
        self.assertEqual(asiento["saldo_pendiente"], 10.0)

    def test_transaccion_duplicada(self) -> None:
        gestor = GestorFallaV9(memoria_path=self.memoria_path)
        gestor.ejecutar_cobro(
            nombre="Jose",
            bruto=100.0,
            concepto="evento",
            fallero_id="F-003",
            transaccion_id="TX-DUP",
        )
        gestor.guardar_memoria()

        gestor2 = GestorFallaV9(memoria_path=self.memoria_path)
        with self.assertRaises(DuplicateTransactionError):
            gestor2.ejecutar_cobro(
                nombre="Jose",
                bruto=100.0,
                concepto="evento",
                fallero_id="F-003",
                transaccion_id="TX-DUP",
            )

    def test_alias_concepto(self) -> None:
        gestor = GestorFallaV9(memoria_path=self.memoria_path)
        asiento = gestor.ejecutar_cobro(
            nombre="Laura",
            bruto=75.0,
            concepto="Cuota Mensual",
            fallero_id="F-004",
            transaccion_id="TX-004",
        )
        self.assertEqual(asiento["concepto"], "cuota")

    def test_procesar_lote_con_error_y_duplicado(self) -> None:
        gestor = GestorFallaV9(memoria_path=self.memoria_path)
        registros = [
            {
                "fallero_nombre": "Paco",
                "fallero_id": "F-005",
                "concepto": "loteria",
                "importe_bruto": 60,
                "transaccion_id": "TX-005",
            },
            {
                "fallero_nombre": "Paco",
                "fallero_id": "F-005",
                "concepto": "loteria",
                "importe_bruto": 60,
                "transaccion_id": "TX-005",
            },
            {
                "fallero_nombre": "Error",
                "fallero_id": "F-ERR",
                "concepto": "invalido",
                "importe_bruto": 60,
                "transaccion_id": "TX-ERR",
            },
        ]
        resultados = gestor.procesar_lote(registros)
        self.assertEqual(resultados[0]["estado"], "Pagado")
        self.assertEqual(resultados[1]["estado"], "DUPLICADO")
        self.assertEqual(resultados[2]["estado"], "ERROR")
        self.assertTrue(self.memoria_path.exists())


if __name__ == "__main__":
    unittest.main()
