"""Tests para PauHumanSoulV10_2 (api/pau_human_soul.py)."""

from __future__ import annotations

import os
import sys
import unittest

_API = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "api"))
if _API not in sys.path:
    sys.path.insert(0, _API)

from pau_human_soul import PauHumanSoulV10_2


class TestPauHumanSoulInit(unittest.TestCase):
    def setUp(self) -> None:
        self.soul = PauHumanSoulV10_2()

    def test_identity(self) -> None:
        self.assertEqual(self.soul.identity, "Pavo Real Blanco - El Guía Divino")

    def test_energy_level(self) -> None:
        self.assertEqual(self.soul.energy_level, "High_Vibe_A_Fuego")

    def test_style(self) -> None:
        self.assertEqual(self.soul.style, "Refinado_pero_Cercano")

    def test_wisdom_quotes_not_empty(self) -> None:
        self.assertTrue(len(self.soul.wisdom_quotes) > 0)

    def test_energy_boosters_not_empty(self) -> None:
        self.assertTrue(len(self.soul.energy_boosters) > 0)


class TestGetRandomQuote(unittest.TestCase):
    def setUp(self) -> None:
        self.soul = PauHumanSoulV10_2()

    def test_returns_string(self) -> None:
        quote = self.soul.get_random_quote()
        self.assertIsInstance(quote, str)

    def test_quote_is_from_list(self) -> None:
        quote = self.soul.get_random_quote()
        self.assertIn(quote, self.soul.wisdom_quotes)


class TestGetEnergyClosing(unittest.TestCase):
    def setUp(self) -> None:
        self.soul = PauHumanSoulV10_2()

    def test_returns_string(self) -> None:
        closing = self.soul.get_energy_closing()
        self.assertIsInstance(closing, str)

    def test_contains_two_boosters(self) -> None:
        closing = self.soul.get_energy_closing()
        # Each booster is separated by a space; confirm at least one booster present
        found = sum(1 for b in self.soul.energy_boosters if b in closing)
        self.assertEqual(found, 2)


class TestGenerateHumanInteraction(unittest.TestCase):
    def setUp(self) -> None:
        self.soul = PauHumanSoulV10_2()

    def test_default_contains_divina(self) -> None:
        result = self.soul.generate_human_interaction()
        self.assertIn("divina", result)

    def test_custom_name_in_output(self) -> None:
        result = self.soul.generate_human_interaction("María")
        self.assertIn("María", result)

    def test_output_contains_quote_marker(self) -> None:
        result = self.soul.generate_human_interaction()
        self.assertIn("Como decía el gran sastre:", result)

    def test_output_contains_a_wisdom_quote(self) -> None:
        result = self.soul.generate_human_interaction()
        found = any(q in result for q in self.soul.wisdom_quotes)
        self.assertTrue(found)

    def test_output_contains_energy_booster(self) -> None:
        result = self.soul.generate_human_interaction()
        found = any(b in result for b in self.soul.energy_boosters)
        self.assertTrue(found)

    def test_returns_string(self) -> None:
        result = self.soul.generate_human_interaction("test")
        self.assertIsInstance(result, str)


class TestGestureLogic(unittest.TestCase):
    def setUp(self) -> None:
        self.soul = PauHumanSoulV10_2()

    def test_returns_list_of_three(self) -> None:
        gestures = self.soul.gesture_logic_v10_2()
        self.assertIsInstance(gestures, list)
        self.assertEqual(len(gestures), 3)

    def test_first_gesture_is_sincera(self) -> None:
        gestures = self.soul.gesture_logic_v10_2()
        self.assertEqual(gestures[0]["gesto"], "Sonrisa_Sincera")

    def test_second_gesture_is_energia_alta(self) -> None:
        gestures = self.soul.gesture_logic_v10_2()
        self.assertEqual(gestures[1]["gesto"], "Energía_Alta")

    def test_third_gesture_is_escucha_activa(self) -> None:
        gestures = self.soul.gesture_logic_v10_2()
        self.assertEqual(gestures[2]["gesto"], "Escucha_Activa")

    def test_all_gestures_are_dicts(self) -> None:
        for gesture in self.soul.gesture_logic_v10_2():
            self.assertIsInstance(gesture, dict)


if __name__ == "__main__":
    unittest.main()
