"""Tests for RobertEngineV10 — fabric physics and rendering (unittest)."""

from __future__ import annotations

import math
import os
import sys
import unittest

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
_API = os.path.join(_ROOT, "api")
for _p in (_ROOT, _API):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from robert_engine import RobertEngineV10


class TestPilotCollection(unittest.TestCase):
    """Validate the built-in collection of 5 pilot looks."""

    def setUp(self) -> None:
        self.engine = RobertEngineV10()

    def test_collection_has_five_looks(self) -> None:
        self.assertEqual(len(self.engine.PILOT_COLLECTION), 5)

    def test_all_look_ids_present(self) -> None:
        for key in ("eg0", "eg1", "eg2", "eg3", "eg4"):
            self.assertIn(key, self.engine.PILOT_COLLECTION)

    def test_eg0_name(self) -> None:
        self.assertEqual(self.engine.PILOT_COLLECTION["eg0"]["name"], "Silk Haussmann")

    def test_eg1_name(self) -> None:
        self.assertEqual(self.engine.PILOT_COLLECTION["eg1"]["name"], "Business Elite")

    def test_eg2_name(self) -> None:
        self.assertEqual(self.engine.PILOT_COLLECTION["eg2"]["name"], "Velvet Night")

    def test_eg3_name(self) -> None:
        self.assertEqual(self.engine.PILOT_COLLECTION["eg3"]["name"], "Tech Shell")

    def test_eg4_name(self) -> None:
        self.assertEqual(self.engine.PILOT_COLLECTION["eg4"]["name"], "Cashmere Cloud")

    def test_fabric_fields_present(self) -> None:
        required = {"name", "drape", "gsm", "elasticity", "recovery", "friction"}
        for look_id, fabric in self.engine.PILOT_COLLECTION.items():
            with self.subTest(look_id=look_id):
                self.assertEqual(required, set(fabric.keys()))


class TestCalculatePhysics(unittest.TestCase):
    """Unit tests for _calculate_physics."""

    def setUp(self) -> None:
        self.engine = RobertEngineV10()

    def test_returns_two_floats(self) -> None:
        fabric = self.engine.PILOT_COLLECTION["eg0"]
        result = self.engine._calculate_physics(fabric, 450, 800, 0)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)

    def test_garment_width_positive(self) -> None:
        fabric = self.engine.PILOT_COLLECTION["eg1"]
        w, h = self.engine._calculate_physics(fabric, 400, 700, 1000)
        self.assertGreater(w, 0)

    def test_gravity_height_positive(self) -> None:
        fabric = self.engine.PILOT_COLLECTION["eg1"]
        w, h = self.engine._calculate_physics(fabric, 400, 700, 1000)
        self.assertGreater(h, 0)

    def test_heavy_fabric_taller_than_light(self) -> None:
        """Heavier fabric (high gsm) should produce a taller garment."""
        light = self.engine.PILOT_COLLECTION["eg0"]   # gsm=60
        heavy = self.engine.PILOT_COLLECTION["eg2"]   # gsm=320
        _, h_light = self.engine._calculate_physics(light, 450, 800, 0)
        _, h_heavy = self.engine._calculate_physics(heavy, 450, 800, 0)
        self.assertGreater(h_heavy, h_light)

    def test_lafayette_factor_applied(self) -> None:
        """Garment width must be wider than raw shoulder width (lafayette_f > 1)."""
        fabric = self.engine.PILOT_COLLECTION["eg3"]
        shoulder_w = 300.0
        w, _ = self.engine._calculate_physics(fabric, shoulder_w, 600, 0)
        self.assertGreater(w, shoulder_w)


class TestGetVisualEffects(unittest.TestCase):
    """Unit tests for _get_visual_effects."""

    def setUp(self) -> None:
        self.engine = RobertEngineV10()

    def test_silk_highlight_present_for_low_friction(self) -> None:
        """Fabrics with friction < 0.35 must emit a highlight effect."""
        fabric = self.engine.PILOT_COLLECTION["eg0"]  # friction=0.22
        fx = self.engine._get_visual_effects(fabric, 900, 800, 0, 88)
        self.assertIn("highlight", fx)

    def test_silk_highlight_absent_for_high_friction(self) -> None:
        """Fabrics with friction >= 0.35 must NOT emit a highlight effect."""
        fabric = self.engine.PILOT_COLLECTION["eg1"]  # friction=0.65
        fx = self.engine._get_visual_effects(fabric, 900, 800, 0, 88)
        self.assertNotIn("highlight", fx)

    def test_folds_present_always(self) -> None:
        for look_id, fabric in self.engine.PILOT_COLLECTION.items():
            with self.subTest(look_id=look_id):
                fx = self.engine._get_visual_effects(fabric, 900, 800, 0, 50)
                self.assertIn("folds", fx)

    def test_folds_count_low_drape(self) -> None:
        """drape < 0.5 → 3 folds."""
        fabric = self.engine.PILOT_COLLECTION["eg1"]  # drape=0.35
        fx = self.engine._get_visual_effects(fabric, 900, 800, 0, 50)
        self.assertEqual(len(fx["folds"]), 3)

    def test_folds_count_high_drape(self) -> None:
        """drape >= 0.5 → 5 folds."""
        fabric = self.engine.PILOT_COLLECTION["eg0"]  # drape=0.85
        fx = self.engine._get_visual_effects(fabric, 900, 800, 0, 50)
        self.assertEqual(len(fx["folds"]), 5)

    def test_scan_line_active_when_fit_score_below_95(self) -> None:
        fabric = self.engine.PILOT_COLLECTION["eg0"]
        fx = self.engine._get_visual_effects(fabric, 900, 800, 1000, 88)
        self.assertIn("scan_line_y", fx)

    def test_scan_line_absent_when_fit_score_is_zero(self) -> None:
        fabric = self.engine.PILOT_COLLECTION["eg0"]
        fx = self.engine._get_visual_effects(fabric, 900, 800, 1000, 0)
        self.assertNotIn("scan_line_y", fx)

    def test_scan_line_absent_when_fit_score_is_95(self) -> None:
        fabric = self.engine.PILOT_COLLECTION["eg0"]
        fx = self.engine._get_visual_effects(fabric, 900, 800, 1000, 95)
        self.assertNotIn("scan_line_y", fx)

    def test_scan_line_within_garment_height(self) -> None:
        fabric = self.engine.PILOT_COLLECTION["eg0"]
        gravity_h = 800.0
        fx = self.engine._get_visual_effects(fabric, 900, gravity_h, 1000, 50)
        self.assertLessEqual(fx["scan_line_y"], gravity_h)
        self.assertGreaterEqual(fx["scan_line_y"], 0.0)


