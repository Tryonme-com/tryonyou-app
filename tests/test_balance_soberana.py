"""Tests para balance_total_soberano y su ledger soberano actualizado."""

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
    BPIFRANCE_LEDGER,
    NODO_LVMH,
    NODO_WESTFIELD,
    SUBVENCION_BFT,
    TRANSFERENCIA_IP_UNIT,
    balance_total_soberano,
    ledger_soberano,
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

    def test_total_is_527588(self) -> None:
        self.assertAlmostEqual(balance_total_soberano(), 527_588.00, places=2)

    def test_prints_capital_line(self) -> None:
        captured = io.StringIO()
        sys.stdout = captured
        try:
            balance_total_soberano()
        finally:
            sys.stdout = sys.__stdout__
        output = captured.getvalue()
        self.assertIn("CAPITAL TOTAL RECLAMADO", output)
        self.assertIn("527,588.00", output)

    def test_prints_estado_line(self) -> None:
        captured = io.StringIO()
        sys.stdout = captured
        try:
            balance_total_soberano()
        finally:
            sys.stdout = sys.__stdout__
        output = captured.getvalue()
        self.assertIn("Pipeline de cobro al 100% de capacidad", output)
        self.assertIn("BPIFRANCE en Ejecución Prioritaria", output)

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
        self.assertAlmostEqual(SUBVENCION_BFT, 226_908.00, places=2)

    def test_nodos_activos_sum(self) -> None:
        self.assertAlmostEqual(NODO_LVMH + NODO_WESTFIELD, 35_000.00, places=2)

    def test_transferencia_ip_double(self) -> None:
        self.assertAlmostEqual(TRANSFERENCIA_IP_UNIT * 2, 196_500.00, places=2)


class TestLedgerSoberano(unittest.TestCase):
    def test_bpifrance_status(self) -> None:
        self.assertEqual(BPIFRANCE_LEDGER["estado_anterior"], "En Proceso")
        self.assertEqual(BPIFRANCE_LEDGER["estado_actual"], "Ejecución Prioritaria")

    def test_ledger_returns_expected_structure(self) -> None:
        ledger = ledger_soberano()
        self.assertEqual(ledger["bpifrance"]["estado_actual"], "Ejecución Prioritaria")
        self.assertAlmostEqual(ledger["capital_total_reclamado_eur"], 527_588.00, places=2)


if __name__ == "__main__":
    unittest.main()
