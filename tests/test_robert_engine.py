"""Tests para el Robert Physics Engine — TRYONYOU Lafayette V10."""

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

from robert_engine import PATENT_ID, RobertEngine


class TestRobertEngineFabricCatalogue(unittest.TestCase):
    """El catálogo de tejidos piloto debe contener los tejidos esperados."""

    def setUp(self) -> None:
        self.engine = RobertEngine()

    def test_silk_haussmann_present(self) -> None:
        self.assertIn("silk_haussmann", self.engine.PILOT_FABRIC_PHYSICS)

    def test_business_elite_present(self) -> None:
        self.assertIn("business_elite", self.engine.PILOT_FABRIC_PHYSICS)

    def test_silk_haussmann_is_lightweight(self) -> None:
        fabric = self.engine.PILOT_FABRIC_PHYSICS["silk_haussmann"]
        self.assertEqual(fabric["weightGSM"], 60)

    def test_business_elite_is_heavy(self) -> None:
        fabric = self.engine.PILOT_FABRIC_PHYSICS["business_elite"]
        self.assertEqual(fabric["weightGSM"], 280)

    def test_silk_haussmann_high_drape(self) -> None:
        fabric = self.engine.PILOT_FABRIC_PHYSICS["silk_haussmann"]
        self.assertGreater(fabric["drapeCoefficient"], 0.8)

    def test_business_elite_low_drape(self) -> None:
        fabric = self.engine.PILOT_FABRIC_PHYSICS["business_elite"]
        self.assertLess(fabric["drapeCoefficient"], 0.4)


class TestCalculateLafayetteFactor(unittest.TestCase):
    """Lafayette Factor: amplitud de silueta según caída del tejido."""

    def setUp(self) -> None:
        self.engine = RobertEngine()

    def test_silk_lafayette_factor(self) -> None:
        fabric = self.engine.PILOT_FABRIC_PHYSICS["silk_haussmann"]
        # drape_pull = 0.85 * 0.4 = 0.34  →  2.2 + (0.5 - 0.34) = 2.36
        expected = 2.2 + (0.5 - 0.85 * 0.4)
        result = self.engine.calculate_lafayette_factor(fabric)
        self.assertAlmostEqual(result, expected, places=10)

    def test_business_elite_lafayette_factor(self) -> None:
        fabric = self.engine.PILOT_FABRIC_PHYSICS["business_elite"]
        # drape_pull = 0.35 * 0.4 = 0.14  →  2.2 + (0.5 - 0.14) = 2.56
        expected = 2.2 + (0.5 - 0.35 * 0.4)
        result = self.engine.calculate_lafayette_factor(fabric)
        self.assertAlmostEqual(result, expected, places=10)

    def test_high_drape_lower_factor_than_low_drape(self) -> None:
        """Un tejido más líquido debe tener un factor menor que uno rígido."""
        silk = self.engine.PILOT_FABRIC_PHYSICS["silk_haussmann"]
        elite = self.engine.PILOT_FABRIC_PHYSICS["business_elite"]
        self.assertLess(
            self.engine.calculate_lafayette_factor(silk),
            self.engine.calculate_lafayette_factor(elite),
        )

    def test_result_is_above_two(self) -> None:
        for fabric in self.engine.PILOT_FABRIC_PHYSICS.values():
            factor = self.engine.calculate_lafayette_factor(fabric)
            self.assertGreater(factor, 2.0)


