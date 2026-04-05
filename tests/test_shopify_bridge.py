"""Tests para shopify_bridge — integración Zero-Size (unittest estándar)."""

from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

_API = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "api"))
if _API not in sys.path:
    sys.path.insert(0, _API)

from shopify_bridge import (
    _shopify_admin_host,
    _shopify_host,
    admin_draft_order_invoice_url,
    build_shopify_perfect_selection_url,
    resolve_shopify_checkout_url,
)


class TestShopifyHost(unittest.TestCase):
    def test_shopify_host_strips_https(self) -> None:
        with patch.dict(os.environ, {"SHOPIFY_STORE_DOMAIN": "https://mystore.myshopify.com"}):
            self.assertEqual(_shopify_host(), "mystore.myshopify.com")

    def test_shopify_host_strips_http(self) -> None:
        with patch.dict(os.environ, {"SHOPIFY_STORE_DOMAIN": "http://mystore.myshopify.com/"}):
            self.assertEqual(_shopify_host(), "mystore.myshopify.com")

    def test_shopify_host_empty(self) -> None:
        with patch.dict(os.environ, {"SHOPIFY_STORE_DOMAIN": ""}, clear=False):
            os.environ.pop("SHOPIFY_STORE_DOMAIN", None)
            self.assertEqual(_shopify_host(), "")

    def test_shopify_admin_host_uses_myshopify_override(self) -> None:
        env = {
            "SHOPIFY_MYSHOPIFY_HOST": "https://override.myshopify.com",
            "SHOPIFY_STORE_DOMAIN": "https://public.brand.com",
        }
        with patch.dict(os.environ, env):
            self.assertEqual(_shopify_admin_host(), "override.myshopify.com")

    def test_shopify_admin_host_falls_back_to_store_domain(self) -> None:
        env = {"SHOPIFY_STORE_DOMAIN": "https://fallback.myshopify.com"}
        with patch.dict(os.environ, env):
            os.environ.pop("SHOPIFY_MYSHOPIFY_HOST", None)
            self.assertEqual(_shopify_admin_host(), "fallback.myshopify.com")


class TestAdminDraftOrderInvoiceUrl(unittest.TestCase):
    def test_returns_none_when_no_token(self) -> None:
        env = {
            "SHOPIFY_STORE_DOMAIN": "mystore.myshopify.com",
            "SHOPIFY_ZERO_SIZE_VARIANT_ID": "123456",
        }
        with patch.dict(os.environ, env):
            os.environ.pop("SHOPIFY_ADMIN_ACCESS_TOKEN", None)
            result = admin_draft_order_invoice_url(1, "drapé")
        self.assertIsNone(result)

    def test_returns_none_when_variant_id_not_digit(self) -> None:
        env = {
            "SHOPIFY_ADMIN_ACCESS_TOKEN": "shpat_test",
            "SHOPIFY_STORE_DOMAIN": "mystore.myshopify.com",
            "SHOPIFY_ZERO_SIZE_VARIANT_ID": "not_a_number",
        }
        with patch.dict(os.environ, env):
            result = admin_draft_order_invoice_url(1, "drapé")
        self.assertIsNone(result)

    def test_returns_none_when_host_not_myshopify(self) -> None:
        env = {
            "SHOPIFY_ADMIN_ACCESS_TOKEN": "shpat_test",
            "SHOPIFY_STORE_DOMAIN": "brand.com",
            "SHOPIFY_ZERO_SIZE_VARIANT_ID": "123456",
        }
        with patch.dict(os.environ, env):
            os.environ.pop("SHOPIFY_MYSHOPIFY_HOST", None)
            result = admin_draft_order_invoice_url(1, "drapé")
        self.assertIsNone(result)

    def test_returns_invoice_url_on_success(self) -> None:
        env = {
            "SHOPIFY_ADMIN_ACCESS_TOKEN": "shpat_valid",
            "SHOPIFY_STORE_DOMAIN": "mystore.myshopify.com",
            "SHOPIFY_ZERO_SIZE_VARIANT_ID": "987654",
            "SHOPIFY_ADMIN_API_VERSION": "2024-10",
        }
        mock_response = MagicMock()
        mock_response.read.return_value = (
            b'{"draft_order": {"invoice_url": "https://mystore.myshopify.com/invoices/abc"}}'
        )
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch.dict(os.environ, env):
            os.environ.pop("SHOPIFY_MYSHOPIFY_HOST", None)
            with patch("urllib.request.urlopen", return_value=mock_response):
                result = admin_draft_order_invoice_url(42, "tension_bias")

        self.assertEqual(result, "https://mystore.myshopify.com/invoices/abc")

    def test_returns_none_on_network_error(self) -> None:
        import urllib.error

        env = {
            "SHOPIFY_ADMIN_ACCESS_TOKEN": "shpat_valid",
            "SHOPIFY_STORE_DOMAIN": "mystore.myshopify.com",
            "SHOPIFY_ZERO_SIZE_VARIANT_ID": "987654",
        }
        with patch.dict(os.environ, env):
            os.environ.pop("SHOPIFY_MYSHOPIFY_HOST", None)
            with patch(
                "urllib.request.urlopen",
                side_effect=urllib.error.URLError("connection refused"),
            ):
                result = admin_draft_order_invoice_url(1, "drapé")
        self.assertIsNone(result)


