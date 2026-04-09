"""Tests para el módulo bunker_stirpe_v10 — Protocolo de Soberanía V10."""

from __future__ import annotations

import os
import sys
import unittest

_API = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "api"))
if _API not in sys.path:
    sys.path.insert(0, _API)

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
    def test_calculate_returns_string(self) -> None:
        engine = ZeroSizeEngine({"chest": 105, "shoulder": 48})
        self.assertIsInstance(engine.calculate_sovereign_fit(), str)

    def test_fit_index_formula(self) -> None:
        engine = ZeroSizeEngine({"chest": 105, "shoulder": 48})
        expected_index = (105 * 48) / 1.05
        result = engine.calculate_sovereign_fit()
        self.assertIn(f"{expected_index:.2f}", result)

    def test_result_contains_soberania(self) -> None:
        engine = ZeroSizeEngine({"chest": 100, "shoulder": 50})
        self.assertIn("Índice de Soberanía", engine.calculate_sovereign_fit())

    def test_result_contains_perfecto(self) -> None:
        engine = ZeroSizeEngine({"chest": 100, "shoulder": 50})
        self.assertIn("PERFECTO", engine.calculate_sovereign_fit())

    def test_sovereignty_buffer_default(self) -> None:
        engine = ZeroSizeEngine({"chest": 100, "shoulder": 50})
        self.assertAlmostEqual(engine.sovereignty_buffer, 1.05)

    def test_legal_attribute_contains_patente(self) -> None:
        self.assertIn("PCT/EP2025/067317", ZeroSizeEngine.LEGAL)

    def test_empty_metrics_raises(self) -> None:
        with self.assertRaises(ValueError):
            ZeroSizeEngine({})

    def test_zero_metrics_returns_zero_index(self) -> None:
        engine = ZeroSizeEngine({"chest": 0, "shoulder": 0})
        result = engine.calculate_sovereign_fit()
        self.assertIn("0.00", result)

    def test_custom_metrics_stored(self) -> None:
        metrics = {"chest": 90, "shoulder": 40}
        engine = ZeroSizeEngine(metrics)
        self.assertEqual(engine.metrics, metrics)


# ---------------------------------------------------------------------------
# verify_ecosystem
# ---------------------------------------------------------------------------


class TestVerifyEcosystem(unittest.TestCase):
    def setUp(self) -> None:
        self.lines = verify_ecosystem(_delay=0)

    def test_returns_list(self) -> None:
        self.assertIsInstance(self.lines, list)

    def test_first_line_contains_v10_omega(self) -> None:
        self.assertIn("V10 OMEGA", self.lines[0])

    def test_contains_paris_2026(self) -> None:
        self.assertIn("PARIS 2026", self.lines[0])

    def test_each_node_present(self) -> None:
        combined = "\n".join(self.lines)
        for node in NODES:
            self.assertIn(node.upper(), combined)

    def test_each_url_present(self) -> None:
        combined = "\n".join(self.lines)
        for url in NODES.values():
            self.assertIn(url, combined)

    def test_consolidated_message_present(self) -> None:
        combined = "\n".join(self.lines)
        self.assertIn("consolidado", combined)

    def test_node_count_matches(self) -> None:
        ok_lines = [line for line in self.lines if "✅ OK" in line]
        self.assertEqual(len(ok_lines), len(NODES))


# ---------------------------------------------------------------------------
# trigger_balmain_snap
# ---------------------------------------------------------------------------


class TestTriggerBalmainSnap(unittest.TestCase):
    def setUp(self) -> None:
        self.result = trigger_balmain_snap(_delay=0)

    def test_returns_dict(self) -> None:
        self.assertIsInstance(self.result, dict)

    def test_ecosystem_status_consolidated(self) -> None:
        self.assertEqual(self.result["ecosystem_status"], "CONSOLIDATED")

    def test_fit_result_present(self) -> None:
        self.assertIn("fit_result", self.result)

    def test_fit_result_contains_soberania(self) -> None:
        self.assertIn("Índice de Soberanía", self.result["fit_result"])

    def test_legal_contains_patente(self) -> None:
        self.assertIn("PCT/EP2025/067317", self.result["legal"])

    def test_custom_metrics_reflected_in_fit(self) -> None:
        result = trigger_balmain_snap(chest=90, shoulder=44, _delay=0)
        expected_index = (90 * 44) / 1.05
        self.assertIn(f"{expected_index:.2f}", result["fit_result"])

    def test_all_keys_present(self) -> None:
        for key in ("ecosystem_status", "fit_result", "legal"):
            self.assertIn(key, self.result)


if __name__ == "__main__":
    unittest.main()