class TestCalculateGravityStretch(unittest.TestCase):
    """Gravity Stretch: elongación por el peso del tejido (máx. 15 %)."""

    def setUp(self) -> None:
        self.engine = RobertEngine()
        self.torso_h = 800.0

    def test_minimum_gsm_no_stretch(self) -> None:
        """Un tejido de 50 GSM (mínimo) no añade estiramiento."""
        fabric = {"weightGSM": 50}
        result = self.engine.calculate_gravity_stretch(fabric, self.torso_h)
        self.assertAlmostEqual(result, self.torso_h, places=5)

    def test_below_minimum_gsm_clamped(self) -> None:
        """GSM por debajo del mínimo queda sujeto a 0 — sin estiramiento."""
        fabric = {"weightGSM": 0}
        result = self.engine.calculate_gravity_stretch(fabric, self.torso_h)
        self.assertAlmostEqual(result, self.torso_h, places=5)

    def test_maximum_gsm_fifteen_percent_stretch(self) -> None:
        """Un tejido de 400 GSM (máximo normalizado) alcanza el 15 %."""
        fabric = {"weightGSM": 400}
        result = self.engine.calculate_gravity_stretch(fabric, self.torso_h)
        self.assertAlmostEqual(result, self.torso_h * 1.15, places=5)

    def test_silk_stretch_less_than_business_elite(self) -> None:
        silk = self.engine.PILOT_FABRIC_PHYSICS["silk_haussmann"]
        elite = self.engine.PILOT_FABRIC_PHYSICS["business_elite"]
        self.assertLess(
            self.engine.calculate_gravity_stretch(silk, self.torso_h),
            self.engine.calculate_gravity_stretch(elite, self.torso_h),
        )

    def test_result_never_exceeds_fifteen_percent(self) -> None:
        for fabric in self.engine.PILOT_FABRIC_PHYSICS.values():
            result = self.engine.calculate_gravity_stretch(fabric, self.torso_h)
            self.assertLessEqual(result, self.torso_h * 1.15 + 1e-9)


class TestCalculateDynamicAlpha(unittest.TestCase):
    """Dynamic Alpha: transparencia y pulso de respiración del tejido."""

    def setUp(self) -> None:
        self.engine = RobertEngine()
        self.fabric = self.engine.PILOT_FABRIC_PHYSICS["silk_haussmann"]

    def test_perfect_fit_returns_095(self) -> None:
        alpha = self.engine.calculate_dynamic_alpha(95, self.fabric, timestamp=0.0)
        self.assertAlmostEqual(alpha, 0.95, places=5)

    def test_perfect_fit_above_threshold(self) -> None:
        alpha = self.engine.calculate_dynamic_alpha(100, self.fabric, timestamp=0.0)
        self.assertAlmostEqual(alpha, 0.95, places=5)

    def test_imperfect_fit_base_alpha_085(self) -> None:
        # timestamp=0 → sin(0) = 0 → pulse = 0 → result = 0.85
        alpha = self.engine.calculate_dynamic_alpha(88, self.fabric, timestamp=0.0)
        self.assertAlmostEqual(alpha, 0.85, places=5)

    def test_pulse_applied_when_fit_below_threshold(self) -> None:
        ts = 1000.0  # sin(1000 * 0.002) = sin(2) ≠ 0
        expected_pulse = math.sin(ts * 0.002) * 0.1
        expected = max(0.65, min(0.95, 0.85 + expected_pulse))
        result = self.engine.calculate_dynamic_alpha(88, self.fabric, timestamp=ts)
        self.assertAlmostEqual(result, expected, places=10)

    def test_alpha_clamped_to_floor(self) -> None:
        # Forzar un pulso muy negativo con un tejido dummy
        alpha = self.engine.calculate_dynamic_alpha(50, self.fabric, timestamp=785.0)
        self.assertGreaterEqual(alpha, 0.65)

    def test_alpha_clamped_to_ceil(self) -> None:
        alpha = self.engine.calculate_dynamic_alpha(88, self.fabric, timestamp=0.0)
        self.assertLessEqual(alpha, 0.95)

    def test_no_timestamp_uses_current_time(self) -> None:
        """Sin timestamp explícito la función debe devolver un valor válido."""
        alpha = self.engine.calculate_dynamic_alpha(88, self.fabric)
        self.assertGreaterEqual(alpha, 0.65)
        self.assertLessEqual(alpha, 0.95)


