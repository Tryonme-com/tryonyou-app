"""Tests para el Daily Planner / CEO Virtual (reporte_diario_soberania_v10)."""

from __future__ import annotations

import os
import sys
import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

# Añadir el directorio raíz al path para importar el módulo
_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from reporte_diario_soberania_v10 import (
    _mensaje_liquidacion,
    enviar_al_centinela,
    reporte_diario_soberania,
)


class TestMensajeLiquidacion(unittest.TestCase):
    """Valida la construcción del mensaje según el estado del hito."""

    def test_dias_positivos(self) -> None:
        msg = _mensaje_liquidacion(30)
        self.assertIn("30 días", msg)
        self.assertIn("MONITOR DE LIQUIDACIÓN", msg)
        self.assertIn("98.000,00", msg)

    def test_dia_cero(self) -> None:
        msg = _mensaje_liquidacion(0)
        self.assertIn("HITO ALCANZADO", msg)
        self.assertIn("BOOM", msg)

    def test_dias_negativos(self) -> None:
        msg = _mensaje_liquidacion(-5)
        self.assertIn("superada", msg)

    def test_mensaje_contiene_siren(self) -> None:
        # dias > 0 y dias == 0 incluyen referencia económica / SIREN
        for dias in (0, 10):
            with self.subTest(dias=dias):
                msg = _mensaje_liquidacion(dias)
                self.assertTrue(
                    "943 610 196" in msg or "98.000,00" in msg,
                    f"El mensaje para dias={dias} debería contener referencia económica.",
                )

    def test_mensaje_negativo_menciona_fecha(self) -> None:
        # Para dias negativos el mensaje advierte que la fecha objetivo fue superada
        msg = _mensaje_liquidacion(-5)
        self.assertIn("superada", msg)


class TestReporteDiarioSoberania(unittest.TestCase):
    """Valida que reporte_diario_soberania() devuelve texto con referencias clave."""

    def test_retorna_string_no_vacio(self) -> None:
        resultado = reporte_diario_soberania()
        self.assertIsInstance(resultado, str)
        self.assertGreater(len(resultado), 0)

    def test_contiene_referencia_economica(self) -> None:
        resultado = reporte_diario_soberania()
        self.assertIn("98.000,00", resultado)


class TestEnviarAlCentinela(unittest.TestCase):
    """Valida el envío de mensajes al centinela Telegram."""

    def test_falla_sin_credenciales(self) -> None:
        env = {"TELEGRAM_BOT_TOKEN": "", "TELEGRAM_TOKEN": "", "TELEGRAM_CHAT_ID": ""}
        with patch.dict(os.environ, env, clear=False):
            result = enviar_al_centinela("Test", "Mensaje")
        self.assertFalse(result)

    def test_exitoso_con_credenciales_mock(self) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 200

        env = {
            "TELEGRAM_BOT_TOKEN": "123456789:AAHtest",
            "TELEGRAM_CHAT_ID": "987654321",
        }
        with patch.dict(os.environ, env, clear=False):
            with patch("requests.post", return_value=mock_resp):
                result = enviar_al_centinela("Título", "Mensaje de prueba")
        self.assertTrue(result)

    def test_falla_con_http_error(self) -> None:
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_resp.text = "Unauthorized"

        env = {
            "TELEGRAM_BOT_TOKEN": "invalid_token",
            "TELEGRAM_CHAT_ID": "123",
        }
        with patch.dict(os.environ, env, clear=False):
            with patch("requests.post", return_value=mock_resp):
                result = enviar_al_centinela("Título", "Mensaje")
        self.assertFalse(result)

    def test_falla_con_excepcion_de_red(self) -> None:
        import requests as req_module

        env = {
            "TELEGRAM_BOT_TOKEN": "123456789:AAHtest",
            "TELEGRAM_CHAT_ID": "987654321",
        }
        with patch.dict(os.environ, env, clear=False):
            with patch("requests.post", side_effect=req_module.RequestException("timeout")):
                result = enviar_al_centinela("Título", "Mensaje")
        self.assertFalse(result)

    def test_skip_telegram_no_envía(self) -> None:
        """Con SKIP_TELEGRAM=1, main() no debe llamar a enviar_al_centinela."""
        import reporte_diario_soberania_v10 as mod

        env = {"SKIP_TELEGRAM": "1"}
        with patch.dict(os.environ, env, clear=False):
            with patch.object(mod, "enviar_al_centinela") as mock_send:
                codigo = mod.main()
        mock_send.assert_not_called()
        self.assertEqual(codigo, 0)


if __name__ == "__main__":
    unittest.main()
