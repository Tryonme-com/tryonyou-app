"""Tests para get_accessory_metrics — posicionamiento automático de bolsos (Peacock_Core)."""

from __future__ import annotations

import os
import sys
import unittest

_API = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "api"))
if _API not in sys.path:
    sys.path.insert(0, _API)

from peacock_core import get_accessory_metrics


class TestGetAccessoryMetricsWithBody(unittest.TestCase):
    """Casos con hasBody=True: dimensiones y posición basadas en shoulderW e hipY."""

    def setUp(self) -> None:
        self.anchors = {
            "cx": 320.0,
            "shoulderW": 200.0,
            "hipY": 400.0,
            "hasBody": True,
        }
        self.canvas_dim = {"w": 640, "h": 960}
        self.img_ar = 1.5  # height / width

    def _metrics(self, img_ar: float | None = None) -> dict:
        return get_accessory_metrics(
            img_ar if img_ar is not None else self.img_ar,
            self.anchors,
            self.canvas_dim,
        )

    def test_bag_width_is_80pct_shoulder_width(self) -> None:
        m = self._metrics()
        self.assertAlmostEqual(m["w"], self.anchors["shoulderW"] * 0.8)

    def test_bag_height_derived_from_aspect_ratio(self) -> None:
        m = self._metrics()
        expected_h = (self.anchors["shoulderW"] * 0.8) * self.img_ar
        self.assertAlmostEqual(m["h"], expected_h)

    def test_bag_x_is_cx_plus_60pct_shoulder(self) -> None:
        m = self._metrics()
        expected_x = self.anchors["cx"] + self.anchors["shoulderW"] * 0.6
        self.assertAlmostEqual(m["x"], expected_x)

    def test_bag_y_is_hip_minus_30pct_height(self) -> None:
        m = self._metrics()
        bag_h = (self.anchors["shoulderW"] * 0.8) * self.img_ar
        expected_y = self.anchors["hipY"] - bag_h * 0.3
        self.assertAlmostEqual(m["y"], expected_y)

    def test_alpha_is_0_88(self) -> None:
        m = self._metrics()
        self.assertAlmostEqual(m["alpha"], 0.88)

    def test_returns_all_required_keys(self) -> None:
        m = self._metrics()
        for key in ("x", "y", "w", "h", "alpha"):
            self.assertIn(key, m)


class TestGetAccessoryMetricsWithoutBody(unittest.TestCase):
    """Casos con hasBody=False: dimensiones y posición basadas en canvas_dim."""

    def setUp(self) -> None:
        self.anchors = {
            "cx": 320.0,
            "shoulderW": 0.0,
            "hipY": 400.0,
            "hasBody": False,
        }
        self.canvas_dim = {"w": 640, "h": 960}
        self.img_ar = 1.2

    def _metrics(self) -> dict:
        return get_accessory_metrics(self.img_ar, self.anchors, self.canvas_dim)

    def test_bag_width_is_18pct_canvas_width(self) -> None:
        m = self._metrics()
        self.assertAlmostEqual(m["w"], self.canvas_dim["w"] * 0.18)

    def test_bag_height_derived_from_aspect_ratio(self) -> None:
        m = self._metrics()
        expected_h = self.canvas_dim["w"] * 0.18 * self.img_ar
        self.assertAlmostEqual(m["h"], expected_h)

    def test_bag_x_is_cx_plus_12pct_canvas_width(self) -> None:
        m = self._metrics()
        expected_x = self.anchors["cx"] + self.canvas_dim["w"] * 0.12
        self.assertAlmostEqual(m["x"], expected_x)

    def test_bag_y_is_hip_minus_30pct_height(self) -> None:
        m = self._metrics()
        bag_h = self.canvas_dim["w"] * 0.18 * self.img_ar
        expected_y = self.anchors["hipY"] - bag_h * 0.3
        self.assertAlmostEqual(m["y"], expected_y)

    def test_alpha_fixed_at_0_88(self) -> None:
        m = self._metrics()
        self.assertAlmostEqual(m["alpha"], 0.88)


class TestGetAccessoryMetricsEdgeCases(unittest.TestCase):
    """Casos extremos: aspect ratio cuadrado, cadera en origen, etc."""

    def test_square_image_height_equals_width(self) -> None:
        anchors = {"cx": 100.0, "shoulderW": 100.0, "hipY": 200.0, "hasBody": True}
        canvas_dim = {"w": 400, "h": 600}
        m = get_accessory_metrics(1.0, anchors, canvas_dim)
        self.assertAlmostEqual(m["w"], m["h"])

    def test_hip_at_zero_gives_negative_y_offset(self) -> None:
        anchors = {"cx": 200.0, "shoulderW": 150.0, "hipY": 0.0, "hasBody": True}
        canvas_dim = {"w": 640, "h": 960}
        m = get_accessory_metrics(2.0, anchors, canvas_dim)
        # bag_h = 150*0.8*2 = 240; bag_y = 0 - 240*0.3 = -72
        self.assertAlmostEqual(m["y"], -(150 * 0.8 * 2 * 0.3))

    def test_alpha_never_changes_with_any_input(self) -> None:
        for has_body in (True, False):
            for img_ar in (0.5, 1.0, 2.5):
                anchors = {
                    "cx": 300.0,
                    "shoulderW": 180.0,
                    "hipY": 350.0,
                    "hasBody": has_body,
                }
                m = get_accessory_metrics(img_ar, anchors, {"w": 600, "h": 800})
                self.assertAlmostEqual(
                    m["alpha"],
                    0.88,
                    msg=f"alpha mismatch for has_body={has_body}, img_ar={img_ar}",
                )


if __name__ == "__main__":
    unittest.main()
