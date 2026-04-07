"""Tests para ShopifySovereignBridge — integración biométrica Robert / Shopify."""

from __future__ import annotations

import io
import json
import os
import sys
import unittest
import urllib.error
from unittest.mock import MagicMock, patch

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
_API = os.path.join(_ROOT, "api")
for _p in (_ROOT, _API):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from shopify_bridge import ShopifySovereignBridge


class TestShopifySovereignBridgeInit(unittest.TestCase):
    def test_api_base_built_from_shop_url(self) -> None:
        bridge = ShopifySovereignBridge("tok_test", "mystore.myshopify.com")
        self.assertIn("mystore.myshopify.com", bridge.api_base)
        self.assertTrue(bridge.api_base.startswith("https://"))
        self.assertIn("/admin/api/", bridge.api_base)

    def test_api_base_strips_https_prefix(self) -> None:
        bridge = ShopifySovereignBridge("tok_test", "https://mystore.myshopify.com")
        self.assertIn("mystore.myshopify.com", bridge.api_base)
        self.assertNotIn("https://https://", bridge.api_base)

    def test_headers_contain_token(self) -> None:
        bridge = ShopifySovereignBridge("secret_token_42", "mystore.myshopify.com")
        self.assertEqual(bridge._headers["X-Shopify-Access-Token"], "secret_token_42")
        self.assertEqual(bridge._headers["Content-Type"], "application/json")

    def test_api_version_default(self) -> None:
        os.environ.pop("SHOPIFY_ADMIN_API_VERSION", None)
        bridge = ShopifySovereignBridge("tok", "shop.myshopify.com")
        self.assertIn("2026-04", bridge.api_base)

    def test_api_version_from_env(self) -> None:
        os.environ["SHOPIFY_ADMIN_API_VERSION"] = "2025-01"
        try:
            bridge = ShopifySovereignBridge("tok", "shop.myshopify.com")
            self.assertIn("2025-01", bridge.api_base)
        finally:
            os.environ.pop("SHOPIFY_ADMIN_API_VERSION", None)


class TestSyncRobertToShopify(unittest.TestCase):
    def _make_bridge(self) -> ShopifySovereignBridge:
        return ShopifySovereignBridge("test_token", "teststore.myshopify.com")

    def test_returns_fallback_string_on_network_error(self) -> None:
        bridge = self._make_bridge()
        with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("no network")):
            result = bridge.sync_robert_to_shopify(99, {"fitScore": 87})
        self.assertEqual(result, "Checkout de Shopify listo para Look 99")

    def test_returns_invoice_url_on_success(self) -> None:
        bridge = self._make_bridge()
        fake_invoice = "https://teststore.myshopify.com/invoice/draft/abc123"
        fake_response_body = json.dumps(
            {"draft_order": {"invoice_url": fake_invoice}}
        ).encode("utf-8")
        mock_resp = MagicMock()
        mock_resp.read.return_value = fake_response_body
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        with patch("urllib.request.urlopen", return_value=mock_resp):
            result = bridge.sync_robert_to_shopify(42, {"fitScore": 95})
        self.assertEqual(result, fake_invoice)

    def test_payload_contains_fit_score(self) -> None:
        bridge = self._make_bridge()
        captured: list[bytes] = []

        def fake_urlopen(req, timeout=None):
            captured.append(req.data)
            raise urllib.error.URLError("abort after capture")

        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            bridge.sync_robert_to_shopify(7, {"fitScore": 73})

        body = json.loads(captured[0].decode("utf-8"))
        props = body["draft_order"]["line_items"][0]["properties"]
        names = {p["name"]: p["value"] for p in props}
        self.assertEqual(names["Robert_Fit_Score"], "73%")
        self.assertEqual(names["Biometric_Validation"], "Sovereign_V10")

    def test_payload_contains_correct_variant_id(self) -> None:
        bridge = self._make_bridge()
        captured: list[bytes] = []

        def fake_urlopen(req, timeout=None):
            captured.append(req.data)
            raise urllib.error.URLError("abort after capture")

        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            bridge.sync_robert_to_shopify(12345, {"fitScore": 80})

        body = json.loads(captured[0].decode("utf-8"))
        self.assertEqual(body["draft_order"]["line_items"][0]["variant_id"], 12345)
        self.assertEqual(body["draft_order"]["line_items"][0]["quantity"], 1)

    def test_note_mentions_espejo_digital(self) -> None:
        bridge = self._make_bridge()
        captured: list[bytes] = []

        def fake_urlopen(req, timeout=None):
            captured.append(req.data)
            raise urllib.error.URLError("abort after capture")

        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            bridge.sync_robert_to_shopify(1, {"fitScore": 50})

        body = json.loads(captured[0].decode("utf-8"))
        self.assertIn("Espejo Digital TryOnYou", body["draft_order"]["note"])

    def test_missing_fit_score_defaults_to_zero(self) -> None:
        bridge = self._make_bridge()
        captured: list[bytes] = []

        def fake_urlopen(req, timeout=None):
            captured.append(req.data)
            raise urllib.error.URLError("abort after capture")

        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            bridge.sync_robert_to_shopify(3, {})

        body = json.loads(captured[0].decode("utf-8"))
        props = {p["name"]: p["value"] for p in body["draft_order"]["line_items"][0]["properties"]}
        self.assertEqual(props["Robert_Fit_Score"], "0%")

    def test_returns_fallback_when_invoice_url_absent(self) -> None:
        bridge = self._make_bridge()
        fake_response_body = json.dumps({"draft_order": {}}).encode("utf-8")
        mock_resp = MagicMock()
        mock_resp.read.return_value = fake_response_body
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        with patch("urllib.request.urlopen", return_value=mock_resp):
            result = bridge.sync_robert_to_shopify(5, {"fitScore": 60})
        self.assertEqual(result, "Checkout de Shopify listo para Look 5")


class TestUpdateInventoryPhysics(unittest.TestCase):
    def _make_bridge(self) -> ShopifySovereignBridge:
        return ShopifySovereignBridge("test_token", "teststore.myshopify.com")

    def test_prints_sync_message(self) -> None:
        bridge = self._make_bridge()
        with patch("builtins.print") as mock_print:
            bridge.update_inventory_physics("linen_coat_v3", -1)
        mock_print.assert_called_once()
        call_args = mock_print.call_args[0][0]
        self.assertIn("linen_coat_v3", call_args)
        self.assertIn("-1", call_args)

    def test_returns_none(self) -> None:
        bridge = self._make_bridge()
        with patch("builtins.print"):
            result = bridge.update_inventory_physics("jacket_42", 5)
        self.assertIsNone(result)

    def test_prints_fabric_key_and_stock_change(self) -> None:
        bridge = self._make_bridge()
        with patch("builtins.print") as mock_print:
            bridge.update_inventory_physics("silk_dress", 3)
        printed = mock_print.call_args[0][0]
        self.assertIn("silk_dress", printed)
        self.assertIn("3", printed)


if __name__ == "__main__":
    unittest.main()
