"""Tests para el Robert Physics Engine — TRYONYOU V10."""

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

from robert_engine import (
    PATENT_ID,
    PILOT_FABRIC_PHYSICS,
    RobertEngine,
    _FIT_PERFECT_THRESHOLD,
    _SHINY_FRICTION_THRESHOLD,
)


class TestRobertEngineConstants(unittest.TestCase):
    def test_patent_id(self) -> None:
        self.assertEqual(PATENT_ID, "PCT/EP2025/067317")

    def test_fit_perfect_threshold(self) -> None:
        self.assertEqual(_FIT_PERFECT_THRESHOLD, 95)

    def test_shiny_threshold(self) -> None:
        self.assertAlmostEqual(_SHINY_FRICTION_THRESHOLD, 0.35)

    def test_pilot_fabric_physics_has_silk_haussmann(self) -> None:
        self.assertIn("silk_haussmann", PILOT_FABRIC_PHYSICS)

    def test_pilot_fabric_physics_has_business_elite(self) -> None:
        self.assertIn("business_elite", PILOT_FABRIC_PHYSICS)


class TestLafayetteFactor(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = RobertEngine()

    def test_silk_haussmann_lafayette_factor(self) -> None:
        fabric = PILOT_FABRIC_PHYSICS["silk_haussmann"]
        # drapeCoefficient=0.85 → drape_pull=0.34 → 2.2 + (0.5 - 0.34) = 2.36
        result = self.engine.calculate_lafayette_factor(fabric)
        self.assertAlmostEqual(result, 2.36, places=6)

    def test_business_elite_lafayette_factor(self) -> None:
        fabric = PILOT_FABRIC_PHYSICS["business_elite"]
        # drapeCoefficient=0.35 → drape_pull=0.14 → 2.2 + (0.5 - 0.14) = 2.56
        result = self.engine.calculate_lafayette_factor(fabric)
        self.assertAlmostEqual(result, 2.56, places=6)

    def test_rigid_fabric_has_higher_factor_than_liquid(self) -> None:
        """Un tejido rígido produce silueta más ancha."""
        liquid = {"drapeCoefficient": 1.0}
        rigid = {"drapeCoefficient": 0.0}
        self.assertGreater(
            self.engine.calculate_lafayette_factor(rigid),
            self.engine.calculate_lafayette_factor(liquid),
        )


class TestGravityStretch(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = RobertEngine()

    def test_light_fabric_minimal_stretch(self) -> None:
        # silk_haussmann: GSM=60, weight_norm=(60-50)/350≈0.0286, stretch≈+0.43%
        fabric = PILOT_FABRIC_PHYSICS["silk_haussmann"]
        result = self.engine.calculate_gravity_stretch(fabric, 800)
        self.assertAlmostEqual(result, 800 * (1.0 + (10 / 350) * 0.15), places=4)

    def test_heavy_fabric_more_stretch(self) -> None:
        fabric = PILOT_FABRIC_PHYSICS["business_elite"]
        light = PILOT_FABRIC_PHYSICS["silk_haussmann"]
        self.assertGreater(
            self.engine.calculate_gravity_stretch(fabric, 800),
            self.engine.calculate_gravity_stretch(light, 800),
        )

    def test_max_stretch_capped_at_15_pct(self) -> None:
        """Un tejido extremadamente pesado no supera el 15 % de estiramiento."""
        very_heavy = {"weightGSM": 9999}
        result = self.engine.calculate_gravity_stretch(very_heavy, 1000)
        self.assertAlmostEqual(result, 1000 * 1.15, places=6)

    def test_very_light_fabric_no_negative_stretch(self) -> None:
        """Un tejido por debajo del mínimo definido no encoge la prenda."""
        very_light = {"weightGSM": 0}
        result = self.engine.calculate_gravity_stretch(very_light, 1000)
        self.assertAlmostEqual(result, 1000.0, places=6)


class TestDynamicAlpha(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = RobertEngine()
        self.fabric = PILOT_FABRIC_PHYSICS["silk_haussmann"]

    def test_perfect_fit_alpha_is_095(self) -> None:
        # fit=100 ≥ 95, pulse=0 → alpha=0.95
        alpha = self.engine.calculate_dynamic_alpha(100, self.fabric, timestamp=0)
        self.assertAlmostEqual(alpha, 0.95, places=6)

    def test_exact_threshold_fit_alpha_is_095(self) -> None:
        alpha = self.engine.calculate_dynamic_alpha(95, self.fabric, timestamp=0)
        self.assertAlmostEqual(alpha, 0.95, places=6)

    def test_imperfect_fit_base_alpha_is_085(self) -> None:
        # fit=88 < 95, timestamp=0 → sin(0)=0 → pulse=0 → alpha=0.85
        alpha = self.engine.calculate_dynamic_alpha(88, self.fabric, timestamp=0)
        self.assertAlmostEqual(alpha, 0.85, places=6)

    def test_alpha_floor_is_065(self) -> None:
        # Pulso negativo máximo: base=0.85, pulse=-0.1 → clamp → 0.75, not below floor
        # Force pulse= -0.1 → timestamp where sin = -1: π*1000/(2*0.002)= π/0.004
        # sin(t*0.002)=-1 → t*0.002 = -π/2 + 2πk → t = (-π/2)/0.002 = -785.4...
        alpha = self.engine.calculate_dynamic_alpha(50, self.fabric, timestamp=-785.4)
        self.assertGreaterEqual(alpha, 0.65)

    def test_alpha_ceiling_is_095(self) -> None:
        alpha = self.engine.calculate_dynamic_alpha(100, self.fabric, timestamp=1000)
        self.assertLessEqual(alpha, 0.95)

    def test_timestamp_defaults_to_now(self) -> None:
        """Sin timestamp explícito la función no lanza error."""
        alpha = self.engine.calculate_dynamic_alpha(88, self.fabric)
        self.assertGreaterEqual(alpha, 0.65)
        self.assertLessEqual(alpha, 0.95)


class TestGetRenderMetrics(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = RobertEngine()

    def test_unknown_fabric_returns_none(self) -> None:
        result = self.engine.get_render_metrics("nonexistent_fabric", 450, 800, 88)
        self.assertIsNone(result)

    def test_silk_haussmann_metrics_keys(self) -> None:
        result = self.engine.get_render_metrics("silk_haussmann", 450, 800, 88)
        self.assertIsNotNone(result)
        for key in ("width", "height", "alpha", "is_shiny", "is_scanning", "patent_id"):
            self.assertIn(key, result)

    def test_silk_haussmann_width(self) -> None:
        # shoulder=450, lafayette_factor=2.36
        result = self.engine.get_render_metrics("silk_haussmann", 450, 800, 88)
        self.assertAlmostEqual(result["width"], 450 * 2.36, places=4)

    def test_silk_haussmann_is_shiny(self) -> None:
        # frictionCoefficient=0.22 < 0.35 → shiny
        result = self.engine.get_render_metrics("silk_haussmann", 450, 800, 88)
        self.assertTrue(result["is_shiny"])

    def test_business_elite_is_not_shiny(self) -> None:
        # frictionCoefficient=0.65 ≥ 0.35 → not shiny
        result = self.engine.get_render_metrics("business_elite", 450, 800, 88)
        self.assertFalse(result["is_shiny"])

    def test_imperfect_fit_is_scanning(self) -> None:
        result = self.engine.get_render_metrics("silk_haussmann", 450, 800, 88)
        self.assertTrue(result["is_scanning"])

    def test_perfect_fit_not_scanning(self) -> None:
        result = self.engine.get_render_metrics("silk_haussmann", 450, 800, 100)
        self.assertFalse(result["is_scanning"])

    def test_patent_id_present(self) -> None:
        result = self.engine.get_render_metrics("silk_haussmann", 450, 800, 88)
        self.assertEqual(result["patent_id"], "PCT/EP2025/067317")

    def test_height_greater_than_torso_for_heavy_fabric(self) -> None:
        result = self.engine.get_render_metrics("business_elite", 450, 800, 88)
        self.assertGreater(result["height"], 800)


class TestCustomFabricPhysics(unittest.TestCase):
    """Verifica que RobertEngine acepta colecciones de tejidos personalizadas."""

    def test_custom_fabric_returned(self) -> None:
        custom = {
            "test_fabric": {
                "drapeCoefficient": 0.5,
                "weightGSM": 200,
                "elasticityPct": 10,
                "frictionCoefficient": 0.40,
            }
        }
        engine = RobertEngine(fabric_physics=custom)
        result = engine.get_render_metrics("test_fabric", 400, 700, 90)
        self.assertIsNotNone(result)
        self.assertEqual(result["patent_id"], PATENT_ID)

    def test_original_fabric_not_in_custom_engine(self) -> None:
        custom = {
            "only_fabric": {
                "drapeCoefficient": 0.5,
                "weightGSM": 200,
                "elasticityPct": 10,
                "frictionCoefficient": 0.40,
            }
        }
        engine = RobertEngine(fabric_physics=custom)
        self.assertIsNone(engine.get_render_metrics("silk_haussmann", 450, 800, 88))


if __name__ == "__main__":
    unittest.main()
