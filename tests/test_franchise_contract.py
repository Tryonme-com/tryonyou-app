"""Tests para FranchiseContract — liquidación mensual de franquicia LUXURY_CARE."""

from __future__ import annotations

import os
import sys
import unittest

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
_API = os.path.join(_ROOT, "api")
for _p in (_ROOT, _API):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from franchise_contract import FranchiseContract


class TestFranchiseContractInit(unittest.TestCase):
    def test_default_tier(self) -> None:
        fc = FranchiseContract("SHOP_001")
        self.assertEqual(fc.tier, "LUXURY_CARE")

    def test_custom_tier(self) -> None:
        fc = FranchiseContract("SHOP_002", tier="PREMIUM")
        self.assertEqual(fc.tier, "PREMIUM")

    def test_shop_id_stored(self) -> None:
        fc = FranchiseContract("SHOP_PARIS")
        self.assertEqual(fc.shop_id, "SHOP_PARIS")

    def test_license_fee(self) -> None:
        fc = FranchiseContract("SHOP_001")
        self.assertAlmostEqual(fc.license_fee, 9900.0)

    def test_entry_fee(self) -> None:
        fc = FranchiseContract("SHOP_001")
        self.assertAlmostEqual(fc.entry_fee, 100000.0)

    def test_variable_commission_rate(self) -> None:
        fc = FranchiseContract("SHOP_001")
        self.assertAlmostEqual(fc.variable_commission, 0.05)


class TestCalculateMonthlySettlement(unittest.TestCase):
    def setUp(self) -> None:
        self.fc = FranchiseContract("SHOP_TEST")

    def test_fixed_fee_in_result(self) -> None:
        result = self.fc.calculate_monthly_settlement(0.0)
        self.assertAlmostEqual(result["fixed_fee"], 9900.0)

    def test_zero_sales_no_commission(self) -> None:
        result = self.fc.calculate_monthly_settlement(0.0)
        self.assertAlmostEqual(result["variable_commission"], 0.0)

    def test_zero_sales_total_equals_license_fee(self) -> None:
        result = self.fc.calculate_monthly_settlement(0.0)
        self.assertAlmostEqual(result["total_to_invoice"], 9900.0)

    def test_commission_five_percent(self) -> None:
        result = self.fc.calculate_monthly_settlement(20000.0)
        self.assertAlmostEqual(result["variable_commission"], 1000.0)

    def test_total_to_invoice(self) -> None:
        result = self.fc.calculate_monthly_settlement(20000.0)
        # 9900 + 1000
        self.assertAlmostEqual(result["total_to_invoice"], 10900.0)

    def test_currency_is_eur(self) -> None:
        result = self.fc.calculate_monthly_settlement(0.0)
        self.assertEqual(result["currency"], "EUR")

    def test_patent_royalty_included(self) -> None:
        result = self.fc.calculate_monthly_settlement(0.0)
        self.assertIn("PCT/EP2025/067317", result["patent_royalty"])

    def test_large_sales_volume(self) -> None:
        result = self.fc.calculate_monthly_settlement(500000.0)
        self.assertAlmostEqual(result["variable_commission"], 25000.0)
        self.assertAlmostEqual(result["total_to_invoice"], 34900.0)


if __name__ == "__main__":
    unittest.main()
