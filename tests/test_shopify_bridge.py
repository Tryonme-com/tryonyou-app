"""Tests for ShopifySovereignBridge — Protocolo Robert / Biometría V10."""

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

from shopify_bridge import ShopifySovereignBridge  # noqa: E402


class TestShopifySovereignBridgeInit(unittest.TestCase):
    def test_api_base_built_from_shop_url(self) -> None:
        bridge = ShopifySovereignBridge("tok", "mystore.myshopify.com")
        self.assertIn("mystore.myshopify.com", bridge.api_base)
        self.assertTrue(bridge.api_base.startswith("https://"))

    def test_api_base_strips_https_prefix(self) -> None:
        bridge = ShopifySovereignBridge("tok", "https://mystore.myshopify.com")
        self.assertNotIn("https://https://", bridge.api_base)
        self.assertIn("mystore.myshopify.com", bridge.api_base)

    def test_headers_contain_access_token(self) -> None:
        bridge = ShopifySovereignBridge("secret-key", "mystore.myshopify.com")
        self.assertEqual(bridge.headers["X-Shopify-Access-Token"], "secret-key")

    def test_headers_content_type_json(self) -> None:
        bridge = ShopifySovereignBridge("tok", "mystore.myshopify.com")
        self.assertEqual(bridge.headers["Content-Type"], "application/json")

    def test_api_base_contains_admin_api(self) -> None:
        bridge = ShopifySovereignBridge("tok", "mystore.myshopify.com")
        self.assertIn("/admin/api/", bridge.api_base)


class TestSyncRobertToShopify(unittest.TestCase):
    def _make_bridge(self) -> ShopifySovereignBridge:
        return ShopifySovereignBridge("tok", "mystore.myshopify.com")

    def test_returns_invoice_url_on_success(self) -> None:
        bridge = self._make_bridge()
        mock_resp = MagicMock()
        mock_resp.status_code = 201
        mock_resp.json.return_value = {
            "draft_order": {"invoice_url": "https://mystore.myshopify.com/invoices/abc"}
        }
        with patch("shopify_bridge._requests.post", return_value=mock_resp):
            result = bridge.sync_robert_to_shopify(42, {"fitScore": 95})
        self.assertEqual(result, "https://mystore.myshopify.com/invoices/abc")

    def test_returns_fallback_string_when_no_invoice_url(self) -> None:
        bridge = self._make_bridge()
        mock_resp = MagicMock()
        mock_resp.status_code = 201
        mock_resp.json.return_value = {"draft_order": {}}
        with patch("shopify_bridge._requests.post", return_value=mock_resp):
            result = bridge.sync_robert_to_shopify(7, {"fitScore": 88})
        self.assertIsNotNone(result)
        self.assertIn("7", str(result))

    def test_returns_none_on_http_error(self) -> None:
        bridge = self._make_bridge()
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_resp.json.return_value = {}
        with patch("shopify_bridge._requests.post", return_value=mock_resp):
            result = bridge.sync_robert_to_shopify(1, {"fitScore": 80})
        self.assertIsNone(result)

    def test_returns_none_on_request_exception(self) -> None:
        import requests as real_requests

        bridge = self._make_bridge()
        with patch(
            "shopify_bridge._requests.post",
            side_effect=real_requests.RequestException("timeout"),
        ):
            result = bridge.sync_robert_to_shopify(1, {"fitScore": 80})
        self.assertIsNone(result)

    def test_payload_includes_fit_score(self) -> None:
        bridge = self._make_bridge()
        mock_resp = MagicMock()
        mock_resp.status_code = 201
        mock_resp.json.return_value = {"draft_order": {}}
        with patch("shopify_bridge._requests.post", return_value=mock_resp) as mock_post:
            bridge.sync_robert_to_shopify(99, {"fitScore": 77})
        _, kwargs = mock_post.call_args
        line = kwargs["json"]["draft_order"]["line_items"][0]
        props = {p["name"]: p["value"] for p in line["properties"]}
        self.assertEqual(props["Robert_Fit_Score"], "77%")
        self.assertEqual(props["Biometric_Validation"], "Sovereign_V10")

    def test_payload_includes_look_id_as_variant(self) -> None:
        bridge = self._make_bridge()
        mock_resp = MagicMock()
        mock_resp.status_code = 201
        mock_resp.json.return_value = {"draft_order": {}}
        with patch("shopify_bridge._requests.post", return_value=mock_resp) as mock_post:
            bridge.sync_robert_to_shopify(55, {"fitScore": 90})
        _, kwargs = mock_post.call_args
        line = kwargs["json"]["draft_order"]["line_items"][0]
        self.assertEqual(line["variant_id"], 55)
        self.assertEqual(line["quantity"], 1)

    def test_note_mentions_tryonyou(self) -> None:
        bridge = self._make_bridge()
        mock_resp = MagicMock()
        mock_resp.status_code = 201
        mock_resp.json.return_value = {"draft_order": {}}
        with patch("shopify_bridge._requests.post", return_value=mock_resp) as mock_post:
            bridge.sync_robert_to_shopify(1, {"fitScore": 85})
        _, kwargs = mock_post.call_args
        note = kwargs["json"]["draft_order"]["note"]
        self.assertIn("TryOnYou", note)


