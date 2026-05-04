"""Tests for telegram_signal_system — TryOnYouSignals."""

from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from telegram_signal_system import TryOnYouSignals


class TestTryOnYouSignalsInit(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["TELEGRAM_BOT_TOKEN"] = "test-bot-token"
        os.environ["TELEGRAM_CHAT_ID"] = "123456789"

    def tearDown(self) -> None:
        for key in ("TELEGRAM_BOT_TOKEN", "TELEGRAM_TOKEN", "TELEGRAM_CHAT_ID"):
            os.environ.pop(key, None)

    def test_reads_bot_token_from_env(self) -> None:
        sig = TryOnYouSignals()
        self.assertEqual(sig.bot_token, "test-bot-token")

    def test_reads_chat_id_from_env(self) -> None:
        sig = TryOnYouSignals()
        self.assertEqual(sig.chat_id, "123456789")

    def test_api_url_contains_token(self) -> None:
        sig = TryOnYouSignals()
        self.assertIn("test-bot-token", sig.api_url)

    def test_api_url_contains_sendmessage(self) -> None:
        sig = TryOnYouSignals()
        self.assertIn("sendMessage", sig.api_url)

    def test_fallback_to_telegram_token(self) -> None:
        os.environ.pop("TELEGRAM_BOT_TOKEN", None)
        os.environ["TELEGRAM_TOKEN"] = "fallback-token"
        sig = TryOnYouSignals()
        self.assertEqual(sig.bot_token, "fallback-token")

    def test_raises_without_token(self) -> None:
        os.environ.pop("TELEGRAM_BOT_TOKEN", None)
        os.environ.pop("TELEGRAM_TOKEN", None)
        with self.assertRaises(RuntimeError):
            TryOnYouSignals()

    def test_raises_without_chat_id(self) -> None:
        os.environ.pop("TELEGRAM_CHAT_ID", None)
        with self.assertRaises(RuntimeError):
            TryOnYouSignals()


class TestTryOnYouSignalsSend(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["TELEGRAM_BOT_TOKEN"] = "test-bot-token"
        os.environ["TELEGRAM_CHAT_ID"] = "123456789"
        self.sig = TryOnYouSignals()

    def tearDown(self) -> None:
        for key in ("TELEGRAM_BOT_TOKEN", "TELEGRAM_TOKEN", "TELEGRAM_CHAT_ID"):
            os.environ.pop(key, None)

    @patch("telegram_signal_system.requests")
    def test_send_posts_to_telegram_api(self, mock_requests: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_requests.post.return_value = mock_response

        self.sig.send_sovereignty_signal("test message")

        mock_requests.post.assert_called_once()
        url = mock_requests.post.call_args[0][0]
        self.assertIn("api.telegram.org", url)

    @patch("telegram_signal_system.requests")
    def test_send_includes_message_in_payload(self, mock_requests: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_requests.post.return_value = mock_response

        self.sig.send_sovereignty_signal("hello world")

        call_kwargs = mock_requests.post.call_args[1]
        payload = call_kwargs["json"]
        self.assertIn("hello world", payload["text"])

    @patch("telegram_signal_system.requests")
    def test_send_includes_chat_id_in_payload(self, mock_requests: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_requests.post.return_value = mock_response

        self.sig.send_sovereignty_signal("test")

        call_kwargs = mock_requests.post.call_args[1]
        payload = call_kwargs["json"]
        self.assertEqual(payload["chat_id"], "123456789")

    @patch("telegram_signal_system.requests")
    def test_send_includes_patent_in_text(self, mock_requests: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_requests.post.return_value = mock_response

        self.sig.send_sovereignty_signal("msg")

        call_kwargs = mock_requests.post.call_args[1]
        payload = call_kwargs["json"]
        self.assertIn("PCT/EP2025/067317", payload["text"])

    @patch("telegram_signal_system.requests")
    def test_send_full_message_format(self, mock_requests: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_requests.post.return_value = mock_response

        self.sig.send_sovereignty_signal("activación completada")

        call_kwargs = mock_requests.post.call_args[1]
        payload = call_kwargs["json"]
        self.assertIn("MASTER OMEGA ALERT", payload["text"])
        self.assertIn("activación completada", payload["text"])
        self.assertIn("PATENTE: PCT/EP2025/067317", payload["text"])
        self.assertEqual(payload["parse_mode"], "Markdown")

    @patch("telegram_signal_system.requests")
    def test_send_handles_request_exception_gracefully(self, mock_requests: MagicMock) -> None:
        mock_requests.post.side_effect = Exception("network error")

        # Should not raise; prints to stderr instead
        try:
            self.sig.send_sovereignty_signal("test")
        except Exception:
            self.fail("send_sovereignty_signal raised an unexpected exception")


if __name__ == "__main__":
    unittest.main()
