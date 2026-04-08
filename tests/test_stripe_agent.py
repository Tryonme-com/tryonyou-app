"""Tests para stripe_agent — gestión de productos y precios (unittest estándar)."""

from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import MagicMock, call, patch

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from stripe_agent import _configure_stripe, create_price, ensure_product, list_active_prices


class _FakeStripeObj(dict):
    """Simula un objeto Stripe serializable con dict(); hereda de dict para que dict(x) funcione."""


class TestConfigureStripe(unittest.TestCase):
    def test_raises_when_key_missing(self) -> None:
        os.environ.pop("STRIPE_SECRET_KEY", None)
        with self.assertRaises(ValueError):
            _configure_stripe()

    def test_raises_when_key_empty(self) -> None:
        os.environ["STRIPE_SECRET_KEY"] = "   "
        try:
            with self.assertRaises(ValueError):
                _configure_stripe()
        finally:
            os.environ.pop("STRIPE_SECRET_KEY", None)

    def test_sets_stripe_api_key(self) -> None:
        os.environ["STRIPE_SECRET_KEY"] = "sk_test_abc123"
        try:
            import stripe as _stripe

            _configure_stripe()
            self.assertEqual(_stripe.api_key, "sk_test_abc123")
        finally:
            os.environ.pop("STRIPE_SECRET_KEY", None)


