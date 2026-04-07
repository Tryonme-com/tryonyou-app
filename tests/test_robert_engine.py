"""Tests para Robert Engine — get_drape_folds (unittest estándar)."""

from __future__ import annotations

import math
import os
import sys
import unittest

_API = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "api"))
if _API not in sys.path:
    sys.path.insert(0, _API)

from robert_engine import get_drape_folds


class TestGetDrapeFoldsCount(unittest.TestCase):
    """Número de pliegues según drapeCoefficient."""

    def test_low_drape_yields_three_folds(self) -> None:
        fabric = {"drapeCoefficient": 0.3}
        folds = get_drape_folds(fabric, garment_w=100.0, gravity_h=200.0, now_ms=0.0)
        self.assertEqual(len(folds), 3)

    def test_high_drape_yields_five_folds(self) -> None:
        fabric = {"drapeCoefficient": 0.7}
        folds = get_drape_folds(fabric, garment_w=100.0, gravity_h=200.0, now_ms=0.0)
        self.assertEqual(len(folds), 5)

    def test_boundary_drape_05_yields_five_folds(self) -> None:
        fabric = {"drapeCoefficient": 0.5}
        folds = get_drape_folds(fabric, garment_w=100.0, gravity_h=200.0, now_ms=0.0)
        self.assertEqual(len(folds), 5)

    def test_boundary_drape_just_below_05_yields_three_folds(self) -> None:
        fabric = {"drapeCoefficient": 0.4999}
        folds = get_drape_folds(fabric, garment_w=100.0, gravity_h=200.0, now_ms=0.0)
        self.assertEqual(len(folds), 3)


class TestGetDrapeFoldsDimensions(unittest.TestCase):
    """Dimensiones de cada pliegue."""

    def test_fold_width_is_eight_percent_of_garment_w(self) -> None:
        fabric = {"drapeCoefficient": 0.4}
        folds = get_drape_folds(fabric, garment_w=200.0, gravity_h=300.0, now_ms=0.0)
        for fold in folds:
            self.assertAlmostEqual(fold["width"], 200.0 * 0.08)

    def test_fold_height_is_seventy_percent_of_gravity_h(self) -> None:
        fabric = {"drapeCoefficient": 0.4}
        folds = get_drape_folds(fabric, garment_w=200.0, gravity_h=300.0, now_ms=0.0)
        for fold in folds:
            self.assertAlmostEqual(fold["height"], 300.0 * 0.7)

    def test_fold_keys_present(self) -> None:
        fabric = {"drapeCoefficient": 0.6}
        folds = get_drape_folds(fabric, garment_w=100.0, gravity_h=200.0, now_ms=0.0)
        for fold in folds:
            self.assertIn("x", fold)
            self.assertIn("width", fold)
            self.assertIn("height", fold)
            self.assertIn("alpha", fold)


class TestGetDrapeFoldsOpacity(unittest.TestCase):
    """Opacidad (alpha) según drapeCoefficient."""

    def test_opacity_formula(self) -> None:
        for coeff in (0.0, 0.3, 0.5, 0.8, 1.0):
            fabric = {"drapeCoefficient": coeff}
            folds = get_drape_folds(fabric, garment_w=100.0, gravity_h=100.0, now_ms=0.0)
            expected_alpha = 0.05 + coeff * 0.1
            for fold in folds:
                self.assertAlmostEqual(fold["alpha"], expected_alpha)


class TestGetDrapeFoldsPosition(unittest.TestCase):
    """Posición X de los pliegues — offset sinusoidal y separación uniforme."""

    def test_first_fold_x_at_now_zero_low_drape(self) -> None:
        # i=0: phase=0, offset_x=sin(0)*... = 0, fold_x = -garment_w/3
        fabric = {"drapeCoefficient": 0.0}
        folds = get_drape_folds(fabric, garment_w=90.0, gravity_h=100.0, now_ms=0.0)
        self.assertAlmostEqual(folds[0]["x"], -90.0 / 3)

    def test_sinusoidal_offset_varies_with_now_ms(self) -> None:
        fabric = {"drapeCoefficient": 0.8}
        folds_t0 = get_drape_folds(fabric, garment_w=100.0, gravity_h=100.0, now_ms=0.0)
        folds_t1 = get_drape_folds(fabric, garment_w=100.0, gravity_h=100.0, now_ms=1000.0)
        # At least one fold should differ between t=0 and t=1000ms
        any_diff = any(
            abs(folds_t0[i]["x"] - folds_t1[i]["x"]) > 1e-9
            for i in range(len(folds_t0))
        )
        self.assertTrue(any_diff)

    def test_fold_x_formula_matches_manual_calculation(self) -> None:
        fabric = {"drapeCoefficient": 0.4}
        garment_w = 120.0
        gravity_h = 200.0
        now_ms = 500.0
        num_folds = 3
        folds = get_drape_folds(fabric, garment_w=garment_w, gravity_h=gravity_h, now_ms=now_ms)
        for i, fold in enumerate(folds):
            phase = i * (math.pi / num_folds)
            offset_x = math.sin(now_ms * 0.0015 + phase) * (5 * fabric["drapeCoefficient"])
            expected_x = (-garment_w / 3) + (i * (garment_w / (num_folds - 1))) + offset_x
            self.assertAlmostEqual(fold["x"], expected_x, places=10)


class TestGetDrapeFoldsReturnType(unittest.TestCase):
    """El valor retornado es una lista de diccionarios con valores float."""

    def test_returns_list(self) -> None:
        fabric = {"drapeCoefficient": 0.5}
        result = get_drape_folds(fabric, garment_w=100.0, gravity_h=100.0, now_ms=0.0)
        self.assertIsInstance(result, list)

    def test_each_element_is_dict(self) -> None:
        fabric = {"drapeCoefficient": 0.5}
        result = get_drape_folds(fabric, garment_w=100.0, gravity_h=100.0, now_ms=0.0)
        for item in result:
            self.assertIsInstance(item, dict)


if __name__ == "__main__":
    unittest.main()
