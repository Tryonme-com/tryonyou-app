"""Tests for RobertEngineV10 — fabric physics engine."""

from __future__ import annotations

import os
import sys
import unittest

_API = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "api"))
if _API not in sys.path:
    sys.path.insert(0, _API)

from robert_engine import RobertEngineV10


class TestPilotCollection(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = RobertEngineV10()

    def test_five_looks_defined(self) -> None:
        self.assertEqual(len(self.engine.PILOT_COLLECTION), 5)

    def test_look_ids_present(self) -> None:
        for key in ("eg0", "eg1", "eg2", "eg3", "eg4"):
            self.assertIn(key, self.engine.PILOT_COLLECTION)

    def test_eg0_is_silk_haussmann(self) -> None:
        self.assertEqual(self.engine.PILOT_COLLECTION["eg0"]["name"], "Silk Haussmann")

    def test_fabric_fields_present(self) -> None:
        for fabric in self.engine.PILOT_COLLECTION.values():
            for field in ("name", "drape", "gsm", "elasticity", "recovery", "friction"):
                self.assertIn(field, fabric)


class TestCalculatePhysics(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = RobertEngineV10()

    def test_returns_two_floats(self) -> None:
        fabric = self.engine.PILOT_COLLECTION["eg0"]
        w, h = self.engine._calculate_physics(fabric, 450, 800, 0)
        self.assertIsInstance(w, float)
        self.assertIsInstance(h, float)

    def test_garment_width_positive(self) -> None:
        fabric = self.engine.PILOT_COLLECTION["eg1"]
        w, _ = self.engine._calculate_physics(fabric, 400, 700, 1000)
        self.assertGreater(w, 0)

    def test_gravity_stretch_increases_height(self) -> None:
        """Heavier fabrics (high gsm) should stretch the torso height."""
        fabric_light = self.engine.PILOT_COLLECTION["eg0"]  # gsm=60
        fabric_heavy = self.engine.PILOT_COLLECTION["eg2"]  # gsm=320
        torso_h = 800
        now_ms = 0
        _, h_light = self.engine._calculate_physics(fabric_light, 450, torso_h, now_ms)
        _, h_heavy = self.engine._calculate_physics(fabric_heavy, 450, torso_h, now_ms)
        self.assertGreater(h_heavy, h_light)

    def test_lafayette_factor_applied(self) -> None:
        fabric = self.engine.PILOT_COLLECTION["eg3"]  # drape=0.15
        w, _ = self.engine._calculate_physics(fabric, 100, 500, 0)
        # lafayette_f = 2.2 + (0.5 - 0.15*0.4) = 2.2 + (0.5 - 0.06) = 2.64
        # garment_w (no breathing) ≈ 100 * 2.64 = 264
        self.assertAlmostEqual(w, 100 * 2.64, delta=2.0)


class TestGetVisualEffects(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = RobertEngineV10()

    def test_silk_highlight_present_for_low_friction(self) -> None:
        fabric = self.engine.PILOT_COLLECTION["eg0"]  # friction=0.22 < 0.35
        fx = self.engine._get_visual_effects(fabric, 500, 800, 1000, 88)
        self.assertIn("highlight", fx)

    def test_no_highlight_for_high_friction(self) -> None:
        fabric = self.engine.PILOT_COLLECTION["eg1"]  # friction=0.65 > 0.35
        fx = self.engine._get_visual_effects(fabric, 500, 800, 1000, 88)
        self.assertNotIn("highlight", fx)

    def test_folds_count_low_drape(self) -> None:
        fabric = self.engine.PILOT_COLLECTION["eg3"]  # drape=0.15 < 0.5
        fx = self.engine._get_visual_effects(fabric, 500, 800, 1000, 88)
        self.assertEqual(len(fx["folds"]), 3)

    def test_folds_count_high_drape(self) -> None:
        fabric = self.engine.PILOT_COLLECTION["eg0"]  # drape=0.85 >= 0.5
        fx = self.engine._get_visual_effects(fabric, 500, 800, 1000, 88)
        self.assertEqual(len(fx["folds"]), 5)

    def test_scan_line_present_when_fit_incomplete(self) -> None:
        fabric = self.engine.PILOT_COLLECTION["eg0"]
        fx = self.engine._get_visual_effects(fabric, 500, 800, 1000, 88)
        self.assertIn("scan_line_y", fx)

    def test_scan_line_absent_when_fit_complete(self) -> None:
        fabric = self.engine.PILOT_COLLECTION["eg0"]
        fx = self.engine._get_visual_effects(fabric, 500, 800, 1000, 95)
        self.assertNotIn("scan_line_y", fx)

    def test_scan_line_absent_when_fit_zero(self) -> None:
        fabric = self.engine.PILOT_COLLECTION["eg0"]
        fx = self.engine._get_visual_effects(fabric, 500, 800, 1000, 0)
        self.assertNotIn("scan_line_y", fx)


class TestGetAccessoryRender(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = RobertEngineV10()

    def test_body_anchor_mode_when_body_present(self) -> None:
        result = self.engine.get_accessory_render(True, 450, 900, 1080, 1.2)
        self.assertEqual(result["mode"], "BodyAnchor")
        self.assertAlmostEqual(result["width"], 450 * 0.8)

    def test_floating_mode_when_no_body(self) -> None:
        result = self.engine.get_accessory_render(False, 450, 900, 1080, 1.2)
        self.assertEqual(result["mode"], "FloatingExhibition")
        self.assertAlmostEqual(result["width"], 1080 * 0.18)

    def test_alpha_always_088(self) -> None:
        r1 = self.engine.get_accessory_render(True, 450, 900, 1080, 1.2)
        r2 = self.engine.get_accessory_render(False, 450, 900, 1080, 1.2)
        self.assertAlmostEqual(r1["alpha"], 0.88)
        self.assertAlmostEqual(r2["alpha"], 0.88)

    def test_height_uses_aspect_ratio(self) -> None:
        result = self.engine.get_accessory_render(True, 400, 900, 1080, 2.0)
        self.assertAlmostEqual(result["height"], result["width"] * 2.0)


class TestProcessFrame(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = RobertEngineV10()
        self.canvas = {"w": 1080, "h": 1920}

    def test_returns_render_and_metadata(self) -> None:
        result = self.engine.process_frame("eg0", 450, 900, 88, self.canvas)
        self.assertIn("render", result)
        self.assertIn("metadata", result)

    def test_render_has_width_height_effects(self) -> None:
        result = self.engine.process_frame("eg0", 450, 900, 88, self.canvas)
        self.assertIn("width", result["render"])
        self.assertIn("height", result["render"])
        self.assertIn("effects", result["render"])

    def test_patent_in_metadata(self) -> None:
        result = self.engine.process_frame("eg0", 450, 900, 88, self.canvas)
        self.assertEqual(result["metadata"]["patent"], "PCT/EP2025/067317")

    def test_claim_in_metadata(self) -> None:
        result = self.engine.process_frame("eg0", 450, 900, 88, self.canvas)
        self.assertEqual(result["metadata"]["claim"], "22_PROTECTED")

    def test_recovery_stable_for_high_recovery_fabric(self) -> None:
        # eg0 recovery=95 > 85 → STABLE
        result = self.engine.process_frame("eg0", 450, 900, 88, self.canvas)
        self.assertEqual(result["metadata"]["recovery_status"], "STABLE")

    def test_recovery_degraded_for_low_recovery_fabric(self) -> None:
        # eg1 recovery=80 <= 85 → DEGRADED
        result = self.engine.process_frame("eg1", 450, 900, 88, self.canvas)
        self.assertEqual(result["metadata"]["recovery_status"], "DEGRADED")

    def test_unknown_look_id_falls_back_to_eg0(self) -> None:
        result = self.engine.process_frame("unknown", 450, 900, 88, self.canvas)
        # eg0 patent still signed
        self.assertEqual(result["metadata"]["patent"], "PCT/EP2025/067317")

    def test_all_five_looks_processable(self) -> None:
        for look_id in ("eg0", "eg1", "eg2", "eg3", "eg4"):
            result = self.engine.process_frame(look_id, 450, 900, 88, self.canvas)
            self.assertGreater(result["render"]["width"], 0)
            self.assertGreater(result["render"]["height"], 0)


if __name__ == "__main__":
    unittest.main()
