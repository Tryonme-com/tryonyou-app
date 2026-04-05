"""Tests for PauDivineSoulV10_2 (pau_divine_soul_v10_2.py)."""

from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import patch

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from pau_divine_soul_v10_2 import PauDivineSoulV10_2  # noqa: E402


class TestPauDivineSoulInit(unittest.TestCase):
    def setUp(self) -> None:
        self.soul = PauDivineSoulV10_2()

    def test_reference(self) -> None:
        self.assertEqual(self.soul.reference, "White_Peacock_Natural_r5vr2He")

    def test_dna_keys(self) -> None:
        for key in ("origin", "personality_type", "voice_tone", "mission"):
            self.assertIn(key, self.soul.dna)

    def test_dna_origin(self) -> None:
        self.assertEqual(self.soul.dna["origin"], "Lafayette_Refinement")

    def test_dna_personality_type(self) -> None:
        self.assertEqual(self.soul.dna["personality_type"], "Eric_The_Hairdresser_Style")

    def test_dna_voice_tone(self) -> None:
        self.assertEqual(self.soul.dna["voice_tone"], "Refined_Close_Soulful")

    def test_dna_mission(self) -> None:
        self.assertEqual(self.soul.dna["mission"], "Zero_Complex_Experience")

    def test_initial_injections_empty(self) -> None:
        self.assertEqual(self.soul._video_injections, [])

    def test_initial_ui_syncs_empty(self) -> None:
        self.assertEqual(self.soul._ui_syncs, [])

    def test_initial_certitude_seals_empty(self) -> None:
        self.assertEqual(self.soul._certitude_seals, [])


class TestExecutePersonalityLogic(unittest.TestCase):
    def setUp(self) -> None:
        self.soul = PauDivineSoulV10_2()

    def test_inject_called_five_times(self) -> None:
        with patch.object(self.soul, "inject_personality_to_video") as mock_inject:
            self.soul.execute_personality_logic()
        self.assertEqual(mock_inject.call_count, 5)

    def test_sync_called_five_times(self) -> None:
        with patch.object(self.soul, "sync_with_million_dollar_ui") as mock_sync:
            self.soul.execute_personality_logic()
        self.assertEqual(mock_sync.call_count, 5)

    def test_seal_called_five_times(self) -> None:
        with patch.object(self.soul, "seal_biometric_certitude") as mock_seal:
            self.soul.execute_personality_logic()
        self.assertEqual(mock_seal.call_count, 5)

    def test_all_trait_names_injected(self) -> None:
        self.soul.execute_personality_logic()
        injected_traits = [e["trait"] for e in self.soul._video_injections]
        for trait in (
            "Refined_Proximity",
            "Absolute_Sincerity",
            "Artistic_Intellect",
            "The_Snap_Master",
            "Empathetic_Authority",
        ):
            self.assertIn(trait, injected_traits)

    def test_runs_without_error(self) -> None:
        try:
            self.soul.execute_personality_logic()
        except Exception as exc:  # pragma: no cover
            self.fail(f"execute_personality_logic raised unexpectedly: {exc}")


class TestInjectPersonalityToVideo(unittest.TestCase):
    def setUp(self) -> None:
        self.soul = PauDivineSoulV10_2()
        self.sample = {
            "trait": "The_Snap_Master",
            "behavior": "Instant_Transformation",
            "action": "Change_Look_Avatar",
            "gestures": ["Sharp_Head_Turn", "Beak_Click_Sync"],
        }

    def test_appends_to_video_injections(self) -> None:
        self.soul.inject_personality_to_video(self.sample)
        self.assertEqual(len(self.soul._video_injections), 1)

    def test_injection_contains_trait(self) -> None:
        self.soul.inject_personality_to_video(self.sample)
        self.assertEqual(self.soul._video_injections[0]["trait"], "The_Snap_Master")

    def test_injection_contains_action(self) -> None:
        self.soul.inject_personality_to_video(self.sample)
        self.assertEqual(self.soul._video_injections[0]["action"], "Change_Look_Avatar")

    def test_injection_contains_gestures(self) -> None:
        self.soul.inject_personality_to_video(self.sample)
        self.assertIn("Sharp_Head_Turn", self.soul._video_injections[0]["gestures"])

    def test_injection_contains_source_reference(self) -> None:
        self.soul.inject_personality_to_video(self.sample)
        self.assertEqual(
            self.soul._video_injections[0]["source"],
            "White_Peacock_Natural_r5vr2He",
        )


