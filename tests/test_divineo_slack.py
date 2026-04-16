"""Tests para notificaciones de soberanía vía Slack."""

from __future__ import annotations

import json
import os
import unittest
from unittest.mock import MagicMock, patch

from divineo_slack import (
    _resolve_sovereignty_webhook_url,
    build_sovereignty_payload,
    notify_sovereignty_status,
)


class TestSovereigntyPayload(unittest.TestCase):
    def test_payload_sets_red_color_for_blocked_status(self) -> None:
        payload = build_sovereignty_payload(484908.0, "BLOQUEO TOTAL ACTIVO")
        attachment = payload["attachments"][0]
        self.assertEqual(attachment["color"], "#FF3B30")
        threshold_field = attachment["fields"][2]
        self.assertEqual(threshold_field["value"], "484908.00 € TTC")

    def test_payload_sets_green_color_for_non_blocked_status(self) -> None:
        payload = build_sovereignty_payload(1200, "OPERATIVO")
        attachment = payload["attachments"][0]
        self.assertEqual(attachment["color"], "#34C759")


class TestSovereigntyWebhookResolution(unittest.TestCase):
    def test_prefers_sovereignty_webhook(self) -> None:
        env = {
            "SOVEREIGNTY_SLACK_WEBHOOK_URL": "https://hooks.slack.com/services/SOV/WEB/HOOK",
            "SLACK_WEBHOOK_URL": "https://hooks.slack.com/services/GEN/WEB/HOOK",
        }
        with patch.dict(os.environ, env, clear=True):
            self.assertEqual(
                _resolve_sovereignty_webhook_url(),
                "https://hooks.slack.com/services/SOV/WEB/HOOK",
            )

    def test_fallbacks_to_general_webhook(self) -> None:
        env = {
            "SLACK_WEBHOOK_URL": "https://hooks.slack.com/services/GEN/WEB/HOOK",
        }
        with patch.dict(os.environ, env, clear=True):
            self.assertEqual(
                _resolve_sovereignty_webhook_url(),
                "https://hooks.slack.com/services/GEN/WEB/HOOK",
            )


class TestNotifySovereigntyStatus(unittest.TestCase):
    def test_returns_false_if_webhook_missing(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(notify_sovereignty_status(1000, "OPERATIVO"))

    @patch("urllib.request.urlopen")
    def test_posts_payload_when_webhook_available(self, mock_urlopen: MagicMock) -> None:
        mock_urlopen.return_value.__enter__.return_value = object()
        env = {
            "SOVEREIGNTY_SLACK_WEBHOOK_URL": (
                "https://hooks.slack.com/services/SOVEREIGNTY/WEBHOOK/ID"
            ),
        }
        with patch.dict(os.environ, env, clear=True):
            ok = notify_sovereignty_status(484908.0, "BLOQUEO TOTAL ACTIVO")

        self.assertTrue(ok)
        self.assertEqual(mock_urlopen.call_count, 1)
        request_obj = mock_urlopen.call_args.args[0]
        self.assertEqual(
            request_obj.full_url,
            "https://hooks.slack.com/services/SOVEREIGNTY/WEBHOOK/ID",
        )
        payload = json.loads(request_obj.data.decode("utf-8"))
        self.assertEqual(payload["attachments"][0]["color"], "#FF3B30")


if __name__ == "__main__":
    unittest.main()
