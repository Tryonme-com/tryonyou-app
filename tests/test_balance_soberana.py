"""Tests para balance_total_soberano y sus constantes."""

from __future__ import annotations

import io
import os
import sys
import unittest

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
_API = os.path.join(_ROOT, "api")
for _p in (_ROOT, _API):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from balance_soberana import (
    ATRASOS_PILOTO,
    NODO_LVMH,
    NODO_WESTFIELD,
    SUBVENCION_BFT,
    TRANSFERENCIA_IP_UNIT,
    balance_total_soberano,
)

EXPECTED_TOTAL = (
    ATRASOS_PILOTO
    + (NODO_LVMH + NODO_WESTFIELD)
    + (TRANSFERENCIA_IP_UNIT * 2)
    + SUBVENCION_BFT
)


class TestBalanceTotalSoberano(unittest.TestCase):
    def test_returns_float(self) -> None:
        self.assertIsInstance(balance_total_soberano(), float)

    def test_total_value(self) -> None:
        self.assertAlmostEqual(balance_total_soberano(), EXPECTED_TOTAL, places=2)

    def test_total_is_390680(self) -> None:
        self.assertAlmostEqual(balance_total_soberano(), 390_680.00, places=2)

    def test_prints_capital_line(self) -> None:
        captured = io.StringIO()
        sys.stdout = captured
        try:
            balance_total_soberano()
        finally:
            sys.stdout = sys.__stdout__
        output = captured.getvalue()
        self.assertIn("CAPITAL TOTAL RECLAMADO", output)
        self.assertIn("390,680.00", output)

    def test_prints_estado_line(self) -> None:
        captured = io.StringIO()
        sys.stdout = captured
        try:
            balance_total_soberano()
        finally:
            sys.stdout = sys.__stdout__
        output = captured.getvalue()
        self.assertIn("Pipeline de cobro al 100% de capacidad", output)

    def test_prints_header_line(self) -> None:
        captured = io.StringIO()
        sys.stdout = captured
        try:
            balance_total_soberano()
        finally:
            sys.stdout = sys.__stdout__
        output = captured.getvalue()
        self.assertIn("ESTADO FINANCIERO TOTAL: TRYONYOU V10", output)


class TestBalanceSoberanaConstants(unittest.TestCase):
    def test_atrasos_piloto(self) -> None:
        self.assertAlmostEqual(ATRASOS_PILOTO, 69_180.00, places=2)

    def test_nodo_lvmh(self) -> None:
        self.assertAlmostEqual(NODO_LVMH, 22_500.00, places=2)

    def test_nodo_westfield(self) -> None:
        self.assertAlmostEqual(NODO_WESTFIELD, 12_500.00, places=2)

    def test_transferencia_ip_unit(self) -> None:
        self.assertAlmostEqual(TRANSFERENCIA_IP_UNIT, 98_250.00, places=2)

    def test_subvencion_bft(self) -> None:
        self.assertAlmostEqual(SUBVENCION_BFT, 90_000.00, places=2)

    def test_nodos_activos_sum(self) -> None:
        self.assertAlmostEqual(NODO_LVMH + NODO_WESTFIELD, 35_000.00, places=2)

    def test_transferencia_ip_double(self) -> None:
        self.assertAlmostEqual(TRANSFERENCIA_IP_UNIT * 2, 196_500.00, places=2)


if __name__ == "__main__":
    unittest.main()
