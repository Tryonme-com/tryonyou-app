"""Tests para reporte_diario_soberania_v10 — _mensaje_liquidacion, DailyManagerV10."""

from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from reporte_diario_soberania_v10 import (
    DailyManagerV10,
    _mensaje_liquidacion,
    reporte_diario_soberania,
)


# ---------------------------------------------------------------------------
# _mensaje_liquidacion
# ---------------------------------------------------------------------------


class TestMensajeLiquidacion(unittest.TestCase):
    def test_future_days_contains_dias_restantes(self) -> None:
        msg = _mensaje_liquidacion(30)
        self.assertIn("30 días", msg)

    def test_future_days_contains_siren(self) -> None:
        msg = _mensaje_liquidacion(10)
        self.assertIn("943 610 196", msg)

    def test_future_days_contains_capital(self) -> None:
        msg = _mensaje_liquidacion(5)
        self.assertIn("98.000", msg)

    def test_zero_days_hito_alcanzado(self) -> None:
        msg = _mensaje_liquidacion(0)
        self.assertIn("HITO ALCANZADO", msg)

    def test_zero_days_contains_siren(self) -> None:
        msg = _mensaje_liquidacion(0)
        self.assertIn("943 610 196", msg)

    def test_zero_days_contains_boom(self) -> None:
        msg = _mensaje_liquidacion(0)
        self.assertIn("BOOM", msg)

    def test_past_days_revisar_estado(self) -> None:
        msg = _mensaje_liquidacion(-1)
        self.assertIn("revisar estado", msg)

    def test_past_days_fecha_objetivo_present(self) -> None:
        msg = _mensaje_liquidacion(-5)
        self.assertIn("2026", msg)


# ---------------------------------------------------------------------------
# reporte_diario_soberania
# ---------------------------------------------------------------------------


class TestReporteDiarioSoberania(unittest.TestCase):
    def test_returns_string(self) -> None:
        result = reporte_diario_soberania()
        self.assertIsInstance(result, str)

    def test_contains_monitor_title(self) -> None:
        result = reporte_diario_soberania()
        self.assertIn("MONITOR DE LIQUIDACIÓN", result)


# ---------------------------------------------------------------------------
# DailyManagerV10
# ---------------------------------------------------------------------------


class TestDailyManagerV10Init(unittest.TestCase):
    def setUp(self) -> None:
        self.manager = DailyManagerV10()

    def test_siren_is_set(self) -> None:
        self.assertEqual(self.manager.siren, "943 610 196")

    def test_today_is_string(self) -> None:
        self.assertIsInstance(self.manager.today, str)

    def test_today_format_dd_mm_yyyy(self) -> None:
        parts = self.manager.today.split("/")
        self.assertEqual(len(parts), 3)
        self.assertEqual(len(parts[2]), 4)  # year is 4 digits


class TestDailyManagerV10GetStatusReport(unittest.TestCase):
    def setUp(self) -> None:
        self.manager = DailyManagerV10()
        self.report = self.manager.get_status_report()

    def test_returns_string(self) -> None:
        self.assertIsInstance(self.report, str)

    def test_contains_daily_report_header(self) -> None:
        self.assertIn("DAILY REPORT", self.report)

    def test_contains_empire_mode(self) -> None:
        self.assertIn("EMPIRE MODE ACTIVE", self.report)

    def test_contains_siren(self) -> None:
        self.assertIn("943 610 196", self.report)

    def test_contains_hitos_del_dia(self) -> None:
        self.assertIn("HITOS DEL DÍA", self.report)

    def test_contains_p0_liquidacion(self) -> None:
        self.assertIn("P0", self.report)

    def test_contains_snap_emotion_sdk(self) -> None:
        self.assertIn("The Snap", self.report)

    def test_contains_supercommit(self) -> None:
        self.assertIn("supercommit_max", self.report)

    def test_contains_dia_d(self) -> None:
        self.assertIn("9 de mayo", self.report)

    def test_contains_today_date(self) -> None:
        self.assertIn(self.manager.today, self.report)

    def test_contains_capital_reference(self) -> None:
        self.assertIn("98.000", self.report)


class TestDailyManagerV10SendUpdateNoToken(unittest.TestCase):
    def setUp(self) -> None:
        for key in ("TELEGRAM_BOT_TOKEN", "TELEGRAM_TOKEN"):
            os.environ.pop(key, None)

    def test_returns_false_without_token(self) -> None:
        manager = DailyManagerV10()
        result = manager.send_update()
        self.assertFalse(result)


class TestDailyManagerV10SendUpdateSuccess(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["TELEGRAM_BOT_TOKEN"] = "test-token-123"
        os.environ["TELEGRAM_CHAT_ID"] = "999999999"

    def tearDown(self) -> None:
        os.environ.pop("TELEGRAM_BOT_TOKEN", None)
        os.environ.pop("TELEGRAM_CHAT_ID", None)

    @patch("reporte_diario_soberania_v10.requests")
    def test_returns_true_on_200(self, mock_requests: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_requests.post.return_value = mock_response

        manager = DailyManagerV10()
        result = manager.send_update()
        self.assertTrue(result)

    @patch("reporte_diario_soberania_v10.requests")
    def test_returns_false_on_non_200(self, mock_requests: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_requests.post.return_value = mock_response

        manager = DailyManagerV10()
        result = manager.send_update()
        self.assertFalse(result)

    @patch("reporte_diario_soberania_v10.requests")
    def test_calls_correct_telegram_url(self, mock_requests: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_requests.post.return_value = mock_response

        manager = DailyManagerV10()
        manager.send_update()

        call_args = mock_requests.post.call_args
        url = call_args[0][0]
        self.assertIn("api.telegram.org", url)
        self.assertIn("test-token-123", url)

    @patch("reporte_diario_soberania_v10.requests")
    def test_uses_env_chat_id(self, mock_requests: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_requests.post.return_value = mock_response

        manager = DailyManagerV10()
        manager.send_update()

        call_kwargs = mock_requests.post.call_args[1]
        payload = call_kwargs["json"]
        self.assertEqual(payload["chat_id"], "999999999")

    @patch("reporte_diario_soberania_v10.requests")
    def test_falls_back_to_default_chat_id_without_env(self, mock_requests: MagicMock) -> None:
        os.environ.pop("TELEGRAM_CHAT_ID", None)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_requests.post.return_value = mock_response

        manager = DailyManagerV10()
        manager.send_update()

        call_kwargs = mock_requests.post.call_args[1]
        payload = call_kwargs["json"]
        self.assertEqual(payload["chat_id"], DailyManagerV10.DEFAULT_CHAT_ID)

    @patch("reporte_diario_soberania_v10.requests")
    def test_returns_false_on_exception(self, mock_requests: MagicMock) -> None:
        mock_requests.post.side_effect = Exception("network error")

        manager = DailyManagerV10()
        result = manager.send_update()
        self.assertFalse(result)

    @patch("reporte_diario_soberania_v10.requests")
    def test_uses_telegram_token_fallback(self, mock_requests: MagicMock) -> None:
        os.environ.pop("TELEGRAM_BOT_TOKEN", None)
        os.environ["TELEGRAM_TOKEN"] = "fallback-token"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_requests.post.return_value = mock_response

        manager = DailyManagerV10()
        result = manager.send_update()
        self.assertTrue(result)

        call_args = mock_requests.post.call_args
        url = call_args[0][0]
        self.assertIn("fallback-token", url)

        os.environ.pop("TELEGRAM_TOKEN", None)


if __name__ == "__main__":
    unittest.main()
