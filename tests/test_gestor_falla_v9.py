from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from gestor_falla_v9 import ESTADO_PAGADO, ESTADO_PENDIENTE, GestorFallaError, GestorFallaV9


class TestGestorFallaV9(unittest.TestCase):
    def _memory_path(self, tmpdir: str) -> Path:
        return Path(tmpdir) / "falla_memories.json"

    def test_calcula_comision_y_asiento_pagado(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            gestor = GestorFallaV9(memoria_path=self._memory_path(tmpdir))

            asiento = gestor.ejecutar_cobro(
                "Pau",
                "100.00",
                "Cuota Abril",
                id_transaccion="pay_001",
                fecha="2026-05-06",
            )

            self.assertEqual(asiento["estado"], ESTADO_PAGADO)
            self.assertEqual(asiento["id_fallero"], "PAU")
            self.assertEqual(asiento["concepto"], "cuota")
            self.assertEqual(asiento["importe_bruto_eur"], "100.00")
            self.assertEqual(asiento["comision_pct"], "0.0800")
            self.assertEqual(asiento["comision_eur"], "8.00")
            self.assertEqual(asiento["neto_resultante_eur"], "92.00")
            self.assertEqual(asiento["saldo_pendiente_eur"], "0.00")
            self.assertFalse(asiento["duplicado"])

    def test_marca_pendiente_si_el_cobro_no_llega_a_cuota(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            gestor = GestorFallaV9(memoria_path=self._memory_path(tmpdir), cuota_base="50")

            asiento = gestor.ejecutar_cobro(
                "Amparo",
                "35",
                "lotería",
                id_transaccion="pay_002",
                fecha="2026-05-06",
            )

            self.assertEqual(asiento["estado"], ESTADO_PENDIENTE)
            self.assertEqual(asiento["concepto"], "loteria")
            self.assertEqual(asiento["deuda_generada_eur"], "15.00")
            self.assertEqual(asiento["saldo_pendiente_eur"], "15.00")

    def test_deduplica_por_id_transaccion_sin_reescribir_memoria(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            memoria = self._memory_path(tmpdir)
            gestor = GestorFallaV9(memoria_path=memoria)

            primero = gestor.ejecutar_cobro(
                "Pau",
                "100",
                "evento",
                id_transaccion="pay_dup",
                fecha="2026-05-06",
            )
            duplicado = gestor.ejecutar_cobro(
                "Pau",
                "100",
                "evento",
                id_transaccion="pay_dup",
                fecha="2026-05-06",
            )

            payload = json.loads(memoria.read_text(encoding="utf-8"))
            self.assertEqual(len(payload["transacciones"]), 1)
            self.assertFalse(primero["duplicado"])
            self.assertTrue(duplicado["duplicado"])
            self.assertEqual(duplicado["id_transaccion"], "pay_dup")

    def test_actualiza_saldo_pendiente_con_regularizacion_posterior(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            gestor = GestorFallaV9(memoria_path=self._memory_path(tmpdir), cuota_base="50")

            gestor.ejecutar_cobro(
                "Pau",
                "30",
                "cuota",
                id_transaccion="pay_partial",
                fecha="2026-05-06",
            )
            regularizacion = gestor.ejecutar_cobro(
                "Pau",
                "70",
                "cuota",
                id_transaccion="pay_regularize",
                fecha="2026-05-07",
            )

            self.assertEqual(regularizacion["estado"], ESTADO_PAGADO)
            self.assertEqual(regularizacion["saldo_pendiente_eur"], "0.00")

    def test_rechaza_concepto_no_permitido(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            gestor = GestorFallaV9(memoria_path=self._memory_path(tmpdir))

            with self.assertRaises(GestorFallaError):
                gestor.ejecutar_cobro("Pau", "100", "merchandising")


if __name__ == "__main__":
    unittest.main()
