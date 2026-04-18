from __future__ import annotations

import unittest
from datetime import datetime

import supercommit_max_autonomia as autonomia


class TestSupercommitMaxAutonomia(unittest.TestCase):
    def test_security_window_true_on_tuesday_8am(self) -> None:
        now = datetime(2026, 4, 21, 8, 0, 0)
        self.assertTrue(autonomia._security_window(now))

    def test_security_window_false_other_time(self) -> None:
        now = datetime(2026, 4, 21, 9, 0, 0)
        self.assertFalse(autonomia._security_window(now))

    def test_truthy_helper(self) -> None:
        self.assertTrue(autonomia._truthy("1"))
        self.assertTrue(autonomia._truthy("YES"))
        self.assertFalse(autonomia._truthy("0"))

    def test_telegram_reporter_not_configured(self) -> None:
        reporter = autonomia.TelegramReporter(token="", chat_id="")
        self.assertFalse(reporter.configured)


if __name__ == "__main__":
    unittest.main()
