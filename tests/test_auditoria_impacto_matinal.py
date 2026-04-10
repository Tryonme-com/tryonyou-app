"""Tests for auditoria_impacto_matinal.py (Protocolo V10)."""

from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout
from datetime import datetime

from auditoria_impacto_matinal import (
    CLEARING_HOUR,
    INGRESOS_ESPERADOS,
    OBJETIVO_TOTAL,
    check_bank_impact,
    formato_consola,
    main,
)


class TestCheckBankImpact(unittest.TestCase):
    def test_clearing_done_after_nine(self) -> None:
        result = check_bank_impact(now=datetime(2026, 4, 10, 10, 30))
        self.assertTrue(result["clearing"])
        self.assertIn("clearing ha finalizado", result["status"])

    def test_clearing_not_done_before_nine(self) -> None:
        result = check_bank_impact(now=datetime(2026, 4, 10, 7, 45))
        self.assertFalse(result["clearing"])
        self.assertIn("Faltan", result["status"])
        self.assertIn("barrido bancario", result["status"])

    def test_clearing_at_exactly_nine(self) -> None:
        result = check_bank_impact(now=datetime(2026, 4, 10, 9, 0))
        self.assertTrue(result["clearing"])

    def test_clearing_at_midnight(self) -> None:
        result = check_bank_impact(now=datetime(2026, 4, 10, 0, 0))
        self.assertFalse(result["clearing"])

    def test_result_has_expected_keys(self) -> None:
        result = check_bank_impact(now=datetime(2026, 4, 10, 12, 0))
        for key in ("status", "clearing", "objetivo", "ingresos", "timestamp"):
            self.assertIn(key, result)

    def test_objetivo_matches_constant(self) -> None:
        result = check_bank_impact(now=datetime(2026, 4, 10, 12, 0))
        self.assertEqual(result["objetivo"], OBJETIVO_TOTAL)

    def test_ingresos_match_constants(self) -> None:
        result = check_bank_impact(now=datetime(2026, 4, 10, 12, 0))
        self.assertEqual(result["ingresos"], INGRESOS_ESPERADOS)

    def test_timestamp_is_iso(self) -> None:
        ts = datetime(2026, 4, 10, 8, 15)
        result = check_bank_impact(now=ts)
        self.assertEqual(result["timestamp"], ts.isoformat())

    def test_minutes_remaining_calculation(self) -> None:
        result = check_bank_impact(now=datetime(2026, 4, 10, 8, 30))
        self.assertIn("30 minutos", result["status"])


class TestFormatoConsola(unittest.TestCase):
    def test_contains_header(self) -> None:
        result = check_bank_impact(now=datetime(2026, 4, 10, 10, 0))
        text = formato_consola(result)
        self.assertIn("AUDITORÍA DE IMPACTO MATINAL", text)

    def test_contains_ingresos(self) -> None:
        result = check_bank_impact(now=datetime(2026, 4, 10, 10, 0))
        text = formato_consola(result)
        self.assertIn("Lafayette", text)
        self.assertIn("LVMH", text)
        self.assertIn("27,500.00", text)
        self.assertIn("22,500.00", text)

    def test_contains_patent(self) -> None:
        result = check_bank_impact(now=datetime(2026, 4, 10, 10, 0))
        text = formato_consola(result)
        self.assertIn("PCT/EP2025/067317", text)
        self.assertIn("Protocolo de Soberanía V10", text)


class TestMain(unittest.TestCase):
    def test_main_returns_zero(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main()
        self.assertEqual(rc, 0)
        self.assertIn("AUDITORÍA DE IMPACTO MATINAL", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
