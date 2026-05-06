from __future__ import annotations

import json
import os
import sys
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
        self.keys = (
            "DOSSIER_FATALITY_ARM",
            "DOSSIER_FATALITY_EVIDENCE_JSON",
            "DOSSIER_FATALITY_EVIDENCE_PATH",
            "DOSSIER_FATALITY_TARGET_CENTS",
            "DOSSIER_FATALITY_TIMEZONE",
        )
        self.old = {key: os.environ.pop(key, None) for key in self.keys}

    def tearDown(self) -> None:
        for key, value in self.old.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def test_does_not_confirm_outside_tuesday_0800(self) -> None:
        os.environ["DOSSIER_FATALITY_ARM"] = "1"
        os.environ["DOSSIER_FATALITY_EVIDENCE_JSON"] = json.dumps(
            {
                "amount_cents": 45_000_000,
                "currency": "EUR",
                "reference": "qonto-450k",
                "source": "qonto",
            }
        )

        result = evaluate_dossier_fatality(
            now=datetime(2026, 5, 6, 8, 0, tzinfo=ZoneInfo("Europe/Paris"))
        )

        self.assertEqual(result["status"], "PENDING_VALIDATION")
        self.assertEqual(result["reason"], "outside_tuesday")

    def test_requires_arm_flag_even_with_valid_evidence(self) -> None:
        os.environ["DOSSIER_FATALITY_EVIDENCE_JSON"] = json.dumps(
            {
                "amount_cents": 45_000_000,
                "currency": "EUR",
                "reference": "qonto-450k",
                "source": "qonto",
            }
        )

        result = evaluate_dossier_fatality(
            now=datetime(2026, 5, 5, 8, 30, tzinfo=ZoneInfo("Europe/Paris"))
        )

        self.assertEqual(result["status"], "PENDING_VALIDATION")
        self.assertEqual(result["reason"], "not_armed")

    def test_ready_only_with_window_arm_and_bank_evidence(self) -> None:
        os.environ["DOSSIER_FATALITY_ARM"] = "1"
        os.environ["DOSSIER_FATALITY_EVIDENCE_JSON"] = json.dumps(
            {
                "received_amount_eur": "450000",
                "currency": "EUR",
                "transaction_id": "qonto-tx-450k",
                "provider": "qonto",
            }
        )

        result = evaluate_dossier_fatality(
            now=datetime(2026, 5, 5, 8, 5, tzinfo=ZoneInfo("Europe/Paris"))
        )

        self.assertEqual(result["status"], "DOSSIER_FATALITY_READY")
        self.assertEqual(result["reason"], "bank_evidence_verified")


if __name__ == "__main__":
    unittest.main()
