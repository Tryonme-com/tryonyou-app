"""Tests for stripe_agent — product and price management."""

from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

import stripe

# Allow importing stripe_agent from project root
_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import stripe_agent


class TestGetStripeClient(unittest.TestCase):
    def test_valid_live_key(self) -> None:
        with patch.dict(os.environ, {"STRIPE_SECRET_KEY": "sk_live_abc123"}):
            key = stripe_agent._get_stripe_client()
            self.assertEqual(key, "sk_live_abc123")

    def test_valid_test_key(self) -> None:
        with patch.dict(os.environ, {"STRIPE_SECRET_KEY": "sk_test_abc123"}):
            key = stripe_agent._get_stripe_client()
            self.assertEqual(key, "sk_test_abc123")

    def test_missing_key_raises(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("STRIPE_SECRET_KEY", None)
            with self.assertRaises(EnvironmentError):
                stripe_agent._get_stripe_client()

    def test_invalid_key_raises(self) -> None:
        with patch.dict(os.environ, {"STRIPE_SECRET_KEY": "pk_live_wrong"}):
            with self.assertRaises(EnvironmentError):
                stripe_agent._get_stripe_client()


class TestCreateProduct(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["STRIPE_SECRET_KEY"] = "sk_test_dummy"

    def test_create_product_success(self) -> None:
        mock_product = MagicMock()
        mock_product.id = "prod_test123"
        with patch("stripe.Product.create", return_value=mock_product):
            result = stripe_agent.create_product("Test Product", description="A product")
        self.assertTrue(result["ok"])
        self.assertEqual(result["product_id"], "prod_test123")
        self.assertIs(result["product"], mock_product)

    def test_create_product_with_metadata(self) -> None:
        mock_product = MagicMock()
        mock_product.id = "prod_meta"
        with patch("stripe.Product.create", return_value=mock_product) as mock_create:
            result = stripe_agent.create_product("Meta Product", metadata={"brand": "divineo"})
        self.assertTrue(result["ok"])
        call_kwargs = mock_create.call_args[1]
        self.assertEqual(call_kwargs["metadata"]["brand"], "divineo")
        self.assertEqual(call_kwargs["metadata"]["siren"], "943 610 196")

    def test_create_product_always_has_siren(self) -> None:
        mock_product = MagicMock()
        mock_product.id = "prod_siren"
        with patch("stripe.Product.create", return_value=mock_product) as mock_create:
            result = stripe_agent.create_product("SIREN Product")
        self.assertTrue(result["ok"])
        call_kwargs = mock_create.call_args[1]
        self.assertEqual(call_kwargs["metadata"]["siren"], "943 610 196")
        self.assertEqual(call_kwargs["metadata"]["patent"], "PCT/EP2025/067317")

    def test_create_product_stripe_error(self) -> None:
        err = stripe.error.StripeError("api error")
        with patch("stripe.Product.create", side_effect=err):
            result = stripe_agent.create_product("Bad Product")
        self.assertFalse(result["ok"])
        self.assertIn("error", result)


class TestRetrieveProduct(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["STRIPE_SECRET_KEY"] = "sk_test_dummy"

    def test_retrieve_product_success(self) -> None:
        mock_product = MagicMock()
        mock_product.id = "prod_abc"
        with patch("stripe.Product.retrieve", return_value=mock_product):
            result = stripe_agent.retrieve_product("prod_abc")
        self.assertTrue(result["ok"])
        self.assertIs(result["product"], mock_product)

    def test_retrieve_product_stripe_error(self) -> None:
        err = stripe.error.StripeError("not found")
        with patch("stripe.Product.retrieve", side_effect=err):
            result = stripe_agent.retrieve_product("prod_bad")
        self.assertFalse(result["ok"])


class TestListProducts(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["STRIPE_SECRET_KEY"] = "sk_test_dummy"

    def test_list_products_success(self) -> None:
        mock_iter = [MagicMock(id="prod_1"), MagicMock(id="prod_2")]
        mock_list = MagicMock()
        mock_list.auto_paging_iter.return_value = iter(mock_iter)
        with patch("stripe.Product.list", return_value=mock_list):
            result = stripe_agent.list_products()
        self.assertTrue(result["ok"])
        self.assertEqual(len(result["products"]), 2)

    def test_list_products_active_filter(self) -> None:
        mock_list = MagicMock()
        mock_list.auto_paging_iter.return_value = iter([])
        with patch("stripe.Product.list", return_value=mock_list) as mock_fn:
            stripe_agent.list_products(active=True)
        self.assertEqual(mock_fn.call_args[1]["active"], True)

    def test_list_products_limit_clamped(self) -> None:
        mock_list = MagicMock()
        mock_list.auto_paging_iter.return_value = iter([])
        with patch("stripe.Product.list", return_value=mock_list) as mock_fn:
            stripe_agent.list_products(limit=200)
        self.assertEqual(mock_fn.call_args[1]["limit"], 100)


class TestArchiveProduct(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["STRIPE_SECRET_KEY"] = "sk_test_dummy"

    def test_archive_product_success(self) -> None:
        mock_product = MagicMock()
        mock_product.id = "prod_abc"
        with patch("stripe.Product.modify", return_value=mock_product):
            result = stripe_agent.archive_product("prod_abc")
        self.assertTrue(result["ok"])
        self.assertEqual(result["product_id"], "prod_abc")

    def test_archive_product_stripe_error(self) -> None:
        err = stripe.error.StripeError("error")
        with patch("stripe.Product.modify", side_effect=err):
            result = stripe_agent.archive_product("prod_bad")
        self.assertFalse(result["ok"])


class TestCreatePrice(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["STRIPE_SECRET_KEY"] = "sk_test_dummy"

    def test_create_price_success(self) -> None:
        mock_price = MagicMock()
        mock_price.id = "price_test123"
        with patch("stripe.Price.create", return_value=mock_price):
            result = stripe_agent.create_price("prod_abc", 9900)
        self.assertTrue(result["ok"])
        self.assertEqual(result["price_id"], "price_test123")
        self.assertIs(result["price"], mock_price)

    def test_create_price_default_currency_eur(self) -> None:
        mock_price = MagicMock()
        mock_price.id = "price_eur"
        with patch("stripe.Price.create", return_value=mock_price) as mock_fn:
            stripe_agent.create_price("prod_abc", 9900)
        self.assertEqual(mock_fn.call_args[1]["currency"], "eur")

    def test_create_price_with_recurring(self) -> None:
        mock_price = MagicMock()
        mock_price.id = "price_sub"
        recurring = {"interval": "month", "interval_count": 1}
        with patch("stripe.Price.create", return_value=mock_price) as mock_fn:
            stripe_agent.create_price("prod_abc", 4900, recurring=recurring)
        self.assertEqual(mock_fn.call_args[1]["recurring"], recurring)

    def test_create_price_currency_lowercased(self) -> None:
        mock_price = MagicMock()
        mock_price.id = "price_usd"
        with patch("stripe.Price.create", return_value=mock_price) as mock_fn:
            stripe_agent.create_price("prod_abc", 9900, currency="USD")
        self.assertEqual(mock_fn.call_args[1]["currency"], "usd")

    def test_create_price_always_has_siren(self) -> None:
        mock_price = MagicMock()
        mock_price.id = "price_siren"
        with patch("stripe.Price.create", return_value=mock_price) as mock_fn:
            stripe_agent.create_price("prod_abc", 2_750_000)
        meta = mock_fn.call_args[1]["metadata"]
        self.assertEqual(meta["siren"], "943 610 196")
        self.assertEqual(meta["patent"], "PCT/EP2025/067317")

    def test_create_price_stripe_error(self) -> None:
        err = stripe.error.StripeError("invalid")
        with patch("stripe.Price.create", side_effect=err):
            result = stripe_agent.create_price("prod_bad", 100)
        self.assertFalse(result["ok"])


class TestRetrievePrice(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["STRIPE_SECRET_KEY"] = "sk_test_dummy"

    def test_retrieve_price_success(self) -> None:
        mock_price = MagicMock()
        mock_price.id = "price_xyz"
        with patch("stripe.Price.retrieve", return_value=mock_price):
            result = stripe_agent.retrieve_price("price_xyz")
        self.assertTrue(result["ok"])
        self.assertIs(result["price"], mock_price)

    def test_retrieve_price_stripe_error(self) -> None:
        err = stripe.error.StripeError("not found")
        with patch("stripe.Price.retrieve", side_effect=err):
            result = stripe_agent.retrieve_price("price_bad")
        self.assertFalse(result["ok"])


class TestListPrices(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["STRIPE_SECRET_KEY"] = "sk_test_dummy"

    def test_list_prices_success(self) -> None:
        mock_iter = [MagicMock(id="price_1"), MagicMock(id="price_2")]
        mock_list = MagicMock()
        mock_list.auto_paging_iter.return_value = iter(mock_iter)
        with patch("stripe.Price.list", return_value=mock_list):
            result = stripe_agent.list_prices()
        self.assertTrue(result["ok"])
        self.assertEqual(len(result["prices"]), 2)

    def test_list_prices_by_product(self) -> None:
        mock_list = MagicMock()
        mock_list.auto_paging_iter.return_value = iter([])
        with patch("stripe.Price.list", return_value=mock_list) as mock_fn:
            stripe_agent.list_prices(product_id="prod_abc")
        self.assertEqual(mock_fn.call_args[1]["product"], "prod_abc")

    def test_list_prices_limit_clamped(self) -> None:
        mock_list = MagicMock()
        mock_list.auto_paging_iter.return_value = iter([])
        with patch("stripe.Price.list", return_value=mock_list) as mock_fn:
            stripe_agent.list_prices(limit=0)
        self.assertEqual(mock_fn.call_args[1]["limit"], 1)


class TestDeactivatePrice(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["STRIPE_SECRET_KEY"] = "sk_test_dummy"

    def test_deactivate_price_success(self) -> None:
        mock_price = MagicMock()
        mock_price.id = "price_xyz"
        with patch("stripe.Price.modify", return_value=mock_price):
            result = stripe_agent.deactivate_price("price_xyz")
        self.assertTrue(result["ok"])
        self.assertEqual(result["price_id"], "price_xyz")

    def test_deactivate_price_stripe_error(self) -> None:
        err = stripe.error.StripeError("error")
        with patch("stripe.Price.modify", side_effect=err):
            result = stripe_agent.deactivate_price("price_bad")
        self.assertFalse(result["ok"])


if __name__ == "__main__":
    unittest.main()
