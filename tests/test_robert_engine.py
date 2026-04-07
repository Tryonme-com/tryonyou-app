"""Tests for RobertEngineV10 — Robert Physics Engine."""

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
    """Module 0: verify the five Pilot Collection looks are correctly configured."""

    def setUp(self) -> None:
        self.engine = RobertEngineV10()

    def test_five_looks_present(self) -> None:
        self.assertEqual(len(self.engine.PILOT_COLLECTION), 5)

    def test_all_look_ids_present(self) -> None:
        for key in ("eg0", "eg1", "eg2", "eg3", "eg4"):
            self.assertIn(key, self.engine.PILOT_COLLECTION)

    def test_silk_haussmann_name(self) -> None:
        self.assertEqual(self.engine.PILOT_COLLECTION["eg0"]["name"], "Silk Haussmann")

    def test_business_elite_name(self) -> None:
        self.assertEqual(self.engine.PILOT_COLLECTION["eg1"]["name"], "Business Elite")

    def test_velvet_night_name(self) -> None:
        self.assertEqual(self.engine.PILOT_COLLECTION["eg2"]["name"], "Velvet Night")

    def test_tech_shell_name(self) -> None:
        self.assertEqual(self.engine.PILOT_COLLECTION["eg3"]["name"], "Tech Shell")

    def test_cashmere_cloud_name(self) -> None:
        self.assertEqual(self.engine.PILOT_COLLECTION["eg4"]["name"], "Cashmere Cloud")

    def test_required_fabric_keys(self) -> None:
        required = {"name", "drape", "gsm", "elasticity", "recovery", "friction"}
        for look_id, fabric in self.engine.PILOT_COLLECTION.items():
            with self.subTest(look_id=look_id):
                self.assertTrue(required.issubset(fabric.keys()))


class TestCalculatePhysics(unittest.TestCase):
    """Module 1: fabric physics — Lafayette factor, gravity stretch, breathing."""

    def setUp(self) -> None:
        self.engine = RobertEngineV10()

    def test_garment_width_greater_than_shoulder(self) -> None:
        fabric = self.engine.PILOT_COLLECTION["eg0"]
        w, _ = self.engine._calculate_physics(fabric, 450, 800, 0)
        self.assertGreater(w, 450)

    def test_gravity_height_at_least_torso(self) -> None:
        fabric = self.engine.PILOT_COLLECTION["eg0"]
        _, h = self.engine._calculate_physics(fabric, 450, 800, 0)
        self.assertGreaterEqual(h, 800)

    def test_heavy_fabric_stretches_more_than_light(self) -> None:
        light = self.engine.PILOT_COLLECTION["eg0"]  # gsm=60
        heavy = self.engine.PILOT_COLLECTION["eg2"]  # gsm=320
        _, h_light = self.engine._calculate_physics(light, 450, 800, 0)
        _, h_heavy = self.engine._calculate_physics(heavy, 450, 800, 0)
        self.assertGreater(h_heavy, h_light)

    def test_breathing_oscillates_with_time(self) -> None:
        fabric = self.engine.PILOT_COLLECTION["eg4"]  # elasticity=15
        w0, _ = self.engine._calculate_physics(fabric, 450, 800, 0)
        # At now_ms = π/0.0015 ≈ 2094 the sin peaks; results must differ
        w1, _ = self.engine._calculate_physics(fabric, 450, 800, 2094)
        self.assertNotAlmostEqual(w0, w1, places=3)

    def test_weight_norm_clamped_to_one_for_very_heavy(self) -> None:
        # GSM well above 400 should clamp weight_norm at 1.0 (15% max elongation)
        fabric = {"drape": 0.5, "gsm": 1000, "elasticity": 0, "recovery": 90, "friction": 0.5}
        _, h = self.engine._calculate_physics(fabric, 100, 500, 0)
        self.assertAlmostEqual(h, 500 * 1.15, places=5)

    def test_weight_norm_clamped_to_zero_for_very_light(self) -> None:
        # GSM at or below 50 should clamp weight_norm at 0.0 (no elongation)
        fabric = {"drape": 0.5, "gsm": 50, "elasticity": 0, "recovery": 90, "friction": 0.5}
        _, h = self.engine._calculate_physics(fabric, 100, 500, 0)
        self.assertAlmostEqual(h, 500.0, places=5)


