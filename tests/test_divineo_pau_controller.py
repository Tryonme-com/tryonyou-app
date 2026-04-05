"""Tests para DivineoPauController (api/divineo_pau_controller.py).

Valida la identidad de Pau (Pavo Real Blanco) y la lógica de estados
de experiencia en la interfaz de lujo V10.2.
"""

from __future__ import annotations

import os
import sys
import unittest

_API = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "api"))
if _API not in sys.path:
    sys.path.insert(0, _API)

from divineo_pau_controller import (
    MOTTO,
    PAU_ID,
    VERSION,
    DivineoPauController,
)


class TestDivineoPauControllerIdentity(unittest.TestCase):
    """Verifica las constantes de identidad del controlador."""

    def setUp(self) -> None:
        self.ctrl = DivineoPauController()

    def test_version_is_10_2(self) -> None:
        self.assertEqual(self.ctrl.version, "10.2")

    def test_pau_id_is_real_white_peacock(self) -> None:
        self.assertEqual(self.ctrl.pau_id, "Real_White_Peacock_Natural")

    def test_motto_is_set(self) -> None:
        self.assertIn("tallas", self.ctrl.motto)

    def test_module_constants_match_instance(self) -> None:
        self.assertEqual(VERSION, self.ctrl.version)
        self.assertEqual(PAU_ID, self.ctrl.pau_id)
        self.assertEqual(MOTTO, self.ctrl.motto)


class TestDivineoPauControllerStates(unittest.TestCase):
    """Verifica los estados de experiencia y sus activos."""

    def setUp(self) -> None:
        self.ctrl = DivineoPauController()

    def test_welcome_state_returns_video_and_phrase(self) -> None:
        state = self.ctrl.get_pau_state("welcome")
        self.assertIn("video", state)
        self.assertIn("phrase", state)

    def test_welcome_video_filename(self) -> None:
        state = self.ctrl.get_pau_state("welcome")
        self.assertEqual(state["video"], "pau_talking_natural.mp4")

    def test_welcome_phrase_mentions_tallas(self) -> None:
        state = self.ctrl.get_pau_state("welcome")
        self.assertIn("tallas", state["phrase"])

    def test_success_state_returns_video_and_phrase(self) -> None:
        state = self.ctrl.get_pau_state("success")
        self.assertEqual(state["video"], "pau_nodding_natural.mp4")
        self.assertIn("impecable", state["phrase"])

    def test_joy_state_returns_video_and_phrase(self) -> None:
        state = self.ctrl.get_pau_state("joy")
        self.assertEqual(state["video"], "pau_laughing_natural.mp4")
        self.assertIn("Divineo", state["phrase"])

    def test_default_mood_is_welcome(self) -> None:
        state_explicit = self.ctrl.get_pau_state("welcome")
        state_default = self.ctrl.get_pau_state()
        self.assertEqual(state_explicit, state_default)

    def test_unknown_mood_falls_back_to_welcome(self) -> None:
        state = self.ctrl.get_pau_state("nonexistent_mood")
        welcome = self.ctrl.get_pau_state("welcome")
        self.assertEqual(state, welcome)

    def test_state_values_are_non_empty_strings(self) -> None:
        for mood in ("welcome", "success", "joy"):
            state = self.ctrl.get_pau_state(mood)
            self.assertIsInstance(state["video"], str)
            self.assertGreater(len(state["video"]), 0)
            self.assertIsInstance(state["phrase"], str)
            self.assertGreater(len(state["phrase"]), 0)


if __name__ == "__main__":
    unittest.main()
