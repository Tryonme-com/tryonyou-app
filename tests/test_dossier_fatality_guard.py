from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from dossier_fatality_guard import evaluate_dossier_fatality


class TestDossierFatalityGuard(unittest.TestCase):
    def setUp(self) -> None:
        self.old_env = {
            k: os.environ.pop(k, None)
            for k in (
                "TRYONYOU_CAPITAL_450K_CONFIRMED",
                "QONTO_CAPITAL_450K_CONFIRMED",
            )
        }
        self.tmp = tempfile.TemporaryDirectory()
        self.evidence = Path(self.tmp.name) / "capital_450k_evidence.json"

    def tearDown(self) -> None:
        self.tmp.cleanup()
        for key, value in self.old_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def test_blocks_outside_tuesday_eight(self) -> None:
        os.environ["TRYONYOU_CAPITAL_450K_CONFIRMED"] = "1"
        self.evidence.write_text(
            json.dumps(
                {
                    "amount_cents": 45_000_000,
                    "currency": "EUR",
                    "source": "qonto",
                    "reference": "QONTO-OK",
                }
            ),
            encoding="utf-8",
        )
        result = evaluate_dossier_fatality(
            now=datetime(2026, 5, 4, 8, 0, tzinfo=ZoneInfo("Europe/Paris")),
            evidence_path=self.evidence,
        )
        self.assertEqual(result["status"], "PENDING_VALIDATION")
        self.assertIn("outside_tuesday_0800_window", result["reasons"])

    def test_blocks_without_flag_and_evidence(self) -> None:
        result = evaluate_dossier_fatality(
            now=datetime(2026, 5, 5, 8, 0, tzinfo=ZoneInfo("Europe/Paris")),
            evidence_path=self.evidence,
        )
        self.assertEqual(result["status"], "PENDING_VALIDATION")
        self.assertIn("confirmation_flag_missing", result["reasons"])
        self.assertIn("evidence_file_missing", result["reasons"])

    def test_activates_with_flag_window_and_valid_evidence(self) -> None:
        os.environ["TRYONYOU_CAPITAL_450K_CONFIRMED"] = "true"
        self.evidence.write_text(
            json.dumps(
                {
                    "amount_cents": 45_000_000,
                    "currency": "EUR",
                    "source": "Qonto",
                    "reference": "QONTO-20260505-450K",
                }
            ),
            encoding="utf-8",
        )
        result = evaluate_dossier_fatality(
            now=datetime(2026, 5, 5, 8, 0, tzinfo=ZoneInfo("Europe/Paris")),
            evidence_path=self.evidence,
        )
        self.assertEqual(result["status"], "DOSSIER_FATALITY_ACTIVE")
        self.assertEqual(result["evidence"]["amount_cents"], 45_000_000)


if __name__ == "__main__":
    unittest.main()
