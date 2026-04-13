"""Tests para LookOrchestrator y Product (esquema técnico Divineo)."""

from __future__ import annotations

import os
import sys
import unittest

_API = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "api"))
if _API not in sys.path:
    sys.path.insert(0, _API)

from look_orchestrator import (
    ELASTICITY_THRESHOLD,
    LAFAYETTE_EXPERIENCE,
    LAFAYETTE_LOCATION,
    MASTER_LOOKS_COUNT,
    SIREN,
    LookOrchestrator,
    Product,
)


def _make_product(elasticity_score: float, look_id: int = 1) -> Product:
    return Product(
        name="Test Item",
        brand="TestBrand",
        category="Top",
        elasticity_score=elasticity_score,
        look_id=look_id,
    )


class TestProductDataclass(unittest.TestCase):
    def test_product_attributes(self) -> None:
        p = Product(
            name="Gabardina",
            brand="Dior",
            category="Top",
            elasticity_score=0.15,
            look_id=1,
        )
        self.assertEqual(p.name, "Gabardina")
        self.assertEqual(p.brand, "Dior")
        self.assertEqual(p.category, "Top")
        self.assertAlmostEqual(p.elasticity_score, 0.15)
        self.assertEqual(p.look_id, 1)


class TestLookOrchestratorInit(unittest.TestCase):
    def test_default_siren(self) -> None:
        orch = LookOrchestrator()
        self.assertEqual(orch.siren, SIREN)

    def test_custom_siren(self) -> None:
        orch = LookOrchestrator(siren="000000000")
        self.assertEqual(orch.siren, "000000000")

    def test_master_looks_count(self) -> None:
        orch = LookOrchestrator()
        self.assertEqual(orch.master_looks_count, MASTER_LOOKS_COUNT)


class TestCalculatePerfectFit(unittest.TestCase):
    def setUp(self) -> None:
        self.orch = LookOrchestrator()
        self.scan_data: dict = {}

    def test_returns_list(self) -> None:
        result = self.orch.calculate_perfect_fit(self.scan_data, [])
        self.assertIsInstance(result, list)

    def test_empty_assets_returns_empty(self) -> None:
        result = self.orch.calculate_perfect_fit(self.scan_data, [])
        self.assertEqual(result, [])

    def test_item_above_threshold_included(self) -> None:
        assets = [_make_product(0.5)]
        result = self.orch.calculate_perfect_fit(self.scan_data, assets)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].elasticity_score, 0.5)

    def test_item_exactly_at_threshold_included(self) -> None:
        assets = [_make_product(ELASTICITY_THRESHOLD)]
        result = self.orch.calculate_perfect_fit(self.scan_data, assets)
        self.assertEqual(len(result), 1)

    def test_item_below_threshold_excluded(self) -> None:
        assets = [_make_product(0.15)]
        result = self.orch.calculate_perfect_fit(self.scan_data, assets)
        self.assertEqual(result, [])

    def test_mixed_assets_only_qualifying_returned(self) -> None:
        assets = [
            _make_product(0.15),  # excluded
            _make_product(0.45),  # included
            _make_product(0.60),  # included
        ]
        result = self.orch.calculate_perfect_fit(self.scan_data, assets)
        self.assertEqual(len(result), 2)
        for item in result:
            self.assertGreaterEqual(item.elasticity_score, ELASTICITY_THRESHOLD)

    def test_capped_at_master_looks_count(self) -> None:
        assets = [_make_product(0.5, look_id=i) for i in range(10)]
        result = self.orch.calculate_perfect_fit(self.scan_data, assets)
        self.assertEqual(len(result), MASTER_LOOKS_COUNT)

    def test_result_preserves_order(self) -> None:
        assets = [_make_product(0.4, look_id=i) for i in range(3)]
        result = self.orch.calculate_perfect_fit(self.scan_data, assets)
        for i, item in enumerate(result):
            self.assertEqual(item.look_id, i)

    def test_mock_assets_from_problem_statement(self) -> None:
        """Replica exacta del ejemplo de la especificación."""
        mock_assets = [
            Product(name="Gabardina", brand="Dior", category="Top", elasticity_score=0.15, look_id=1),
            Product(name="Pantalón", brand="Prada", category="Bottom", elasticity_score=0.45, look_id=1),
            Product(name="Vestido", brand="Versace", category="Full", elasticity_score=0.60, look_id=2),
        ]
        result = self.orch.calculate_perfect_fit({}, mock_assets)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].name, "Pantalón")
        self.assertEqual(result[1].name, "Vestido")


class TestGetLafayettePayload(unittest.TestCase):
    def setUp(self) -> None:
        self.orch = LookOrchestrator()

    def test_returns_dict(self) -> None:
        result = self.orch.get_lafayette_payload(look_id=1)
        self.assertIsInstance(result, dict)

    def test_status_locked_and_ready(self) -> None:
        result = self.orch.get_lafayette_payload(look_id=1)
        self.assertEqual(result["status"], "LOCKED_AND_READY")

    def test_payout_verified(self) -> None:
        result = self.orch.get_lafayette_payload(look_id=1)
        self.assertTrue(result["payout_verified"])

    def test_location(self) -> None:
        result = self.orch.get_lafayette_payload(look_id=1)
        self.assertEqual(result["location"], LAFAYETTE_LOCATION)

    def test_experience(self) -> None:
        result = self.orch.get_lafayette_payload(look_id=1)
        self.assertEqual(result["experience"], LAFAYETTE_EXPERIENCE)

    def test_selected_look(self) -> None:
        result = self.orch.get_lafayette_payload(look_id=42)
        self.assertEqual(result["selected_look"], 42)

    def test_all_keys_present(self) -> None:
        result = self.orch.get_lafayette_payload(look_id=1)
        for key in ("status", "payout_verified", "location", "experience", "selected_look"):
            self.assertIn(key, result)


if __name__ == "__main__":
    unittest.main()
