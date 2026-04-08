"""Tests para StripeAgent — gestión de catálogo y pagos (Espejo Digital)."""

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

from stripe_agent import StripeAgent


class TestStripeAgentInit(unittest.TestCase):
    def test_version_is_set(self) -> None:
        agent = StripeAgent("sk_test_dummy")
        self.assertEqual(agent.version, "2026-04-08")

    def test_api_key_propagated(self) -> None:
        import stripe as _stripe

        agent = StripeAgent("sk_test_init_check")
        self.assertEqual(_stripe.api_key, "sk_test_init_check")


class TestCreateProductWithPrice(unittest.TestCase):
    def _make_agent(self) -> StripeAgent:
        return StripeAgent("sk_test_dummy")

    def test_success_returns_expected_keys(self) -> None:
        mock_product = MagicMock()
        mock_product.id = "prod_abc123"
        mock_price = MagicMock()
        mock_price.id = "price_xyz789"

        with patch("stripe.Product.create", return_value=mock_product) as mp, \
             patch("stripe.Price.create", return_value=mock_price) as mpr:
            result = self._make_agent().create_product_with_price(
                name="Blazer Balmain", amount=145000
            )
            mp.assert_called_once_with(name="Blazer Balmain")
            mpr.assert_called_once_with(
                product="prod_abc123", unit_amount=145000, currency="eur"
            )

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["product_id"], "prod_abc123")
        self.assertEqual(result["price_id"], "price_xyz789")
        self.assertEqual(result["name"], "Blazer Balmain")

    def test_custom_currency(self) -> None:
        mock_product = MagicMock()
        mock_product.id = "prod_usd"
        mock_price = MagicMock()
        mock_price.id = "price_usd"

        with patch("stripe.Product.create", return_value=mock_product), \
             patch("stripe.Price.create", return_value=mock_price) as mpr:
            self._make_agent().create_product_with_price(
                name="Item USD", amount=5000, currency="usd"
            )
            mpr.assert_called_once_with(
                product="prod_usd", unit_amount=5000, currency="usd"
            )

    def test_stripe_error_returns_error_dict(self) -> None:
        import stripe as _stripe

        with patch(
            "stripe.Product.create",
            side_effect=_stripe.error.StripeError("network failure"),
        ):
            result = self._make_agent().create_product_with_price(
                name="Item", amount=1000
            )

        self.assertEqual(result["status"], "error")
        self.assertIn("message", result)


class TestListRecentActivity(unittest.TestCase):
    def test_calls_product_list_with_limit(self) -> None:
        mock_list = MagicMock()
        agent = StripeAgent("sk_test_dummy")

        with patch("stripe.Product.list", return_value=mock_list) as ml:
            result = agent.list_recent_activity(limit=3)
            ml.assert_called_once_with(limit=3)

        self.assertIs(result, mock_list)

    def test_default_limit_is_five(self) -> None:
        with patch("stripe.Product.list") as ml:
            StripeAgent("sk_test_dummy").list_recent_activity()
            ml.assert_called_once_with(limit=5)


if __name__ == "__main__":
    unittest.main()
