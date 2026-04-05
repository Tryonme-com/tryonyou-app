"""Tests para PauDivineHyperExpressiveV10_2."""

from __future__ import annotations

import os
import sys
import unittest

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from pau_divine_hyper_expressive_v10_2 import PauDivineHyperExpressiveV10_2


class TestPauDivineHyperExpressiveV10_2(unittest.TestCase):
    def setUp(self) -> None:
        self.pau = PauDivineHyperExpressiveV10_2()

    def test_initial_attributes(self) -> None:
        self.assertEqual(self.pau.reference, "White_Peacock_Natural_r5vr2He")
        self.assertEqual(self.pau.ui_element, "Moneda_Biometrica_Oro")
        self.assertEqual(self.pau.state, "MAX_EXPRESSIVITY")

    def test_execute_joy_and_nature_mix_returns_list(self) -> None:
        result = self.pau.execute_joy_and_nature_mix()
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

    def test_each_moment_has_required_keys(self) -> None:
        required_keys = {"moment", "human_gesture", "peacock_gesture", "audio_sync"}
        for item in self.pau.execute_joy_and_nature_mix():
            self.assertEqual(set(item.keys()), required_keys)

    def test_first_moment_is_explosion_de_alegria(self) -> None:
        sequence = self.pau.execute_joy_and_nature_mix()
        self.assertEqual(sequence[0]["moment"], "Explosión de Alegría")
        self.assertEqual(sequence[0]["human_gesture"], "Risa_Cerrando_Ojos")
        self.assertEqual(sequence[0]["peacock_gesture"], "Sacudida_Leve_Cuello")
        self.assertEqual(sequence[0]["audio_sync"], "Chuckle_High_Couture")

    def test_all_values_are_non_empty_strings(self) -> None:
        for item in self.pau.execute_joy_and_nature_mix():
            for key, value in item.items():
                self.assertIsInstance(value, str, msg=f"Key '{key}' should be str")
                self.assertTrue(value.strip(), msg=f"Key '{key}' should not be empty")


if __name__ == "__main__":
    unittest.main()