class TestGetRenderMetrics(unittest.TestCase):
    """get_render_metrics: salida completa del motor para el overlay."""

    def setUp(self) -> None:
        self.engine = RobertEngine()
        self.shoulder_w = 450.0
        self.torso_h = 800.0

    def test_unknown_fabric_returns_none(self) -> None:
        result = self.engine.get_render_metrics(
            "unknown_fabric", self.shoulder_w, self.torso_h, 90
        )
        self.assertIsNone(result)

    def test_output_keys(self) -> None:
        result = self.engine.get_render_metrics(
            "silk_haussmann", self.shoulder_w, self.torso_h, 88
        )
        self.assertIsNotNone(result)
        for key in ("width", "height", "alpha", "is_shiny", "is_scanning", "patent_id"):
            self.assertIn(key, result)

    def test_patent_id(self) -> None:
        result = self.engine.get_render_metrics(
            "silk_haussmann", self.shoulder_w, self.torso_h, 88
        )
        self.assertEqual(result["patent_id"], PATENT_ID)
        self.assertEqual(result["patent_id"], "PCT/EP2025/067317")

    def test_silk_is_shiny(self) -> None:
        result = self.engine.get_render_metrics(
            "silk_haussmann", self.shoulder_w, self.torso_h, 88
        )
        self.assertTrue(result["is_shiny"])

    def test_business_elite_not_shiny(self) -> None:
        result = self.engine.get_render_metrics(
            "business_elite", self.shoulder_w, self.torso_h, 88
        )
        self.assertFalse(result["is_shiny"])

    def test_is_scanning_when_fit_below_95(self) -> None:
        result = self.engine.get_render_metrics(
            "silk_haussmann", self.shoulder_w, self.torso_h, 88
        )
        self.assertTrue(result["is_scanning"])

    def test_not_scanning_when_fit_is_95(self) -> None:
        result = self.engine.get_render_metrics(
            "silk_haussmann", self.shoulder_w, self.torso_h, 95
        )
        self.assertFalse(result["is_scanning"])

    def test_width_scaled_by_lafayette_factor(self) -> None:
        fabric = self.engine.PILOT_FABRIC_PHYSICS["silk_haussmann"]
        expected_w = self.shoulder_w * self.engine.calculate_lafayette_factor(fabric)
        result = self.engine.get_render_metrics(
            "silk_haussmann", self.shoulder_w, self.torso_h, 88
        )
        self.assertAlmostEqual(result["width"], expected_w, places=5)

    def test_height_scaled_by_gravity_stretch(self) -> None:
        fabric = self.engine.PILOT_FABRIC_PHYSICS["silk_haussmann"]
        expected_h = self.engine.calculate_gravity_stretch(fabric, self.torso_h)
        result = self.engine.get_render_metrics(
            "silk_haussmann", self.shoulder_w, self.torso_h, 88
        )
        self.assertAlmostEqual(result["height"], expected_h, places=5)

    def test_example_from_problem_statement(self) -> None:
        """Replica el ejemplo de prueba real (Soberanía V10)."""
        result = self.engine.get_render_metrics("silk_haussmann", 450, 800, 88)
        self.assertIsNotNone(result)
        # Anchura: 450 * (2.2 + 0.5 - 0.85*0.4) = 450 * 2.36 = 1062
        self.assertAlmostEqual(result["width"], 1062.0, places=5)
        # Altura: 800 * (1 + ((60-50)/350)*0.15) ≈ 800 * 1.00428... ≈ 803.43
        weight_norm = (60 - 50) / 350
        expected_h = 800 * (1.0 + weight_norm * 0.15)
        self.assertAlmostEqual(result["height"], expected_h, places=5)
        self.assertTrue(result["is_scanning"])
        self.assertTrue(result["is_shiny"])
        self.assertEqual(result["patent_id"], "PCT/EP2025/067317")


if __name__ == "__main__":
    unittest.main()
