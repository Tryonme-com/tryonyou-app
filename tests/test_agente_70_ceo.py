"""Tests para Agente70CEO: veto de calidad, payout y purga de legado."""

from __future__ import annotations

import io
import sys
import os
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from agente_70_ceo import PAYOUT_CLOSE_HOUR, PAYOUT_OPEN_HOUR, QUALITY_THRESHOLD, Agente70CEO


class TestAgente70CEOInit(unittest.TestCase):
    def setUp(self) -> None:
        self.ceo = Agente70CEO()

    def test_identity(self) -> None:
        self.assertEqual(self.ceo.identity, "Agente 70")

    def test_role(self) -> None:
        self.assertEqual(self.ceo.role, "CEO & Supreme Auditor")

    def test_siren(self) -> None:
        self.assertEqual(self.ceo.siren, "943610196")

    def test_vault_status(self) -> None:
        self.assertEqual(self.ceo.vault_status, "LOCKED_UNTIL_0900")


class TestPowerOfVeto(unittest.TestCase):
    def setUp(self) -> None:
        self.ceo = Agente70CEO()

    def test_approves_at_threshold(self) -> None:
        self.assertTrue(self.ceo.power_of_veto("task-1", QUALITY_THRESHOLD))

    def test_approves_above_threshold(self) -> None:
        self.assertTrue(self.ceo.power_of_veto("task-2", 0.99))

    def test_approves_perfect_quality(self) -> None:
        self.assertTrue(self.ceo.power_of_veto("task-3", 1.0))

    def test_rejects_below_threshold(self) -> None:
        self.assertFalse(self.ceo.power_of_veto("task-4", 0.94))

    def test_rejects_zero_quality(self) -> None:
        self.assertFalse(self.ceo.power_of_veto("task-5", 0.0))

    def test_veto_prints_task_id(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.ceo.power_of_veto("e5090863", 0.50)
        self.assertIn("e5090863", buf.getvalue())

    def test_approval_prints_nothing(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.ceo.power_of_veto("task-ok", 1.0)
        self.assertEqual(buf.getvalue(), "")


class TestAuthorizePayout(unittest.TestCase):
    def setUp(self) -> None:
        self.ceo = Agente70CEO()

    def test_authorized_at_open_hour(self) -> None:
        with patch("agente_70_ceo.datetime") as mock_dt:
            mock_dt.now.return_value.hour = PAYOUT_OPEN_HOUR
            self.assertTrue(self.ceo.authorize_payout(1000.0))

    def test_authorized_after_open_hour(self) -> None:
        with patch("agente_70_ceo.datetime") as mock_dt:
            mock_dt.now.return_value.hour = 12
            self.assertTrue(self.ceo.authorize_payout(500.0))

    def test_authorized_before_close_hour(self) -> None:
        with patch("agente_70_ceo.datetime") as mock_dt:
            mock_dt.now.return_value.hour = 2
            self.assertTrue(self.ceo.authorize_payout(750.0))

    def test_not_authorized_in_locked_window(self) -> None:
        with patch("agente_70_ceo.datetime") as mock_dt:
            mock_dt.now.return_value.hour = 5
            self.assertFalse(self.ceo.authorize_payout(999.0))

    def test_not_authorized_at_close_boundary(self) -> None:
        with patch("agente_70_ceo.datetime") as mock_dt:
            mock_dt.now.return_value.hour = PAYOUT_CLOSE_HOUR
            self.assertFalse(self.ceo.authorize_payout(100.0))

    def test_authorized_prints_amount(self) -> None:
        buf = io.StringIO()
        with patch("agente_70_ceo.datetime") as mock_dt:
            mock_dt.now.return_value.hour = 10
            with redirect_stdout(buf):
                self.ceo.authorize_payout(450000.0)
        self.assertIn("450000.0", buf.getvalue())

    def test_locked_prints_wait_message(self) -> None:
        buf = io.StringIO()
        with patch("agente_70_ceo.datetime") as mock_dt:
            mock_dt.now.return_value.hour = 6
            with redirect_stdout(buf):
                self.ceo.authorize_payout(100.0)
        self.assertIn("09:00", buf.getvalue())


class TestPurgeLegacy(unittest.TestCase):
    def setUp(self) -> None:
        self.ceo = Agente70CEO()

    def test_returns_clean_state(self) -> None:
        result = self.ceo.purge_legacy()
        self.assertEqual(result, "Clean State Confirmed.")

    def test_prints_purge_message(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.ceo.purge_legacy()
        self.assertIn("PURGE", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
