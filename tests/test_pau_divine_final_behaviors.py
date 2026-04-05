"""Tests para PauDivineFinalBehaviors (pau_divine_final_behaviors.py).

@CertezaAbsoluta @lo+erestu PCT/EP2025/067317
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""

from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import MagicMock, call, patch

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from pau_divine_final_behaviors import PauDivineFinalBehaviors


class TestPauDivineFinalBehaviorsInit(unittest.TestCase):
    """Verifica los atributos iniciales del avatar."""

    def setUp(self) -> None:
        self.pau = PauDivineFinalBehaviors()

    def test_reference_is_white_peacock(self) -> None:
        self.assertEqual(self.pau.reference, "White_Peacock_Natural_r5vr2He")

    def test_ui_layer_is_golden_coin(self) -> None:
        self.assertEqual(self.pau.ui_layer, "Golden_Coin_Million_Dollar")

    def test_philosophy_is_fin_de_las_tallas(self) -> None:
        self.assertEqual(self.pau.philosophy, "El_Fin_De_Las_Tallas")


class TestExecuteAbsoluteGestures(unittest.TestCase):
    """Verifica la secuencia completa de gestos absolutos."""

    def setUp(self) -> None:
        self.pau = PauDivineFinalBehaviors()

    def test_pipeline_called_for_each_gesture(self) -> None:
        with (
            patch.object(self.pau, "buffer_raw_pau_asset") as mock_buffer,
            patch.object(self.pau, "apply_million_dollar_mask") as mock_mask,
            patch.object(self.pau, "render_to_v10_2_interface") as mock_render,
        ):
            self.pau.execute_absolute_gestures()

        self.assertEqual(mock_buffer.call_count, 20)
        self.assertEqual(mock_mask.call_count, 20)
        self.assertEqual(mock_render.call_count, 20)

    def test_pipeline_order_per_gesture(self) -> None:
        """buffer → mask → render must be called in that order for every step."""
        call_order: list[str] = []

        with (
            patch.object(self.pau, "buffer_raw_pau_asset", side_effect=lambda d: call_order.append("buffer")),
            patch.object(self.pau, "apply_million_dollar_mask", side_effect=lambda d: call_order.append("mask")),
            patch.object(self.pau, "render_to_v10_2_interface", side_effect=lambda d: call_order.append("render")),
        ):
            self.pau.execute_absolute_gestures()

        expected = ["buffer", "mask", "render"] * 20
        self.assertEqual(call_order, expected)

    def test_first_gesture_is_majestic_vocal_sync(self) -> None:
        received: list[dict] = []
        with patch.object(self.pau, "buffer_raw_pau_asset", side_effect=received.append):
            with patch.object(self.pau, "apply_million_dollar_mask"):
                with patch.object(self.pau, "render_to_v10_2_interface"):
                    self.pau.execute_absolute_gestures()

        self.assertEqual(received[0]["gesture"], "majestic_vocal_sync")

    def test_last_gesture_is_reawakening(self) -> None:
        received: list[dict] = []
        with patch.object(self.pau, "buffer_raw_pau_asset", side_effect=received.append):
            with patch.object(self.pau, "apply_million_dollar_mask"):
                with patch.object(self.pau, "render_to_v10_2_interface"):
                    self.pau.execute_absolute_gestures()

        self.assertEqual(received[-1]["gesture"], "reawakening")

    def test_royal_dismissal_of_sizes_present(self) -> None:
        received: list[dict] = []
        with patch.object(self.pau, "buffer_raw_pau_asset", side_effect=received.append):
            with patch.object(self.pau, "apply_million_dollar_mask"):
                with patch.object(self.pau, "render_to_v10_2_interface"):
                    self.pau.execute_absolute_gestures()

        names = [s["gesture"] for s in received]
        self.assertIn("royal_dismissal_of_sizes", names)

    def test_all_gestures_have_gesture_key(self) -> None:
        received: list[dict] = []
        with patch.object(self.pau, "buffer_raw_pau_asset", side_effect=received.append):
            with patch.object(self.pau, "apply_million_dollar_mask"):
                with patch.object(self.pau, "render_to_v10_2_interface"):
                    self.pau.execute_absolute_gestures()

        for step in received:
            self.assertIn("gesture", step)


class TestPipelineMethods(unittest.TestCase):
    """Verifica que los métodos del pipeline no lanzan excepciones."""

    def setUp(self) -> None:
        self.pau = PauDivineFinalBehaviors()

    def test_buffer_raw_pau_asset_accepts_dict(self) -> None:
        self.pau.buffer_raw_pau_asset({"gesture": "test"})

    def test_apply_million_dollar_mask_accepts_dict(self) -> None:
        self.pau.apply_million_dollar_mask({"gesture": "test"})

    def test_render_to_v10_2_interface_accepts_dict(self) -> None:
        self.pau.render_to_v10_2_interface({"gesture": "test"})

    def test_execute_absolute_gestures_runs_without_error(self) -> None:
        self.pau.execute_absolute_gestures()


if __name__ == "__main__":
    unittest.main()
