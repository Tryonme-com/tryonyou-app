"""Tests para api/stirpe_v10: ZeroSizeEngine, verify_ecosystem, trigger_balmain_snap."""

from __future__ import annotations

import os
import sys
import unittest

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
_API = os.path.join(_ROOT, "api")
for _p in (_ROOT, _API):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from stirpe_v10 import (
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

    def test_nodes_keys(self) -> None:
        for key in ("core", "foundation", "retail", "art", "security"):
            self.assertIn(key, NODES)

    def test_nodes_core_url(self) -> None:
        self.assertEqual(NODES["core"], "TryOnYou.app")

    def test_nodes_foundation_url(self) -> None:
        self.assertEqual(NODES["foundation"], "TryOnYou.org")

    def test_nodes_security_url(self) -> None:
        self.assertEqual(NODES["security"], "abvetos.com")


# ---------------------------------------------------------------------------
# ZeroSizeEngine
# ---------------------------------------------------------------------------


class TestZeroSizeEngine(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = ZeroSizeEngine({"chest": 105.0, "shoulder": 48.0})

    def test_default_sovereignty_buffer(self) -> None:
        self.assertAlmostEqual(self.engine.sovereignty_buffer, 1.05, places=5)

    def test_calculate_sovereign_fit_returns_string(self) -> None:
        result = self.engine.calculate_sovereign_fit()
        self.assertIsInstance(result, str)

    def test_calculate_sovereign_fit_contains_fit_index(self) -> None:
        result = self.engine.calculate_sovereign_fit()
        # chest=105, shoulder=48, buffer=1.05 → 105*48/1.05 = 4800.0
        self.assertIn("4800.00", result)

    def test_calculate_sovereign_fit_label(self) -> None:
        result = self.engine.calculate_sovereign_fit()
        self.assertIn("Índice de Soberanía", result)

    def test_calculate_sovereign_fit_verdict(self) -> None:
        result = self.engine.calculate_sovereign_fit()
        self.assertIn("AJUSTE ARQUITECTÓNICO: PERFECTO", result)

    def test_custom_metrics(self) -> None:
        engine = ZeroSizeEngine({"chest": 100.0, "shoulder": 42.0})
        result = engine.calculate_sovereign_fit()
        expected_index = (100.0 * 42.0) / 1.05
        self.assertIn(f"{expected_index:.2f}", result)

    def test_custom_sovereignty_buffer(self) -> None:
        engine = ZeroSizeEngine({"chest": 100.0, "shoulder": 50.0}, sovereignty_buffer=2.0)
        result = engine.calculate_sovereign_fit()
        # 100*50/2.0 = 2500.0
        self.assertIn("2500.00", result)

    def test_empty_metrics_raises(self) -> None:
        with self.assertRaises(ValueError):
            ZeroSizeEngine({})

    def test_invalid_buffer_raises(self) -> None:
        with self.assertRaises(ValueError):
            ZeroSizeEngine({"chest": 100.0, "shoulder": 50.0}, sovereignty_buffer=0)

    def test_as_dict_returns_dict(self) -> None:
        result = self.engine.as_dict()
        self.assertIsInstance(result, dict)

    def test_as_dict_fit_index(self) -> None:
        result = self.engine.as_dict()
        self.assertAlmostEqual(result["fit_index"], 4800.0, places=2)

    def test_as_dict_chest(self) -> None:
        result = self.engine.as_dict()
        self.assertAlmostEqual(result["chest"], 105.0, places=2)

    def test_as_dict_shoulder(self) -> None:
        result = self.engine.as_dict()
        self.assertAlmostEqual(result["shoulder"], 48.0, places=2)

    def test_as_dict_verdict(self) -> None:
        result = self.engine.as_dict()
        self.assertEqual(result["verdict"], "PERFECT")

    def test_as_dict_legal(self) -> None:
        result = self.engine.as_dict()
        self.assertIn("PCT/EP2025/067317", result["legal"])

    def test_missing_chest_key_raises(self) -> None:
        engine = ZeroSizeEngine({"shoulder": 48.0})
        with self.assertRaises(KeyError):
            engine.calculate_sovereign_fit()

    def test_missing_shoulder_key_raises(self) -> None:
        engine = ZeroSizeEngine({"chest": 105.0})
        with self.assertRaises(KeyError):
            engine.calculate_sovereign_fit()


# ---------------------------------------------------------------------------
# verify_ecosystem
# ---------------------------------------------------------------------------


class TestVerifyEcosystem(unittest.TestCase):
    def test_returns_list(self) -> None:
        result = verify_ecosystem()
        self.assertIsInstance(result, list)

    def test_all_nodes_present(self) -> None:
        result = verify_ecosystem()
        output = "\n".join(result)
        for node in NODES:
            self.assertIn(node.upper(), output)

    def test_all_urls_present(self) -> None:
        result = verify_ecosystem()
        output = "\n".join(result)
        for url in NODES.values():
            self.assertIn(url, output)

    def test_header_present(self) -> None:
        result = verify_ecosystem()
        self.assertTrue(any("V10 OMEGA" in line for line in result))

    def test_footer_present(self) -> None:
        result = verify_ecosystem()
        self.assertTrue(any("global" in line for line in result))

    def test_ok_markers(self) -> None:
        result = verify_ecosystem()
        ok_lines = [line for line in result if "✅ OK" in line]
        self.assertEqual(len(ok_lines), len(NODES))


# ---------------------------------------------------------------------------
# trigger_balmain_snap
# ---------------------------------------------------------------------------


class TestTriggerBalmainSnap(unittest.TestCase):
    def test_returns_dict(self) -> None:
        result = trigger_balmain_snap()
        self.assertIsInstance(result, dict)

    def test_default_metrics_fit_index(self) -> None:
        result = trigger_balmain_snap()
        self.assertAlmostEqual(result["fit_index"], 4800.0, places=2)

    def test_snap_key_present(self) -> None:
        result = trigger_balmain_snap()
        self.assertIn("snap", result)

    def test_snap_contains_index(self) -> None:
        result = trigger_balmain_snap()
        self.assertIn("4800.00", result["snap"])

    def test_validation_key(self) -> None:
        result = trigger_balmain_snap()
        self.assertEqual(result["validation"], "PAVO BLANCO ACTIVO")

    def test_legal_key(self) -> None:
        result = trigger_balmain_snap()
        self.assertIn("PCT/EP2025/067317", result["legal"])

    def test_custom_metrics(self) -> None:
        result = trigger_balmain_snap({"chest": 100.0, "shoulder": 50.0})
        expected = round((100.0 * 50.0) / 1.05, 2)
        self.assertAlmostEqual(result["fit_index"], expected, places=2)


if __name__ == "__main__":
    unittest.main()