class TestBuildShopifyPerfectSelectionUrl(unittest.TestCase):
    def test_uses_direct_checkout_url(self) -> None:
        import urllib.parse

        env = {"SHOPIFY_PERFECT_CHECKOUT_URL": "https://mystore.com/checkout/cart"}
        with patch.dict(os.environ, env):
            url = build_shopify_perfect_selection_url(7, "aligned")
        # The URL uses urllib.parse.urlencode which percent-encodes brackets
        decoded = urllib.parse.unquote(url)
        self.assertIn("tryonyou_lead]=7", decoded)
        self.assertIn("siren]=943610196", decoded)
        self.assertIn("patente]=PCT", decoded)

    def test_falls_back_to_product_path(self) -> None:
        env = {
            "SHOPIFY_STORE_DOMAIN": "https://mystore.myshopify.com",
            "SHOPIFY_PERFECT_PRODUCT_PATH": "/products/tryonyou-perfect-snap",
        }
        with patch.dict(os.environ, env):
            os.environ.pop("SHOPIFY_PERFECT_CHECKOUT_URL", None)
            url = build_shopify_perfect_selection_url(3, "drapé")
        self.assertIsNotNone(url)
        assert url is not None
        self.assertIn("utm_source=tryonyou_v10", url)
        self.assertIn("lead_3", url)

    def test_returns_none_when_no_domain_and_no_direct_url(self) -> None:
        with patch.dict(os.environ, {}):
            os.environ.pop("SHOPIFY_PERFECT_CHECKOUT_URL", None)
            os.environ.pop("SHOPIFY_STORE_DOMAIN", None)
            result = build_shopify_perfect_selection_url(1, "test")
        self.assertIsNone(result)


class TestResolveShopifyCheckoutUrl(unittest.TestCase):
    def test_prefers_admin_invoice_when_available(self) -> None:
        with (
            patch(
                "shopify_bridge.admin_draft_order_invoice_url",
                return_value="https://mystore.myshopify.com/invoices/123",
            ),
            patch(
                "shopify_bridge.build_shopify_perfect_selection_url",
                return_value="https://mystore.com/products/snap?utm=1",
            ),
        ):
            result = resolve_shopify_checkout_url(1, "drapé")
        self.assertEqual(result, "https://mystore.myshopify.com/invoices/123")

    def test_falls_back_to_storefront_url(self) -> None:
        with (
            patch("shopify_bridge.admin_draft_order_invoice_url", return_value=None),
            patch(
                "shopify_bridge.build_shopify_perfect_selection_url",
                return_value="https://mystore.com/products/snap?utm=1",
            ),
        ):
            result = resolve_shopify_checkout_url(1, "drapé")
        self.assertEqual(result, "https://mystore.com/products/snap?utm=1")

    def test_returns_none_when_both_unavailable(self) -> None:
        with (
            patch("shopify_bridge.admin_draft_order_invoice_url", return_value=None),
            patch("shopify_bridge.build_shopify_perfect_selection_url", return_value=None),
        ):
            result = resolve_shopify_checkout_url(1, "drapé")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
