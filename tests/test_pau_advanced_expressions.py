"""Tests para PauAdvancedExpressions (pau_advanced_expressions.py).

PCT/EP2025/067317 · SIREN 943 610 196
Bajo Protocolo de Soberanía V10 — Founder: Rubén
"""

from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import call, patch

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from pau_advanced_expressions import PauAdvancedExpressions  # noqa: E402


class TestPauAdvancedExpressionsInit(unittest.TestCase):
    """Verifica los atributos del constructor."""

    def setUp(self) -> None:
        self.pau = PauAdvancedExpressions()

    def test_pau_ref(self) -> None:
        self.assertEqual(self.pau.pau_ref, "WhitePeacock_Natural_Real")

    def test_container(self) -> None:
        self.assertEqual(self.pau.container, "MonedaBiometrica_V10.2")

    def test_engine(self) -> None:
        self.assertEqual(self.pau.engine, "HighFidelity_Render")


class TestLoadPauAsset(unittest.TestCase):
    """Verifica load_pau_asset con distintos gestos."""

    def setUp(self) -> None:
        self.pau = PauAdvancedExpressions()

    def test_load_pau_asset_prints_ref_and_gesture(self) -> None:
        data = {"type": "charismatic_speech", "beak": "sync_audio"}
        with patch("builtins.print") as mock_print:
            self.pau.load_pau_asset(data)
        output = " ".join(str(a) for a in mock_print.call_args[0])
        self.assertIn("WhitePeacock_Natural_Real", output)
        self.assertIn("charismatic_speech", output)

    def test_load_pau_asset_handles_missing_type(self) -> None:
        data = {}
        with patch("builtins.print") as mock_print:
            self.pau.load_pau_asset(data)
        output = " ".join(str(a) for a in mock_print.call_args[0])
        self.assertIn("unknown", output)


class TestApplyGoldCoinMask(unittest.TestCase):
    """Verifica apply_gold_coin_mask con distintos gestos."""

    def setUp(self) -> None:
        self.pau = PauAdvancedExpressions()

    def test_apply_gold_coin_mask_prints_container_and_gesture(self) -> None:
        data = {"type": "authority_nod"}
        with patch("builtins.print") as mock_print:
            self.pau.apply_gold_coin_mask(data)
        output = " ".join(str(a) for a in mock_print.call_args[0])
        self.assertIn("MonedaBiometrica_V10.2", output)
        self.assertIn("authority_nod", output)

    def test_apply_gold_coin_mask_handles_missing_type(self) -> None:
        data = {}
        with patch("builtins.print") as mock_print:
            self.pau.apply_gold_coin_mask(data)
        output = " ".join(str(a) for a in mock_print.call_args[0])
        self.assertIn("unknown", output)


class TestStreamToInterface(unittest.TestCase):
    """Verifica stream_to_interface con distintos gestos."""

    def setUp(self) -> None:
        self.pau = PauAdvancedExpressions()

    def test_stream_to_interface_prints_engine_and_gesture(self) -> None:
        data = {"type": "divine_transformation"}
        with patch("builtins.print") as mock_print:
            self.pau.stream_to_interface(data)
        output = " ".join(str(a) for a in mock_print.call_args[0])
        self.assertIn("HighFidelity_Render", output)
        self.assertIn("divine_transformation", output)

    def test_stream_to_interface_handles_missing_type(self) -> None:
        data = {}
        with patch("builtins.print") as mock_print:
            self.pau.stream_to_interface(data)
        output = " ".join(str(a) for a in mock_print.call_args[0])
        self.assertIn("unknown", output)


class TestSequenceGesturesContinuous(unittest.TestCase):
    """Verifica que sequence_gestures_continuous recorre los 10 gestos y llama los 3 métodos."""

    EXPECTED_GESTURES = [
        "charismatic_speech",
        "sophisticated_laugh",
        "authority_nod",
        "puzzled_interest",
        "regal_stare",
        "warm_greeting",
        "fashion_critique_focus",
        "success_celebration",
        "silent_approval",
        "divine_transformation",
    ]

    def setUp(self) -> None:
        self.pau = PauAdvancedExpressions()

    def test_calls_all_three_methods_per_gesture(self) -> None:
        load_calls = []
        mask_calls = []
        stream_calls = []

        self.pau.load_pau_asset = lambda d: load_calls.append(d)
        self.pau.apply_gold_coin_mask = lambda d: mask_calls.append(d)
        self.pau.stream_to_interface = lambda d: stream_calls.append(d)

        self.pau.sequence_gestures_continuous()

        self.assertEqual(len(load_calls), 10)
        self.assertEqual(len(mask_calls), 10)
        self.assertEqual(len(stream_calls), 10)

    def test_all_gesture_types_present(self) -> None:
        captured = []
        self.pau.load_pau_asset = lambda d: captured.append(d.get("type"))
        self.pau.apply_gold_coin_mask = lambda d: None
        self.pau.stream_to_interface = lambda d: None

        self.pau.sequence_gestures_continuous()

        self.assertEqual(captured, self.EXPECTED_GESTURES)

    def test_methods_called_in_order_per_gesture(self) -> None:
        order: list[str] = []
        self.pau.load_pau_asset = lambda d: order.append(f"load:{d['type']}")
        self.pau.apply_gold_coin_mask = lambda d: order.append(f"mask:{d['type']}")
        self.pau.stream_to_interface = lambda d: order.append(f"stream:{d['type']}")

        self.pau.sequence_gestures_continuous()

        for i, gesture in enumerate(self.EXPECTED_GESTURES):
            base = i * 3
            self.assertEqual(order[base], f"load:{gesture}")
            self.assertEqual(order[base + 1], f"mask:{gesture}")
            self.assertEqual(order[base + 2], f"stream:{gesture}")


if __name__ == "__main__":
    unittest.main()