class TestSyncWithMillionDollarUI(unittest.TestCase):
    def setUp(self) -> None:
        self.soul = PauDivineSoulV10_2()
        self.sample = {
            "trait": "Refined_Proximity",
            "behavior": "Not_Robotic",
            "action": "Elegant_Compliment",
            "gestures": ["Soft_Beak_Move"],
        }

    def test_appends_to_ui_syncs(self) -> None:
        self.soul.sync_with_million_dollar_ui(self.sample)
        self.assertEqual(len(self.soul._ui_syncs), 1)

    def test_sync_contains_trait(self) -> None:
        self.soul.sync_with_million_dollar_ui(self.sample)
        self.assertEqual(self.soul._ui_syncs[0]["trait"], "Refined_Proximity")

    def test_sync_contains_behavior(self) -> None:
        self.soul.sync_with_million_dollar_ui(self.sample)
        self.assertEqual(self.soul._ui_syncs[0]["behavior"], "Not_Robotic")

    def test_sync_ui_layer(self) -> None:
        self.soul.sync_with_million_dollar_ui(self.sample)
        self.assertEqual(self.soul._ui_syncs[0]["ui_layer"], "Million_Dollar_UI")

    def test_sync_origin_from_dna(self) -> None:
        self.soul.sync_with_million_dollar_ui(self.sample)
        self.assertEqual(self.soul._ui_syncs[0]["origin"], "Lafayette_Refinement")


class TestSealBiometricCertitude(unittest.TestCase):
    def setUp(self) -> None:
        self.soul = PauDivineSoulV10_2()
        self.sample = {
            "trait": "Empathetic_Authority",
            "behavior": "Anti_Return_Logic",
            "action": "Perfect_Fit_Validation",
            "gestures": ["Triple_Fast_Nod"],
        }

    def test_appends_to_certitude_seals(self) -> None:
        self.soul.seal_biometric_certitude(self.sample)
        self.assertEqual(len(self.soul._certitude_seals), 1)

    def test_seal_contains_trait(self) -> None:
        self.soul.seal_biometric_certitude(self.sample)
        self.assertEqual(self.soul._certitude_seals[0]["trait"], "Empathetic_Authority")

    def test_seal_certitude_value(self) -> None:
        self.soul.seal_biometric_certitude(self.sample)
        self.assertEqual(self.soul._certitude_seals[0]["certitude"], "Sealed")

    def test_seal_patent(self) -> None:
        self.soul.seal_biometric_certitude(self.sample)
        self.assertEqual(
            self.soul._certitude_seals[0]["patent"], "PCT/EP2025/067317"
        )

    def test_seal_contains_action(self) -> None:
        self.soul.seal_biometric_certitude(self.sample)
        self.assertEqual(
            self.soul._certitude_seals[0]["action"], "Perfect_Fit_Validation"
        )


class TestGetSoulSummary(unittest.TestCase):
    def setUp(self) -> None:
        self.soul = PauDivineSoulV10_2()
        self.soul.execute_personality_logic()
        self.summary = self.soul.get_soul_summary()

    def test_summary_has_reference(self) -> None:
        self.assertEqual(self.summary["reference"], "White_Peacock_Natural_r5vr2He")

    def test_layers_injected_count(self) -> None:
        self.assertEqual(self.summary["layers_injected"], 5)

    def test_ui_syncs_count(self) -> None:
        self.assertEqual(self.summary["ui_syncs"], 5)

    def test_certitude_seals_count(self) -> None:
        self.assertEqual(self.summary["certitude_seals"], 5)

    def test_summary_includes_dna(self) -> None:
        self.assertIn("dna", self.summary)
        self.assertEqual(self.summary["dna"]["origin"], "Lafayette_Refinement")


if __name__ == "__main__":
    unittest.main()
