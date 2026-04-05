"""Tests para el Tracker de Liquidez 75001."""

from __future__ import annotations

import datetime
import os
import sys
import unittest

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from tracker_liquidez_75001 import (
    PAYOUTS,
    _fecha_llegada,
    _status_pago,
    main,
    reporte_llegada,
)

_HOY = datetime.date(2026, 4, 5)


class TestStatusPago(unittest.TestCase):
    def test_dias_espera_positivo_devuelve_esperando(self) -> None:
        self.assertEqual(_status_pago({"dias_espera": 2}), "⏳ ESPERANDO")

    def test_dias_espera_cero_devuelve_bloqueado(self) -> None:
        self.assertEqual(_status_pago({"dias_espera": 0}), "🔐 BLOQUEADO (KYC)")


class TestFechaLlegada(unittest.TestCase):
    def test_con_dias_espera_dos(self) -> None:
        resultado = _fecha_llegada({"dias_espera": 2}, hoy=_HOY)
        self.assertEqual(resultado, datetime.date(2026, 4, 7))

    def test_con_dias_espera_cero(self) -> None:
        resultado = _fecha_llegada({"dias_espera": 0}, hoy=_HOY)
        self.assertEqual(resultado, _HOY)


class TestReporteLlegada(unittest.TestCase):
    def test_retorna_string_no_vacio(self) -> None:
        resultado = reporte_llegada(hoy=_HOY)
        self.assertIsInstance(resultado, str)
        self.assertGreater(len(resultado), 0)

    def test_contiene_cabecera(self) -> None:
        resultado = reporte_llegada(hoy=_HOY)
        self.assertIn("ESTADO DE LAS ARTERIAS FINANCIERAS", resultado)

    def test_contiene_stripe(self) -> None:
        resultado = reporte_llegada(hoy=_HOY)
        self.assertIn("Stripe", resultado)
        self.assertIn("1600.0", resultado)
        self.assertIn("⏳ ESPERANDO", resultado)

    def test_contiene_bnl_bloqueado(self) -> None:
        resultado = reporte_llegada(hoy=_HOY)
        self.assertIn("BNL Interno", resultado)
        self.assertIn("32800.0", resultado)
        self.assertIn("🔐 BLOQUEADO (KYC)", resultado)

    def test_contiene_cierre(self) -> None:
        resultado = reporte_llegada(hoy=_HOY)
        self.assertIn("PA, PA, PA.", resultado)

    def test_payouts_por_defecto(self) -> None:
        # Sin parámetros usa la lista PAYOUTS global
        resultado = reporte_llegada(hoy=_HOY)
        self.assertEqual(resultado.count("💰"), len(PAYOUTS))

    def test_payouts_personalizados(self) -> None:
        custom = [{"fuente": "Test", "monto": 500.0, "dias_espera": 3}]
        resultado = reporte_llegada(payouts=custom, hoy=_HOY)
        self.assertIn("Test", resultado)
        self.assertIn("500.0", resultado)
        self.assertIn("⏳ ESPERANDO", resultado)


class TestMain(unittest.TestCase):
    def test_main_retorna_cero(self) -> None:
        self.assertEqual(main(), 0)


if __name__ == "__main__":
    unittest.main()
