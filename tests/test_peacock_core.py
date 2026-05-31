"""Reglas de integración Peacock_Core / Zero-Size (unittest estándar)."""

from __future__ import annotations

import os
import sys
import unittest

_API = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "api"))
if _API not in sys.path:
    sys.path.insert(0, _API)

from peacock_core import ZERO_SIZE_LATENCY_BUDGET_MS, is_webhook_destination_forbidden


class TestPeacockCoreIntegration(unittest.TestCase):
    def test_latency_budget_is_25ms(self) -> None:
        self.assertEqual(ZERO_SIZE_LATENCY_BUDGET_MS, 25)

    def test_abvetos_webhook_blocked(self) -> None:
        self.assertTrue(
            is_webhook_destination_forbidden("https://api.abvetos.com/hook/xyz"),
        )
        self.assertTrue(
            is_webhook_destination_forbidden("https://abvetos.com/webhook"),
        )

    def test_make_and_slack_like_urls_allowed(self) -> None:
        self.assertFalse(
            is_webhook_destination_forbidden("https://hook.eu2.make.com/abc"),
        )
        self.assertFalse(
            is_webhook_destination_forbidden("https://hooks.slack.com/services/XX/YY/ZZ"),
        )


if __name__ == "__main__":
    unittest.main()
