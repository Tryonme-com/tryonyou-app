"""Tests para el Fit Engine — analyze_fit_return_risk (Robert Engine physics)."""

from __future__ import annotations

import os
import sys
import unittest

_API = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "api"))
if _API not in sys.path:
    sys.path.insert(0, _API)

from fit_engine import UserAnchors, analyze_fit_return_risk


class TestAnalyzeFitReturnRisk(unittest.TestCase):
    """Verifies the return risk logic of the Robert Engine."""

    def _make_fabric(self, elasticity_pct: float, recovery_pct: float) -> dict:
        return {"elasticityPct": elasticity_pct, "recoveryPct": recovery_pct}

    # ------------------------------------------------------------------
    # Recomendación: "Talla Correcta" (return_risk < 0.3)
    # ------------------------------------------------------------------

    def test_low_risk_returns_correct_size(self) -> None:
        """Tejido muy elástico + buen recovery → riesgo bajo → Talla Correcta."""
        fabric = self._make_fabric(elasticity_pct=100.0, recovery_pct=90.0)
        anchors = UserAnchors(shoulder_w=40.0)
        result = analyze_fit_return_risk(fabric, anchors, "G-001")
        self.assertEqual(result["garment_id"], "G-001")
        self.assertLess(result["return_risk_pct"], 30.0)
        self.assertEqual(result["recommendation"], "Talla Correcta")

    # ------------------------------------------------------------------
    # Recomendación: "Sugerir Talla Superior" (return_risk >= 0.3)
    # ------------------------------------------------------------------

    def test_high_risk_suggests_larger_size(self) -> None:
        """Tejido poco elástico + hombros anchos → riesgo alto → Sugerir Talla Superior."""
        fabric = self._make_fabric(elasticity_pct=10.0, recovery_pct=20.0)
        anchors = UserAnchors(shoulder_w=60.0)
        result = analyze_fit_return_risk(fabric, anchors, "G-002")
        self.assertEqual(result["garment_id"], "G-002")
        self.assertGreaterEqual(result["return_risk_pct"], 30.0)
        self.assertEqual(result["recommendation"], "Sugerir Talla Superior")

    # ------------------------------------------------------------------
    # Límite de 95 %
    # ------------------------------------------------------------------

    def test_return_risk_capped_at_95(self) -> None:
        """El riesgo nunca supera 95 %."""
        fabric = self._make_fabric(elasticity_pct=1.0, recovery_pct=0.0)
        anchors = UserAnchors(shoulder_w=200.0)
        result = analyze_fit_return_risk(fabric, anchors, "G-003")
        self.assertLessEqual(result["return_risk_pct"], 95.0)

    # ------------------------------------------------------------------
    # Estructura de la respuesta
    # ------------------------------------------------------------------

    def test_result_keys(self) -> None:
        """La respuesta contiene exactamente las claves esperadas."""
        fabric = self._make_fabric(elasticity_pct=50.0, recovery_pct=50.0)
        anchors = UserAnchors(shoulder_w=45.0)
        result = analyze_fit_return_risk(fabric, anchors, "BALMAIN-X1")
        self.assertIn("garment_id", result)
        self.assertIn("return_risk_pct", result)
        self.assertIn("recommendation", result)

    def test_garment_id_preserved(self) -> None:
        """El garment_id de entrada se propaga sin modificación."""
        fabric = self._make_fabric(elasticity_pct=50.0, recovery_pct=50.0)
        anchors = UserAnchors(shoulder_w=45.0)
        result = analyze_fit_return_risk(fabric, anchors, "V10-BALMAIN-WHITE-SNAP")
        self.assertEqual(result["garment_id"], "V10-BALMAIN-WHITE-SNAP")

    def test_return_risk_pct_is_rounded_to_two_decimals(self) -> None:
        """return_risk_pct tiene como máximo dos decimales."""
        fabric = self._make_fabric(elasticity_pct=33.0, recovery_pct=66.0)
        anchors = UserAnchors(shoulder_w=42.0)
        result = analyze_fit_return_risk(fabric, anchors, "G-004")
        pct = result["return_risk_pct"]
        self.assertEqual(pct, round(pct, 2))

    # ------------------------------------------------------------------
    # Umbral exacto de recomendación (return_risk == 0.3 → Sugerir Talla Superior)
    # ------------------------------------------------------------------

    def test_boundary_at_30_percent_suggests_larger(self) -> None:
        """Un riesgo exactamente en el umbral (≥ 0.3) sugiere talla superior."""
        # Construir entradas que produzcan return_risk == 0.3 exacto:
        # tension_factor * 0.1 + (1 - recoveryPct/100) = 0.3
        # Con recoveryPct=90 → recovery_term=0.1; tension_term=0.2
        # tension_factor=2.0 → shoulder_w * 1.2 / elasticityPct = 2.0
        # shoulder_w=20, elasticityPct=12 → 20*1.2/12 = 2.0 ✓
        fabric = self._make_fabric(elasticity_pct=12.0, recovery_pct=90.0)
        anchors = UserAnchors(shoulder_w=20.0)
        result = analyze_fit_return_risk(fabric, anchors, "G-BOUNDARY")
        self.assertAlmostEqual(result["return_risk_pct"], 30.0, places=5)
        self.assertEqual(result["recommendation"], "Sugerir Talla Superior")


class TestUserAnchors(unittest.TestCase):
    """Verifies the UserAnchors dataclass."""

    def test_shoulder_w_stored(self) -> None:
        anchors = UserAnchors(shoulder_w=48.5)
        self.assertAlmostEqual(anchors.shoulder_w, 48.5)


class TestAnalyzeFitReturnRiskEdgeCases(unittest.TestCase):
    """Edge cases: invalid inputs."""

    def test_zero_elasticity_raises(self) -> None:
        """elasticityPct == 0 must raise ValueError (avoids division by zero)."""
        fabric = {"elasticityPct": 0.0, "recoveryPct": 50.0}
        anchors = UserAnchors(shoulder_w=45.0)
        with self.assertRaises(ValueError):
            analyze_fit_return_risk(fabric, anchors, "G-ZERO")

    def test_negative_elasticity_raises(self) -> None:
        """elasticityPct < 0 must also raise ValueError."""
        fabric = {"elasticityPct": -5.0, "recoveryPct": 50.0}
        anchors = UserAnchors(shoulder_w=45.0)
        with self.assertRaises(ValueError):
            analyze_fit_return_risk(fabric, anchors, "G-NEG")


if __name__ == "__main__":
    unittest.main()
