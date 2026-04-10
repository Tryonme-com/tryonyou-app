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
    SEPA_SWEEP_MARGIN_MINUTES,
    check_bank_impact,
    check_immediate_liquidity,
    formato_consola,
    formato_liquidez,
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


class TestCheckImmediateLiquidity(unittest.TestCase):
    def test_before_sweep_returns_minutes(self) -> None:
        result = check_immediate_liquidity(now=datetime(2026, 4, 10, 7, 30))
        self.assertFalse(result["sweep_started"])
        self.assertEqual(result["minutes_left"], 90)
        self.assertIn("EN TRÁNSITO", result["status"])
        self.assertIn("90 minutos", result["status"])
        self.assertIn("SEPA", result["status"])

    def test_after_sweep_started(self) -> None:
        result = check_immediate_liquidity(now=datetime(2026, 4, 10, 9, 5))
        self.assertTrue(result["sweep_started"])
        self.assertEqual(result["minutes_left"], 0)
        self.assertIn("BARRIDO INICIADO", result["status"])
        self.assertIn(str(SEPA_SWEEP_MARGIN_MINUTES), result["status"])

    def test_at_exactly_nine(self) -> None:
        result = check_immediate_liquidity(now=datetime(2026, 4, 10, 9, 0))
        self.assertTrue(result["sweep_started"])

    def test_at_midnight(self) -> None:
        result = check_immediate_liquidity(now=datetime(2026, 4, 10, 0, 0))
        self.assertFalse(result["sweep_started"])
        self.assertEqual(result["minutes_left"], 540)

    def test_one_minute_before(self) -> None:
        result = check_immediate_liquidity(now=datetime(2026, 4, 10, 8, 59))
        self.assertFalse(result["sweep_started"])
        self.assertEqual(result["minutes_left"], 1)

    def test_result_has_expected_keys(self) -> None:
        result = check_immediate_liquidity(now=datetime(2026, 4, 10, 10, 0))
        for key in ("status", "sweep_started", "minutes_left", "timestamp"):
            self.assertIn(key, result)

    def test_timestamp_is_iso(self) -> None:
        ts = datetime(2026, 4, 10, 6, 45)
        result = check_immediate_liquidity(now=ts)
        self.assertEqual(result["timestamp"], ts.isoformat())


class TestFormatoLiquidez(unittest.TestCase):
    def test_contains_header(self) -> None:
        result = check_immediate_liquidity(now=datetime(2026, 4, 10, 8, 0))
        text = formato_liquidez(result)
        self.assertIn("MONITOR DE LIQUIDEZ", text)

    def test_contains_patent(self) -> None:
        result = check_immediate_liquidity(now=datetime(2026, 4, 10, 10, 0))
        text = formato_liquidez(result)
        self.assertIn("PCT/EP2025/067317", text)
        self.assertIn("Protocolo de Soberanía V10", text)


class TestMain(unittest.TestCase):
    def test_main_returns_zero(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main([])
        self.assertEqual(rc, 0)
        output = buf.getvalue()
        self.assertIn("AUDITORÍA DE IMPACTO MATINAL", output)
        self.assertIn("MONITOR DE LIQUIDEZ", output)

    def test_main_liquidez_only(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--liquidez"])
        self.assertEqual(rc, 0)
        output = buf.getvalue()
        self.assertNotIn("AUDITORÍA DE IMPACTO MATINAL", output)
        self.assertIn("MONITOR DE LIQUIDEZ", output)


if __name__ == "__main__":
    unittest.main()
