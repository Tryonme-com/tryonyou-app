"""Tests para PauDisneyGuideV10_2 (api/pau_disney_guide.py)."""

from __future__ import annotations

import os
import sys
import unittest

_API = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "api"))
if _API not in sys.path:
    sys.path.insert(0, _API)

from pau_disney_guide import PauDisneyGuideV10_2, _JOURNEY


class TestPauDisneyGuideInit(unittest.TestCase):
    """Verifica los atributos iniciales de PauDisneyGuideV10_2."""

    def setUp(self) -> None:
        self.guide = PauDisneyGuideV10_2()

    def test_guide_state_is_idle_in_coin(self) -> None:
        self.assertEqual(self.guide.guide_state, "IDLE_IN_COIN")

    def test_user_position_is_landing(self) -> None:
        self.assertEqual(self.guide.user_position, "LANDING")

    def test_pau_reference_is_set(self) -> None:
        self.assertEqual(self.guide.pau_reference, "White_Peacock_Natural_r5vr2He")


class TestUpdateExperienceFlow(unittest.TestCase):
    """Valida update_experience_flow para todas las etapas conocidas y fallback."""

    def setUp(self) -> None:
        self.guide = PauDisneyGuideV10_2()

    def test_entrada_returns_correct_action(self) -> None:
        result = self.guide.update_experience_flow("ENTRADA")
        self.assertEqual(result["pau_action"], "Emerger_de_Moneda")
        self.assertEqual(result["gesture"], "Vuelo_Hacia_Centro")
        self.assertEqual(result["speech"], "Bienvenida_Magica")

    def test_escaneando_returns_correct_action(self) -> None:
        result = self.guide.update_experience_flow("ESCANEANDO")
        self.assertEqual(result["pau_action"], "Caminar_Sobre_Interfaz")
        self.assertEqual(result["gesture"], "Curiosidad_Natural")
        self.assertEqual(result["speech"], "Analisis_Biometrico_En_Curso")

    def test_look_ready_returns_correct_action(self) -> None:
        result = self.guide.update_experience_flow("LOOK_READY")
        self.assertEqual(result["pau_action"], "El_Chasquido_Maestro")
        self.assertEqual(result["gesture"], "Apertura_Abanico_Total")
        self.assertEqual(result["speech"], "Validacion_Divineo")

    def test_salida_returns_correct_action(self) -> None:
        result = self.guide.update_experience_flow("SALIDA")
        self.assertEqual(result["pau_action"], "Regreso_A_Moneda")
        self.assertEqual(result["gesture"], "Reverencia_Final")
        self.assertEqual(result["speech"], "Despedida_Elegante")

    def test_unknown_action_falls_back_to_entrada(self) -> None:
        result = self.guide.update_experience_flow("UNKNOWN_STAGE")
        self.assertEqual(result, _JOURNEY["ENTRADA"])

    def test_empty_string_falls_back_to_entrada(self) -> None:
        result = self.guide.update_experience_flow("")
        self.assertEqual(result, _JOURNEY["ENTRADA"])

    def test_result_contains_required_keys(self) -> None:
        for stage in ("ENTRADA", "ESCANEANDO", "LOOK_READY", "SALIDA"):
            with self.subTest(stage=stage):
                result = self.guide.update_experience_flow(stage)
                self.assertIn("pau_action", result)
                self.assertIn("gesture", result)
                self.assertIn("speech", result)


class TestSyncAnimationEngine(unittest.TestCase):
    """Verifica que sync_animation_engine no lanza excepciones."""

    def setUp(self) -> None:
        self.guide = PauDisneyGuideV10_2()

    def test_sync_returns_none(self) -> None:
        self.assertIsNone(self.guide.sync_animation_engine("LOOK_READY"))

    def test_sync_accepts_no_args(self) -> None:
        self.assertIsNone(self.guide.sync_animation_engine())


class TestJourneyConstant(unittest.TestCase):
    """Verifica la integridad del mapa de jornada."""

    def test_all_stages_present(self) -> None:
        expected = {"ENTRADA", "ESCANEANDO", "LOOK_READY", "SALIDA"}
        self.assertEqual(set(_JOURNEY.keys()), expected)

    def test_all_stages_have_three_keys(self) -> None:
        for stage, mapping in _JOURNEY.items():
            with self.subTest(stage=stage):
                self.assertEqual(len(mapping), 3)


if __name__ == "__main__":
    unittest.main()
