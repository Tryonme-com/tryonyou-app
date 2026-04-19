from __future__ import annotations

import os
import unittest
from datetime import datetime
from unittest.mock import patch
from zoneinfo import ZoneInfo

import master_fatality


PARIS = ZoneInfo("Europe/Paris")


class TestFatalitySecurityStatus(unittest.TestCase):
    def test_slot_open_without_capital_confirmation_awaits_entry(self) -> None:
        now = datetime(2026, 4, 21, 8, 30, tzinfo=PARIS)  # martes
        with patch.dict(os.environ, {}, clear=True):
            status = master_fatality.dossier_fatality_security_status(now=now)
        self.assertTrue(status["checkpoint_window_open"])
        self.assertFalse(status["entry_confirmed"])
        self.assertFalse(status["dossier_fatality_activated"])
        self.assertEqual("awaiting_capital_confirmation", status["status"])

    def test_slot_open_with_450k_entry_activates_dossier(self) -> None:
        now = datetime(2026, 4, 21, 8, 5, tzinfo=PARIS)  # martes
        with patch.dict(os.environ, {"FATALITY_CAPITAL_ENTRY_EUR": "450000"}, clear=True):
            status = master_fatality.dossier_fatality_security_status(now=now)
        self.assertTrue(status["checkpoint_window_open"])
        self.assertTrue(status["entry_confirmed"])
        self.assertTrue(status["dossier_fatality_activated"])
        self.assertEqual("active", status["status"])

    def test_before_slot_keeps_status_scheduled_even_with_manual_confirmation(self) -> None:
        now = datetime(2026, 4, 21, 7, 59, tzinfo=PARIS)  # martes antes de 08:00
        with patch.dict(os.environ, {"FATALITY_CAPITAL_CONFIRMED": "1"}, clear=True):
            status = master_fatality.dossier_fatality_security_status(now=now)
        self.assertFalse(status["checkpoint_window_open"])
        self.assertTrue(status["entry_confirmed"])
        self.assertFalse(status["dossier_fatality_activated"])
        self.assertEqual("scheduled", status["status"])


if __name__ == "__main__":
    unittest.main()
