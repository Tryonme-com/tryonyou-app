"""Tests para PauDisneyExperienceV10_2 (api/pau_disney_experience.py).

Valida:
  1. Atributos de identidad y configuración de negocio.
  2. Estados del funnel Disney (WELCOME, SCANNING, THE_SNAP, CHECKOUT).
  3. Protocolo Zero-Display: nunca se exponen pesos ni tallas numéricas.
  4. Lógica de personalidad y movimiento de Pau.
  5. Manejo de estados desconocidos.
"""

from __future__ import annotations

import os
import sys
import unittest

_API = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "api"))
if _API not in sys.path:
    sys.path.insert(0, _API)

from pau_disney_experience import PauDisneyExperienceV10_2


class TestPauDisneyExperienceIdentity(unittest.TestCase):
    """Verifica los atributos de identidad del motor."""

    def setUp(self) -> None:
        self.pau = PauDisneyExperienceV10_2()

    def test_identity(self) -> None:
        self.assertEqual(self.pau.identity, "P.A.U. (Personal Assistant Unit)")

    def test_avatar(self) -> None:
        self.assertEqual(self.pau.avatar, "White_Peacock_Natural_Ref_r5vr2He")

    def test_location(self) -> None:
        self.assertEqual(self.pau.location, "Galeries_Lafayette_Haussmann")

    def test_philosophy(self) -> None:
        self.assertEqual(self.pau.philosophy, "La_Certitude_Biometrique")

    def test_tone(self) -> None:
        self.assertEqual(self.pau.tone, "Refinado_Cercano_Eric")

    def test_business_logic_setup_fee(self) -> None:
        self.assertEqual(self.pau.business_logic["setup_fee"], 12500)

    def test_business_logic_exclusivity_months(self) -> None:
        self.assertEqual(self.pau.business_logic["exclusivity_months"], 3)

    def test_business_logic_royalties(self) -> None:
        self.assertAlmostEqual(self.pau.business_logic["royalties"], 0.08)


class TestJourneyStates(unittest.TestCase):
    """Verifica que los cuatro estados del funnel Disney están correctamente definidos."""

    def setUp(self) -> None:
        self.pau = PauDisneyExperienceV10_2()
        self.states = self.pau.get_journey_states()

    def test_all_states_present(self) -> None:
        for state in ("WELCOME", "SCANNING", "THE_SNAP", "CHECKOUT"):
            self.assertIn(state, self.states)

    def test_each_state_has_required_keys(self) -> None:
        for state, data in self.states.items():
            with self.subTest(state=state):
                self.assertIn("animation", data)
                self.assertIn("phrase", data)
                self.assertIn("ui_effect", data)

    def test_welcome_animation(self) -> None:
        self.assertEqual(self.states["WELCOME"]["animation"], "pau_emerging_from_coin")

    def test_welcome_ui_effect(self) -> None:
        self.assertEqual(self.states["WELCOME"]["ui_effect"], "gold_dust_explosion")

    def test_scanning_animation(self) -> None:
        self.assertEqual(self.states["SCANNING"]["animation"], "pau_walking_on_interface")

    def test_scanning_ui_effect(self) -> None:
        self.assertEqual(self.states["SCANNING"]["ui_effect"], "biometric_scan_glow")

    def test_snap_animation(self) -> None:
        self.assertEqual(self.states["THE_SNAP"]["animation"], "pau_tail_fan_climax")

    def test_snap_ui_effect(self) -> None:
        self.assertEqual(self.states["THE_SNAP"]["ui_effect"], "instant_avatar_swap")

    def test_checkout_animation(self) -> None:
        self.assertEqual(self.states["CHECKOUT"]["animation"], "pau_elegant_bow")

    def test_checkout_ui_effect(self) -> None:
        self.assertEqual(self.states["CHECKOUT"]["ui_effect"], "qr_code_generation")

    def test_get_journey_states_returns_copy(self) -> None:
        """Modificar el resultado no debe alterar el estado interno."""
        states = self.pau.get_journey_states()
        states["WELCOME"]["animation"] = "tampered"
        fresh = self.pau.get_journey_states()
        self.assertEqual(fresh["WELCOME"]["animation"], "pau_emerging_from_coin")


class TestProtocolZeroDisplay(unittest.TestCase):
    """Verifica que nunca se expongan pesos ni tallas numéricas."""

    def setUp(self) -> None:
        self.pau = PauDisneyExperienceV10_2()

    def test_weight_key_is_bunkerized(self) -> None:
        result = self.pau.apply_protocol_zero_display({"weight": 65})
        self.assertEqual(result, "Dato_Bunkerizado_Seguro")

    def test_size_cm_key_is_bunkerized(self) -> None:
        result = self.pau.apply_protocol_zero_display({"size_cm": 170})
        self.assertEqual(result, "Dato_Bunkerizado_Seguro")

    def test_both_forbidden_keys_are_bunkerized(self) -> None:
        result = self.pau.apply_protocol_zero_display({"weight": 65, "size_cm": 170})
        self.assertEqual(result, "Dato_Bunkerizado_Seguro")

    def test_safe_data_returns_visual_validation(self) -> None:
        result = self.pau.apply_protocol_zero_display({"color": "azul", "style": "floral"})
        self.assertEqual(result, "Visual_Validation_Active")

    def test_empty_data_returns_visual_validation(self) -> None:
        result = self.pau.apply_protocol_zero_display({})
        self.assertEqual(result, "Visual_Validation_Active")

    def test_unrelated_numeric_data_is_safe(self) -> None:
        result = self.pau.apply_protocol_zero_display({"lead_id": 42, "brand": "Balmain"})
        self.assertEqual(result, "Visual_Validation_Active")


class TestExecutePersonalityLogic(unittest.TestCase):
    """Verifica la lógica de personalidad para cada estado del funnel."""

    def setUp(self) -> None:
        self.pau = PauDisneyExperienceV10_2()

    def test_welcome_returns_correct_animation(self) -> None:
        result = self.pau.execute_personality_logic("WELCOME")
        self.assertIn("pau_emerging_from_coin", result)
        self.assertIn(self.pau.tone, result)

    def test_scanning_returns_correct_animation(self) -> None:
        result = self.pau.execute_personality_logic("SCANNING")
        self.assertIn("pau_walking_on_interface", result)

    def test_snap_returns_correct_animation(self) -> None:
        result = self.pau.execute_personality_logic("THE_SNAP")
        self.assertIn("pau_tail_fan_climax", result)

    def test_checkout_returns_correct_animation(self) -> None:
        result = self.pau.execute_personality_logic("CHECKOUT")
        self.assertIn("pau_elegant_bow", result)

    def test_unknown_state_returns_error_message(self) -> None:
        result = self.pau.execute_personality_logic("UNKNOWN_STATE")
        self.assertIn("UNKNOWN_STATE", result)
        self.assertNotIn("Ejecutando", result)

    def test_result_is_string(self) -> None:
        result = self.pau.execute_personality_logic("WELCOME")
        self.assertIsInstance(result, str)


class TestMovePau(unittest.TestCase):
    """Verifica que move_pau es invocable sin errores."""

    def setUp(self) -> None:
        self.pau = PauDisneyExperienceV10_2()

    def test_move_pau_returns_none(self) -> None:
        result = self.pau.move_pau(from_pos="top_right", to_pos="center", scale=1.5)
        self.assertIsNone(result)

    def test_move_pau_with_any_params_returns_none(self) -> None:
        result = self.pau.move_pau(from_pos="bottom_left", to_pos="top_center", scale=0.5)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
