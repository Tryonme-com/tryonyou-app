"""Tests para el módulo bunker_stirpe_v10."""

from __future__ import annotations

import os
import sys
import unittest

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
_API = os.path.join(_ROOT, "api")
for _p in (_ROOT, _API):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from bunker_stirpe_v10 import (
    NODES,
    ZeroSizeEngine,
    trigger_balmain_snap,
    verify_ecosystem,
)


# ---------------------------------------------------------------------------
# NODES
# ---------------------------------------------------------------------------


class TestNodes(unittest.TestCase):
    def test_nodes_is_dict(self) -> None:
        self.assertIsInstance(NODES, dict)

    def test_nodes_has_five_entries(self) -> None:
        self.assertEqual(len(NODES), 5)

    def test_core_node(self) -> None:
        self.assertEqual(NODES["core"], "TryOnYou.app")

    def test_foundation_node(self) -> None:
        self.assertEqual(NODES["foundation"], "TryOnYou.org")

    def test_retail_node(self) -> None:
        self.assertEqual(NODES["retail"], "liveitfashion.com")

    def test_art_node(self) -> None:
        self.assertEqual(NODES["art"], "vvlart.com")

    def test_security_node(self) -> None:
        self.assertEqual(NODES["security"], "abvetos.com")


# ---------------------------------------------------------------------------
# ZeroSizeEngine
# ---------------------------------------------------------------------------


class TestZeroSizeEngine(unittest.TestCase):
    def _engine(self, chest: float = 105, shoulder: float = 48) -> ZeroSizeEngine:
        return ZeroSizeEngine({"chest": chest, "shoulder": shoulder})

    def test_default_sovereignty_buffer(self) -> None:
        engine = self._engine()
        self.assertAlmostEqual(engine.sovereignty_buffer, 1.05, places=5)

    def test_calculate_sovereign_fit_returns_string(self) -> None:
        result = self._engine().calculate_sovereign_fit()
        self.assertIsInstance(result, str)

    def test_calculate_sovereign_fit_contains_index(self) -> None:
        engine = self._engine(chest=105, shoulder=48)
        expected_index = round((105 * 48) / 1.05, 2)
        result = engine.calculate_sovereign_fit()
        self.assertIn(f"{expected_index:.2f}", result)

    def test_calculate_sovereign_fit_contains_verdict(self) -> None:
        result = self._engine().calculate_sovereign_fit()
        self.assertIn("AJUSTE ARQUITECTÓNICO: PERFECTO", result)

    def test_calculate_sovereign_fit_balmain_reference(self) -> None:
        # Referencia: chest=105, shoulder=48 → índice ≈ 4800
        engine = self._engine(chest=105, shoulder=48)
        expected = round((105 * 48) / 1.05, 2)
        result = engine.calculate_sovereign_fit()
        self.assertIn(f"{expected:.2f}", result)

    def test_calculate_sovereign_fit_custom_metrics(self) -> None:
        engine = ZeroSizeEngine({"chest": 90, "shoulder": 40})
        expected = round((90 * 40) / 1.05, 2)
        result = engine.calculate_sovereign_fit()
        self.assertIn(f"{expected:.2f}", result)

    def test_missing_key_raises(self) -> None:
        engine = ZeroSizeEngine({"chest": 100})
        with self.assertRaises(KeyError):
            engine.calculate_sovereign_fit()

    def test_metrics_stored(self) -> None:
        metrics = {"chest": 100, "shoulder": 45}
        engine = ZeroSizeEngine(metrics)
        self.assertEqual(engine.metrics, metrics)


# ---------------------------------------------------------------------------
# verify_ecosystem
# ---------------------------------------------------------------------------


class TestVerifyEcosystem(unittest.TestCase):
    def test_returns_list(self) -> None:
        result = verify_ecosystem(sleep=False)
        self.assertIsInstance(result, list)

    def test_returns_non_empty_list(self) -> None:
        result = verify_ecosystem(sleep=False)
        self.assertTrue(len(result) > 0)

    def test_header_present(self) -> None:
        result = verify_ecosystem(sleep=False)
        combined = "\n".join(result)
        self.assertIn("PROTOCOLO V10 OMEGA", combined)

    def test_all_nodes_mentioned(self) -> None:
        result = verify_ecosystem(sleep=False)
        combined = "\n".join(result)
        for node in NODES:
            self.assertIn(node.upper(), combined)

    def test_footer_present(self) -> None:
        result = verify_ecosystem(sleep=False)
        combined = "\n".join(result)
        self.assertIn("Ecosistema consolidado", combined)


# ---------------------------------------------------------------------------
# trigger_balmain_snap
# ---------------------------------------------------------------------------


class TestTriggerBalmainSnap(unittest.TestCase):
    def test_returns_dict(self) -> None:
        result = trigger_balmain_snap()
        self.assertIsInstance(result, dict)

    def test_fit_index_key_present(self) -> None:
        result = trigger_balmain_snap()
        self.assertIn("fit_index", result)

    def test_legal_key_present(self) -> None:
        result = trigger_balmain_snap()
        self.assertIn("legal", result)

    def test_legal_contains_patente(self) -> None:
        result = trigger_balmain_snap()
        self.assertIn("PCT/EP2025/067317", result["legal"])

    def test_default_fit_index(self) -> None:
        # chest=105, shoulder=48, buffer=1.05
        expected = round((105 * 48) / 1.05, 2)
        result = trigger_balmain_snap()
        self.assertAlmostEqual(result["fit_index"], expected, places=2)

    def test_custom_metrics_fit_index(self) -> None:
        metrics = {"chest": 90, "shoulder": 40}
        expected = round((90 * 40) / 1.05, 2)
        result = trigger_balmain_snap(metrics=metrics)
        self.assertAlmostEqual(result["fit_index"], expected, places=2)


if __name__ == "__main__":
    unittest.main()
