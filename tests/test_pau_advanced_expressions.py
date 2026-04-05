"""Tests for PauAdvancedExpressions (pau_advanced_expressions.py)."""

from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import patch

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from pau_advanced_expressions import PauAdvancedExpressions


class TestPauAdvancedExpressionsInit(unittest.TestCase):
    def setUp(self) -> None:
        self.pau = PauAdvancedExpressions()

    def test_pau_ref(self) -> None:
        self.assertEqual(self.pau.pau_ref, "WhitePeacock_Natural_Real")

    def test_container(self) -> None:
        self.assertEqual(self.pau.container, "MonedaBiometrica_V10.2")

    def test_engine(self) -> None:
        self.assertEqual(self.pau.engine, "HighFidelity_Render")


class TestSequenceGesturesContinuous(unittest.TestCase):
    def setUp(self) -> None:
        self.pau = PauAdvancedExpressions()

    def test_calls_pipeline_for_every_gesture(self) -> None:
        with (
            patch.object(self.pau, "load_pau_asset") as mock_load,
            patch.object(self.pau, "apply_gold_coin_mask") as mock_mask,
            patch.object(self.pau, "stream_to_interface") as mock_stream,
        ):
            self.pau.sequence_gestures_continuous()

        self.assertEqual(mock_load.call_count, 10)
        self.assertEqual(mock_mask.call_count, 10)
        self.assertEqual(mock_stream.call_count, 10)

    def test_pipeline_order_per_gesture(self) -> None:
        call_order: list[str] = []
        with (
            patch.object(self.pau, "load_pau_asset", side_effect=lambda g: call_order.append("load")),
            patch.object(self.pau, "apply_gold_coin_mask", side_effect=lambda g: call_order.append("mask")),
            patch.object(self.pau, "stream_to_interface", side_effect=lambda g: call_order.append("stream")),
        ):
            self.pau.sequence_gestures_continuous()

        for i in range(0, 30, 3):
            self.assertEqual(call_order[i], "load")
            self.assertEqual(call_order[i + 1], "mask")
            self.assertEqual(call_order[i + 2], "stream")

    def test_gestures_contain_type_key(self) -> None:
        captured: list[dict] = []
        with (
            patch.object(self.pau, "load_pau_asset", side_effect=lambda g: captured.append(g)),
            patch.object(self.pau, "apply_gold_coin_mask"),
            patch.object(self.pau, "stream_to_interface"),
        ):
            self.pau.sequence_gestures_continuous()

        for gesture in captured:
            self.assertIn("type", gesture)

    def test_includes_divine_transformation_gesture(self) -> None:
        captured: list[dict] = []
        with (
            patch.object(self.pau, "load_pau_asset", side_effect=lambda g: captured.append(g)),
            patch.object(self.pau, "apply_gold_coin_mask"),
            patch.object(self.pau, "stream_to_interface"),
        ):
            self.pau.sequence_gestures_continuous()

        types = [g["type"] for g in captured]
        self.assertIn("divine_transformation", types)

    def test_includes_charismatic_speech_gesture(self) -> None:
        captured: list[dict] = []
        with (
            patch.object(self.pau, "load_pau_asset", side_effect=lambda g: captured.append(g)),
            patch.object(self.pau, "apply_gold_coin_mask"),
            patch.object(self.pau, "stream_to_interface"),
        ):
            self.pau.sequence_gestures_continuous()

        types = [g["type"] for g in captured]
        self.assertIn("charismatic_speech", types)


class TestPauAdvancedExpressionsStubs(unittest.TestCase):
    """Ensure stub methods exist and accept data without raising."""

    def setUp(self) -> None:
        self.pau = PauAdvancedExpressions()

    def test_load_pau_asset_accepts_dict(self) -> None:
        self.pau.load_pau_asset({"type": "test"})

    def test_apply_gold_coin_mask_accepts_dict(self) -> None:
        self.pau.apply_gold_coin_mask({"type": "test"})

    def test_stream_to_interface_accepts_dict(self) -> None:
        self.pau.stream_to_interface({"type": "test"})


if __name__ == "__main__":
    unittest.main()
