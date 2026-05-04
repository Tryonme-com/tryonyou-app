"""Pruebas unitarias para GLOBAL_SETTLEMENT_CORE: AssetSettlementManager."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from GLOBAL_SETTLEMENT_CORE import AssetSettlementManager, main


class TestAssetSettlementManager(unittest.TestCase):
    def setUp(self) -> None:
        self._env_patch = patch.dict(os.environ, {}, clear=False)
        self._env_patch.start()
        for key in (
            "TRYONYOU_CAPITAL_450K_CONFIRMED",
            "TRYONYOU_FUNDS_450K_CONFIRMED",
            "BUNKER_CAPITAL_ENTRY_CONFIRMED",
            "GLOBAL_SETTLEMENT_EVIDENCE_FILE",
            "TRYONYOU_CAPITAL_450K_EVIDENCE_FILE",
            "TRYONYOU_FUNDS_450K_EVIDENCE_FILE",
        ):
            os.environ.pop(key, None)

    def tearDown(self) -> None:
        self._env_patch.stop()

    def test_default_attributes(self) -> None:
        manager = AssetSettlementManager()
        self.assertAlmostEqual(manager.total_target, 450000.00)
        self.assertEqual(manager.target_cents, 45000000)
        self.assertEqual(manager.location, "Paris-Oberkampf")

    def test_custom_attributes(self) -> None:
        manager = AssetSettlementManager(total_target=100000.0, location="Lyon")
        self.assertAlmostEqual(manager.total_target, 100000.0)
        self.assertEqual(manager.target_cents, 10000000)
        self.assertEqual(manager.location, "Lyon")

    def test_execute_global_reconciliation_blocks_without_flag(self) -> None:
        manager = AssetSettlementManager()
        result = manager.execute_global_reconciliation()
        self.assertFalse(result)
        self.assertEqual(manager.last_status["reason"], "missing_confirmation_flag")

    def test_execute_global_reconciliation_blocks_without_evidence(self) -> None:
        os.environ["TRYONYOU_CAPITAL_450K_CONFIRMED"] = "1"
        manager = AssetSettlementManager()
        result = manager.execute_global_reconciliation()
        self.assertFalse(result)
        self.assertEqual(manager.last_status["reason"], "missing_or_insufficient_evidence")

    def test_execute_global_reconciliation_requires_sufficient_evidence(self) -> None:
        os.environ["TRYONYOU_CAPITAL_450K_CONFIRMED"] = "1"
        with tempfile.TemporaryDirectory() as tmpdir:
            evidence_path = Path(tmpdir) / "capital_450k_evidence.json"
            evidence_path.write_text(
                json.dumps(
                    {
                        "amount_cents": 45000000,
                        "currency": "EUR",
                        "source": "qonto",
                        "reference": "txn_450k_verified",
                    }
                ),
                encoding="utf-8",
            )
            manager = AssetSettlementManager(evidence_path=evidence_path)
            result = manager.execute_global_reconciliation()

        self.assertTrue(result)
        self.assertEqual(manager.last_status["status"], "VERIFIED")

    def test_execute_global_reconciliation_failure_path(self) -> None:
        manager = AssetSettlementManager()
        with patch.object(manager, "execute_global_reconciliation", return_value=False):
            result = manager.execute_global_reconciliation()
        self.assertFalse(result)

    def test_final_deployment_check_runs_without_error(self) -> None:
        manager = AssetSettlementManager()
        self.assertFalse(manager.final_deployment_check())

    def test_final_deployment_check_returns_true_after_verified_status(self) -> None:
        manager = AssetSettlementManager()
        manager.last_status = {"status": "VERIFIED"}
        self.assertTrue(manager.final_deployment_check())

    def test_main_returns_one_by_default_without_evidence(self) -> None:
        self.assertEqual(main(), 1)

    def test_main_returns_zero_on_success(self) -> None:
        with (
            patch("GLOBAL_SETTLEMENT_CORE.AssetSettlementManager.execute_global_reconciliation", return_value=True),
            patch("GLOBAL_SETTLEMENT_CORE.AssetSettlementManager.final_deployment_check", return_value=True),
        ):
            self.assertEqual(main(), 0)

    def test_main_returns_one_on_failure(self) -> None:
        with patch("GLOBAL_SETTLEMENT_CORE.AssetSettlementManager.execute_global_reconciliation", return_value=False):
            self.assertEqual(main(), 1)


if __name__ == "__main__":
    unittest.main()
