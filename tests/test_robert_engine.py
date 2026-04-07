"""Tests for Robert Engine — elastic oscillation and drape waves."""

from __future__ import annotations

import math
import os
import sys
import unittest

_API = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "api"))
if _API not in sys.path:
    sys.path.insert(0, _API)

from robert_engine import (
    BREATHING_FREQUENCY,
    DRAPE_WAVE_FREQUENCY,
    ELASTICITY_AMPLITUDE_FACTOR,
    MAX_DRAPE_AMPLITUDE_PX,
    calculate_drape_wave,
    calculate_elasticity_breathing,
)


class TestCalculateElasticityBreathing(unittest.TestCase):
    def _fabric(self, elasticity_pct: float) -> dict:
        return {"elasticityPct": elasticity_pct, "drapeCoefficient": 0.5}

    def test_returns_one_at_zero_timestamp(self) -> None:
        """sin(0) == 0 → result should be exactly 1.0 regardless of elasticity."""
        fabric = self._fabric(100.0)
        result = calculate_elasticity_breathing(fabric, 0.0)
        self.assertAlmostEqual(result, 1.0)

    def test_oscillates_above_and_below_one(self) -> None:
        """At different timestamps the value should oscillate around 1.0."""
        fabric = self._fabric(100.0)
        # sin > 0 → result > 1
        t_pos = math.pi / (2 * BREATHING_FREQUENCY)  # sin(t*BREATHING_FREQUENCY) == 1
        self.assertGreater(calculate_elasticity_breathing(fabric, t_pos), 1.0)
        # sin < 0 → result < 1
        t_neg = 3 * math.pi / (2 * BREATHING_FREQUENCY)  # sin(t*BREATHING_FREQUENCY) == -1
        self.assertLess(calculate_elasticity_breathing(fabric, t_neg), 1.0)

    def test_amplitude_scales_with_elasticity_pct(self) -> None:
        """Higher elasticityPct should produce a larger deviation from 1.0."""
        t = math.pi / (2 * BREATHING_FREQUENCY)  # peak sin value
        low = calculate_elasticity_breathing(self._fabric(10.0), t)
        high = calculate_elasticity_breathing(self._fabric(200.0), t)
        self.assertGreater(high, low)

    def test_zero_elasticity_always_returns_one(self) -> None:
        fabric = self._fabric(0.0)
        for t in [0.0, 100.0, 9999.0]:
            self.assertAlmostEqual(calculate_elasticity_breathing(fabric, t), 1.0)

    def test_formula_values(self) -> None:
        """Exact numeric check against the documented formula."""
        fabric = self._fabric(50.0)
        t = 1000.0
        amplitude = 50.0 * ELASTICITY_AMPLITUDE_FACTOR
        expected = 1.0 + math.sin(t * BREATHING_FREQUENCY) * amplitude
        self.assertAlmostEqual(calculate_elasticity_breathing(fabric, t), expected)


class TestCalculateDrapeWave(unittest.TestCase):
    def _fabric(self, drape_coeff: float) -> dict:
        return {"elasticityPct": 80.0, "drapeCoefficient": drape_coeff}

    def test_returns_correct_number_of_points(self) -> None:
        waves = calculate_drape_wave(self._fabric(0.5), 0.0, 300.0)
        self.assertEqual(len(waves), 8)

    def test_custom_num_points(self) -> None:
        waves = calculate_drape_wave(self._fabric(0.5), 0.0, 300.0, num_points=4)
        self.assertEqual(len(waves), 4)

    def test_zero_drape_coefficient_gives_zero_waves(self) -> None:
        """drapeCoefficient == 0 → all wave offsets should be 0."""
        waves = calculate_drape_wave(self._fabric(0.0), 500.0, 300.0)
        for w in waves:
            self.assertAlmostEqual(w, 0.0)

    def test_waves_differ_due_to_phase_offset(self) -> None:
        """Each wave point should have a distinct phase so they differ."""
        waves = calculate_drape_wave(self._fabric(1.0), 100.0, 300.0)
        # At least two values must differ (phase offsets guarantee this for n > 1)
        self.assertGreater(len(set(round(w, 6) for w in waves)), 1)

    def test_amplitude_bounded_by_drape_times_six(self) -> None:
        coeff = 0.7
        max_amp = coeff * MAX_DRAPE_AMPLITUDE_PX
        waves = calculate_drape_wave(self._fabric(coeff), 500.0, 300.0, num_points=32)
        for w in waves:
            self.assertLessEqual(abs(w), max_amp + 1e-9)

    def test_formula_values(self) -> None:
        """Exact numeric check for the first two wave points."""
        fabric = self._fabric(0.5)
        t = 200.0
        amplitude = 0.5 * MAX_DRAPE_AMPLITUDE_PX
        num_points = 8
        expected_0 = math.sin(t * DRAPE_WAVE_FREQUENCY + 0 * (math.pi / num_points)) * amplitude
        expected_1 = math.sin(t * DRAPE_WAVE_FREQUENCY + 1 * (math.pi / num_points)) * amplitude
        waves = calculate_drape_wave(fabric, t, 300.0, num_points=num_points)
        self.assertAlmostEqual(waves[0], expected_0)
        self.assertAlmostEqual(waves[1], expected_1)


if __name__ == "__main__":
    unittest.main()
