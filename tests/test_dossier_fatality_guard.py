"""Tests para dossier_fatality_guard.py."""

from __future__ import annotations

import os
import unittest
from datetime import datetime

from dossier_fatality_guard import evaluate_dossier_fatality_window, parse_now


class TestDossierFatalityGuard(unittest.TestCase):
    def test_parse_now_iso(self) -> None:
        dt = parse_now("2026-04-21T08:00:00")
        self.assertIsInstance(dt, datetime)
        self.assertEqual(dt.year, 2026)
        self.assertEqual(dt.month, 4)
        self.assertEqual(dt.day, 21)
        self.assertEqual(dt.hour, 8)

    def test_guard_blocks_outside_window_even_with_confirmation(self) -> None:
        outcome = evaluate_dossier_fatality_window(
            now_dt=parse_now("2026-04-21T07:59:00"),
            capital_confirmed=True,
        )
        self.assertEqual(outcome["status"], "PENDING_VALIDATION")
        self.assertFalse(outcome["activation_allowed"])

    def test_guard_blocks_without_confirmation_in_window(self) -> None:
        outcome = evaluate_dossier_fatality_window(
            now_dt=parse_now("2026-04-21T08:00:00"),
            capital_confirmed=False,
        )
        self.assertEqual(outcome["status"], "PENDING_VALIDATION")
        self.assertFalse(outcome["activation_allowed"])

    def test_guard_allows_with_confirmation_in_window(self) -> None:
        outcome = evaluate_dossier_fatality_window(
            now_dt=parse_now("2026-04-21T08:00:00"),
            capital_confirmed=True,
        )
        self.assertEqual(outcome["status"], "ACTIVATION_ALLOWED")
        self.assertTrue(outcome["activation_allowed"])

    def test_env_confirmation_parser(self) -> None:
        from dossier_fatality_guard import env_confirmed_450k

        prev = os.environ.get("TRYONYOU_CAPITAL_450K_CONFIRMED")
        try:
            os.environ["TRYONYOU_CAPITAL_450K_CONFIRMED"] = "1"
            self.assertTrue(env_confirmed_450k())
            os.environ["TRYONYOU_CAPITAL_450K_CONFIRMED"] = "true"
            self.assertTrue(env_confirmed_450k())
            os.environ["TRYONYOU_CAPITAL_450K_CONFIRMED"] = "0"
            self.assertFalse(env_confirmed_450k())
        finally:
            if prev is None:
                os.environ.pop("TRYONYOU_CAPITAL_450K_CONFIRMED", None)
            else:
                os.environ["TRYONYOU_CAPITAL_450K_CONFIRMED"] = prev


if __name__ == "__main__":
    unittest.main()
