"""Tests for stripe_inflow_check — check_real_inflow function."""

from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import stripe_inflow_check
from stripe_inflow_check import HIGH_VOLUME_THRESHOLD_CENTS, check_real_inflow


def _make_bt(amount: int, status: str = "available", bt_type: str = "charge") -> MagicMock:
    bt = MagicMock()
    bt.amount = amount
    bt.status = status
    bt.type = bt_type
    return bt


class TestCheckRealInflowNoKey(unittest.TestCase):
    def test_returns_empty_without_key(self) -> None:
        env = {k: "" for k in ("STRIPE_SECRET_KEY_FR", "STRIPE_SECRET_KEY_NUEVA", "STRIPE_SECRET_KEY")}
        with patch.dict(os.environ, env, clear=False):
            result = check_real_inflow()
        self.assertEqual(result, [])

    def test_prints_error_without_key(self) -> None:
        env = {k: "" for k in ("STRIPE_SECRET_KEY_FR", "STRIPE_SECRET_KEY_NUEVA", "STRIPE_SECRET_KEY")}
        with patch.dict(os.environ, env, clear=False):
            import io
            captured = io.StringIO()
            with patch("sys.stderr", captured):
                check_real_inflow()
        self.assertIn("STRIPE_SECRET_KEY", captured.getvalue())


class TestCheckRealInflowWithKey(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["STRIPE_SECRET_KEY_FR"] = "sk_test_dummy"

    def tearDown(self) -> None:
        os.environ.pop("STRIPE_SECRET_KEY_FR", None)

    def test_no_high_volume_returns_empty(self) -> None:
        mock_list = MagicMock()
        mock_list.data = [_make_bt(50_000), _make_bt(99_999)]
        with patch("stripe.BalanceTransaction.list", return_value=mock_list):
            result = check_real_inflow()
        self.assertEqual(result, [])

    def test_high_volume_returned(self) -> None:
        mock_list = MagicMock()
        mock_list.data = [_make_bt(200_000, "available", "charge")]
        with patch("stripe.BalanceTransaction.list", return_value=mock_list):
            result = check_real_inflow()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["amount"], 200_000)
        self.assertEqual(result[0]["status"], "available")
        self.assertEqual(result[0]["type"], "charge")

    def test_only_above_threshold_included(self) -> None:
        mock_list = MagicMock()
        mock_list.data = [
            _make_bt(HIGH_VOLUME_THRESHOLD_CENTS + 1),
            _make_bt(HIGH_VOLUME_THRESHOLD_CENTS),
            _make_bt(HIGH_VOLUME_THRESHOLD_CENTS - 1),
        ]
        with patch("stripe.BalanceTransaction.list", return_value=mock_list):
            result = check_real_inflow()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["amount"], HIGH_VOLUME_THRESHOLD_CENTS + 1)

    def test_multiple_high_volume(self) -> None:
        mock_list = MagicMock()
        mock_list.data = [_make_bt(150_000), _make_bt(250_000)]
        with patch("stripe.BalanceTransaction.list", return_value=mock_list):
            result = check_real_inflow()
        self.assertEqual(len(result), 2)

    def test_stripe_error_returns_empty(self) -> None:
        import stripe
        with patch("stripe.BalanceTransaction.list", side_effect=stripe.error.StripeError("fail")):
            result = check_real_inflow()
        self.assertEqual(result, [])

    def test_limit_passed_to_stripe(self) -> None:
        mock_list = MagicMock()
        mock_list.data = []
        with patch("stripe.BalanceTransaction.list", return_value=mock_list) as mock_fn:
            check_real_inflow(limit=5)
        mock_fn.assert_called_once_with(limit=5)

    def test_sets_stripe_api_key(self) -> None:
        import stripe
        mock_list = MagicMock()
        mock_list.data = []
        with patch("stripe.BalanceTransaction.list", return_value=mock_list):
            check_real_inflow()
        self.assertEqual(stripe.api_key, "sk_test_dummy")


class TestMain(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["STRIPE_SECRET_KEY_FR"] = "sk_test_dummy"

    def tearDown(self) -> None:
        os.environ.pop("STRIPE_SECRET_KEY_FR", None)

    def test_main_returns_zero(self) -> None:
        mock_list = MagicMock()
        mock_list.data = []
        with patch("stripe.BalanceTransaction.list", return_value=mock_list):
            rc = stripe_inflow_check.main()
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
