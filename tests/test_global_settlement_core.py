"""Pruebas unitarias para GLOBAL_SETTLEMENT_CORE: AssetSettlementManager."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from GLOBAL_SETTLEMENT_CORE import AssetSettlementManager, main


class TestAssetSettlementManager(unittest.TestCase):
    def test_default_attributes(self) -> None:
        manager = AssetSettlementManager()
        self.assertAlmostEqual(manager.total_target, 398744.50)
        self.assertEqual(manager.location, "Paris-Oberkampf")

    def test_custom_attributes(self) -> None:
        manager = AssetSettlementManager(total_target=100000.0, location="Lyon")
        self.assertAlmostEqual(manager.total_target, 100000.0)
        self.assertEqual(manager.location, "Lyon")

    def test_execute_global_reconciliation_returns_true(self) -> None:
        manager = AssetSettlementManager()
        result = manager.execute_global_reconciliation()
        self.assertTrue(result)

    def test_final_deployment_check_runs_without_error(self) -> None:
        manager = AssetSettlementManager()
        # Should complete without raising any exception
        manager.final_deployment_check()

    def test_main_returns_zero_on_success(self) -> None:
        self.assertEqual(main(), 0)


if __name__ == "__main__":
    unittest.main()
