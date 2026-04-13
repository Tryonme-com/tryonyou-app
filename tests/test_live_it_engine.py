"""
Tests para LiveItSales (live_it_engine):
  - validate_purchase → READY_FOR_PAYOUT cuando el ajuste es perfecto
  - validate_purchase → FIT_ADJUSTMENT_REQUIRED cuando el ajuste no alcanza el umbral
  - Almacenamiento de stock_ref en self.stock
  - Constante LVT_PRECISION_THRESHOLD
"""

from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import MagicMock

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
_API = os.path.join(_ROOT, "api")
for _p in (_ROOT, _API):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from live_it_engine import LVT_PRECISION_THRESHOLD, LiveItSales


def _make_avatar(matches: bool) -> MagicMock:
    """Devuelve un avatar simulado cuyo método matches() retorna el valor dado."""
    avatar = MagicMock()
    avatar.matches.return_value = matches
    return avatar


class TestLiveItSalesInit(unittest.TestCase):
    def test_stock_ref_stored(self) -> None:
        stock = {"items": []}
        sales = LiveItSales(stock_ref=stock)
        self.assertIs(sales.stock, stock)

    def test_stock_ref_none_allowed(self) -> None:
        sales = LiveItSales(stock_ref=None)
        self.assertIsNone(sales.stock)


class TestLiveItSalesValidatePurchase(unittest.TestCase):
    def setUp(self) -> None:
        self.sales = LiveItSales(stock_ref=MagicMock())

    # ------------------------------------------------------------------
    # Caso: ajuste perfecto → READY_FOR_PAYOUT
    # ------------------------------------------------------------------

    def test_ready_for_payout_status(self) -> None:
        avatar = _make_avatar(True)
        result = self.sales.validate_purchase(avatar, "LVT-DRESS-001")
        self.assertEqual(result["status"], "READY_FOR_PAYOUT")

    def test_ready_for_payout_url(self) -> None:
        avatar = _make_avatar(True)
        result = self.sales.validate_purchase(avatar, "LVT-DRESS-001")
        self.assertEqual(result["url"], "/checkout")

    def test_ready_for_payout_returns_dict(self) -> None:
        avatar = _make_avatar(True)
        result = self.sales.validate_purchase(avatar, "LVT-DRESS-001")
        self.assertIsInstance(result, dict)

    def test_avatar_matches_called_with_garment_and_precision(self) -> None:
        avatar = _make_avatar(True)
        self.sales.validate_purchase(avatar, "LVT-DRESS-001")
        avatar.matches.assert_called_once_with(
            "LVT-DRESS-001", precision=LVT_PRECISION_THRESHOLD
        )

    # ------------------------------------------------------------------
    # Caso: ajuste insuficiente → FIT_ADJUSTMENT_REQUIRED
    # ------------------------------------------------------------------

    def test_fit_adjustment_required_status(self) -> None:
        avatar = _make_avatar(False)
        result = self.sales.validate_purchase(avatar, "LVT-JACKET-002")
        self.assertEqual(result["status"], "FIT_ADJUSTMENT_REQUIRED")

    def test_fit_adjustment_required_no_url(self) -> None:
        avatar = _make_avatar(False)
        result = self.sales.validate_purchase(avatar, "LVT-JACKET-002")
        self.assertNotIn("url", result)

    def test_fit_adjustment_required_returns_dict(self) -> None:
        avatar = _make_avatar(False)
        result = self.sales.validate_purchase(avatar, "LVT-JACKET-002")
        self.assertIsInstance(result, dict)

    # ------------------------------------------------------------------
    # Constante de precisión LVT
    # ------------------------------------------------------------------

    def test_lvt_precision_threshold_value(self) -> None:
        self.assertAlmostEqual(LVT_PRECISION_THRESHOLD, 0.98, places=5)

    def test_precision_threshold_passed_to_avatar(self) -> None:
        avatar = _make_avatar(True)
        self.sales.validate_purchase(avatar, "LVT-SKIRT-003")
        _, kwargs = avatar.matches.call_args
        self.assertAlmostEqual(kwargs["precision"], 0.98, places=5)

    # ------------------------------------------------------------------
    # Diferentes garment_id
    # ------------------------------------------------------------------

    def test_different_garment_ids_perfect_fit(self) -> None:
        for garment_id in ("LVT-A", "LVT-B", "LVT-C"):
            avatar = _make_avatar(True)
            result = self.sales.validate_purchase(avatar, garment_id)
            self.assertEqual(result["status"], "READY_FOR_PAYOUT")

    def test_different_garment_ids_no_fit(self) -> None:
        for garment_id in ("LVT-X", "LVT-Y", "LVT-Z"):
            avatar = _make_avatar(False)
            result = self.sales.validate_purchase(avatar, garment_id)
            self.assertEqual(result["status"], "FIT_ADJUSTMENT_REQUIRED")


if __name__ == "__main__":
    unittest.main()
