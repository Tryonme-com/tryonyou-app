"""Tests for pau_divine_soul_v10.PauDivineSoulV10_2."""

from __future__ import annotations

import io
import os
import sys
import unittest
from contextlib import redirect_stdout

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from pau_divine_soul_v10 import PauDivineSoulV10_2


def _make_soul() -> PauDivineSoulV10_2:
    """Instantiate PauDivineSoulV10_2 while suppressing init stdout."""
    with redirect_stdout(io.StringIO()):
        return PauDivineSoulV10_2()


class TestPauDivineSoulV10Init(unittest.TestCase):
    def setUp(self) -> None:
        self.soul = _make_soul()

    def test_reference(self) -> None:
        self.assertEqual(self.soul.reference, "White_Peacock_Natural_r5vr2He")

    def test_dna_keys(self) -> None:
        for key in ("origin", "personality_type", "voice_tone", "mission"):
            self.assertIn(key, self.soul.dna)

    def test_dna_origin(self) -> None:
        self.assertEqual(self.soul.dna["origin"], "Lafayette_Refinement")

    def test_dna_mission(self) -> None:
        self.assertEqual(self.soul.dna["mission"], "Zero_Complex_Experience")


class TestPauDivineSoulV10Logic(unittest.TestCase):
    def setUp(self) -> None:
        self.soul = _make_soul()

    def _run_logic(self) -> str:
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.soul.execute_personality_logic()
        return buf.getvalue()

    def test_all_traits_appear_in_output(self) -> None:
        output = self._run_logic()
        for trait in (
            "Refined_Proximity",
            "Absolute_Sincerity",
            "Artistic_Intellect",
            "The_Snap_Master",
            "Empathetic_Authority",
        ):
            self.assertIn(trait, output)

    def test_inject_video_marker_present(self) -> None:
        output = self._run_logic()
        self.assertIn("[VIDEO]", output)

    def test_ui_sync_marker_present(self) -> None:
        output = self._run_logic()
        self.assertIn("[UI]", output)

    def test_biometric_seal_marker_present(self) -> None:
        output = self._run_logic()
        self.assertIn("[BIO]", output)

    def test_zero_return_margin_message(self) -> None:
        output = self._run_logic()
        self.assertIn("0 % return margin", output)

    def test_gestures_queued(self) -> None:
        output = self._run_logic()
        self.assertIn("Soft_Beak_Move", output)
        self.assertIn("Beak_Click_Sync", output)


class TestPauDivineSoulV10IndividualMethods(unittest.TestCase):
    def setUp(self) -> None:
        self.soul = _make_soul()

    def test_inject_personality_to_video(self) -> None:
        layer = {
            "trait": "Test_Trait",
            "action": "Test_Action",
            "gestures": ["Gesture_A", "Gesture_B"],
        }
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.soul.inject_personality_to_video(layer)
        output = buf.getvalue()
        self.assertIn("Test_Trait", output)
        self.assertIn("Test_Action", output)
        self.assertIn("Gesture_A", output)
        self.assertIn("Gesture_B", output)

    def test_sync_with_million_dollar_ui(self) -> None:
        layer = {"trait": "Test_Trait", "behavior": "Test_Behavior"}
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.soul.sync_with_million_dollar_ui(layer)
        output = buf.getvalue()
        self.assertIn("Test_Trait", output)
        self.assertIn("Test_Behavior", output)

    def test_seal_biometric_certitude(self) -> None:
        layer = {"trait": "Test_Trait", "action": "Test_Action"}
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.soul.seal_biometric_certitude(layer)
        output = buf.getvalue()
        self.assertIn("Test_Trait", output)
        self.assertIn("Test_Action", output)


if __name__ == "__main__":
    unittest.main()
