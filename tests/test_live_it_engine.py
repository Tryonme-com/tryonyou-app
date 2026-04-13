"""Tests para LiveItSales.validate_purchase (live_it_engine)."""

from __future__ import annotations

import os
import sys
import unittest

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
_API = os.path.join(_ROOT, "api")
for _p in (_ROOT, _API):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from live_it_engine import LiveItSales


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class _Avatar:
    """Avatar stub cuyo método matches devuelve un valor configurable."""

    def __init__(self, *, match: bool) -> None:
        self._match = match
        self.last_garment_id: str | None = None
        self.last_precision: float | None = None

    def matches(self, garment_id: str, *, precision: float) -> bool:
        self.last_garment_id = garment_id
        self.last_precision = precision
        return self._match


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestLiveItSalesInit(unittest.TestCase):
    def test_stock_ref_stored(self) -> None:
        stock = object()
        engine = LiveItSales(stock_ref=stock)
        self.assertIs(engine.stock, stock)

    def test_precision_threshold_default(self) -> None:
        self.assertAlmostEqual(LiveItSales.PRECISION_THRESHOLD, 0.98)


class TestValidatePurchasePerfectFit(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = LiveItSales(stock_ref=None)
        self.avatar = _Avatar(match=True)
        self.result = self.engine.validate_purchase(self.avatar, "LVT-DRESS-001")

    def test_status_ready_for_payout(self) -> None:
        self.assertEqual(self.result["status"], "READY_FOR_PAYOUT")

    def test_url_checkout(self) -> None:
        self.assertEqual(self.result["url"], "/checkout")

    def test_returns_dict(self) -> None:
        self.assertIsInstance(self.result, dict)

    def test_passes_correct_garment_id(self) -> None:
        self.assertEqual(self.avatar.last_garment_id, "LVT-DRESS-001")

    def test_passes_standard_lvt_precision(self) -> None:
        self.assertAlmostEqual(self.avatar.last_precision, 0.98)


class TestValidatePurchaseFitAdjustment(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = LiveItSales(stock_ref=None)
        self.avatar = _Avatar(match=False)
        self.result = self.engine.validate_purchase(self.avatar, "LVT-JACKET-002")

    def test_status_fit_adjustment_required(self) -> None:
        self.assertEqual(self.result["status"], "FIT_ADJUSTMENT_REQUIRED")

    def test_no_url_key(self) -> None:
        self.assertNotIn("url", self.result)

    def test_returns_dict(self) -> None:
        self.assertIsInstance(self.result, dict)

    def test_passes_correct_garment_id(self) -> None:
        self.assertEqual(self.avatar.last_garment_id, "LVT-JACKET-002")

    def test_passes_standard_lvt_precision(self) -> None:
        self.assertAlmostEqual(self.avatar.last_precision, 0.98)


class TestValidatePurchaseWithStockRef(unittest.TestCase):
    def test_stock_ref_accessible_during_purchase(self) -> None:
        stock = {"LVT-SHIRT-003": {"size": "M", "qty": 10}}
        engine = LiveItSales(stock_ref=stock)
        avatar = _Avatar(match=True)
        result = engine.validate_purchase(avatar, "LVT-SHIRT-003")
        self.assertEqual(result["status"], "READY_FOR_PAYOUT")
        self.assertIs(engine.stock, stock)


if __name__ == "__main__":
    unittest.main()
