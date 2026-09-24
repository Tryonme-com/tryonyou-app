import json
import os
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo

from dossier_fatality_guard import evaluate_dossier_fatality

PARIS = ZoneInfo("Europe/Paris")


class DossierFatalityGuardTest(unittest.TestCase):
    def test_thursday_without_evidence_stays_pending(self):
        moment = datetime(2026, 9, 24, 8, 0, tzinfo=PARIS)
        with patch.dict(os.environ, {}, clear=True):
            decision = evaluate_dossier_fatality(now=moment)
        self.assertEqual(decision.status, "PENDING_VALIDATION")
        self.assertFalse(decision.active)
        self.assertIn("outside_tuesday_0800_europe_paris", decision.reasons)
        self.assertIn("missing_explicit_capital_confirmation_flag", decision.reasons)
        self.assertIn("missing_evidence_path", decision.reasons)

    def test_tuesday_0800_without_bank_evidence_does_not_activate(self):
        moment = datetime(2026, 9, 22, 8, 0, tzinfo=PARIS)
        env = {"TRYONYOU_CAPITAL_450K_CONFIRMED": "true"}
        with patch.dict(os.environ, env, clear=True):
            decision = evaluate_dossier_fatality(now=moment)
        self.assertFalse(decision.active)
        self.assertNotIn("outside_tuesday_0800_europe_paris", decision.reasons)
        self.assertIn("missing_evidence_path", decision.reasons)

    def test_activates_only_with_window_flag_and_eur_reference(self):
        moment = datetime(2026, 9, 22, 8, 0, tzinfo=PARIS)
        with tempfile.TemporaryDirectory() as tmp:
            evidence = Path(tmp) / "capital.json"
            evidence.write_text(
                json.dumps(
                    {
                        "amount_eur": "450.000",
                        "currency": "EUR",
                        "reference": "QONTO-REF-TEST",
                        "source": "unit-test",
                    }
                ),
                encoding="utf-8",
            )
            env = {
                "TRYONYOU_CAPITAL_450K_CONFIRMED": "true",
                "DOSSIER_FATALITY_EVIDENCE_PATH": str(evidence),
            }
            with patch.dict(os.environ, env, clear=True):
                decision = evaluate_dossier_fatality(now=moment)
        self.assertTrue(decision.active)
        self.assertEqual(decision.status, "DOSSIER_FATALITY_ACTIVE")
        self.assertEqual(decision.evidence_summary["amount_cents"], 45_000_000)
        self.assertTrue(decision.evidence_summary["has_reference"])


if __name__ == "__main__":
    unittest.main()
