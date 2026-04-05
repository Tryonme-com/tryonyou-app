"""Tests para PauEmotionalMasterV10_2 (api/pau_emotional_master.py).

Cubre:
  1. Atributos de identidad del motor emocional.
  2. map_human_to_avian: mapeo correcto de gestos.
  3. render_million_dollar_frame: generación de frames de lujo.
  4. stream_to_moneda_biometrica: transmisión al registro biométrico.
  5. execute_deep_personality_sync: orquestación completa de los 7 arquetipos.
  6. get_sync_summary: resumen de la sincronización.
"""

from __future__ import annotations

import os
import sys
import unittest

_API = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "api"))
if _API not in sys.path:
    sys.path.insert(0, _API)

from pau_emotional_master import PauEmotionalMasterV10_2


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SAMPLE_GESTURE = {
    "emotion": "Biometric_Pride",
    "human_action": "Determined_Approval_Nod",
    "peacock_action": "Chest_Puff_Max",
    "tail_status": "Full_White_Display",
    "impact": "Certification_Authority",
}

_TOTAL_GESTURES = 7


# ---------------------------------------------------------------------------
# 1. Identidad del motor
# ---------------------------------------------------------------------------


class TestPauEmotionalMasterIdentity(unittest.TestCase):
    def setUp(self) -> None:
        self.master = PauEmotionalMasterV10_2()

    def test_reference_is_white_peacock(self) -> None:
        self.assertEqual(self.master.reference, "White_Peacock_Natural_r5vr2He")

    def test_luxury_tier(self) -> None:
        self.assertEqual(self.master.luxury_tier, "Million_Dollar_Interface")

    def test_emotion_engine(self) -> None:
        self.assertEqual(
            self.master.emotion_engine, "Human_Peacock_Hybrid_Expressivity"
        )

    def test_initial_state_is_empty(self) -> None:
        self.assertEqual(self.master._avian_mappings, [])
        self.assertEqual(self.master._rendered_frames, [])
        self.assertEqual(self.master._biometric_stream, [])


# ---------------------------------------------------------------------------
# 2. map_human_to_avian
# ---------------------------------------------------------------------------


class TestMapHumanToAvian(unittest.TestCase):
    def setUp(self) -> None:
        self.master = PauEmotionalMasterV10_2()

    def test_returns_dict_with_required_keys(self) -> None:
        result = self.master.map_human_to_avian(_SAMPLE_GESTURE)
        for key in (
            "reference",
            "emotion",
            "human_action",
            "avian_action",
            "tail_status",
            "avian_intensity",
            "engine",
        ):
            self.assertIn(key, result)

    def test_reference_is_propagated(self) -> None:
        result = self.master.map_human_to_avian(_SAMPLE_GESTURE)
        self.assertEqual(result["reference"], self.master.reference)

    def test_engine_is_propagated(self) -> None:
        result = self.master.map_human_to_avian(_SAMPLE_GESTURE)
        self.assertEqual(result["engine"], self.master.emotion_engine)

    def test_avian_action_matches_peacock_action(self) -> None:
        result = self.master.map_human_to_avian(_SAMPLE_GESTURE)
        self.assertEqual(result["avian_action"], _SAMPLE_GESTURE["peacock_action"])

    def test_full_white_display_intensity_is_100(self) -> None:
        result = self.master.map_human_to_avian(_SAMPLE_GESTURE)
        self.assertEqual(result["avian_intensity"], 100)

    def test_closed_elegant_intensity_is_10(self) -> None:
        gesture = {**_SAMPLE_GESTURE, "tail_status": "Closed_Elegant"}
        result = self.master.map_human_to_avian(gesture)
        self.assertEqual(result["avian_intensity"], 10)

    def test_unknown_tail_status_defaults_to_50(self) -> None:
        gesture = {**_SAMPLE_GESTURE, "tail_status": "Unknown_Status"}
        result = self.master.map_human_to_avian(gesture)
        self.assertEqual(result["avian_intensity"], 50)

    def test_result_is_accumulated(self) -> None:
        self.master.map_human_to_avian(_SAMPLE_GESTURE)
        self.master.map_human_to_avian(_SAMPLE_GESTURE)
        self.assertEqual(len(self.master._avian_mappings), 2)


# ---------------------------------------------------------------------------
# 3. render_million_dollar_frame
# ---------------------------------------------------------------------------


class TestRenderMillionDollarFrame(unittest.TestCase):
    def setUp(self) -> None:
        self.master = PauEmotionalMasterV10_2()

    def test_returns_dict_with_required_keys(self) -> None:
        result = self.master.render_million_dollar_frame(_SAMPLE_GESTURE)
        for key in (
            "tier",
            "emotion",
            "impact",
            "impact_weight",
            "human_action",
            "peacock_action",
            "tail_status",
            "frame_label",
        ):
            self.assertIn(key, result)

    def test_tier_matches_luxury_tier(self) -> None:
        result = self.master.render_million_dollar_frame(_SAMPLE_GESTURE)
        self.assertEqual(result["tier"], self.master.luxury_tier)

    def test_certification_authority_weight_is_1(self) -> None:
        result = self.master.render_million_dollar_frame(_SAMPLE_GESTURE)
        self.assertEqual(result["impact_weight"], 1.00)

    def test_frame_label_contains_tier_emotion_impact(self) -> None:
        result = self.master.render_million_dollar_frame(_SAMPLE_GESTURE)
        label = result["frame_label"]
        self.assertIn(self.master.luxury_tier, label)
        self.assertIn(_SAMPLE_GESTURE["emotion"], label)
        self.assertIn(_SAMPLE_GESTURE["impact"], label)

    def test_unknown_impact_defaults_to_0_5(self) -> None:
        gesture = {**_SAMPLE_GESTURE, "impact": "Unknown_Impact"}
        result = self.master.render_million_dollar_frame(gesture)
        self.assertEqual(result["impact_weight"], 0.5)

    def test_result_is_accumulated(self) -> None:
        self.master.render_million_dollar_frame(_SAMPLE_GESTURE)
        self.master.render_million_dollar_frame(_SAMPLE_GESTURE)
        self.assertEqual(len(self.master._rendered_frames), 2)


