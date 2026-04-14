from __future__ import annotations

import unittest
from datetime import datetime

from supercommit_max_autonomia import (
    SecurityEvaluation,
    evaluate_security,
    is_security_window,
    parse_eur_amount,
)


class TestParseEurAmount(unittest.TestCase):
    def test_parse_plain_integer(self) -> None:
        self.assertEqual(parse_eur_amount("450000"), 450000.0)

    def test_parse_european_format(self) -> None:
        self.assertEqual(parse_eur_amount("450.000,00"), 450000.0)

    def test_parse_thousand_dot_without_decimals(self) -> None:
        self.assertEqual(parse_eur_amount("450.000"), 450000.0)

    def test_parse_us_format_with_currency(self) -> None:
        self.assertEqual(parse_eur_amount("EUR 450,000.50"), 450000.5)

    def test_parse_empty(self) -> None:
        self.assertEqual(parse_eur_amount(""), 0.0)


class TestSecurityWindow(unittest.TestCase):
    def test_tuesday_8am_inside_window(self) -> None:
        tuesday = datetime(2026, 4, 14, 8, 5)
        self.assertTrue(is_security_window(tuesday, window_minutes=15))

    def test_tuesday_after_window(self) -> None:
        tuesday = datetime(2026, 4, 14, 8, 20)
        self.assertFalse(is_security_window(tuesday, window_minutes=15))

    def test_not_tuesday(self) -> None:
        monday = datetime(2026, 4, 13, 8, 5)
        self.assertFalse(is_security_window(monday, window_minutes=15))


class TestEvaluateSecurity(unittest.TestCase):
    def test_not_due_outside_window(self) -> None:
        monday = datetime(2026, 4, 13, 8, 5)
        result = evaluate_security(
            now=monday,
            amount_raw="450000",
            capital_confirmed=True,
            force_due=False,
        )
        self.assertIsInstance(result, SecurityEvaluation)
        self.assertFalse(result.due_now)
        self.assertFalse(result.should_activate)

    def test_due_but_not_confirmed(self) -> None:
        tuesday = datetime(2026, 4, 14, 8, 1)
        result = evaluate_security(
            now=tuesday,
            amount_raw="450000",
            capital_confirmed=False,
            force_due=False,
        )
        self.assertTrue(result.due_now)
        self.assertFalse(result.should_activate)

    def test_due_confirmed_below_threshold(self) -> None:
        tuesday = datetime(2026, 4, 14, 8, 1)
        result = evaluate_security(
            now=tuesday,
            amount_raw="449999",
            capital_confirmed=True,
            force_due=False,
        )
        self.assertTrue(result.due_now)
        self.assertFalse(result.should_activate)

    def test_due_confirmed_equal_threshold(self) -> None:
        tuesday = datetime(2026, 4, 14, 8, 1)
        result = evaluate_security(
            now=tuesday,
            amount_raw="450000",
            capital_confirmed=True,
            force_due=False,
        )
        self.assertTrue(result.due_now)
        self.assertTrue(result.should_activate)

    def test_force_due_even_outside_window(self) -> None:
        monday = datetime(2026, 4, 13, 20, 30)
        result = evaluate_security(
            now=monday,
            amount_raw="450000",
            capital_confirmed=True,
            force_due=True,
        )
        self.assertTrue(result.due_now)
        self.assertTrue(result.should_activate)


if __name__ == "__main__":
    unittest.main()
