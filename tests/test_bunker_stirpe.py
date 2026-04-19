"""Tests para el módulo bunker_stirpe — Arquitectura de Soberanía V10."""

from __future__ import annotations

import io
import os
import sys
import unittest

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
_API = os.path.join(_ROOT, "api")
for _p in (_ROOT, _API):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from bunker_stirpe import (
    NODES,
    PATENTE,
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

    def test_nodes_contains_core(self) -> None:
        self.assertIn("core", NODES)
        self.assertEqual(NODES["core"], "TryOnYou.app")

    def test_nodes_contains_foundation(self) -> None:
        self.assertIn("foundation", NODES)
        self.assertEqual(NODES["foundation"], "TryOnYou.org")

    def test_nodes_contains_retail(self) -> None:
        self.assertIn("retail", NODES)
        self.assertEqual(NODES["retail"], "liveitfashion.com")

    def test_nodes_contains_art(self) -> None:
        self.assertIn("art", NODES)
        self.assertEqual(NODES["art"], "vvlart.com")

    def test_nodes_contains_security(self) -> None:
        self.assertIn("security", NODES)
        self.assertEqual(NODES["security"], "abvetos.com")


# ---------------------------------------------------------------------------
# ZeroSizeEngine
# ---------------------------------------------------------------------------


class TestZeroSizeEngine(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = ZeroSizeEngine({"chest": 105, "shoulder": 48})

    def test_sovereignty_buffer_default(self) -> None:
        self.assertAlmostEqual(self.engine.sovereignty_buffer, 1.05, places=5)

    def test_calculate_sovereign_fit_returns_string(self) -> None:
        result = self.engine.calculate_sovereign_fit()
        self.assertIsInstance(result, str)

    def test_calculate_sovereign_fit_contains_index(self) -> None:
        result = self.engine.calculate_sovereign_fit()
        self.assertIn("Índice de Soberanía", result)

    def test_calculate_sovereign_fit_value(self) -> None:
        # fit_index = (105 * 48) / 1.05 = 4800.00
        result = self.engine.calculate_sovereign_fit()
        self.assertIn("4800.00", result)

    def test_calculate_sovereign_fit_perfect_verdict(self) -> None:
        result = self.engine.calculate_sovereign_fit()
        self.assertIn("AJUSTE ARQUITECTÓNICO: PERFECTO", result)

    def test_custom_metrics(self) -> None:
        engine = ZeroSizeEngine({"chest": 90.0, "shoulder": 40.0})
        expected_index = (90.0 * 40.0) / 1.05
        result = engine.calculate_sovereign_fit()
        self.assertIn(f"{expected_index:.2f}", result)

    def test_missing_key_raises(self) -> None:
        engine = ZeroSizeEngine({"chest": 105})
        with self.assertRaises(KeyError):
            engine.calculate_sovereign_fit()


# ---------------------------------------------------------------------------
# verify_ecosystem
# ---------------------------------------------------------------------------


class TestVerifyEcosystem(unittest.TestCase):
    def _run_silently(self) -> list:
        buf = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = buf
        try:
            results = verify_ecosystem(delay=0.0)
        finally:
            sys.stdout = old_stdout
        return results

    def test_returns_list(self) -> None:
        results = self._run_silently()
        self.assertIsInstance(results, list)

    def test_returns_one_entry_per_node(self) -> None:
        results = self._run_silently()
        self.assertEqual(len(results), len(NODES))

    def test_all_statuses_ok(self) -> None:
        results = self._run_silently()
        for entry in results:
            self.assertEqual(entry["status"], "OK")

    def test_result_keys_present(self) -> None:
        results = self._run_silently()
        for entry in results:
            self.assertIn("node", entry)
            self.assertIn("url", entry)
            self.assertIn("status", entry)

    def test_core_node_in_results(self) -> None:
        results = self._run_silently()
        nodes_in_results = [e["node"] for e in results]
        self.assertIn("core", nodes_in_results)

    def test_output_contains_protocolo(self) -> None:
        buf = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = buf
        try:
            verify_ecosystem(delay=0.0)
        finally:
            sys.stdout = old_stdout
        self.assertIn("PROTOCOLO V10 OMEGA", buf.getvalue())


# ---------------------------------------------------------------------------
# trigger_balmain_snap
# ---------------------------------------------------------------------------


class TestTriggerBalmainSnap(unittest.TestCase):
    def _run_silently(self, **kwargs) -> dict:
        buf = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = buf
        try:
            result = trigger_balmain_snap(**kwargs)
        finally:
            sys.stdout = old_stdout
        return result

    def test_returns_dict(self) -> None:
        result = self._run_silently()
        self.assertIsInstance(result, dict)

    def test_fit_result_key_present(self) -> None:
        result = self._run_silently()
        self.assertIn("fit_result", result)

    def test_validation_key_present(self) -> None:
        result = self._run_silently()
        self.assertIn("validation", result)

    def test_legal_key_present(self) -> None:
        result = self._run_silently()
        self.assertIn("legal", result)

    def test_legal_contains_patente(self) -> None:
        result = self._run_silently()
        self.assertIn(PATENTE, result["legal"])

    def test_fit_result_contains_index(self) -> None:
        result = self._run_silently()
        self.assertIn("Índice de Soberanía", result["fit_result"])

    def test_default_chest_shoulder_fit_value(self) -> None:
        # Default: chest=105, shoulder=48 → fit_index = 4800.00
        result = self._run_silently()
        self.assertIn("4800.00", result["fit_result"])

    def test_custom_metrics_reflected(self) -> None:
        result = self._run_silently(chest=90.0, shoulder=40.0)
        expected = (90.0 * 40.0) / 1.05
        self.assertIn(f"{expected:.2f}", result["fit_result"])

    def test_validation_pavo_blanco(self) -> None:
        result = self._run_silently()
        self.assertIn("PAVO BLANCO", result["validation"])


if __name__ == "__main__":
    unittest.main()
