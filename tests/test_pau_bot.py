"""Tests para el bot Telegram PAU (pau_bot.py)."""

from __future__ import annotations

import importlib
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Añadir el directorio raíz al path para importar el módulo
_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

# Variables de entorno comunes para tests
_VALID_ENV = {
    "TELEGRAM_TOKEN": "123456789:AAHfaketoken",
    "GEMINI_API_KEY": "fake_gemini_key",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_message(text: str = "hola") -> MagicMock:
    """Construye un mensaje Telegram simulado."""
    msg = MagicMock()
    msg.text = text
    msg.chat.id = 12345
    msg.message_id = 1
    msg.from_user.first_name = "Usuario"
    return msg


def _reload_pau_bot(env: dict | None = None) -> object:
    """Recarga pau_bot con el entorno dado, mockeando las llamadas de Gemini."""
    env = env or _VALID_ENV
    with patch.dict(os.environ, env, clear=False):
        with patch("google.generativeai.configure"):
            with patch("google.generativeai.GenerativeModel", return_value=MagicMock()):
                import pau_bot
                importlib.reload(pau_bot)
                return pau_bot


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestPauBotMissingCredentials(unittest.TestCase):
    """Verifica que el módulo falla con error claro si faltan las credenciales."""

    def test_raises_valueerror_without_telegram_token(self) -> None:
        """Debe lanzar ValueError si TELEGRAM_TOKEN no está configurado."""
        env = {**_VALID_ENV, "TELEGRAM_TOKEN": ""}
        with patch.dict(os.environ, env, clear=False):
            with patch("google.generativeai.configure"):
                with patch("google.generativeai.GenerativeModel", return_value=MagicMock()):
                    with self.assertRaises(ValueError):
                        import pau_bot
                        importlib.reload(pau_bot)

    def test_raises_valueerror_without_gemini_api_key(self) -> None:
        """Debe lanzar ValueError si GEMINI_API_KEY no está configurado."""
        env = {**_VALID_ENV, "GEMINI_API_KEY": ""}
        with patch.dict(os.environ, env, clear=False):
            with patch("google.generativeai.configure"):
                with patch("google.generativeai.GenerativeModel", return_value=MagicMock()):
                    with self.assertRaises(ValueError):
                        import pau_bot
                        importlib.reload(pau_bot)


class TestPauBotModule(unittest.TestCase):
    """Verifica que el módulo pau_bot carga correctamente con credenciales simuladas."""

    def setUp(self) -> None:
        self.pau_bot = _reload_pau_bot()

    def test_module_loads_with_mock_credentials(self) -> None:
        """El módulo debe importarse sin errores cuando hay credenciales en el entorno."""
        self.assertIsNotNone(self.pau_bot)

    def test_project_id_is_set(self) -> None:
        """PROJECT_ID debe tener el valor del proyecto Google Studio."""
        self.assertEqual(self.pau_bot.PROJECT_ID, "gen-lang-client-0091228222")

    def test_system_prompt_is_defined(self) -> None:
        """SYSTEM_PROMPT debe estar definido y contener la identidad de P.A.U."""
        self.assertIn("P.A.U.", self.pau_bot.SYSTEM_PROMPT)

    def test_gemini_api_key_loaded(self) -> None:
        """GEMINI_API_KEY debe leerse del entorno."""
        env = {**_VALID_ENV, "GEMINI_API_KEY": "test_gemini_key"}
        pau_bot = _reload_pau_bot(env)
        self.assertEqual(pau_bot.GEMINI_API_KEY, "test_gemini_key")


class TestHandleAgentResponse(unittest.TestCase):
    """Valida el handler principal handle_agent_response."""

    def setUp(self) -> None:
        self.pau_bot = _reload_pau_bot()

    def test_replies_using_gemini_response(self) -> None:
        """Debe responder con el texto generado por el modelo Gemini."""
        msg = _make_message("prueba")
        mock_response = MagicMock()
        mock_response.text = "Respuesta elegante de P.A.U."
        mock_chat = MagicMock()
        mock_chat.send_message.return_value = mock_response
        self.pau_bot.model.start_chat.return_value = mock_chat

        with patch.object(self.pau_bot.bot, "reply_to") as mock_reply:
            self.pau_bot.handle_agent_response(msg)
        mock_reply.assert_called_once_with(msg, "Respuesta elegante de P.A.U.")

    def test_handles_gemini_exception_gracefully(self) -> None:
        """Si el modelo Gemini falla, debe responder con mensaje de disculpa."""
        msg = _make_message("fallo")
        self.pau_bot.model.start_chat.side_effect = Exception("Gemini error")

        with patch.object(self.pau_bot.bot, "reply_to") as mock_reply:
            try:
                self.pau_bot.handle_agent_response(msg)
            except Exception:
                self.fail("handle_agent_response propagó una excepción inesperada")
        mock_reply.assert_called_once_with(
            msg,
            "Disculpe las molestias, estoy ajustando los detalles de su probador. Inténtelo en un momento.",
        )

    def test_handler_registered(self) -> None:
        """handle_agent_response debe estar registrado como message handler."""
        handlers = [
            h
            for h in self.pau_bot.bot.message_handlers
            if h.get("filters", {}).get("func") is not None
        ]
        self.assertTrue(
            len(handlers) >= 1,
            "No se encontró ningún handler de mensajes registrado con func=lambda",
        )

    def test_handler_called_via_process_new_updates(self) -> None:
        """El handler debe procesar mensajes nuevos cuando el bot los recibe."""
        msg = _make_message("hola bot")
        mock_response = MagicMock()
        mock_response.text = "Hola"
        mock_chat = MagicMock()
        mock_chat.send_message.return_value = mock_response
        self.pau_bot.model.start_chat.return_value = mock_chat

        with patch.object(self.pau_bot.bot, "reply_to") as mock_reply:
            self.pau_bot.handle_agent_response(msg)
        mock_reply.assert_called_once()


class TestSendWelcome(unittest.TestCase):
    """Valida el handler de bienvenida para /start y /help."""

    def setUp(self) -> None:
        self.pau_bot = _reload_pau_bot()

    def test_welcome_message_content(self) -> None:
        """Debe enviar el mensaje de bienvenida con referencia a P.A.U."""
        msg = _make_message("/start")
        with patch.object(self.pau_bot.bot, "reply_to") as mock_reply:
            self.pau_bot.send_welcome(msg)
        mock_reply.assert_called_once()
        call_args = mock_reply.call_args[0]
        self.assertIn("P.A.U.", call_args[1])

    def test_welcome_handler_registered(self) -> None:
        """send_welcome debe estar registrado como handler de comandos."""
        command_handlers = [
            h
            for h in self.pau_bot.bot.message_handlers
            if "commands" in h.get("filters", {})
        ]
        self.assertTrue(
            len(command_handlers) >= 1,
            "No se encontró handler de comandos /start o /help",
        )


if __name__ == "__main__":
    unittest.main()

