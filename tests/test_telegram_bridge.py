"""Tests para el módulo telegram_bridge — TelegramBunkerBridge V9."""

from __future__ import annotations

import io
import os
import sys
import unittest

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from telegram_bridge import (
    AUTHORIZED_USERS,
    BOT_STATUS_ACTIVE,
    BOT_STATUS_PENDING,
    BOT_VERSION,
    OBJETIVO_EUR,
    PATENTE_REF,
    PRIORITY_CHANNELS,
    TelegramBunkerBridge,
)


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------


class TestModuleConstants(unittest.TestCase):
    def test_bot_status_pending_value(self) -> None:
        self.assertEqual(BOT_STATUS_PENDING, "SYNC_PENDING")

    def test_bot_status_active_value(self) -> None:
        self.assertEqual(BOT_STATUS_ACTIVE, "ACTIVE")

    def test_authorized_users_contains_ruben(self) -> None:
        self.assertIn("RUBEN_ESPINAR", AUTHORIZED_USERS)

    def test_priority_channels_contains_payments(self) -> None:
        self.assertIn("PAYMENTS", PRIORITY_CHANNELS)

    def test_priority_channels_contains_leads(self) -> None:
        self.assertIn("LEADS", PRIORITY_CHANNELS)

    def test_priority_channels_contains_alerts(self) -> None:
        self.assertIn("ALERTS", PRIORITY_CHANNELS)

    def test_priority_channels_has_three_entries(self) -> None:
        self.assertEqual(len(PRIORITY_CHANNELS), 3)

    def test_objetivo_eur_value(self) -> None:
        self.assertAlmostEqual(OBJETIVO_EUR, 27_500.0, places=2)

    def test_patente_ref_value(self) -> None:
        self.assertEqual(PATENTE_REF, "PCT/EP2025/067317")

    def test_bot_version_value(self) -> None:
        self.assertEqual(BOT_VERSION, "V9")


# ---------------------------------------------------------------------------
# TelegramBunkerBridge — initial state
# ---------------------------------------------------------------------------


class TestTelegramBunkerBridgeInit(unittest.TestCase):
    def setUp(self) -> None:
        self.bridge = TelegramBunkerBridge()

    def test_initial_bot_status_is_pending(self) -> None:
        self.assertEqual(self.bridge.bot_status, BOT_STATUS_PENDING)

    def test_authorized_users_contains_ruben(self) -> None:
        self.assertIn("RUBEN_ESPINAR", self.bridge.authorized_users)

    def test_priority_channels_has_payments(self) -> None:
        self.assertIn("PAYMENTS", self.bridge.priority_channels)

    def test_priority_channels_has_leads(self) -> None:
        self.assertIn("LEADS", self.bridge.priority_channels)

    def test_priority_channels_has_alerts(self) -> None:
        self.assertIn("ALERTS", self.bridge.priority_channels)

    def test_authorized_users_is_copy(self) -> None:
        self.bridge.authorized_users.append("EXTRA")
        self.assertNotIn("EXTRA", AUTHORIZED_USERS)

    def test_priority_channels_is_copy(self) -> None:
        self.bridge.priority_channels.append("EXTRA")
        self.assertNotIn("EXTRA", PRIORITY_CHANNELS)


# ---------------------------------------------------------------------------
# connect_backbone
# ---------------------------------------------------------------------------


class TestConnectBackbone(unittest.TestCase):
    def _run_silently(self) -> bool:
        buf = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = buf
        try:
            result = TelegramBunkerBridge().connect_backbone()
        finally:
            sys.stdout = old_stdout
        self._output = buf.getvalue()
        return result

    def setUp(self) -> None:
        self._output = ""
        self._result = self._run_silently()

    def test_returns_true(self) -> None:
        self.assertTrue(self._result)

    def test_output_contains_activando(self) -> None:
        self.assertIn("ACTIVANDO PUENTE TELEGRAM", self._output)

    def test_output_contains_jules(self) -> None:
        self.assertIn("Jules", self._output)

    def test_output_contains_qonto(self) -> None:
        self.assertIn("Qonto", self._output)

    def test_output_contains_patente_ref(self) -> None:
        self.assertIn(PATENTE_REF, self._output)

    def test_output_contains_test_signal(self) -> None:
        self.assertIn("Señal de prueba", self._output)


class TestConnectBackboneSetsStatus(unittest.TestCase):
    def test_status_becomes_active(self) -> None:
        bridge = TelegramBunkerBridge()
        buf = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = buf
        try:
            bridge.connect_backbone()
        finally:
            sys.stdout = old_stdout
        self.assertEqual(bridge.bot_status, BOT_STATUS_ACTIVE)


# ---------------------------------------------------------------------------
# send_test_signal
# ---------------------------------------------------------------------------


class TestSendTestSignal(unittest.TestCase):
    def _run_silently(self) -> dict:
        bridge = TelegramBunkerBridge()
        buf = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = buf
        try:
            payload = bridge.send_test_signal()
        finally:
            sys.stdout = old_stdout
        self._output = buf.getvalue()
        return payload

    def setUp(self) -> None:
        self._output = ""
        self._payload = self._run_silently()

    def test_returns_dict(self) -> None:
        self.assertIsInstance(self._payload, dict)

    def test_payload_has_origin(self) -> None:
        self.assertIn("origin", self._payload)

    def test_payload_origin_is_bunker_v11(self) -> None:
        self.assertEqual(self._payload["origin"], "Bunker_V11")

    def test_payload_has_message(self) -> None:
        self.assertIn("message", self._payload)

    def test_payload_message_contains_operativo(self) -> None:
        self.assertIn("Operativo", self._payload["message"])

    def test_payload_message_contains_objetivo(self) -> None:
        self.assertIn("27.500", self._payload["message"])

    def test_payload_has_timestamp(self) -> None:
        self.assertIn("timestamp", self._payload)

    def test_output_contains_senal(self) -> None:
        self.assertIn("Señal de prueba", self._output)


if __name__ == "__main__":
    unittest.main()