class TestUpdateInventoryPhysics(unittest.TestCase):
    def _make_bridge(self) -> ShopifySovereignBridge:
        return ShopifySovereignBridge("tok", "mystore.myshopify.com")

    def _set_location(self, loc: str = "98765") -> None:
        os.environ["SHOPIFY_LOCATION_ID"] = loc

    def tearDown(self) -> None:
        os.environ.pop("SHOPIFY_LOCATION_ID", None)

    def test_returns_true_on_success(self) -> None:
        self._set_location()
        bridge = self._make_bridge()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        with patch("shopify_bridge._requests.post", return_value=mock_resp):
            result = bridge.update_inventory_physics("LOC-123", -1)
        self.assertTrue(result)

    def test_returns_false_without_location_id_env(self) -> None:
        os.environ.pop("SHOPIFY_LOCATION_ID", None)
        bridge = self._make_bridge()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        with patch("shopify_bridge._requests.post", return_value=mock_resp):
            result = bridge.update_inventory_physics("LOC-123", -1)
        self.assertFalse(result)

    def test_returns_false_on_http_error(self) -> None:
        self._set_location()
        bridge = self._make_bridge()
        mock_resp = MagicMock()
        mock_resp.status_code = 422
        with patch("shopify_bridge._requests.post", return_value=mock_resp):
            result = bridge.update_inventory_physics("LOC-123", -1)
        self.assertFalse(result)

    def test_returns_false_on_request_exception(self) -> None:
        import requests as real_requests

        self._set_location()
        bridge = self._make_bridge()
        with patch(
            "shopify_bridge._requests.post",
            side_effect=real_requests.RequestException("conn error"),
        ):
            result = bridge.update_inventory_physics("LOC-999", -2)
        self.assertFalse(result)

    def test_prints_sync_message(self) -> None:
        self._set_location()
        bridge = self._make_bridge()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        with patch("shopify_bridge._requests.post", return_value=mock_resp):
            with patch("builtins.print") as mock_print:
                bridge.update_inventory_physics("FABRIC-7", -3)
        mock_print.assert_called_once()
        args = mock_print.call_args[0][0]
        self.assertIn("FABRIC-7", args)
        self.assertIn("-3", args)

    def test_calls_inventory_adjust_endpoint(self) -> None:
        self._set_location()
        bridge = self._make_bridge()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        with patch("shopify_bridge._requests.post", return_value=mock_resp) as mock_post:
            bridge.update_inventory_physics("LOC-42", 5)
        url = mock_post.call_args[0][0]
        self.assertIn("inventory_levels/adjust", url)

    def test_payload_uses_fabric_key_as_inventory_item_id(self) -> None:
        self._set_location("12345")
        bridge = self._make_bridge()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        with patch("shopify_bridge._requests.post", return_value=mock_resp) as mock_post:
            bridge.update_inventory_physics("ITEM-99", -2)
        _, kwargs = mock_post.call_args
        self.assertEqual(kwargs["json"]["inventory_item_id"], "ITEM-99")
        self.assertEqual(kwargs["json"]["location_id"], 12345)
        self.assertEqual(kwargs["json"]["available_adjustment"], -2)


if __name__ == "__main__":
    unittest.main()