class TestEnsureProduct(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["STRIPE_SECRET_KEY"] = "sk_test_fake"

    def tearDown(self) -> None:
        os.environ.pop("STRIPE_SECRET_KEY", None)

    def test_raises_on_empty_name(self) -> None:
        with self.assertRaises(ValueError):
            ensure_product("")

    def test_raises_on_whitespace_name(self) -> None:
        with self.assertRaises(ValueError):
            ensure_product("   ")

    def test_returns_existing_product_when_found(self) -> None:
        existing = _FakeStripeObj(id="prod_existing", name="TryOnYou Snap", active=True)
        mock_results = MagicMock()
        mock_results.data = [existing]

        with patch("stripe.Product.search", return_value=mock_results):
            result = ensure_product("TryOnYou Snap")

        self.assertEqual(result["id"], "prod_existing")
        self.assertEqual(result["name"], "TryOnYou Snap")

    def test_creates_product_when_not_found(self) -> None:
        mock_results = MagicMock()
        mock_results.data = []
        new_product = _FakeStripeObj(id="prod_new", name="New Snap", active=True)

        with patch("stripe.Product.search", return_value=mock_results), \
                patch("stripe.Product.create", return_value=new_product) as mock_create:
            result = ensure_product("New Snap")

        mock_create.assert_called_once()
        _, kwargs = mock_create.call_args
        self.assertEqual(kwargs["name"], "New Snap")
        self.assertTrue(kwargs["active"])
        self.assertEqual(result["id"], "prod_new")

    def test_create_includes_description_and_metadata(self) -> None:
        mock_results = MagicMock()
        mock_results.data = []
        new_product = _FakeStripeObj(id="prod_meta", name="Meta Product")

        with patch("stripe.Product.search", return_value=mock_results), \
                patch("stripe.Product.create", return_value=new_product) as mock_create:
            ensure_product("Meta Product", description="desc test", metadata={"env": "prod"})

        _, kwargs = mock_create.call_args
        self.assertEqual(kwargs["description"], "desc test")
        self.assertEqual(kwargs["metadata"], {"env": "prod"})

    def test_create_skips_description_when_empty(self) -> None:
        mock_results = MagicMock()
        mock_results.data = []
        new_product = _FakeStripeObj(id="prod_nodesc", name="No Desc")

        with patch("stripe.Product.search", return_value=mock_results), \
                patch("stripe.Product.create", return_value=new_product) as mock_create:
            ensure_product("No Desc")

        _, kwargs = mock_create.call_args
        self.assertNotIn("description", kwargs)
        self.assertNotIn("metadata", kwargs)

    def test_falls_back_to_create_on_invalid_request_error(self) -> None:
        import stripe as _stripe

        new_product = _FakeStripeObj(id="prod_fallback", name="Fallback")

        with patch("stripe.Product.search", side_effect=_stripe.error.InvalidRequestError("err", "param")), \
                patch("stripe.Product.create", return_value=new_product) as mock_create:
            result = ensure_product("Fallback")

        mock_create.assert_called_once()
        self.assertEqual(result["id"], "prod_fallback")


class TestCreatePrice(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["STRIPE_SECRET_KEY"] = "sk_test_fake"

    def tearDown(self) -> None:
        os.environ.pop("STRIPE_SECRET_KEY", None)

    def test_raises_on_empty_product_id(self) -> None:
        with self.assertRaises(ValueError):
            create_price("", 1000)

    def test_raises_on_whitespace_product_id(self) -> None:
        with self.assertRaises(ValueError):
            create_price("   ", 1000)

    def test_raises_on_negative_amount(self) -> None:
        with self.assertRaises(ValueError):
            create_price("prod_abc", -1)

    def test_zero_amount_is_valid(self) -> None:
        fake_price = _FakeStripeObj(id="price_free", unit_amount=0, currency="eur")
        with patch("stripe.Price.create", return_value=fake_price):
            result = create_price("prod_abc", 0)
        self.assertEqual(result["unit_amount"], 0)

    def test_creates_price_with_defaults(self) -> None:
        fake_price = _FakeStripeObj(id="price_eur", unit_amount=9800, currency="eur")
        with patch("stripe.Price.create", return_value=fake_price) as mock_create:
            result = create_price("prod_abc", 9800)

        _, kwargs = mock_create.call_args
        self.assertEqual(kwargs["product"], "prod_abc")
        self.assertEqual(kwargs["unit_amount"], 9800)
        self.assertEqual(kwargs["currency"], "eur")
        self.assertNotIn("recurring", kwargs)
        self.assertEqual(result["id"], "price_eur")

    def test_currency_is_lowercased(self) -> None:
        fake_price = _FakeStripeObj(id="price_usd", currency="usd")
        with patch("stripe.Price.create", return_value=fake_price) as mock_create:
            create_price("prod_abc", 5000, "USD")

        _, kwargs = mock_create.call_args
        self.assertEqual(kwargs["currency"], "usd")

    def test_creates_recurring_price(self) -> None:
        fake_price = _FakeStripeObj(id="price_sub", unit_amount=10000)
        with patch("stripe.Price.create", return_value=fake_price) as mock_create:
            create_price("prod_abc", 10000, recurring={"interval": "month"})

        _, kwargs = mock_create.call_args
        self.assertEqual(kwargs["recurring"], {"interval": "month"})

    def test_creates_price_with_metadata(self) -> None:
        fake_price = _FakeStripeObj(id="price_meta")
        with patch("stripe.Price.create", return_value=fake_price) as mock_create:
            create_price("prod_abc", 9800, metadata={"plan": "basic"})

        _, kwargs = mock_create.call_args
        self.assertEqual(kwargs["metadata"], {"plan": "basic"})


class TestListActivePrices(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["STRIPE_SECRET_KEY"] = "sk_test_fake"

    def tearDown(self) -> None:
        os.environ.pop("STRIPE_SECRET_KEY", None)

    def test_raises_on_empty_product_id(self) -> None:
        with self.assertRaises(ValueError):
            list_active_prices("")

    def test_raises_on_whitespace_product_id(self) -> None:
        with self.assertRaises(ValueError):
            list_active_prices("   ")

    def test_returns_empty_list_when_no_prices(self) -> None:
        mock_page = MagicMock()
        mock_page.auto_paging_iter.return_value = iter([])
        with patch("stripe.Price.list", return_value=mock_page):
            result = list_active_prices("prod_empty")
        self.assertEqual(result, [])

    def test_returns_list_of_dicts(self) -> None:
        p1 = _FakeStripeObj(id="price_1", active=True, unit_amount=9800)
        p2 = _FakeStripeObj(id="price_2", active=True, unit_amount=10000)
        mock_page = MagicMock()
        mock_page.auto_paging_iter.return_value = iter([p1, p2])
        with patch("stripe.Price.list", return_value=mock_page):
            result = list_active_prices("prod_abc")
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "price_1")
        self.assertEqual(result[1]["id"], "price_2")

    def test_calls_stripe_with_product_and_active_true(self) -> None:
        mock_page = MagicMock()
        mock_page.auto_paging_iter.return_value = iter([])
        with patch("stripe.Price.list", return_value=mock_page) as mock_list:
            list_active_prices("prod_xyz")
        _, kwargs = mock_list.call_args
        self.assertEqual(kwargs["product"], "prod_xyz")
        self.assertTrue(kwargs["active"])


if __name__ == "__main__":
    unittest.main()
