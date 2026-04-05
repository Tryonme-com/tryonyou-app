"""Tests for PauPersonalityEngineV10_2 (pau_personality_engine_v10_2.py)."""

from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import patch

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from pau_personality_engine_v10_2 import PauPersonalityEngineV10_2  # noqa: E402


class TestPauPersonalityEngineInit(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = PauPersonalityEngineV10_2()

    def test_identity(self) -> None:
        self.assertEqual(self.engine.identity, "White_Peacock_Natural_Real")

    def test_archetype(self) -> None:
        self.assertEqual(self.engine.archetype, "Refined_Authority_Divine")

    def test_philosophy(self) -> None:
        self.assertEqual(self.engine.philosophy, "The_End_of_Sizes")

    def test_traits_keys(self) -> None:
        for key in ("tone", "charisma", "empathy", "standard"):
            self.assertIn(key, self.engine.traits)

    def test_traits_values(self) -> None:
        self.assertEqual(self.engine.traits["tone"], "Refined_yet_Close")
        self.assertEqual(self.engine.traits["charisma"], "High_Couture_Magnetic")
        self.assertEqual(self.engine.traits["empathy"], "Sincere_Supportive")
        self.assertEqual(self.engine.traits["standard"], "Million_Dollar_Luxury")


class TestGetBehavioralMetadata(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = PauPersonalityEngineV10_2()
        self.metadata = self.engine.get_behavioral_metadata()

    def test_returns_four_traits(self) -> None:
        self.assertEqual(len(self.metadata), 4)

    def test_trait_names(self) -> None:
        names = [entry["trait"] for entry in self.metadata]
        self.assertIn("Confidence", names)
        self.assertIn("Elegance", names)
        self.assertIn("Warmth", names)
        self.assertIn("Authority", names)

    def test_elegance_value_is_1(self) -> None:
        elegance = next(e for e in self.metadata if e["trait"] == "Elegance")
        self.assertEqual(elegance["value"], 1.0)

    def test_confidence_value(self) -> None:
        confidence = next(e for e in self.metadata if e["trait"] == "Confidence")
        self.assertAlmostEqual(confidence["value"], 0.98)

    def test_each_entry_has_gestures_list(self) -> None:
        for entry in self.metadata:
            self.assertIsInstance(entry.get("gestures"), list)
            self.assertTrue(len(entry["gestures"]) > 0)


class TestMapPersonalityToVideoLoops(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = PauPersonalityEngineV10_2()

    def test_attach_metadata_called_four_times(self) -> None:
        with patch.object(self.engine, "attach_metadata_to_asset") as mock_attach:
            self.engine.map_personality_to_video_loops()
        self.assertEqual(mock_attach.call_count, 4)

    def test_sync_with_biometric_coin_called_four_times(self) -> None:
        with patch.object(self.engine, "sync_with_biometric_coin") as mock_sync:
            self.engine.map_personality_to_video_loops()
        self.assertEqual(mock_sync.call_count, 4)

    def test_optimize_for_million_dollar_ui_called_four_times(self) -> None:
        with patch.object(self.engine, "optimize_for_million_dollar_ui") as mock_opt:
            self.engine.map_personality_to_video_loops()
        self.assertEqual(mock_opt.call_count, 4)

    def test_states_covered(self) -> None:
        captured = []

        def capture(data):
            captured.append(data["state"])

        with patch.object(self.engine, "attach_metadata_to_asset", side_effect=capture):
            with patch.object(self.engine, "sync_with_biometric_coin"):
                with patch.object(self.engine, "optimize_for_million_dollar_ui"):
                    self.engine.map_personality_to_video_loops()

        for state in ("IDLE", "TALKING", "LAUGHING", "NODDING"):
            self.assertIn(state, captured)

    def test_map_runs_without_error(self) -> None:
        try:
            self.engine.map_personality_to_video_loops()
        except Exception as exc:  # pragma: no cover
            self.fail(f"map_personality_to_video_loops raised unexpectedly: {exc}")


class TestHelperMethodsExist(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = PauPersonalityEngineV10_2()

    def test_attach_metadata_to_asset_callable(self) -> None:
        self.assertTrue(callable(self.engine.attach_metadata_to_asset))

    def test_sync_with_biometric_coin_callable(self) -> None:
        self.assertTrue(callable(self.engine.sync_with_biometric_coin))

    def test_optimize_for_million_dollar_ui_callable(self) -> None:
        self.assertTrue(callable(self.engine.optimize_for_million_dollar_ui))

    def test_helper_methods_accept_dict(self) -> None:
        sample = {"state": "TEST"}
        self.engine.attach_metadata_to_asset(sample)
        self.engine.sync_with_biometric_coin(sample)
        self.engine.optimize_for_million_dollar_ui(sample)


if __name__ == "__main__":
    unittest.main()
