"""Tests para FranchiseContract — Protocolo de franquicia TryOnYou V10."""

from __future__ import annotations

import os
import sys
import unittest

_API = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "api"))
if _API not in sys.path:
    sys.path.insert(0, _API)

from franchise_contract import FranchiseContract


class TestFranchiseContractInit(unittest.TestCase):
    def test_default_tier(self) -> None:
        contract = FranchiseContract("SHOP_001")
        self.assertEqual(contract.tier, "LUXURY_CARE")

    def test_custom_tier(self) -> None:
        contract = FranchiseContract("SHOP_002", tier="PREMIUM")
        self.assertEqual(contract.tier, "PREMIUM")

    def test_shop_id_stored(self) -> None:
        contract = FranchiseContract("SHOP_XYZ")
        self.assertEqual(contract.shop_id, "SHOP_XYZ")

    def test_license_fee(self) -> None:
        contract = FranchiseContract("SHOP_001")
        self.assertAlmostEqual(contract.license_fee, 9900.0)

    def test_entry_fee(self) -> None:
        contract = FranchiseContract("SHOP_001")
        self.assertAlmostEqual(contract.entry_fee, 100000.0)

    def test_variable_commission(self) -> None:
        contract = FranchiseContract("SHOP_001")
        self.assertAlmostEqual(contract.variable_commission, 0.05)


class TestCalculateMonthlySettlement(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = FranchiseContract("SHOP_TEST")

    def test_fixed_fee_in_result(self) -> None:
        result = self.contract.calculate_monthly_settlement(0)
        self.assertAlmostEqual(result["fixed_fee"], 9900.0)

    def test_zero_sales_no_commission(self) -> None:
        result = self.contract.calculate_monthly_settlement(0)
        self.assertAlmostEqual(result["variable_commission"], 0.0)

    def test_zero_sales_total_equals_license_fee(self) -> None:
        result = self.contract.calculate_monthly_settlement(0)
        self.assertAlmostEqual(result["total_to_invoice"], 9900.0)

    def test_commission_calculation(self) -> None:
        result = self.contract.calculate_monthly_settlement(10000.0)
        self.assertAlmostEqual(result["variable_commission"], 500.0)

    def test_total_invoice_with_sales(self) -> None:
        result = self.contract.calculate_monthly_settlement(10000.0)
        self.assertAlmostEqual(result["total_to_invoice"], 10400.0)

    def test_currency_is_eur(self) -> None:
        result = self.contract.calculate_monthly_settlement(5000.0)
        self.assertEqual(result["currency"], "EUR")

    def test_patent_royalty_included(self) -> None:
        result = self.contract.calculate_monthly_settlement(5000.0)
        self.assertIn("PCT/EP2025/067317", result["patent_royalty"])

    def test_large_sales_volume(self) -> None:
        result = self.contract.calculate_monthly_settlement(200000.0)
        self.assertAlmostEqual(result["variable_commission"], 10000.0)
        self.assertAlmostEqual(result["total_to_invoice"], 19900.0)


if __name__ == "__main__":
    unittest.main()
