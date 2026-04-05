"""Tests para el bot Telegram PAU (pau_bot.py).

@CertezaAbsoluta @lo+erestu PCT/EP2025/067317
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""

from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


def _make_message(text: str = "hola") -> MagicMock:
    """Construye un mensaje Telegram simulado."""
    msg = MagicMock()
    msg.text = text
    msg.chat.id = 12345
    msg.message_id = 1
    return msg


def _load_pau_bot():
    """Load/reload pau_bot with a fake token."""
    import importlib

    env = {
        "TELEGRAM_TOKEN": "123456789:AAHfaketoken",
        "GEMINI_API_KEY": "",
        "PROJECT_ID": "gen-lang-client-0091228222",
        "ENVIRONMENT": "testing",
    }
    with patch.dict(os.environ, env, clear=False):
        import pau_bot

        importlib.reload(pau_bot)
        return pau_bot


class TestPauBotMissingToken(unittest.TestCase):
    """Verifica que el módulo falla con error claro si falta el token."""

    def test_raises_valueerror_without_token(self) -> None:
        import importlib

        env = {"TELEGRAM_TOKEN": ""}
        with patch.dict(os.environ, env, clear=False):
            with self.assertRaises(ValueError):
                import pau_bot

                importlib.reload(pau_bot)


class TestPauBotModule(unittest.TestCase):
    """Verifica que el módulo pau_bot carga correctamente con token simulado."""

    def test_module_loads_with_mock_token(self) -> None:
        pb = _load_pau_bot()
        self.assertTrue(True)

    def test_project_id_is_set(self) -> None:
        pb = _load_pau_bot()
        self.assertEqual(pb.PROJECT_ID, "gen-lang-client-0091228222")

    def test_environment_from_env(self) -> None:
        pb = _load_pau_bot()
        self.assertEqual(pb.ENVIRONMENT, "testing")


class TestGenerateResponse(unittest.TestCase):
    """Valida generate_response en modo fallback (sin Gemini key)."""

    def setUp(self) -> None:
        self.pau_bot = _load_pau_bot()

    def test_fallback_response_without_gemini(self) -> None:
        resp = self.pau_bot.generate_response("hola")
        self.assertIn("P.A.U.", resp)
        self.assertIn("activo", resp.lower())

    def test_fallback_contains_tryonyou(self) -> None:
        resp = self.pau_bot.generate_response("test")
        self.assertIn("TryOnYou", resp)


class TestHandlePauLogic(unittest.TestCase):
    """Valida el handler principal handle_pau_logic."""

    def setUp(self) -> None:
        self.pau_bot = _load_pau_bot()

    def test_replies_to_message(self) -> None:
        msg = _make_message("prueba")
        with patch.object(self.pau_bot.bot, "reply_to") as mock_reply:
            self.pau_bot.handle_pau_logic(msg)
        mock_reply.assert_called_once()
        reply_text = mock_reply.call_args[0][1]
        self.assertIn("P.A.U.", reply_text)

    def test_handles_reply_to_exception_gracefully(self) -> None:
        msg = _make_message("fallo")
        with patch.object(
            self.pau_bot.bot, "reply_to", side_effect=Exception("network error")
        ):
            try:
                self.pau_bot.handle_pau_logic(msg)
            except Exception:
                self.fail("handle_pau_logic propagó una excepción inesperada")

    def test_handler_registered(self) -> None:
        handlers = [
            h
            for h in self.pau_bot.bot.message_handlers
            if h.get("filters", {}).get("func") is not None
        ]
        self.assertTrue(
            len(handlers) >= 1,
            "No se encontró ningún handler de mensajes registrado con func=lambda",
        )

    def test_ignores_empty_text(self) -> None:
        msg = _make_message("")
        with patch.object(self.pau_bot.bot, "reply_to") as mock_reply:
            self.pau_bot.handle_pau_logic(msg)
        mock_reply.assert_not_called()


class TestHandleStart(unittest.TestCase):
    """Valida /start y /help."""

    def setUp(self) -> None:
        self.pau_bot = _load_pau_bot()

    def test_start_replies_with_welcome(self) -> None:
        msg = _make_message("/start")
        with patch.object(self.pau_bot.bot, "reply_to") as mock_reply:
            self.pau_bot.handle_start(msg)
        mock_reply.assert_called_once()
        text = mock_reply.call_args[0][1]
        self.assertIn("Bienvenido", text)
        self.assertIn("P.A.U.", text)

    def test_start_handles_exception(self) -> None:
        msg = _make_message("/start")
        with patch.object(
            self.pau_bot.bot, "reply_to", side_effect=Exception("err")
        ):
            self.pau_bot.handle_start(msg)


class TestHandleStatus(unittest.TestCase):
    """Valida /status."""

    def setUp(self) -> None:
        self.pau_bot = _load_pau_bot()

    def test_status_includes_project_id(self) -> None:
        msg = _make_message("/status")
        with patch.object(self.pau_bot.bot, "reply_to") as mock_reply:
            self.pau_bot.handle_status(msg)
        mock_reply.assert_called_once()
        text = mock_reply.call_args[0][1]
        self.assertIn("gen-lang-client-0091228222", text)

    def test_status_shows_gemini_off(self) -> None:
        msg = _make_message("/status")
        with patch.object(self.pau_bot.bot, "reply_to") as mock_reply:
            self.pau_bot.handle_status(msg)
        text = mock_reply.call_args[0][1]
        self.assertIn("🔴", text)


class TestNoHardcodedSecrets(unittest.TestCase):
    """Verify no real tokens in source."""

    def test_no_real_telegram_token_in_source(self) -> None:
        with open(os.path.join(_ROOT, "pau_bot.py"), encoding="utf-8") as f:
            content = f.read()
        self.assertNotIn("8788913760", content)
        self.assertNotIn("AAE2g87I0e", content)

    def test_no_real_gemini_key_in_source(self) -> None:
        with open(os.path.join(_ROOT, "pau_bot.py"), encoding="utf-8") as f:
            content = f.read()
        self.assertNotIn("AIzaSy", content)


class TestSystemPrompt(unittest.TestCase):
    """Validate PAU_SYSTEM_PROMPT content."""

    def setUp(self) -> None:
        self.pau_bot = _load_pau_bot()

    def test_prompt_mentions_tryonyou(self) -> None:
        self.assertIn("TryOnYou", self.pau_bot.PAU_SYSTEM_PROMPT)

    def test_prompt_mentions_patent(self) -> None:
        self.assertIn("PCT/EP2025/067317", self.pau_bot.PAU_SYSTEM_PROMPT)

    def test_prompt_mentions_eric_lafayette(self) -> None:
        self.assertIn("Eric Lafayette", self.pau_bot.PAU_SYSTEM_PROMPT)

    def test_prompt_mentions_project_id(self) -> None:
        self.assertIn("gen-lang-client-0091228222", self.pau_bot.PAU_SYSTEM_PROMPT)


if __name__ == "__main__":
    unittest.main()
