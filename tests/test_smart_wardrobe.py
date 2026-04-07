"""Tests para SmartWardrobe — BodyAnchors, PilotEngine, SmartWardrobe."""

from __future__ import annotations

import os
import sys
import time
import unittest

_API = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "api"))
if _API not in sys.path:
    sys.path.insert(0, _API)

from smart_wardrobe import BodyAnchors, PilotEngine, SmartWardrobe


class TestBodyAnchors(unittest.TestCase):
    def test_stores_shoulder_and_torso(self) -> None:
        anchors = BodyAnchors(shoulder_w=44.0, torso_h=60.0)
        self.assertEqual(anchors.shoulder_w, 44.0)
        self.assertEqual(anchors.torso_h, 60.0)


class TestSmartWardrobeInit(unittest.TestCase):
    def test_initial_state(self) -> None:
        w = SmartWardrobe("user_123")
        self.assertEqual(w.user_id, "user_123")
        self.assertEqual(w.inventory, [])
        self.assertIsNone(w.saved_silhouette)


class TestSaveSilhouette(unittest.TestCase):
    def test_returns_expected_message(self) -> None:
        w = SmartWardrobe("u1")
        anchors = BodyAnchors(shoulder_w=42.0, torso_h=58.0)
        result = w.save_silhouette(anchors)
        self.assertEqual(result, "Silueta protegida bajo cifrado local.")

    def test_stores_shoulder_w(self) -> None:
        w = SmartWardrobe("u1")
        anchors = BodyAnchors(shoulder_w=42.0, torso_h=58.0)
        w.save_silhouette(anchors)
        self.assertIsNotNone(w.saved_silhouette)
        self.assertEqual(w.saved_silhouette["shoulderW"], 42.0)

    def test_stores_torso_h(self) -> None:
        w = SmartWardrobe("u1")
        anchors = BodyAnchors(shoulder_w=42.0, torso_h=58.0)
        w.save_silhouette(anchors)
        self.assertIsNotNone(w.saved_silhouette)
        self.assertEqual(w.saved_silhouette["torsoH"], 58.0)

    def test_timestamp_is_recent(self) -> None:
        w = SmartWardrobe("u1")
        anchors = BodyAnchors(shoulder_w=42.0, torso_h=58.0)
        before = time.time()
        w.save_silhouette(anchors)
        after = time.time()
        self.assertIsNotNone(w.saved_silhouette)
        self.assertGreaterEqual(w.saved_silhouette["timestamp"], before)
        self.assertLessEqual(w.saved_silhouette["timestamp"], after)

    def test_overwrites_previous_silhouette(self) -> None:
        w = SmartWardrobe("u1")
        w.save_silhouette(BodyAnchors(shoulder_w=40.0, torso_h=55.0))
        w.save_silhouette(BodyAnchors(shoulder_w=43.0, torso_h=59.0))
        self.assertEqual(w.saved_silhouette["shoulderW"], 43.0)
        self.assertEqual(w.saved_silhouette["torsoH"], 59.0)


class TestGetMixAndMatch(unittest.TestCase):
    def setUp(self) -> None:
        self.wardrobe = SmartWardrobe("u1")
        self.engine = PilotEngine()

    def test_excludes_current_look(self) -> None:
        suggestions = self.wardrobe.get_mix_and_match(self.engine, "eg0")
        self.assertNotIn("eg0", suggestions)

    def test_returns_at_most_four(self) -> None:
        suggestions = self.wardrobe.get_mix_and_match(self.engine, "eg0")
        self.assertLessEqual(len(suggestions), 4)

    def test_returns_list(self) -> None:
        suggestions = self.wardrobe.get_mix_and_match(self.engine, "eg1")
        self.assertIsInstance(suggestions, list)

    def test_unknown_look_returns_all_four(self) -> None:
        suggestions = self.wardrobe.get_mix_and_match(self.engine, "unknown")
        self.assertEqual(len(suggestions), 4)


class TestPilotCollection(unittest.TestCase):
    def test_has_at_least_five_looks(self) -> None:
        self.assertGreaterEqual(len(PilotEngine.PILOT_COLLECTION), 5)

    def test_each_look_has_recovery_pct(self) -> None:
        for key, val in PilotEngine.PILOT_COLLECTION.items():
            self.assertIn("recoveryPct", val, f"Missing recoveryPct in {key}")

    def test_each_look_has_garment_id(self) -> None:
        for key, val in PilotEngine.PILOT_COLLECTION.items():
            self.assertIn("garment_id", val, f"Missing garment_id in {key}")


if __name__ == "__main__":
    unittest.main()
