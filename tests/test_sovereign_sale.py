"""
Tests para el flujo execute_sovereign_sale y sus componentes:
  - RobertEngine.process_frame
  - FranchiseContract.calculate_monthly_settlement
  - ShopifyBridge.sync_robert_to_shopify
  - execute_sovereign_sale (integración completa)
"""

from __future__ import annotations

import os
import sys
import unittest

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
_API = os.path.join(_ROOT, "api")
for _p in (_ROOT, _API):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from franchise_contract import DEFAULT_FIXED_FEE, DEFAULT_VARIABLE_RATE, FranchiseContract
from robert_engine import RobertEngine, UserAnchors
from shopify_bridge import ShopifyBridge
from sovereign_sale import execute_sovereign_sale, generate_sovereignty_report


# ---------------------------------------------------------------------------
# RobertEngine
# ---------------------------------------------------------------------------

class TestRobertEngine(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = RobertEngine()

    def test_status_operational(self) -> None:
        self.assertEqual(self.engine.status, "OPERATIONAL")

    def test_process_frame_returns_dict(self) -> None:
        result = self.engine.process_frame(
            "BALMAIN-WHITE-SNAP", 420.0, 960.0, 100, {"w": 1080, "h": 1920}
        )
        self.assertIsInstance(result, dict)

    def test_process_frame_fabric_key(self) -> None:
        result = self.engine.process_frame("BALMAIN-WHITE-SNAP", 420.0, 960.0, 100, {"w": 1080, "h": 1920})
        self.assertEqual(result["fabric_key"], "BALMAIN-WHITE-SNAP")

    def test_process_frame_perfect_fit_verdict(self) -> None:
        result = self.engine.process_frame("FAB-01", 400.0, 900.0, 100, {"w": 1080, "h": 1920})
        self.assertEqual(result["verdict"], "PERFECT_FIT")

    def test_process_frame_needs_adjustment_verdict(self) -> None:
        result = self.engine.process_frame("FAB-01", 400.0, 900.0, 50, {"w": 1080, "h": 1920})
        self.assertEqual(result["verdict"], "NEEDS_ADJUSTMENT")

    def test_process_frame_fit_score_clamped_high(self) -> None:
        result = self.engine.process_frame("FAB-01", 400.0, 900.0, 200, {"w": 1080, "h": 1920})
        self.assertEqual(result["fit_score"], 100.0)

    def test_process_frame_fit_score_clamped_low(self) -> None:
        result = self.engine.process_frame("FAB-01", 400.0, 900.0, -10, {"w": 1080, "h": 1920})
        self.assertEqual(result["fit_score"], 0.0)

    def test_process_frame_protocol_zero_size(self) -> None:
        result = self.engine.process_frame("FAB-01", 400.0, 900.0, 100, {"w": 1080, "h": 1920})
        self.assertEqual(result["protocol"], "zero_size")

    def test_process_frame_legal_patente(self) -> None:
        result = self.engine.process_frame("FAB-01", 400.0, 900.0, 100, {"w": 1080, "h": 1920})
        self.assertIn("PCT/EP2025/067317", result["legal"])

    def test_process_frame_anchors_normalized(self) -> None:
        result = self.engine.process_frame("FAB-01", 540.0, 960.0, 100, {"w": 1080, "h": 1920})
        self.assertAlmostEqual(result["anchors"]["shoulder_norm"], 0.5, places=3)
        self.assertAlmostEqual(result["anchors"]["hip_norm"], 0.5, places=3)

    def test_process_frame_frame_spec_stored(self) -> None:
        result = self.engine.process_frame("FAB-01", 400.0, 900.0, 100, {"w": 1080, "h": 1920})
        self.assertEqual(result["frame_spec"], {"w": 1080, "h": 1920})


# ---------------------------------------------------------------------------
# UserAnchors
# ---------------------------------------------------------------------------

class TestUserAnchors(unittest.TestCase):
    def test_user_anchors_attributes(self) -> None:
        anchors = UserAnchors(shoulder_w=420.0, hip_y=960.0)
        self.assertEqual(anchors.shoulder_w, 420.0)
        self.assertEqual(anchors.hip_y, 960.0)


# ---------------------------------------------------------------------------
# FranchiseContract
# ---------------------------------------------------------------------------

class TestFranchiseContract(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = FranchiseContract()

    def test_default_variable_rate(self) -> None:
        self.assertEqual(self.contract.variable_rate, DEFAULT_VARIABLE_RATE)

    def test_default_fixed_fee(self) -> None:
        self.assertEqual(self.contract.fixed_fee, DEFAULT_FIXED_FEE)

    def test_calculate_monthly_settlement_returns_dict(self) -> None:
        result = self.contract.calculate_monthly_settlement(4000.0)
        self.assertIsInstance(result, dict)

    def test_variable_commission_balmain_dress(self) -> None:
        result = self.contract.calculate_monthly_settlement(4000.0)
        expected = round(4000.0 * DEFAULT_VARIABLE_RATE, 2)
        self.assertAlmostEqual(result["variable_commission"], expected, places=2)

    def test_total_due_includes_fixed_fee(self) -> None:
        result = self.contract.calculate_monthly_settlement(4000.0)
        expected_total = round(result["variable_commission"] + DEFAULT_FIXED_FEE, 2)
        self.assertAlmostEqual(result["total_due"], expected_total, places=2)

    def test_item_price_in_settlement(self) -> None:
        result = self.contract.calculate_monthly_settlement(4000.0)
        self.assertEqual(result["item_price"], 4000.0)

    def test_legal_contains_patente(self) -> None:
        result = self.contract.calculate_monthly_settlement(4000.0)
        self.assertIn("PCT/EP2025/067317", result["legal"])

    def test_zero_price_settlement(self) -> None:
        result = self.contract.calculate_monthly_settlement(0.0)
        self.assertEqual(result["variable_commission"], 0.0)
        self.assertEqual(result["total_due"], DEFAULT_FIXED_FEE)

    def test_custom_rate(self) -> None:
        contract = FranchiseContract(variable_rate=0.20)
        result = contract.calculate_monthly_settlement(1000.0)
        self.assertAlmostEqual(result["variable_commission"], 200.0, places=2)

    def test_invalid_rate_raises(self) -> None:
        with self.assertRaises(ValueError):
            FranchiseContract(variable_rate=1.5)

    def test_invalid_fee_raises(self) -> None:
        with self.assertRaises(ValueError):
            FranchiseContract(fixed_fee=-50.0)


# ---------------------------------------------------------------------------
# ShopifyBridge
# ---------------------------------------------------------------------------

class TestShopifyBridge(unittest.TestCase):
    def setUp(self) -> None:
        # Clear env vars so no real HTTP calls are attempted
        for key in (
            "SHOPIFY_ADMIN_ACCESS_TOKEN",
            "SHOPIFY_STORE_DOMAIN",
            "SHOPIFY_ZERO_SIZE_VARIANT_ID",
            "SHOPIFY_PERFECT_CHECKOUT_URL",
        ):
            os.environ.pop(key, None)
        self.bridge = ShopifyBridge()

    def test_sync_returns_dict(self) -> None:
        result = self.bridge.sync_robert_to_shopify("BALMAIN-WHITE-SNAP", {"fitScore": 100})
        self.assertIsInstance(result, dict)

    def test_sync_fabric_key_preserved(self) -> None:
        result = self.bridge.sync_robert_to_shopify("BALMAIN-WHITE-SNAP", {"fitScore": 100})
        self.assertEqual(result["fabric_key"], "BALMAIN-WHITE-SNAP")

    def test_sync_fit_score_preserved(self) -> None:
        result = self.bridge.sync_robert_to_shopify("FAB-01", {"fitScore": 98})
        self.assertEqual(result["fit_score"], 98.0)

    def test_sync_status_pending_without_env(self) -> None:
        result = self.bridge.sync_robert_to_shopify("FAB-01", {"fitScore": 100})
        self.assertEqual(result["status"], "PENDING")

    def test_sync_status_checkout_url_with_domain(self) -> None:
        os.environ["SHOPIFY_STORE_DOMAIN"] = "test-store.myshopify.com"
        try:
            result = self.bridge.sync_robert_to_shopify("FAB-01", {"fitScore": 100})
            self.assertIn(result["status"], ("DRAFT_CREATED", "CHECKOUT_URL", "PENDING"))
        finally:
            os.environ.pop("SHOPIFY_STORE_DOMAIN", None)

    def test_sync_legal_contains_patente(self) -> None:
        result = self.bridge.sync_robert_to_shopify("FAB-01", {"fitScore": 100})
        self.assertIn("PCT/EP2025/067317", result["legal"])


# ---------------------------------------------------------------------------
# execute_sovereign_sale (integration)
# ---------------------------------------------------------------------------

class TestExecuteSovereignSale(unittest.TestCase):
    def setUp(self) -> None:
        for key in (
            "SHOPIFY_ADMIN_ACCESS_TOKEN",
            "SHOPIFY_STORE_DOMAIN",
            "SHOPIFY_ZERO_SIZE_VARIANT_ID",
            "SHOPIFY_PERFECT_CHECKOUT_URL",
        ):
            os.environ.pop(key, None)
        self.franchise = FranchiseContract()
        self.shopify = ShopifyBridge()
        self.user_anchors = UserAnchors(shoulder_w=420.0, hip_y=960.0)

    def test_sale_status_success(self) -> None:
        result = execute_sovereign_sale(
            self.franchise, self.shopify, self.user_anchors, "BALMAIN-WHITE-SNAP"
        )
        self.assertEqual(result["sale_status"], "SUCCESS")

    def test_legal_contains_patente(self) -> None:
        result = execute_sovereign_sale(
            self.franchise, self.shopify, self.user_anchors, "BALMAIN-WHITE-SNAP"
        )
        self.assertIn("PCT/EP2025/067317", result["legal"])

    def test_franchise_commission_correct(self) -> None:
        result = execute_sovereign_sale(
            self.franchise, self.shopify, self.user_anchors, "BALMAIN-WHITE-SNAP"
        )
        # Vestido Balmain 4.000€ × 15 % = 600€
        expected = round(4000.0 * DEFAULT_VARIABLE_RATE, 2)
        self.assertAlmostEqual(result["franchise_commission"], expected, places=2)

    def test_shopify_ref_is_dict(self) -> None:
        result = execute_sovereign_sale(
            self.franchise, self.shopify, self.user_anchors, "BALMAIN-WHITE-SNAP"
        )
        self.assertIsInstance(result["shopify_ref"], dict)

    def test_all_keys_present(self) -> None:
        result = execute_sovereign_sale(
            self.franchise, self.shopify, self.user_anchors, "BALMAIN-WHITE-SNAP"
        )
        for key in ("sale_status", "shopify_ref", "franchise_commission", "legal"):
            self.assertIn(key, result)

    def test_custom_franchise_rate(self) -> None:
        contract = FranchiseContract(variable_rate=0.20)
        result = execute_sovereign_sale(
            contract, self.shopify, self.user_anchors, "BALMAIN-WHITE-SNAP"
        )
        self.assertAlmostEqual(result["franchise_commission"], 800.0, places=2)


# ---------------------------------------------------------------------------
# generate_sovereignty_report
# ---------------------------------------------------------------------------

class TestGenerateSovereigntyReport(unittest.TestCase):
    def _capture_report(self) -> str:
        import io
        buf = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = buf
        try:
            generate_sovereignty_report()
        finally:
            sys.stdout = old_stdout
        return buf.getvalue()

    def test_output_contains_header(self) -> None:
        output = self._capture_report()
        self.assertIn("GENERANDO REPORTE DE SOBERANÍA V10", output)

    def test_output_contains_patente(self) -> None:
        output = self._capture_report()
        self.assertIn("PCT/EP2025/067317", output)

    def test_output_contains_conversion_metric(self) -> None:
        output = self._capture_report()
        self.assertIn("+34.2%", output)

    def test_output_contains_reduction_metric(self) -> None:
        output = self._capture_report()
        self.assertIn("-67%", output)

    def test_output_contains_financial_impact(self) -> None:
        output = self._capture_report()
        self.assertIn("98.000,00 € NETOS (Inbound)", output)

    def test_output_contains_vivido_footer(self) -> None:
        output = self._capture_report()
        self.assertIn("VÍVIDO", output)
        self.assertIn("Lafayette", output)

    def test_keys_have_underscores_replaced(self) -> None:
        output = self._capture_report()
        self.assertNotIn("Métrica_Conversión", output)
        self.assertIn("Métrica Conversión", output)

    def test_returns_none(self) -> None:
        import io
        buf = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = buf
        try:
            result = generate_sovereignty_report()
        finally:
            sys.stdout = old_stdout
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