class TestGetAccessoryRender(unittest.TestCase):
    """Unit tests for get_accessory_render."""

    def setUp(self) -> None:
        self.engine = RobertEngineV10()

    def test_alpha_always_088(self) -> None:
        for has_body in (True, False):
            with self.subTest(has_body=has_body):
                result = self.engine.get_accessory_render(has_body, 450, 900, 1080, 1.5)
                self.assertAlmostEqual(result["alpha"], 0.88)

    def test_mode_body_anchor(self) -> None:
        result = self.engine.get_accessory_render(True, 450, 900, 1080, 1.5)
        self.assertEqual(result["mode"], "BodyAnchor")

    def test_mode_floating_exhibition(self) -> None:
        result = self.engine.get_accessory_render(False, 450, 900, 1080, 1.5)
        self.assertEqual(result["mode"], "FloatingExhibition")

    def test_width_body_anchor_is_80_percent_shoulder(self) -> None:
        result = self.engine.get_accessory_render(True, 400, 900, 1080, 1.0)
        self.assertAlmostEqual(result["width"], 320.0)

    def test_width_floating_is_18_percent_canvas(self) -> None:
        result = self.engine.get_accessory_render(False, 400, 900, 1080, 1.0)
        self.assertAlmostEqual(result["width"], 1080 * 0.18)

    def test_height_equals_width_times_aspect_ratio(self) -> None:
        ar = 1.33
        result = self.engine.get_accessory_render(True, 400, 900, 1080, ar)
        self.assertAlmostEqual(result["height"], result["width"] * ar)


class TestProcessFrame(unittest.TestCase):
    """Integration tests for process_frame."""

    def setUp(self) -> None:
        self.engine = RobertEngineV10()

    def test_returns_render_and_metadata_keys(self) -> None:
        result = self.engine.process_frame("eg0", 450, 900, 88, {"w": 1080, "h": 1920})
        self.assertIn("render", result)
        self.assertIn("metadata", result)

    def test_render_has_width_height_effects(self) -> None:
        result = self.engine.process_frame("eg0", 450, 900, 88, {"w": 1080, "h": 1920})
        render = result["render"]
        self.assertIn("width", render)
        self.assertIn("height", render)
        self.assertIn("effects", render)

    def test_patent_in_metadata(self) -> None:
        result = self.engine.process_frame("eg0", 450, 900, 88, {"w": 1080, "h": 1920})
        self.assertEqual(result["metadata"]["patent"], "PCT/EP2025/067317")

    def test_claim_in_metadata(self) -> None:
        result = self.engine.process_frame("eg0", 450, 900, 88, {"w": 1080, "h": 1920})
        self.assertEqual(result["metadata"]["claim"], "22_PROTECTED")

    def test_recovery_status_stable_high_recovery(self) -> None:
        """eg0 has recovery=95 → STABLE."""
        result = self.engine.process_frame("eg0", 450, 900, 88, {"w": 1080, "h": 1920})
        self.assertEqual(result["metadata"]["recovery_status"], "STABLE")

    def test_recovery_status_degraded_low_recovery(self) -> None:
        """eg1 has recovery=80 → DEGRADED."""
        result = self.engine.process_frame("eg1", 450, 900, 88, {"w": 1080, "h": 1920})
        self.assertEqual(result["metadata"]["recovery_status"], "DEGRADED")

    def test_unknown_look_falls_back_to_eg0(self) -> None:
        """An unknown look_id must silently fall back to eg0."""
        result = self.engine.process_frame("unknown", 450, 900, 88, {"w": 1080, "h": 1920})
        self.assertEqual(result["metadata"]["recovery_status"], "STABLE")

    def test_render_dimensions_positive(self) -> None:
        result = self.engine.process_frame("eg2", 450, 900, 50, {"w": 1080, "h": 1920})
        self.assertGreater(result["render"]["width"], 0)
        self.assertGreater(result["render"]["height"], 0)


if __name__ == "__main__":
    unittest.main()
