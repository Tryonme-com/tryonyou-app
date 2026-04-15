"""Tests para SovereigntyEngine y guard 402 de V11."""

from __future__ import annotations

import datetime as dt
import os
import sys
import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_API = _ROOT / "api"
for _p in (str(_ROOT), str(_API)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from sovereignty_engine import SovereigntyEngine, v11_payment_required_guard


class TestSovereigntyEngineThreshold(unittest.TestCase):
    def test_threshold_applies_discount_before_expiration(self) -> None:
        engine = SovereigntyEngine()
        threshold, status = engine.calculate_current_threshold(today=dt.date(2026, 4, 21))
        self.assertEqual(status, "OFFRE_FLASH_ACTIVE_15")
        self.assertEqual(threshold, 484_908.0)

    def test_threshold_uses_full_rate_after_expiration(self) -> None:
        engine = SovereigntyEngine()
        threshold, status = engine.calculate_current_threshold(today=dt.date(2026, 4, 23))
        self.assertEqual(status, "TARIF_STANDARD_PENALITÉ")
        self.assertEqual(threshold, 570_480.0)


class TestV11PaymentRequiredGuard(unittest.TestCase):
    def setUp(self) -> None:
        self._old_env = {
            "QONTO_BALANCE_EUR": os.environ.get("QONTO_BALANCE_EUR"),
            "TREASURY_CAPITAL_EUR": os.environ.get("TREASURY_CAPITAL_EUR"),
        }

    def tearDown(self) -> None:
        for key, value in self._old_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def test_returns_402_when_balance_below_threshold(self) -> None:
        os.environ["QONTO_BALANCE_EUR"] = "1000"
        guard = v11_payment_required_guard()
        self.assertIsNotNone(guard)
        payload, code = guard  # type: ignore[misc]
        self.assertEqual(code, 402)
        self.assertEqual(payload.get("payment_status"), "PAYMENT_REQUIRED")
        self.assertEqual(payload.get("qonto_balance_eur"), 1000.0)

    def test_returns_none_when_balance_meets_threshold(self) -> None:
        os.environ["QONTO_BALANCE_EUR"] = "700000"
        guard = v11_payment_required_guard()
        self.assertIsNone(guard)


if __name__ == "__main__":
    unittest.main()
