"""Tests para PauIdentidadRealV10_2 (pau_identidad_real_v10_2.py).

@CertezaAbsoluta PCT/EP2025/067317
Bajo Protocolo de Soberanía V10 — Founder: Rubén
"""

from __future__ import annotations

import io
import os
import sys
import unittest

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from pau_identidad_real_v10_2 import PauIdentidadRealV10_2


class TestPauIdentidadInit(unittest.TestCase):
    """Verifica los atributos iniciales del motor de identidad."""

    def setUp(self) -> None:
        self.pau = PauIdentidadRealV10_2()

    def test_pau_is_user_is_true(self) -> None:
        self.assertTrue(self.pau.pau_is_user)

    def test_training_hours(self) -> None:
        self.assertEqual(self.pau.training_hours, "Infinite")

    def test_energy(self) -> None:
        self.assertEqual(self.pau.energy, "Divineo_Puro")

    def test_tone(self) -> None:
        self.assertEqual(self.pau.tone, "Refinado_Cercano_Eric")

    def test_motto(self) -> None:
        self.assertEqual(self.pau.motto, "¡A fuego! ¡Boom! ¡Vivido!")


class TestApplyPauSoul(unittest.TestCase):
    """Valida el filtro de humanidad de Pau."""

    def setUp(self) -> None:
        self.pau = PauIdentidadRealV10_2()

    def test_soul_includes_input_text(self) -> None:
        result = self.pau.apply_pau_soul("mi pregunta")
        self.assertIn("mi pregunta", result)

    def test_soul_includes_divina(self) -> None:
        result = self.pau.apply_pau_soul("cualquier cosa")
        self.assertIn("divina", result.lower())

    def test_soul_includes_real(self) -> None:
        result = self.pau.apply_pau_soul("test")
        self.assertIn("real", result.lower())


class TestInjectPauVibe(unittest.TestCase):
    """Valida la inyección de vibra y frases de Pau."""

    def setUp(self) -> None:
        self.pau = PauIdentidadRealV10_2()

    def test_vibe_includes_core_text(self) -> None:
        result = self.pau.inject_pau_vibe("texto base")
        self.assertIn("texto base", result)

    def test_vibe_includes_chanel_quote(self) -> None:
        result = self.pau.inject_pau_vibe("cualquier texto")
        self.assertIn("Chanel", result)

    def test_vibe_includes_espectacular(self) -> None:
        result = self.pau.inject_pau_vibe("algo")
        self.assertIn("espectacular", result.lower())


class TestGenerateResponse(unittest.TestCase):
    """Valida el método principal generate_response."""

    def setUp(self) -> None:
        self.pau = PauIdentidadRealV10_2()

    def test_response_includes_motto(self) -> None:
        result = self.pau.generate_response("¿Cómo me queda este abrigo?")
        self.assertIn(self.pau.motto, result)

    def test_response_includes_context_request(self) -> None:
        result = self.pau.generate_response("mi consulta de moda")
        self.assertIn("mi consulta de moda", result)

    def test_response_includes_chanel_quote(self) -> None:
        result = self.pau.generate_response("prueba")
        self.assertIn("Chanel", result)

    def test_response_includes_soul_filter(self) -> None:
        result = self.pau.generate_response("test")
        self.assertIn("real", result.lower())

    def test_response_ends_with_motto(self) -> None:
        result = self.pau.generate_response("¿qué look me recomiendas?")
        self.assertTrue(result.strip().endswith(self.pau.motto))


class TestExecuteSnapTransformation(unittest.TestCase):
    """Valida el gesto maestro: El Chasquido."""

    def test_snap_prints_balmain_message(self) -> None:
        pau = PauIdentidadRealV10_2()
        captured = io.StringIO()
        sys.stdout = captured
        try:
            pau.execute_snap_transformation()
        finally:
            sys.stdout = sys.__stdout__
        output = captured.getvalue()
        self.assertIn("Transformación completada", output)
        self.assertIn("Balmain", output)


if __name__ == "__main__":
    unittest.main()
