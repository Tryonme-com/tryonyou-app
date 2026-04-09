"""Tests for main_orchestrator — background agent runner."""

from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
_API = os.path.join(_ROOT, "api")
for _p in (_ROOT, _API):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import main_orchestrator


class TestRunPeacockCore(unittest.TestCase):
    def test_returns_ok_status(self) -> None:
        result = main_orchestrator.run_peacock_core()
        self.assertEqual(result["status"], "OK")

    def test_latency_budget_is_25ms(self) -> None:
        result = main_orchestrator.run_peacock_core()
        self.assertEqual(result["latency_budget_ms"], 25)

    def test_webhook_guard_is_active(self) -> None:
        result = main_orchestrator.run_peacock_core()
        self.assertTrue(result["webhook_guard"])


class TestRunRobertEngine(unittest.TestCase):
    def test_returns_dict(self) -> None:
        result = main_orchestrator.run_robert_engine()
        self.assertIsInstance(result, dict)

    def test_perfect_fit_verdict(self) -> None:
        result = main_orchestrator.run_robert_engine("BALMAIN-WHITE-SNAP")
        self.assertEqual(result["verdict"], "PERFECT_FIT")

    def test_legal_contains_patente(self) -> None:
        result = main_orchestrator.run_robert_engine()
        self.assertIn("legal", result)
        self.assertIn("PCT/EP2025/067317", result["legal"])


class TestRunSovereignSale(unittest.TestCase):
    def setUp(self) -> None:
        for key in (
            "SHOPIFY_ADMIN_ACCESS_TOKEN",
            "SHOPIFY_STORE_DOMAIN",
            "SHOPIFY_ZERO_SIZE_VARIANT_ID",
            "SHOPIFY_PERFECT_CHECKOUT_URL",
        ):
            os.environ.pop(key, None)

    def test_sale_status_success(self) -> None:
        result = main_orchestrator.run_sovereign_sale()
        self.assertEqual(result["sale_status"], "SUCCESS")

    def test_legal_contains_patente(self) -> None:
        result = main_orchestrator.run_sovereign_sale()
        self.assertIn("legal", result)
        self.assertIn("PCT/EP2025/067317", result["legal"])

    def test_commission_is_numeric(self) -> None:
        result = main_orchestrator.run_sovereign_sale()
        self.assertIsInstance(result["franchise_commission"], float)


class TestRunBillingStatus(unittest.TestCase):
    def test_returns_ok_without_key(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("STRIPE_SECRET_KEY", None)
            result = main_orchestrator.run_billing_status()
        self.assertEqual(result["status"], "OK")
        self.assertFalse(result["stripe_key_present"])

    def test_returns_ok_with_key(self) -> None:
        with patch.dict(os.environ, {"STRIPE_SECRET_KEY": "sk_test_dummy"}):
            result = main_orchestrator.run_billing_status()
        self.assertEqual(result["status"], "OK")
        self.assertTrue(result["stripe_key_present"])


class TestMainFunction(unittest.TestCase):
    def setUp(self) -> None:
        for key in (
            "SHOPIFY_ADMIN_ACCESS_TOKEN",
            "SHOPIFY_STORE_DOMAIN",
            "SHOPIFY_ZERO_SIZE_VARIANT_ID",
            "SHOPIFY_PERFECT_CHECKOUT_URL",
            "STRIPE_SECRET_KEY",
        ):
            os.environ.pop(key, None)

    def test_main_returns_zero_on_success(self) -> None:
        self.assertEqual(main_orchestrator.main(), 0)

    def test_main_returns_one_on_partial_error(self) -> None:
        with patch.object(
            main_orchestrator,
            "run_peacock_core",
            side_effect=RuntimeError("simulated failure"),
        ):
            result = main_orchestrator.main()
        self.assertEqual(result, 1)


if __name__ == "__main__":
    unittest.main()
