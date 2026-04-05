"""Tests para tryonyou_deploy_bot — bot de despliegue @tryonyou_deploy_bot."""

from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import MagicMock, call, patch

# Añadir el directorio raíz al path para importar el módulo
_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


# ---------------------------------------------------------------------------
# Stub de telebot para no requerir la instalación en tests
# ---------------------------------------------------------------------------

_telebot_stub = MagicMock()
_telebot_stub.TeleBot = MagicMock
_telebot_stub.types = MagicMock()

# Inyectar el stub antes de importar el módulo real
sys.modules.setdefault("telebot", _telebot_stub)

import tryonyou_deploy_bot as bot_module  # noqa: E402


class TestGetToken(unittest.TestCase):
    """Valida la lectura segura del token desde el entorno."""

    def test_usa_telegram_bot_token(self) -> None:
        with patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "token-abc", "TELEGRAM_TOKEN": ""}):
            self.assertEqual(bot_module._get_token(), "token-abc")

    def test_fallback_a_telegram_token(self) -> None:
        with patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "", "TELEGRAM_TOKEN": "token-xyz"}):
            self.assertEqual(bot_module._get_token(), "token-xyz")

    def test_telegram_bot_token_tiene_preferencia(self) -> None:
        with patch.dict(
            os.environ,
            {"TELEGRAM_BOT_TOKEN": "primero", "TELEGRAM_TOKEN": "segundo"},
        ):
            self.assertEqual(bot_module._get_token(), "primero")

    def test_error_sin_token(self) -> None:
        with patch.dict(os.environ, {"TELEGRAM_BOT_TOKEN": "", "TELEGRAM_TOKEN": ""}):
            with self.assertRaises(RuntimeError):
                bot_module._get_token()


class TestWelcomeMessage(unittest.TestCase):
    """Valida el contenido del mensaje de bienvenida."""

    def test_mensaje_bienvenida_no_vacio(self) -> None:
        self.assertTrue(bot_module.WELCOME_MESSAGE)

    def test_mensaje_contiene_tryonyou(self) -> None:
        self.assertIn("TryOnYou", bot_module.WELCOME_MESSAGE)

    def test_mensaje_contiene_abvet(self) -> None:
        self.assertIn("Abvet", bot_module.WELCOME_MESSAGE)


class TestInitializeTryonYouBot(unittest.TestCase):
    """Valida que el bot registra el handler y arranca el polling."""

    def _make_bot_mock(self):
        bot_mock = MagicMock()
        # Captura el handler registrado con @bot.message_handler
        registered_handler = {}

        def capture_handler(**kwargs):
            def decorator(fn):
                registered_handler["fn"] = fn
                return fn

            return decorator

        bot_mock.message_handler.side_effect = capture_handler
        return bot_mock, registered_handler

    def test_polling_iniciado(self) -> None:
        bot_mock, _ = self._make_bot_mock()
        with patch("tryonyou_deploy_bot.telebot") as mock_telebot:
            mock_telebot.TeleBot.return_value = bot_mock
            bot_module.initialize_tryonyou_bot("fake-token")

        bot_mock.polling.assert_called_once_with(none_stop=True)

    def test_handler_registrado_para_start_y_help(self) -> None:
        bot_mock, _ = self._make_bot_mock()
        with patch("tryonyou_deploy_bot.telebot") as mock_telebot:
            mock_telebot.TeleBot.return_value = bot_mock
            bot_module.initialize_tryonyou_bot("fake-token")

        bot_mock.message_handler.assert_called_once()
        _, kwargs = bot_mock.message_handler.call_args
        self.assertIn("commands", kwargs)
        self.assertIn("start", kwargs["commands"])
        self.assertIn("help", kwargs["commands"])

    def test_reply_to_enviado_con_mensaje_bienvenida(self) -> None:
        bot_mock, registered = self._make_bot_mock()
        with patch("tryonyou_deploy_bot.telebot") as mock_telebot:
            mock_telebot.TeleBot.return_value = bot_mock
            bot_module.initialize_tryonyou_bot("fake-token")

        fake_message = MagicMock()
        registered["fn"](fake_message)
        bot_mock.reply_to.assert_called_once_with(fake_message, bot_module.WELCOME_MESSAGE)

    def test_excepcion_en_polling_es_propagada(self) -> None:
        bot_mock, _ = self._make_bot_mock()
        bot_mock.polling.side_effect = RuntimeError("poll error")
        with patch("tryonyou_deploy_bot.telebot") as mock_telebot:
            mock_telebot.TeleBot.return_value = bot_mock
            with self.assertRaises(RuntimeError):
                bot_module.initialize_tryonyou_bot("fake-token")


if __name__ == "__main__":
    unittest.main()