# ---------------------------------------------------------------------------
# 4. stream_to_moneda_biometrica
# ---------------------------------------------------------------------------


class TestStreamToMonedaBiometrica(unittest.TestCase):
    def setUp(self) -> None:
        self.master = PauEmotionalMasterV10_2()

    def test_returns_dict_with_required_keys(self) -> None:
        result = self.master.stream_to_moneda_biometrica(_SAMPLE_GESTURE)
        for key in (
            "source",
            "tier",
            "engine",
            "emotion",
            "impact",
            "sovereignty_weight",
            "tail_status",
            "avian_intensity",
        ):
            self.assertIn(key, result)

    def test_source_is_reference(self) -> None:
        result = self.master.stream_to_moneda_biometrica(_SAMPLE_GESTURE)
        self.assertEqual(result["source"], self.master.reference)

    def test_sovereignty_weight_matches_impact(self) -> None:
        result = self.master.stream_to_moneda_biometrica(_SAMPLE_GESTURE)
        self.assertEqual(result["sovereignty_weight"], 1.00)

    def test_avian_intensity_matches_tail_status(self) -> None:
        result = self.master.stream_to_moneda_biometrica(_SAMPLE_GESTURE)
        self.assertEqual(result["avian_intensity"], 100)

    def test_result_is_accumulated(self) -> None:
        self.master.stream_to_moneda_biometrica(_SAMPLE_GESTURE)
        self.master.stream_to_moneda_biometrica(_SAMPLE_GESTURE)
        self.assertEqual(len(self.master._biometric_stream), 2)


# ---------------------------------------------------------------------------
# 5. execute_deep_personality_sync
# ---------------------------------------------------------------------------


class TestExecuteDeepPersonalitySync(unittest.TestCase):
    def setUp(self) -> None:
        self.master = PauEmotionalMasterV10_2()
        self.master.execute_deep_personality_sync()

    def test_all_gestures_are_mapped(self) -> None:
        self.assertEqual(len(self.master._avian_mappings), _TOTAL_GESTURES)

    def test_all_frames_are_rendered(self) -> None:
        self.assertEqual(len(self.master._rendered_frames), _TOTAL_GESTURES)

    def test_all_stream_entries_are_created(self) -> None:
        self.assertEqual(len(self.master._biometric_stream), _TOTAL_GESTURES)

    def test_first_emotion_is_euphoric_recognition(self) -> None:
        self.assertEqual(
            self.master._avian_mappings[0]["emotion"], "Euphoric_Recognition"
        )

    def test_last_emotion_is_victory_laugh(self) -> None:
        self.assertEqual(
            self.master._avian_mappings[-1]["emotion"], "Victory_Laugh"
        )

    def test_biometric_pride_frame_has_max_weight(self) -> None:
        biometric_pride_frames = [
            f
            for f in self.master._rendered_frames
            if f["emotion"] == "Biometric_Pride"
        ]
        self.assertEqual(len(biometric_pride_frames), 1)
        self.assertEqual(biometric_pride_frames[0]["impact_weight"], 1.00)

    def test_all_avian_mappings_have_reference(self) -> None:
        for mapping in self.master._avian_mappings:
            self.assertEqual(mapping["reference"], self.master.reference)

    def test_all_frames_have_tier(self) -> None:
        for frame in self.master._rendered_frames:
            self.assertEqual(frame["tier"], self.master.luxury_tier)


# ---------------------------------------------------------------------------
# 6. get_sync_summary
# ---------------------------------------------------------------------------


class TestGetSyncSummary(unittest.TestCase):
    def setUp(self) -> None:
        self.master = PauEmotionalMasterV10_2()
        self.master.execute_deep_personality_sync()
        self.summary = self.master.get_sync_summary()

    def test_summary_has_required_keys(self) -> None:
        for key in (
            "reference",
            "luxury_tier",
            "emotion_engine",
            "gestures_mapped",
            "frames_rendered",
            "stream_entries",
            "total_sovereignty_weight",
        ):
            self.assertIn(key, self.summary)

    def test_counts_match_total_gestures(self) -> None:
        self.assertEqual(self.summary["gestures_mapped"], _TOTAL_GESTURES)
        self.assertEqual(self.summary["frames_rendered"], _TOTAL_GESTURES)
        self.assertEqual(self.summary["stream_entries"], _TOTAL_GESTURES)

    def test_total_sovereignty_weight_is_positive(self) -> None:
        self.assertGreater(self.summary["total_sovereignty_weight"], 0)

    def test_total_sovereignty_weight_is_sum_of_all_impacts(self) -> None:
        expected = round(
            sum(e["sovereignty_weight"] for e in self.master._biometric_stream), 4
        )
        self.assertEqual(self.summary["total_sovereignty_weight"], expected)

    def test_summary_reference_matches(self) -> None:
        self.assertEqual(self.summary["reference"], self.master.reference)

    def test_empty_master_summary_has_zero_counts(self) -> None:
        empty = PauEmotionalMasterV10_2()
        s = empty.get_sync_summary()
        self.assertEqual(s["gestures_mapped"], 0)
        self.assertEqual(s["frames_rendered"], 0)
        self.assertEqual(s["stream_entries"], 0)
        self.assertEqual(s["total_sovereignty_weight"], 0.0)


if __name__ == "__main__":
    unittest.main()
