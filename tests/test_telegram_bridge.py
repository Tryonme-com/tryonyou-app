"""Tests for telegram_bridge.TelegramBunkerBridge."""

from __future__ import annotations

import io
import os
import sys
import unittest
from unittest.mock import patch

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from telegram_bridge import TelegramBunkerBridge


class TestTelegramBunkerBridgeInit(unittest.TestCase):
    def setUp(self) -> None:
        self.bridge = TelegramBunkerBridge()

    def test_initial_bot_status_is_sync_pending(self) -> None:
        self.assertEqual(self.bridge.bot_status, "SYNC_PENDING")

    def test_authorized_users_contains_ruben_espinar(self) -> None:
        self.assertIn("RUBEN_ESPINAR", self.bridge.authorized_users)

    def test_priority_channels_contains_payments(self) -> None:
        self.assertIn("PAYMENTS", self.bridge.priority_channels)

    def test_priority_channels_contains_leads(self) -> None:
        self.assertIn("LEADS", self.bridge.priority_channels)

    def test_priority_channels_contains_alerts(self) -> None:
        self.assertIn("ALERTS", self.bridge.priority_channels)


class TestConnectBackbone(unittest.TestCase):
    def setUp(self) -> None:
        self.bridge = TelegramBunkerBridge()

    def test_connect_backbone_returns_true(self) -> None:
        with patch("builtins.print"):
            result = self.bridge.connect_backbone()
        self.assertTrue(result)

    def test_connect_backbone_sets_status_active(self) -> None:
        with patch("builtins.print"):
            self.bridge.connect_backbone()
        self.assertEqual(self.bridge.bot_status, "ACTIVE")

    def test_connect_backbone_prints_activation_header(self) -> None:
        with patch("builtins.print") as mock_print:
            self.bridge.connect_backbone()
        printed = " ".join(str(c) for c in [call.args[0] for call in mock_print.call_args_list])
        self.assertIn("ACTIVANDO PUENTE TELEGRAM", printed)

    def test_connect_backbone_prints_jules_sync(self) -> None:
        with patch("builtins.print") as mock_print:
            self.bridge.connect_backbone()
        printed = " ".join(str(call.args[0]) for call in mock_print.call_args_list)
        self.assertIn("Jules", printed)

    def test_connect_backbone_prints_qonto_webhook(self) -> None:
        with patch("builtins.print") as mock_print:
            self.bridge.connect_backbone()
        printed = " ".join(str(call.args[0]) for call in mock_print.call_args_list)
        self.assertIn("Qonto", printed)

    def test_connect_backbone_prints_patent_monitor(self) -> None:
        with patch("builtins.print") as mock_print:
            self.bridge.connect_backbone()
        printed = " ".join(str(call.args[0]) for call in mock_print.call_args_list)
        self.assertIn("PCT/EP2025/067317", printed)


class TestSendTestSignal(unittest.TestCase):
    def setUp(self) -> None:
        self.bridge = TelegramBunkerBridge()

    def test_send_test_signal_prints_message(self) -> None:
        with patch("builtins.print") as mock_print:
            self.bridge.send_test_signal()
        printed = " ".join(str(call.args[0]) for call in mock_print.call_args_list)
        self.assertIn("Señal de prueba", printed)

    def test_send_test_signal_prints_objetivo(self) -> None:
        with patch("builtins.print") as mock_print:
            self.bridge.send_test_signal()
        printed = " ".join(str(call.args[0]) for call in mock_print.call_args_list)
        self.assertIn("27.500", printed)

    def test_send_test_signal_prints_operativo(self) -> None:
        with patch("builtins.print") as mock_print:
            self.bridge.send_test_signal()
        printed = " ".join(str(call.args[0]) for call in mock_print.call_args_list)
        self.assertIn("Operativo", printed)


if __name__ == "__main__":
    unittest.main()
