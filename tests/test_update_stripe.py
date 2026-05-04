"""Tests para update_stripe — creación de productos/precios V10 en Stripe."""

from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import MagicMock, call, patch

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import update_stripe


class TestCrearProductosV10Success(unittest.TestCase):
    """Todos los productos y la suscripción se crean sin error."""

    def setUp(self) -> None:
        os.environ["STRIPE_SECRET_KEY_FR"] = "sk_test_dummy"

    def tearDown(self) -> None:
        os.environ.pop("STRIPE_SECRET_KEY_FR", None)

    def _make_product(self, pid: str) -> MagicMock:
        m = MagicMock()
        m.id = pid
        return m

    def _make_price(self, price_id: str) -> MagicMock:
        m = MagicMock()
        m.id = price_id
        return m

    def test_returns_zero_on_full_success(self) -> None:
        prod_mock = self._make_product("prod_ok")
        price_mock = self._make_price("price_ok")
        with patch("stripe.Product.create", return_value=prod_mock), \
             patch("stripe.Price.create", return_value=price_mock):
            result = update_stripe.crear_productos_v10()
        self.assertEqual(result, 0)

    def test_creates_five_one_time_products(self) -> None:
        prod_mock = self._make_product("prod_ok")
        price_mock = self._make_price("price_ok")
        with patch("stripe.Product.create", return_value=prod_mock) as mock_prod, \
             patch("stripe.Price.create", return_value=price_mock):
            update_stripe.crear_productos_v10()
        # 5 one-time products + 1 subscription product = 6 total Product.create calls
        self.assertEqual(mock_prod.call_count, 6)

    def test_creates_one_recurring_price(self) -> None:
        prod_mock = self._make_product("prod_ok")
        price_mock = self._make_price("price_ok")
        with patch("stripe.Product.create", return_value=prod_mock), \
             patch("stripe.Price.create", return_value=price_mock) as mock_price:
            update_stripe.crear_productos_v10()
        # Find the call with recurring kwarg
        recurring_calls = [
            c for c in mock_price.call_args_list
            if c.kwargs.get("recurring") is not None
        ]
        self.assertEqual(len(recurring_calls), 1)
        self.assertEqual(recurring_calls[0].kwargs["recurring"], {"interval": "month"})

    def test_all_prices_use_eur(self) -> None:
        prod_mock = self._make_product("prod_ok")
        price_mock = self._make_price("price_ok")
        with patch("stripe.Product.create", return_value=prod_mock), \
             patch("stripe.Price.create", return_value=price_mock) as mock_price:
            update_stripe.crear_productos_v10()
        for c in mock_price.call_args_list:
            self.assertEqual(c.kwargs.get("currency"), "eur")

    def test_monthly_subscription_amount(self) -> None:
        prod_mock = self._make_product("prod_ok")
        price_mock = self._make_price("price_ok")
        with patch("stripe.Product.create", return_value=prod_mock), \
             patch("stripe.Price.create", return_value=price_mock) as mock_price:
            update_stripe.crear_productos_v10()
        recurring_calls = [
            c for c in mock_price.call_args_list
            if c.kwargs.get("recurring") is not None
        ]
        self.assertEqual(recurring_calls[0].kwargs["unit_amount"], 990000)


class TestCrearProductosV10Errors(unittest.TestCase):
    """Comprueba el comportamiento cuando alguna llamada a Stripe falla."""

    def setUp(self) -> None:
        os.environ["STRIPE_SECRET_KEY_FR"] = "sk_test_dummy"

    def tearDown(self) -> None:
        os.environ.pop("STRIPE_SECRET_KEY_FR", None)

    def test_returns_one_when_product_creation_fails(self) -> None:
        with patch("stripe.Product.create", side_effect=Exception("Stripe error")):
            result = update_stripe.crear_productos_v10()
        self.assertEqual(result, 1)

    def test_returns_one_when_only_subscription_fails(self) -> None:
        prod_mock = MagicMock()
        prod_mock.id = "prod_ok"
        price_mock = MagicMock()
        price_mock.id = "price_ok"

        call_count = {"n": 0}

        def product_side_effect(**kwargs: object) -> MagicMock:
            call_count["n"] += 1
            # Fail only on the subscription product (last call)
            if call_count["n"] > len(update_stripe._PRODUCTOS):
                raise Exception("subscription error")
            return prod_mock

        with patch("stripe.Product.create", side_effect=product_side_effect), \
             patch("stripe.Price.create", return_value=price_mock):
            result = update_stripe.crear_productos_v10()
        self.assertEqual(result, 1)

    def test_continues_after_individual_product_error(self) -> None:
        """Un error en un producto no debe abortar los productos restantes."""
        prod_mock = MagicMock()
        prod_mock.id = "prod_ok"
        price_mock = MagicMock()
        price_mock.id = "price_ok"

        call_count = {"n": 0}

        def product_side_effect(**kwargs: object) -> MagicMock:
            call_count["n"] += 1
            if call_count["n"] == 1:
                raise Exception("first product error")
            return prod_mock

        with patch("stripe.Product.create", side_effect=product_side_effect), \
             patch("stripe.Price.create", return_value=price_mock) as mock_price:
            result = update_stripe.crear_productos_v10()
        # Still attempted Price.create for the remaining 5 products (4 one-time + 1 subscription)
        self.assertGreaterEqual(mock_price.call_count, 4)
        self.assertEqual(result, 1)


class TestMain(unittest.TestCase):
    """main() debe devolver el mismo código que crear_productos_v10()."""

    def setUp(self) -> None:
        os.environ["STRIPE_SECRET_KEY_FR"] = "sk_test_dummy"

    def tearDown(self) -> None:
        os.environ.pop("STRIPE_SECRET_KEY_FR", None)

    def test_main_returns_zero_on_success(self) -> None:
        prod_mock = MagicMock()
        prod_mock.id = "prod_ok"
        price_mock = MagicMock()
        price_mock.id = "price_ok"
        with patch("stripe.Product.create", return_value=prod_mock), \
             patch("stripe.Price.create", return_value=price_mock):
            result = update_stripe.main()
        self.assertEqual(result, 0)

    def test_main_returns_nonzero_on_error(self) -> None:
        with patch("stripe.Product.create", side_effect=Exception("fail")):
            result = update_stripe.main()
        self.assertNotEqual(result, 0)
