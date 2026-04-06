"""Tests para activar_pau.py — activador unificado de P.A.U.

PCT/EP2025/067317 · Bajo Protocolo de Soberanía V10 — Founder: Rubén
"""

from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import importlib
import activar_pau


class TestActivarPauStatus(unittest.TestCase):
    """Modo 'status' (por defecto): muestra estado y retorna 0."""

    def test_default_mode_returns_zero(self) -> None:
        with patch.dict(os.environ, {"PAU_MODE": "status"}, clear=False):
            rc = activar_pau.activar_pau()
        self.assertEqual(rc, 0)

    def test_missing_pau_mode_defaults_to_status(self) -> None:
        env = {k: v for k, v in os.environ.items() if k != "PAU_MODE"}
        with patch.dict(os.environ, env, clear=True):
            rc = activar_pau.activar_pau()
        self.assertEqual(rc, 0)

    def test_invalid_mode_returns_one(self) -> None:
        with patch.dict(os.environ, {"PAU_MODE": "desconocido"}, clear=False):
            rc = activar_pau.activar_pau()
        self.assertEqual(rc, 1)


class TestMostrarEstado(unittest.TestCase):
    """Verifica el output de _mostrar_estado."""

    def _capturar_estado(self, telegram: str = "", gemini: str = "") -> str:
        import io

        buf = io.StringIO()
        with patch.dict(
            os.environ,
            {"TELEGRAM_TOKEN": telegram, "GEMINI_API_KEY": gemini},
            clear=False,
        ):
            with patch("sys.stdout", buf):
                activar_pau._mostrar_estado()
        return buf.getvalue()

    def test_contiene_pau(self) -> None:
        out = self._capturar_estado()
        self.assertIn("P.A.U.", out)

    def test_contiene_patente(self) -> None:
        out = self._capturar_estado()
        self.assertIn("PCT/EP2025/067317", out)

    def test_telegram_verde_cuando_token_presente(self) -> None:
        out = self._capturar_estado(telegram="faketoken123")
        self.assertIn("🟢", out)

    def test_telegram_rojo_cuando_token_ausente(self) -> None:
        out = self._capturar_estado(telegram="")
        self.assertIn("🔴", out)

    def test_gemini_verde_cuando_clave_presente(self) -> None:
        out = self._capturar_estado(gemini="AIzaSyfake")
        lines = out.split("\n")
        gemini_lines = [ln for ln in lines if "Gemini" in ln]
        self.assertTrue(any("🟢" in ln for ln in gemini_lines))

    def test_contiene_modos(self) -> None:
        out = self._capturar_estado()
        for mode in ("bot", "orquesta", "vigilancia", "status"):
            self.assertIn(mode, out)


class TestIniciarBot(unittest.TestCase):
    """Verifica _iniciar_bot: fallo sin token, llamada correcta con token."""

    def test_falla_sin_telegram_token(self) -> None:
        with patch.dict(os.environ, {"TELEGRAM_TOKEN": ""}, clear=False):
            with self.assertRaises(SystemExit) as cm:
                activar_pau._iniciar_bot()
        self.assertEqual(cm.exception.code, 1)

    def test_llama_run_polling_con_token(self) -> None:
        mock_run_polling = MagicMock()
        with patch.dict(os.environ, {"TELEGRAM_TOKEN": "faketoken"}, clear=False):
            with patch.dict(
                sys.modules,
                {"pau_bot": MagicMock(run_polling=mock_run_polling)},
            ):
                activar_pau._iniciar_bot()
        mock_run_polling.assert_called_once()


class TestIniciarOrquesta(unittest.TestCase):
    """Verifica que _iniciar_orquesta delega en orquestador_pau_total.orquestar."""

    def test_llama_orquestar(self) -> None:
        mock_orquestar = MagicMock()
        with patch.dict(
            sys.modules,
            {"orquestador_pau_total": MagicMock(orquestar=mock_orquestar)},
        ):
            activar_pau._iniciar_orquesta()
        mock_orquestar.assert_called_once()


class TestIniciarVigilancia(unittest.TestCase):
    """Verifica que _iniciar_vigilancia delega en vigilancia_pau.vigilancia_silenciosa."""

    def test_llama_vigilancia_silenciosa(self) -> None:
        mock_vigilancia = MagicMock()
        with patch.dict(
            sys.modules,
            {"vigilancia_pau": MagicMock(vigilancia_silenciosa=mock_vigilancia)},
        ):
            activar_pau._iniciar_vigilancia()
        mock_vigilancia.assert_called_once()


class TestActivarPauModos(unittest.TestCase):
    """Prueba de integración de los modos bot, orquesta y vigilancia."""

    def test_modo_orquesta_llama_orquestar(self) -> None:
        mock_orquestar = MagicMock()
        with patch.dict(os.environ, {"PAU_MODE": "orquesta"}, clear=False):
            with patch.dict(
                sys.modules,
                {"orquestador_pau_total": MagicMock(orquestar=mock_orquestar)},
            ):
                rc = activar_pau.activar_pau()
        self.assertEqual(rc, 0)
        mock_orquestar.assert_called_once()

    def test_modo_vigilancia_llama_vigilancia_silenciosa(self) -> None:
        mock_vigilancia = MagicMock()
        with patch.dict(os.environ, {"PAU_MODE": "vigilancia"}, clear=False):
            with patch.dict(
                sys.modules,
                {"vigilancia_pau": MagicMock(vigilancia_silenciosa=mock_vigilancia)},
            ):
                rc = activar_pau.activar_pau()
        self.assertEqual(rc, 0)
        mock_vigilancia.assert_called_once()

    def test_modo_bot_sin_token_termina_con_sysexit(self) -> None:
        with patch.dict(
            os.environ,
            {"PAU_MODE": "bot", "TELEGRAM_TOKEN": ""},
            clear=False,
        ):
            with self.assertRaises(SystemExit):
                activar_pau.activar_pau()

    def test_modo_bot_con_token_llama_run_polling(self) -> None:
        mock_run_polling = MagicMock()
        with patch.dict(
            os.environ,
            {"PAU_MODE": "bot", "TELEGRAM_TOKEN": "faketoken"},
            clear=False,
        ):
            with patch.dict(
                sys.modules,
                {"pau_bot": MagicMock(run_polling=mock_run_polling)},
            ):
                rc = activar_pau.activar_pau()
        self.assertEqual(rc, 0)
        mock_run_polling.assert_called_once()


class TestNoSecretsInSource(unittest.TestCase):
    """Verifica que no hay tokens o claves hardcodeados en activar_pau.py."""

    def test_no_real_telegram_token(self) -> None:
        with open(os.path.join(_ROOT, "activar_pau.py"), encoding="utf-8") as f:
            content = f.read()
        self.assertNotIn("8788913760", content)
        self.assertNotIn("AAE2g87I0e", content)

    def test_no_real_gemini_key(self) -> None:
        with open(os.path.join(_ROOT, "activar_pau.py"), encoding="utf-8") as f:
            content = f.read()
        self.assertNotIn("AIzaSy", content)


if __name__ == "__main__":
    unittest.main()
