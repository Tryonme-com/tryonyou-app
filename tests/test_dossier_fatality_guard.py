"""Tests para el guard seguro de Dossier Fatality."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from GLOBAL_SETTLEMENT_CORE import AssetSettlementManager
from dossier_fatality_guard import evaluate_fatality_guard


class TestDossierFatalityGuard(unittest.TestCase):
    def setUp(self) -> None:
        self._env_patch = patch.dict(os.environ, {}, clear=False)
        self._env_patch.start()
        for key in (
            "TRYONYOU_CAPITAL_450K_CONFIRMED",
            "TRYONYOU_FUNDS_450K_CONFIRMED",
            "BUNKER_CAPITAL_ENTRY_CONFIRMED",
        ):
            os.environ.pop(key, None)

    def tearDown(self) -> None:
        self._env_patch.stop()

    def test_blocks_outside_tuesday_0800_window(self) -> None:
        decision = evaluate_fatality_guard(
            now=datetime(2026, 5, 4, 8, 0, tzinfo=ZoneInfo("Europe/Paris"))
        )
        self.assertFalse(decision.activated)
        self.assertEqual(decision.reason, "outside_tuesday_0800_window")

    def test_blocks_inside_window_without_verified_settlement(self) -> None:
        decision = evaluate_fatality_guard(
            now=datetime(2026, 5, 5, 8, 0, tzinfo=ZoneInfo("Europe/Paris"))
        )
        self.assertFalse(decision.activated)
        self.assertEqual(decision.reason, "missing_confirmation_flag")

    def test_activates_with_window_flag_and_evidence(self) -> None:
        os.environ["TRYONYOU_CAPITAL_450K_CONFIRMED"] = "1"
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            evidence_path = tmp / "capital_450k_evidence.json"
            activation_path = tmp / "dossier_fatality_activation.json"
            evidence_path.write_text(
                json.dumps(
                    {
                        "amount_cents": 45000000,
                        "currency": "EUR",
                        "source": "qonto",
                        "reference": "qonto_txn_450k",
                    }
                ),
                encoding="utf-8",
            )
            manager = AssetSettlementManager(evidence_path=evidence_path)

            decision = evaluate_fatality_guard(
                now=datetime(2026, 5, 5, 8, 0, tzinfo=ZoneInfo("Europe/Paris")),
                activation_file=activation_path,
                manager=manager,
            )

            self.assertTrue(decision.activated)
            self.assertTrue(activation_path.exists())
            payload = json.loads(activation_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "DOSSIER_FATALITY_ACTIVE")
            self.assertEqual(payload["settlement_status"]["amount_cents"], 45000000)


if __name__ == "__main__":
    unittest.main()
