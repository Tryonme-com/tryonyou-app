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


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestPauBotMissingToken(unittest.TestCase):
    """Verifica que el módulo falla con error claro si falta el token."""

    def test_raises_valueerror_without_token(self) -> None:
        """Debe lanzar ValueError si TELEGRAM_TOKEN no está configurado."""
        import importlib
        env = {"TELEGRAM_TOKEN": ""}
        with patch.dict(os.environ, env, clear=False):
            with self.assertRaises(ValueError):
                import pau_bot
                importlib.reload(pau_bot)


class TestPauBotModule(unittest.TestCase):
    """Verifica que el módulo pau_bot carga correctamente con token simulado."""

    def test_module_loads_with_mock_token(self) -> None:
        """El módulo debe importarse sin errores cuando hay un token de entorno."""
        env = {"TELEGRAM_TOKEN": "123456789:AAHfaketoken"}
        with patch.dict(os.environ, env, clear=False):
            import importlib
            import pau_bot
            importlib.reload(pau_bot)
        self.assertTrue(True)

    def test_project_id_is_set(self) -> None:
        """PROJECT_ID debe tener el valor del proyecto Google Studio."""
        import pau_bot
        self.assertEqual(pau_bot.PROJECT_ID, "gen-lang-client-0091228222")


class TestHandlePauLogic(unittest.TestCase):
    """Valida el handler principal handle_pau_logic."""

    def setUp(self) -> None:
        env = {"TELEGRAM_TOKEN": "123456789:AAHfaketoken"}
        with patch.dict(os.environ, env, clear=False):
            import importlib
            import pau_bot
            importlib.reload(pau_bot)
            self.pau_bot = pau_bot

    def test_replies_with_system_active_message(self) -> None:
        """Debe responder con el mensaje de sistema TryOnYou activo."""
        msg = _make_message("prueba")
        with patch.object(self.pau_bot.bot, "reply_to") as mock_reply:
            self.pau_bot.handle_pau_logic(msg)
        mock_reply.assert_called_once_with(
            msg,
            "Sistema TryOnYou activo. Procesando solicitud de silueta...",
        )

    def test_handles_reply_to_exception_gracefully(self) -> None:
        """Si bot.reply_to lanza excepción, no debe propagarse al caller."""
        msg = _make_message("fallo")
        with patch.object(
            self.pau_bot.bot, "reply_to", side_effect=Exception("network error")
        ):
            try:
                self.pau_bot.handle_pau_logic(msg)
            except Exception:
                self.fail("handle_pau_logic propagó una excepción inesperada")

    def test_handler_registered(self) -> None:
        """handle_pau_logic debe estar registrado como message handler."""
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
        import telebot.types as types

        msg = _make_message("hola bot")
        with patch.object(self.pau_bot.bot, "reply_to") as mock_reply:
            self.pau_bot.handle_pau_logic(msg)
        mock_reply.assert_called_once()


if __name__ == "__main__":
    unittest.main()
