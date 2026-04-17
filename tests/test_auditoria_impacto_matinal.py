"""Tests for auditoria_impacto_matinal.py (Protocolo V10)."""

from __future__ import annotations

import io
import types
import unittest
from contextlib import redirect_stdout
from datetime import datetime
from unittest.mock import patch

from auditoria_impacto_matinal import (
    CLEARING_HOUR,
    INGRESOS_ESPERADOS,
    OBJETIVO_TOTAL,
    SEPA_SWEEP_MARGIN_MINUTES,
    SIREN_REF,
    TARGET_INVOICE_AMOUNTS_CENTS,
    aggressive_invoice_reconciliation,
    check_bank_impact,
    check_immediate_liquidity,
    formato_consola,
    formato_liquidez,
    formato_reconciliacion,
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


class TestAggressiveInvoiceReconciliation(unittest.TestCase):
    def test_returns_error_when_key_missing(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            result = aggressive_invoice_reconciliation(now=datetime(2026, 4, 10, 10, 0))
        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], "stripe_secret_missing_or_invalid")
        self.assertEqual(result["retried"], 0)

    def test_retries_only_target_open_or_processing(self) -> None:
        calls_modify: list[tuple[str, dict]] = []
        calls_pay: list[str] = []

        invoices = [
            {
                "id": "in_laf_open",
                "total": 2_750_000,
                "status": "open",
                "metadata": {"legacy": "1"},
            },
            {
                "id": "in_lvmh_processing",
                "amount_due": 2_250_000,
                "status": "processing",
                "metadata": {},
            },
            {
                "id": "in_lvmh_paid",
                "total": 2_250_000,
                "status": "paid",
                "metadata": {},
            },
            {
                "id": "in_other",
                "total": 999,
                "status": "open",
                "metadata": {},
            },
        ]

        class _FakeList:
            def auto_paging_iter(self):
                return iter(invoices)

        def _list(limit: int = 100):  # noqa: ARG001
            return _FakeList()

        def _modify(invoice_id: str, metadata: dict):
            calls_modify.append((invoice_id, metadata))
            return {"id": invoice_id}

        def _pay(invoice_id: str):
            calls_pay.append(invoice_id)
            return {"id": invoice_id, "status": "paid"}

        fake_invoice_api = types.SimpleNamespace(list=_list, modify=_modify, pay=_pay)
        fake_stripe = types.SimpleNamespace(Invoice=fake_invoice_api, api_key="")

        with patch.dict("sys.modules", {"stripe": fake_stripe}):
            with patch.dict("os.environ", {"STRIPE_SECRET_KEY": "sk_test_dummy"}):
                result = aggressive_invoice_reconciliation(
                    now=datetime(2026, 4, 10, 10, 0)
                )

        self.assertTrue(result["ok"])
        self.assertEqual(result["status"], "done")
        self.assertEqual(result["scanned"], 4)
        self.assertEqual(result["matched"], 3)
        self.assertEqual(result["retried"], 2)
        self.assertEqual(result["errors"], 0)
        self.assertEqual(calls_pay, ["in_laf_open", "in_lvmh_processing"])

        modified_ids = [invoice_id for invoice_id, _ in calls_modify]
        self.assertEqual(modified_ids, ["in_laf_open", "in_lvmh_processing"])

        for invoice_id, metadata in calls_modify:
            self.assertEqual(metadata["siren"], SIREN_REF.replace(" ", ""))
            self.assertIn(metadata["target_amount_cents"], {"2750000", "2250000"})
            self.assertIn(
                metadata["target_origin"],
                {TARGET_INVOICE_AMOUNTS_CENTS[2_750_000], TARGET_INVOICE_AMOUNTS_CENTS[2_250_000]},
            )
            self.assertEqual(metadata["reconciliation_phase"], "aggressive_retry_v10")
            if invoice_id == "in_laf_open":
                self.assertEqual(metadata["legacy"], "1")


class TestFormatoReconciliacion(unittest.TestCase):
    def test_contains_core_fields(self) -> None:
        text = formato_reconciliacion(
            {
                "timestamp": "2026-04-10T10:00:00",
                "status": "done",
                "error": "",
                "scanned": 2,
                "matched": 2,
                "retried": 1,
                "errors": 0,
                "items": [
                    {
                        "invoice_id": "in_123",
                        "origin": "Lafayette",
                        "amount_cents": 2750000,
                        "status": "open",
                        "action": "forced_retry_sent",
                    }
                ],
            }
        )
        self.assertIn("FASE DE RECONCILIACIÓN AGRESIVA", text)
        self.assertIn("in_123", text)
        self.assertIn("2750000 cents", text)
        self.assertIn("Retries forzados: 1", text)
        self.assertIn("SIREN", text)


if __name__ == "__main__":
    unittest.main()
