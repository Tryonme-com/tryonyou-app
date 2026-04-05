"""Tests para OraculoStudio — thinking_config y generation_config (unittest estándar)."""

from __future__ import annotations

import os
import sys
import types
import unittest
from unittest.mock import MagicMock, patch

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


def _make_genai_mock() -> MagicMock:
    """Devuelve un mock mínimo de google.generativeai."""
    mock_genai = MagicMock()
    mock_model = MagicMock()
    mock_genai.GenerativeModel.return_value = mock_model
    return mock_genai


def _stub_modules(genai_mock: MagicMock) -> dict:
    """Devuelve el dict de módulos falsos necesarios para parchear google.generativeai."""
    fake_genai = types.ModuleType("google.generativeai")
    fake_genai.configure = genai_mock.configure
    fake_genai.GenerativeModel = genai_mock.GenerativeModel

    fake_google = types.ModuleType("google")
    fake_google.generativeai = fake_genai

    return {"google": fake_google, "google.generativeai": fake_genai}


class TestOraculoStudioGenerationConfig(unittest.TestCase):
    """Valida que OraculoStudio inicializa el modelo con la generation_config correcta."""

    def _create_studio(self, genai_mock: MagicMock, extra_env: dict | None = None) -> object:
        """Crea un OraculoStudio parcheando las dependencias externas."""
        import importlib
        import oraculo_studio

        env = {"GOOGLE_STUDIO_API_KEY": "test-key-123", **(extra_env or {})}
        with patch.dict(os.environ, env, clear=False):
            with patch.dict(sys.modules, _stub_modules(genai_mock)):
                importlib.reload(oraculo_studio)
                return oraculo_studio.OraculoStudio()

    def test_default_model_is_gemini_25_flash(self) -> None:
        genai_mock = _make_genai_mock()
        self._create_studio(genai_mock, {"ORACLE_GEMINI_MODEL": ""})
        cfg_kwargs = genai_mock.GenerativeModel.call_args.kwargs
        model_name = cfg_kwargs["model_name"]
        self.assertEqual(model_name, "gemini-2.5-flash")

    def test_generation_config_temperature(self) -> None:
        genai_mock = _make_genai_mock()
        self._create_studio(genai_mock)
        cfg = genai_mock.GenerativeModel.call_args.kwargs["generation_config"]
        self.assertAlmostEqual(cfg["temperature"], 0.1)

    def test_generation_config_top_p(self) -> None:
        genai_mock = _make_genai_mock()
        self._create_studio(genai_mock)
        cfg = genai_mock.GenerativeModel.call_args.kwargs["generation_config"]
        self.assertAlmostEqual(cfg["top_p"], 0.95)

    def test_generation_config_top_k(self) -> None:
        genai_mock = _make_genai_mock()
        self._create_studio(genai_mock)
        cfg = genai_mock.GenerativeModel.call_args.kwargs["generation_config"]
        self.assertEqual(cfg["top_k"], 40)

    def test_generation_config_max_output_tokens(self) -> None:
        genai_mock = _make_genai_mock()
        self._create_studio(genai_mock)
        cfg = genai_mock.GenerativeModel.call_args.kwargs["generation_config"]
        self.assertEqual(cfg["max_output_tokens"], 8192)

    def test_thinking_config_include_thoughts(self) -> None:
        genai_mock = _make_genai_mock()
        self._create_studio(genai_mock)
        cfg = genai_mock.GenerativeModel.call_args.kwargs["generation_config"]
        self.assertTrue(cfg["thinking_config"]["include_thoughts"])

    def test_thinking_config_budget(self) -> None:
        genai_mock = _make_genai_mock()
        self._create_studio(genai_mock)
        cfg = genai_mock.GenerativeModel.call_args.kwargs["generation_config"]
        self.assertEqual(cfg["thinking_config"]["thinking_budget"], 1024)

    def test_thinking_config_level_high(self) -> None:
        genai_mock = _make_genai_mock()
        self._create_studio(genai_mock)
        cfg = genai_mock.GenerativeModel.call_args.kwargs["generation_config"]
        self.assertEqual(cfg["thinking_config"]["thinking_level"], "high")

    def test_custom_model_env_override(self) -> None:
        genai_mock = _make_genai_mock()
        self._create_studio(genai_mock, {"ORACLE_GEMINI_MODEL": "gemini-2.0-pro"})
        model_name = genai_mock.GenerativeModel.call_args.kwargs["model_name"]
        self.assertEqual(model_name, "gemini-2.0-pro")


if __name__ == "__main__":
    unittest.main()
