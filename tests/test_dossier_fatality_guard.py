import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from dossier_fatality_guard import (
    ACTIVATION_AMOUNT_CENTS,
    evaluate_guard,
    load_evidence,
)


class TestDossierFatalityGuard(unittest.TestCase):
    def setUp(self) -> None:
        self.tuesday_8 = datetime(2026, 5, 5, 8, 0, tzinfo=ZoneInfo("Europe/Paris"))
        self.valid_evidence = {
            "amount_cents": ACTIVATION_AMOUNT_CENTS,
            "currency": "EUR",
            "source": "qonto",
            "reference": "qonto-trx-450k",
        }

    def test_requires_explicit_confirmation_flag(self) -> None:
        result = evaluate_guard(
            now=self.tuesday_8,
            env={},
            evidence=self.valid_evidence,
        )

        self.assertEqual(result["status"], "PENDING_VALIDATION")
        self.assertFalse(result["active"])
        self.assertIn("missing_confirmation_flag", result["reasons"])

    def test_requires_tuesday_0800_paris_window(self) -> None:
        result = evaluate_guard(
            now=datetime(2026, 5, 5, 7, 59, tzinfo=ZoneInfo("Europe/Paris")),
            env={"TRYONYOU_CAPITAL_450K_CONFIRMED": "1"},
            evidence=self.valid_evidence,
        )

        self.assertEqual(result["status"], "PENDING_VALIDATION")
        self.assertFalse(result["active"])
        self.assertIn("outside_tuesday_0800_paris_window", result["reasons"])

    def test_requires_sufficient_bank_evidence(self) -> None:
        result = evaluate_guard(
            now=self.tuesday_8,
            env={"TRYONYOU_CAPITAL_450K_CONFIRMED": "1"},
            evidence={
                "amount_cents": ACTIVATION_AMOUNT_CENTS - 1,
                "currency": "EUR",
                "source": "stripe",
                "reference": "po_low",
            },
        )

        self.assertEqual(result["status"], "PENDING_VALIDATION")
        self.assertFalse(result["active"])
        self.assertIn("insufficient_amount_cents", result["reasons"])

    def test_activates_with_all_invariants(self) -> None:
        result = evaluate_guard(
            now=self.tuesday_8,
            env={"TRYONYOU_CAPITAL_450K_CONFIRMED": "1"},
            evidence=self.valid_evidence,
        )

        self.assertEqual(result["status"], "DOSSIER_FATALITY_ACTIVE")
        self.assertTrue(result["active"])
        self.assertEqual(result["amount_cents"], ACTIVATION_AMOUNT_CENTS)

    def test_load_evidence_from_json_path(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "evidence.json"
            path.write_text(json.dumps(self.valid_evidence), encoding="utf-8")

            self.assertEqual(load_evidence(str(path)), self.valid_evidence)


if __name__ == "__main__":
    unittest.main()
