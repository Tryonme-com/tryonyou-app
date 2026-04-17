"""Tests para GestorFallaV9."""

from __future__ import annotations

import datetime
import os
import sys
import tempfile
import unittest

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from gestor_falla_v9 import GestorFallaV9


class TestGestorFallaV9(unittest.TestCase):
    def test_ejecutar_cobro_pagado_calcula_comision_y_neto(self) -> None:
        gestor = GestorFallaV9(comision_pct=0.08, cuota_base=50.0, memoria_path=None)
        asiento = gestor.ejecutar_cobro(
            nombre="Pau",
            bruto=100.0,
            concepto="Cuota Abril",
            fallero_id="fallero_001",
            referencia_externa="stripe_001",
            fecha=datetime.date(2026, 4, 17),
        )

        self.assertEqual(asiento["ID de Fallero"], "FALLERO_001")
        self.assertEqual(asiento["Importe Bruto"], 100.0)
        self.assertEqual(asiento["Comisión Aplicada"], 8.0)
        self.assertEqual(asiento["Neto Resultante"], 92.0)
        self.assertEqual(asiento["Estado"], "PAGADO")
        self.assertEqual(asiento["Saldo Pendiente"], 0.0)

    def test_cobro_inferior_a_cuota_marca_pendiente_regularizar(self) -> None:
        gestor = GestorFallaV9(comision_pct=0.08, cuota_base=50.0, memoria_path=None)
        asiento = gestor.ejecutar_cobro(
            nombre="Lola",
            bruto=40.0,
            concepto="Cuota Mayo",
            fecha=datetime.date(2026, 4, 17),
        )

        self.assertEqual(asiento["Estado"], "Pendiente de regularizar")
        self.assertEqual(asiento["Saldo Pendiente"], 10.0)

    def test_detecta_duplicados_por_referencia_externa(self) -> None:
        gestor = GestorFallaV9(comision_pct=0.08, cuota_base=50.0, memoria_path=None)
        gestor.ejecutar_cobro(
            nombre="Paco",
            bruto=60.0,
            concepto="Evento Primavera",
            referencia_externa="checkout_abc",
            fecha=datetime.date(2026, 4, 17),
        )

        with self.assertRaises(ValueError):
            gestor.ejecutar_cobro(
                nombre="Paco",
                bruto=60.0,
                concepto="Evento Primavera",
                referencia_externa="checkout_abc",
                fecha=datetime.date(2026, 4, 17),
            )

    def test_concepto_invalido_lanza_error(self) -> None:
        gestor = GestorFallaV9(memoria_path=None)
        with self.assertRaises(ValueError):
            gestor.ejecutar_cobro(
                nombre="Ana",
                bruto=50.0,
                concepto="Donación libre",
            )

    def test_persistencia_memoria_y_recarga(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            memoria_path = os.path.join(tmpdir, "falla_memorias.json")
            gestor = GestorFallaV9(memoria_path=memoria_path)
            gestor.ejecutar_cobro(
                nombre="Marta",
                bruto=45.0,
                concepto="Cuota Abril",
                fallero_id="id_marta",
                referencia_externa="ext_001",
                fecha=datetime.date(2026, 4, 17),
            )

            gestor_recargado = GestorFallaV9(memoria_path=memoria_path)
            self.assertEqual(len(gestor_recargado.registro_memoria), 1)
            self.assertIn("ID_MARTA", gestor_recargado.saldos_pendientes)
            self.assertEqual(gestor_recargado.saldos_pendientes["ID_MARTA"], 5.0)

    def test_procesar_registros_devuelve_ok_y_errores(self) -> None:
        gestor = GestorFallaV9(memoria_path=None)
        resultados = gestor.procesar_registros(
            [
                {"nombre": "Pau", "bruto": 100, "concepto": "Cuota Abril"},
                {"nombre": "A", "bruto": 10, "concepto": "Cuota Abril"},
            ]
        )
        self.assertEqual(len(resultados), 2)
        self.assertTrue(resultados[0]["ok"])
        self.assertFalse(resultados[1]["ok"])


if __name__ == "__main__":
    unittest.main()
