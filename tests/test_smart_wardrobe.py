"""Tests para SmartWardrobe — Puntos 3 y 4 del Piloto TryOnYou V10."""

from __future__ import annotations

import os
import sys
import unittest

_API = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "api"))
if _API not in sys.path:
    sys.path.insert(0, _API)

from smart_wardrobe import BodyAnchors, PilotEngine, SmartWardrobe


class TestSmartWardrobeInit(unittest.TestCase):
    def test_user_id_stored(self) -> None:
        sw = SmartWardrobe("user_001")
        self.assertEqual(sw.user_id, "user_001")

    def test_inventory_starts_empty(self) -> None:
        sw = SmartWardrobe("user_001")
        self.assertEqual(sw.inventory, [])

    def test_saved_silhouette_starts_none(self) -> None:
        sw = SmartWardrobe("user_001")
        self.assertIsNone(sw.saved_silhouette)


class TestSaveSilhouette(unittest.TestCase):
    def setUp(self) -> None:
        self.sw = SmartWardrobe("user_002")
        self.anchors = BodyAnchors(shoulder_w=42.5, torso_h=55.0)

    def test_returns_protection_message(self) -> None:
        result = self.sw.save_silhouette(self.anchors)
        self.assertEqual(result, "Silueta protegida bajo cifrado local.")

    def test_shoulder_w_stored(self) -> None:
        self.sw.save_silhouette(self.anchors)
        self.assertEqual(self.sw.saved_silhouette["shoulderW"], 42.5)

    def test_torso_h_stored(self) -> None:
        self.sw.save_silhouette(self.anchors)
        self.assertEqual(self.sw.saved_silhouette["torsoH"], 55.0)

    def test_timestamp_is_positive_float(self) -> None:
        self.sw.save_silhouette(self.anchors)
        self.assertGreater(self.sw.saved_silhouette["timestamp"], 0)

    def test_silhouette_overwritten_on_second_scan(self) -> None:
        self.sw.save_silhouette(self.anchors)
        new_anchors = BodyAnchors(shoulder_w=44.0, torso_h=57.0)
        self.sw.save_silhouette(new_anchors)
        self.assertEqual(self.sw.saved_silhouette["shoulderW"], 44.0)
        self.assertEqual(self.sw.saved_silhouette["torsoH"], 57.0)


class TestGetMixAndMatch(unittest.TestCase):
    def setUp(self) -> None:
        self.sw = SmartWardrobe("user_003")
        self.engine = PilotEngine()

    def test_excludes_current_look(self) -> None:
        suggestions = self.sw.get_mix_and_match(self.engine, "eg0")
        self.assertNotIn("eg0", suggestions)

    def test_returns_at_most_four(self) -> None:
        suggestions = self.sw.get_mix_and_match(self.engine, "eg0")
        self.assertLessEqual(len(suggestions), 4)

    def test_returns_four_when_collection_has_five(self) -> None:
        suggestions = self.sw.get_mix_and_match(self.engine, "eg0")
        self.assertEqual(len(suggestions), 4)

    def test_returns_fewer_when_collection_is_small(self) -> None:
        class SmallEngine:
            PILOT_COLLECTION = {
                "eg0": {"recoveryPct": 90},
                "eg1": {"recoveryPct": 88},
            }

        suggestions = self.sw.get_mix_and_match(SmallEngine(), "eg0")
        self.assertEqual(suggestions, ["eg1"])

    def test_ordered_by_recovery_pct_similarity(self) -> None:
        class OrderedEngine:
            PILOT_COLLECTION = {
                "base": {"recoveryPct": 80},
                "far":  {"recoveryPct": 60},
                "near": {"recoveryPct": 78},
                "mid":  {"recoveryPct": 70},
            }

        suggestions = self.sw.get_mix_and_match(OrderedEngine(), "base")
        # near (diff=2) < mid (diff=10) < far (diff=20)
        self.assertEqual(suggestions, ["near", "mid", "far"])

    def test_all_suggestions_are_valid_keys(self) -> None:
        suggestions = self.sw.get_mix_and_match(self.engine, "eg1")
        for s in suggestions:
            self.assertIn(s, self.engine.PILOT_COLLECTION)


class TestPilotCollection(unittest.TestCase):
    def test_has_five_entries(self) -> None:
        self.assertEqual(len(PilotEngine.PILOT_COLLECTION), 5)

    def test_all_entries_have_recovery_pct(self) -> None:
        for key, val in PilotEngine.PILOT_COLLECTION.items():
            self.assertIn("recoveryPct", val, f"Missing recoveryPct in {key}")


if __name__ == "__main__":
    unittest.main()
