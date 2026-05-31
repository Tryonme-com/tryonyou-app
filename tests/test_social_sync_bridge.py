"""Tests para el Social Sync Bridge — Protocolo_Soberania_V10_Social_Sync."""

from __future__ import annotations

import os
import sys
import unittest

_API = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "api"))
if _API not in sys.path:
    sys.path.insert(0, _API)

from social_sync_bridge import (
    SOCIAL_SYNC_FLOW,
    _SOCIAL_SYNC_ALLOWED_EVENTS,
    _social_sync_webhook_url,
)


class TestSocialSyncFlow(unittest.TestCase):
    def test_flow_name(self) -> None:
        self.assertEqual(SOCIAL_SYNC_FLOW["name"], "Protocolo_Soberania_V10_Social_Sync")

    def test_flow_has_three_modules(self) -> None:
        self.assertEqual(len(SOCIAL_SYNC_FLOW["flow"]), 3)

    def test_module_1_google_drive(self) -> None:
        mod = SOCIAL_SYNC_FLOW["flow"][0]
        self.assertEqual(mod["id"], 1)
        self.assertEqual(mod["module"], "google-drive:watch-files")
        self.assertEqual(mod["metadata"]["folder"], "PAU_ASSETS_STIRPE")

    def test_module_2_openai(self) -> None:
        mod = SOCIAL_SYNC_FLOW["flow"][1]
        self.assertEqual(mod["id"], 2)
        self.assertEqual(mod["module"], "openai:create-completion")
        self.assertIn("PCT/EP2025/067317", mod["metadata"]["prompt"])
        self.assertIn("gpt-4-luxury-edition", mod["metadata"]["model"])

    def test_module_3_instagram(self) -> None:
        mod = SOCIAL_SYNC_FLOW["flow"][2]
        self.assertEqual(mod["id"], 3)
        self.assertEqual(mod["module"], "instagram-business:create-photo-post")
        self.assertIn("webContentLink", mod["metadata"]["image_url"])
        self.assertIn("choices", mod["metadata"]["caption"])

    def test_flow_version(self) -> None:
        self.assertEqual(SOCIAL_SYNC_FLOW["metadata"]["version"], "V10_OMEGA")

    def test_flow_author(self) -> None:
        self.assertEqual(SOCIAL_SYNC_FLOW["metadata"]["author"], "P.A.U. Agent")


class TestSocialSyncAllowedEvents(unittest.TestCase):
    def test_social_post_pau_allowed(self) -> None:
        self.assertIn("social_post_pau", _SOCIAL_SYNC_ALLOWED_EVENTS)

    def test_unknown_event_not_allowed(self) -> None:
        self.assertNotIn("unknown_event", _SOCIAL_SYNC_ALLOWED_EVENTS)

    def test_balmain_event_not_in_social_sync(self) -> None:
        self.assertNotIn("balmain_brand_click", _SOCIAL_SYNC_ALLOWED_EVENTS)


class TestSocialSyncWebhookUrl(unittest.TestCase):
    def test_returns_empty_when_not_set(self) -> None:
        os.environ.pop("MAKE_SOCIAL_SYNC_WEBHOOK_URL", None)
        self.assertEqual(_social_sync_webhook_url(), "")

    def test_returns_value_when_set(self) -> None:
        os.environ["MAKE_SOCIAL_SYNC_WEBHOOK_URL"] = "https://hook.eu2.make.com/test123"
        try:
            self.assertEqual(
                _social_sync_webhook_url(),
                "https://hook.eu2.make.com/test123",
            )
        finally:
            os.environ.pop("MAKE_SOCIAL_SYNC_WEBHOOK_URL", None)

    def test_strips_whitespace(self) -> None:
        os.environ["MAKE_SOCIAL_SYNC_WEBHOOK_URL"] = "  https://hook.eu2.make.com/abc  "
        try:
            self.assertEqual(
                _social_sync_webhook_url(),
                "https://hook.eu2.make.com/abc",
            )
        finally:
            os.environ.pop("MAKE_SOCIAL_SYNC_WEBHOOK_URL", None)


if __name__ == "__main__":
    unittest.main()
