from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from global_settlement_manager import GlobalSettlementManager, SettlementConfig


class TestGlobalSettlementManager(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.evidence = Path(self.tmp.name) / "evidence.json"
        self.audit = Path(self.tmp.name) / "audit.jsonl"
        self.old_env = {
            key: os.environ.pop(key, None)
            for key in (
                "TRYONYOU_CAPITAL_450K_CONFIRMED",
                "QONTO_450K_CONFIRMED",
                "CAPITAL_450K_CONFIRMED",
            )
        }

    def tearDown(self) -> None:
        for key, value in self.old_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        self.tmp.cleanup()

    def _manager(self) -> GlobalSettlementManager:
        return GlobalSettlementManager(
            SettlementConfig(
                target_amount_cents=45_000_000,
                evidence_path=self.evidence,
                audit_log_path=self.audit,
            )
        )

    def test_pending_without_flag_or_evidence(self) -> None:
        result = self._manager().validate_global_settlement()

        self.assertEqual(result["status"], "PENDING_VALIDATION")
        self.assertFalse(result["verified"])
        self.assertEqual(result["reason"], "confirmation_flag_missing")
        self.assertTrue(self.audit.exists())

    def test_pending_when_flag_set_but_evidence_missing(self) -> None:
        os.environ["TRYONYOU_CAPITAL_450K_CONFIRMED"] = "1"

        result = self._manager().validate_global_settlement()

        self.assertEqual(result["status"], "PENDING_VALIDATION")
        self.assertEqual(result["reason"], "evidence_file_missing")

    def test_verified_with_flag_and_valid_bank_evidence(self) -> None:
        os.environ["TRYONYOU_CAPITAL_450K_CONFIRMED"] = "1"
        self.evidence.write_text(
            json.dumps(
                {
                    "amount_cents": 45_000_000,
                    "currency": "EUR",
                    "source": "qonto",
                    "reference": "QONTO-E2E-450K",
                }
            ),
            encoding="utf-8",
        )

        result = self._manager().validate_global_settlement()

        self.assertEqual(result["status"], "VERIFIED")
        self.assertTrue(result["verified"])
        self.assertEqual(result["amount_cents"], 45_000_000)
        audit_rows = self.audit.read_text(encoding="utf-8").strip().splitlines()
        self.assertEqual(len(audit_rows), 1)
        self.assertEqual(json.loads(audit_rows[0])["event"], "global_settlement_validation")

    def test_rejects_insufficient_amount(self) -> None:
        os.environ["TRYONYOU_CAPITAL_450K_CONFIRMED"] = "1"
        self.evidence.write_text(
            json.dumps(
                {
                    "amount_cents": 44_999_999,
                    "currency": "EUR",
                    "source": "bank",
                    "reference": "BANK-LOW",
                }
            ),
            encoding="utf-8",
        )

        result = self._manager().validate_global_settlement()

        self.assertEqual(result["status"], "PENDING_VALIDATION")
        self.assertEqual(result["reason"], "amount_below_target")


if __name__ == "__main__":
    unittest.main()
