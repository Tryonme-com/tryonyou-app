"""Tests para el bot Telegram PAU (pau_bot.py)."""

from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Añadir el directorio raíz al path para importar el módulo
_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_message(text: str = "hola") -> MagicMock:
    """Construye un mensaje Telegram simulado."""
    msg = MagicMock()
    msg.text = text
    msg.chat.id = 12345
    msg.message_id = 1
    return msg


def _make_env(extra: dict | None = None) -> dict:
    """Entorno mínimo para cargar pau_bot sin errores."""
    env = {
        "TELEGRAM_TOKEN": "123456789:AAHfaketoken",
        "GEMINI_API_KEY": "fake-gemini-key",
    }
    if extra:
        env.update(extra)
    return env


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestPauBotMissingToken(unittest.TestCase):
    """Verifica que el módulo falla con error claro si falta el token."""

    def test_raises_valueerror_without_token(self) -> None:
        """Debe lanzar ValueError si TELEGRAM_TOKEN no está configurado."""
        import importlib
        env = {"TELEGRAM_TOKEN": "", "GEMINI_API_KEY": "fake-gemini-key"}
        with patch("google.generativeai.configure"), \
             patch("google.generativeai.GenerativeModel"):
            with patch.dict(os.environ, env, clear=False):
                with self.assertRaises(ValueError):
                    import pau_bot
                    importlib.reload(pau_bot)

    def test_raises_valueerror_without_gemini_key(self) -> None:
        """Debe lanzar ValueError si GEMINI_API_KEY no está configurado."""
        import importlib
        env = {"TELEGRAM_TOKEN": "123456789:AAHfaketoken", "GEMINI_API_KEY": ""}
        with patch("google.generativeai.configure"), \
             patch("google.generativeai.GenerativeModel"):
            with patch.dict(os.environ, env, clear=False):
                with self.assertRaises(ValueError):
                    import pau_bot
                    importlib.reload(pau_bot)


class TestPauBotModule(unittest.TestCase):
    """Verifica que el módulo pau_bot carga correctamente con token simulado."""

    def test_module_loads_with_mock_token(self) -> None:
        """El módulo debe importarse sin errores cuando hay un token de entorno."""
        with patch("google.generativeai.configure"), \
             patch("google.generativeai.GenerativeModel"):
            with patch.dict(os.environ, _make_env(), clear=False):
                import importlib
                import pau_bot
                importlib.reload(pau_bot)
        self.assertTrue(True)

    def test_project_id_is_set(self) -> None:
        """PROJECT_ID debe tener el valor del proyecto Google Studio."""
        with patch("google.generativeai.configure"), \
             patch("google.generativeai.GenerativeModel"):
            with patch.dict(os.environ, _make_env(), clear=False):
                import importlib
                import pau_bot
                importlib.reload(pau_bot)
        self.assertEqual(pau_bot.PROJECT_ID, "gen-lang-client-0091228222")

    def test_system_instructions_contains_pau(self) -> None:
        """SYSTEM_INSTRUCTIONS debe mencionar a P.A.U. y Eric Lafayette."""
        with patch("google.generativeai.configure"), \
             patch("google.generativeai.GenerativeModel"):
            with patch.dict(os.environ, _make_env(), clear=False):
                import importlib
                import pau_bot
                importlib.reload(pau_bot)
        self.assertIn("P.A.U.", pau_bot.SYSTEM_INSTRUCTIONS)
        self.assertIn("Eric Lafayette", pau_bot.SYSTEM_INSTRUCTIONS)


class TestHandleMessage(unittest.TestCase):
    """Valida el handler principal handle_message con integración Gemini."""

    def setUp(self) -> None:
        with patch("google.generativeai.configure"), \
             patch("google.generativeai.GenerativeModel"):
            with patch.dict(os.environ, _make_env(), clear=False):
                import importlib
                import pau_bot
                importlib.reload(pau_bot)
                self.pau_bot = pau_bot

    def test_replies_using_gemini_response(self) -> None:
        """Debe enviar la respuesta generada por el modelo Gemini al usuario."""
        msg = _make_message("¿qué puedes hacer?")
        mock_ai_response = MagicMock()
        mock_ai_response.text = "Puedo ayudarte con tu silueta perfecta."

        with patch.object(self.pau_bot.model, "generate_content", return_value=mock_ai_response) as mock_gen, \
             patch.object(self.pau_bot.bot, "reply_to") as mock_reply:
            self.pau_bot.handle_message(msg)

        mock_gen.assert_called_once()
        prompt_used = mock_gen.call_args[0][0]
        self.assertIn(self.pau_bot.SYSTEM_INSTRUCTIONS, prompt_used)
        self.assertIn(msg.text, prompt_used)
        mock_reply.assert_called_once_with(msg, mock_ai_response.text)

    def test_replies_with_error_message_on_exception(self) -> None:
        """Si generate_content lanza excepción, responde con mensaje de error amable."""
        msg = _make_message("fallo")
        with patch.object(self.pau_bot.model, "generate_content", side_effect=Exception("API error")), \
             patch.object(self.pau_bot.bot, "reply_to") as mock_reply:
            self.pau_bot.handle_message(msg)

        mock_reply.assert_called_once_with(
            msg,
            "Lo lamento, estoy experimentando una breve interrupción en la conexión del probador.",
        )

    def test_handles_reply_to_exception_gracefully(self) -> None:
        """Si bot.reply_to lanza excepción en la respuesta de Gemini, el handler debe capturarla y responder con mensaje de error."""
        msg = _make_message("fallo2")
        mock_ai_response = MagicMock()
        mock_ai_response.text = "respuesta"

        with patch.object(self.pau_bot.model, "generate_content", return_value=mock_ai_response), \
             patch.object(self.pau_bot.bot, "reply_to", side_effect=[Exception("network error"), None]) as mock_reply:
            try:
                self.pau_bot.handle_message(msg)
            except Exception:
                self.fail("handle_message propagó una excepción inesperada")

        self.assertEqual(mock_reply.call_count, 2)

    def test_handler_registered(self) -> None:
        """handle_message debe estar registrado como message handler."""
        handlers = [
            h
            for h in self.pau_bot.bot.message_handlers
            if h.get("filters", {}).get("func") is not None
        ]
        self.assertTrue(
            len(handlers) >= 1,
            "No se encontró ningún handler de mensajes registrado con func=lambda",
        )


class TestWelcomeHandler(unittest.TestCase):
    """Valida el handler /start."""

    def setUp(self) -> None:
        with patch("google.generativeai.configure"), \
             patch("google.generativeai.GenerativeModel"):
            with patch.dict(os.environ, _make_env(), clear=False):
                import importlib
                import pau_bot
                importlib.reload(pau_bot)
                self.pau_bot = pau_bot

    def test_welcome_replies_with_greeting(self) -> None:
        """El handler /start debe responder con el saludo de bienvenida."""
        msg = _make_message("/start")
        with patch.object(self.pau_bot.bot, "reply_to") as mock_reply:
            self.pau_bot.welcome(msg)
        mock_reply.assert_called_once_with(
            msg,
            "Bienvenido a TryOnYou. Soy P.A.U., su asistente personal de imagen. ¿En qué puedo asistirle hoy con su silueta?",
        )


if __name__ == "__main__":
    unittest.main()
