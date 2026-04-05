"""Tests for PauLuxuryBehaviorV10_2 (pau_luxury_behavior_v10_2.py)."""

from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import patch

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from pau_luxury_behavior_v10_2 import PauLuxuryBehaviorV10_2


class TestPauLuxuryBehaviorV10_2Init(unittest.TestCase):
    def setUp(self) -> None:
        self.pau = PauLuxuryBehaviorV10_2()

    def test_identity(self) -> None:
        self.assertEqual(self.pau.identity, "White_Peacock_Natural_Real")

    def test_environment(self) -> None:
        self.assertEqual(self.pau.environment, "Moneda_Biometrica_Million_Dollar")

    def test_render_mode(self) -> None:
        self.assertEqual(self.pau.render_mode, "Real-Time_Ultra_Luxe")


class TestSequenceExtremeGestures(unittest.TestCase):
    def setUp(self) -> None:
        self.pau = PauLuxuryBehaviorV10_2()

    def test_calls_pipeline_for_every_movement(self) -> None:
        with (
            patch.object(self.pau, "load_pau_asset") as mock_load,
            patch.object(self.pau, "apply_gold_coin_mask") as mock_mask,
            patch.object(self.pau, "stream_to_interface") as mock_stream,
        ):
            self.pau.sequence_extreme_gestures()

        self.assertEqual(mock_load.call_count, 14)
        self.assertEqual(mock_mask.call_count, 14)
        self.assertEqual(mock_stream.call_count, 14)

    def test_pipeline_order_per_movement(self) -> None:
        call_order: list[str] = []
        with (
            patch.object(self.pau, "load_pau_asset", side_effect=lambda g: call_order.append("load")),
            patch.object(self.pau, "apply_gold_coin_mask", side_effect=lambda g: call_order.append("mask")),
            patch.object(self.pau, "stream_to_interface", side_effect=lambda g: call_order.append("stream")),
        ):
            self.pau.sequence_extreme_gestures()

        for i in range(0, 42, 3):
            self.assertEqual(call_order[i], "load")
            self.assertEqual(call_order[i + 1], "mask")
            self.assertEqual(call_order[i + 2], "stream")

    def test_movements_contain_type_key(self) -> None:
        captured: list[dict] = []
        with (
            patch.object(self.pau, "load_pau_asset", side_effect=lambda g: captured.append(g)),
            patch.object(self.pau, "apply_gold_coin_mask"),
            patch.object(self.pau, "stream_to_interface"),
        ):
            self.pau.sequence_extreme_gestures()

        for movement in captured:
            self.assertIn("type", movement)

    def test_includes_moneda_spin_sync(self) -> None:
        captured: list[dict] = []
        with (
            patch.object(self.pau, "load_pau_asset", side_effect=lambda g: captured.append(g)),
            patch.object(self.pau, "apply_gold_coin_mask"),
            patch.object(self.pau, "stream_to_interface"),
        ):
            self.pau.sequence_extreme_gestures()

        types = [g["type"] for g in captured]
        self.assertIn("moneda_spin_sync", types)

    def test_includes_majestic_vocal(self) -> None:
        captured: list[dict] = []
        with (
            patch.object(self.pau, "load_pau_asset", side_effect=lambda g: captured.append(g)),
            patch.object(self.pau, "apply_gold_coin_mask"),
            patch.object(self.pau, "stream_to_interface"),
        ):
            self.pau.sequence_extreme_gestures()

        types = [g["type"] for g in captured]
        self.assertIn("majestic_vocal", types)

    def test_includes_regal_pause(self) -> None:
        captured: list[dict] = []
        with (
            patch.object(self.pau, "load_pau_asset", side_effect=lambda g: captured.append(g)),
            patch.object(self.pau, "apply_gold_coin_mask"),
            patch.object(self.pau, "stream_to_interface"),
        ):
            self.pau.sequence_extreme_gestures()

        types = [g["type"] for g in captured]
        self.assertIn("regal_pause", types)


class TestPauLuxuryBehaviorV10_2Stubs(unittest.TestCase):
    """Ensure stub methods exist and accept data without raising."""

    def setUp(self) -> None:
        self.pau = PauLuxuryBehaviorV10_2()

    def test_load_pau_asset_accepts_dict(self) -> None:
        self.pau.load_pau_asset({"type": "test"})

    def test_apply_gold_coin_mask_accepts_dict(self) -> None:
        self.pau.apply_gold_coin_mask({"type": "test"})

    def test_stream_to_interface_accepts_dict(self) -> None:
        self.pau.stream_to_interface({"type": "test"})


if __name__ == "__main__":
    unittest.main()
