from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from gestor_falla_v9 import CobroDuplicadoError, GestorFallaV9, MemoryStore, ValidacionCobroError


class TestGestorFallaV9(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.mem_path = os.path.join(self.tmp.name, "falla_memories_test.json")
        self.store = MemoryStore(self.mem_path)
        self.gestor = GestorFallaV9(
            comision_pct=0.08,
            cuota_base=50.0,
            memory_store=self.store,
        )

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_cobro_pagado_calcula_comision_y_neto(self) -> None:
        asiento = self.gestor.ejecutar_cobro("Pau", 100.0, "Cuota", transaccion_id="TX-1")
        self.assertEqual(asiento["estado"], "Pagado")
        self.assertEqual(asiento["comision_aplicada"], 8.0)
        self.assertEqual(asiento["neto_resultante"], 92.0)
        self.assertEqual(asiento["saldo_pendiente"], 0.0)

    def test_cobro_menor_cuota_queda_pendiente(self) -> None:
        asiento = self.gestor.ejecutar_cobro("Lola", 40.0, "Evento", transaccion_id="TX-2")
        self.assertEqual(asiento["estado"], "Pendiente de regularizar")
        self.assertEqual(asiento["saldo_pendiente"], 10.0)

    def test_concepto_invalido_falla_validacion(self) -> None:
        with self.assertRaises(ValidacionCobroError):
            self.gestor.ejecutar_cobro("Pau", 100.0, "donacion", transaccion_id="TX-3")

    def test_deduplicacion_por_transaccion_id(self) -> None:
        self.gestor.ejecutar_cobro("Pau", 100.0, "cuota", transaccion_id="TX-4")
        with self.assertRaises(CobroDuplicadoError):
            self.gestor.ejecutar_cobro("Pau", 100.0, "cuota", transaccion_id="TX-4")

    def test_memoria_persistida_con_ledger(self) -> None:
        self.gestor.ejecutar_cobro("Pau", 60.0, "lotería", transaccion_id="TX-5")
        data = json.loads(Path(self.mem_path).read_text(encoding="utf-8"))
        self.assertEqual(len(data["ledger"]), 1)
        self.assertIn("TX-5", data["dedupe_keys"][0])


if __name__ == "__main__":
    unittest.main()
