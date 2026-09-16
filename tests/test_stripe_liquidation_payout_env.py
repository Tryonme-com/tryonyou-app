import unittest
import sys
import os

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from stripe_liquidation_payout_env import _as_amount_currency

class DummyObject:
    def __init__(self, amount=None, currency=None):
        if amount is not None:
            self.amount = amount
        if currency is not None:
            self.currency = currency

class TestAsAmountCurrency(unittest.TestCase):
    def test_dict_with_all_keys(self):
        val = {"amount": 1000, "currency": "USD"}
        amt, cur = _as_amount_currency(val)
        self.assertEqual(amt, 1000)
        self.assertEqual(cur, "usd")

    def test_dict_missing_keys(self):
        val = {}
        amt, cur = _as_amount_currency(val)
        self.assertEqual(amt, 0)
        self.assertEqual(cur, "")

    def test_dict_with_invalid_amount_type(self):
        val = {"amount": "500", "currency": "EUR"}
        amt, cur = _as_amount_currency(val)
        self.assertEqual(amt, 500)
        self.assertEqual(cur, "eur")

    def test_object_with_all_attributes(self):
        val = DummyObject(amount=2500, currency="GBP")
        amt, cur = _as_amount_currency(val)
        self.assertEqual(amt, 2500)
        self.assertEqual(cur, "gbp")

    def test_object_missing_attributes(self):
        val = DummyObject()
        amt, cur = _as_amount_currency(val)
        self.assertEqual(amt, 0)
        self.assertEqual(cur, "")

    def test_object_with_none_attributes(self):
        val = DummyObject(amount=None, currency=None)
        # hasattr check fails in logic because None is False-y. Wait, getattr(x, "amount", 0) returns None.
        # Then (None or 0) gives 0. int(0) -> 0.
        amt, cur = _as_amount_currency(val)
        self.assertEqual(amt, 0)
        self.assertEqual(cur, "")

if __name__ == "__main__":
    unittest.main()