class TestGetVisualEffects(unittest.TestCase):
    """Module 2: visual effects — highlight, folds, scan line."""

    def setUp(self) -> None:
        self.engine = RobertEngineV10()

    def test_silk_has_highlight(self) -> None:
        fabric = self.engine.PILOT_COLLECTION["eg0"]  # friction=0.22
        fx = self.engine._get_visual_effects(fabric, 900, 800, 0, 88)
        self.assertIn("highlight", fx)

    def test_high_friction_no_highlight(self) -> None:
        fabric = self.engine.PILOT_COLLECTION["eg1"]  # friction=0.65
        fx = self.engine._get_visual_effects(fabric, 900, 800, 0, 88)
        self.assertNotIn("highlight", fx)

    def test_low_drape_three_folds(self) -> None:
        fabric = self.engine.PILOT_COLLECTION["eg3"]  # drape=0.15
        fx = self.engine._get_visual_effects(fabric, 900, 800, 0, 88)
        self.assertEqual(len(fx["folds"]), 3)

    def test_high_drape_five_folds(self) -> None:
        fabric = self.engine.PILOT_COLLECTION["eg0"]  # drape=0.85
        fx = self.engine._get_visual_effects(fabric, 900, 800, 0, 88)
        self.assertEqual(len(fx["folds"]), 5)

    def test_scan_line_present_when_fit_score_in_range(self) -> None:
        fabric = self.engine.PILOT_COLLECTION["eg0"]
        fx = self.engine._get_visual_effects(fabric, 900, 800, 0, 50)
        self.assertIn("scan_line_y", fx)

    def test_scan_line_absent_when_fit_score_zero(self) -> None:
        fabric = self.engine.PILOT_COLLECTION["eg0"]
        fx = self.engine._get_visual_effects(fabric, 900, 800, 0, 0)
        self.assertNotIn("scan_line_y", fx)

    def test_scan_line_absent_when_fit_score_95(self) -> None:
        fabric = self.engine.PILOT_COLLECTION["eg0"]
        fx = self.engine._get_visual_effects(fabric, 900, 800, 0, 95)
        self.assertNotIn("scan_line_y", fx)

    def test_scan_line_absent_when_fit_score_100(self) -> None:
        fabric = self.engine.PILOT_COLLECTION["eg0"]
        fx = self.engine._get_visual_effects(fabric, 900, 800, 0, 100)
        self.assertNotIn("scan_line_y", fx)

    def test_fold_alpha_formula(self) -> None:
        fabric = self.engine.PILOT_COLLECTION["eg3"]  # drape=0.15
        fx = self.engine._get_visual_effects(fabric, 900, 800, 0, 50)
        expected_alpha = 0.05 + (0.15 * 0.1)
        for fold in fx["folds"]:
            self.assertAlmostEqual(fold["alpha"], expected_alpha, places=6)


class TestGetAccessoryRender(unittest.TestCase):
    """Module 3: accessory rendering — body-anchored vs floating."""

    def setUp(self) -> None:
        self.engine = RobertEngineV10()

    def test_body_anchor_mode(self) -> None:
        result = self.engine.get_accessory_render(True, 450, 900, 1080, 1.5)
        self.assertEqual(result["mode"], "BodyAnchor")

    def test_floating_mode(self) -> None:
        result = self.engine.get_accessory_render(False, 450, 900, 1080, 1.5)
        self.assertEqual(result["mode"], "FloatingExhibition")

    def test_alpha_always_088(self) -> None:
        for has_body in (True, False):
            with self.subTest(has_body=has_body):
                result = self.engine.get_accessory_render(has_body, 450, 900, 1080, 1.5)
                self.assertAlmostEqual(result["alpha"], 0.88)

    def test_body_anchor_width(self) -> None:
        result = self.engine.get_accessory_render(True, 450, 900, 1080, 1.5)
        self.assertAlmostEqual(result["width"], 450 * 0.8)

    def test_floating_width_18_percent_canvas(self) -> None:
        result = self.engine.get_accessory_render(False, 450, 900, 1080, 1.5)
        self.assertAlmostEqual(result["width"], 1080 * 0.18)

    def test_height_respects_aspect_ratio(self) -> None:
        result = self.engine.get_accessory_render(True, 450, 900, 1080, 2.0)
        self.assertAlmostEqual(result["height"], result["width"] * 2.0)


class TestProcessFrame(unittest.TestCase):
    """Module 4: process_frame — full pipeline + metadata."""

    def setUp(self) -> None:
        self.engine = RobertEngineV10()

    def test_returns_render_and_metadata(self) -> None:
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

    def test_recovery_stable_for_eg0(self) -> None:
        result = self.engine.process_frame("eg0", 450, 900, 88, {"w": 1080, "h": 1920})
        self.assertEqual(result["metadata"]["recovery_status"], "STABLE")

    def test_recovery_degraded_for_eg1(self) -> None:
        # eg1 recovery=80, which is <= 85 → DEGRADED
        result = self.engine.process_frame("eg1", 450, 900, 88, {"w": 1080, "h": 1920})
        self.assertEqual(result["metadata"]["recovery_status"], "DEGRADED")

    def test_unknown_look_falls_back_to_eg0(self) -> None:
        result = self.engine.process_frame("unknown", 450, 900, 88, {"w": 1080, "h": 1920})
        # eg0 recovery=95 → STABLE
        self.assertEqual(result["metadata"]["recovery_status"], "STABLE")

    def test_scan_line_active_when_fit_score_88(self) -> None:
        result = self.engine.process_frame("eg0", 450, 900, 88, {"w": 1080, "h": 1920})
        self.assertIn("scan_line_y", result["render"]["effects"])


if __name__ == "__main__":
    unittest.main()
