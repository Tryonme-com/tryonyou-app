"""Dossier Fatality permanece en validación sin evidencia bancaria real."""
from __future__ import annotations

import json
import unittest
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from dossier_fatality_guard import evaluate_dossier_fatality

PARIS = ZoneInfo("Europe/Paris")


class DossierFatalityGuardTest(unittest.TestCase):
    def test_friday_without_evidence_stays_pending(self) -> None:
        friday = datetime(2026, 9, 25, 11, 49, tzinfo=PARIS)
        decision = evaluate_dossier_fatality(env={}, now=friday)
        self.assertEqual(decision.status, "PENDING_VALIDATION")
        self.assertFalse(decision.active)
        self.assertIn("outside_tuesday_0800_europe_paris", decision.reasons)
        self.assertIn("missing_explicit_capital_confirmation_flag", decision.reasons)
        self.assertIn("missing_evidence_path", decision.reasons)

    def test_tuesday_0800_still_pending_without_bank_evidence(self) -> None:
        tuesday = datetime(2026, 9, 29, 8, 0, tzinfo=PARIS)
        decision = evaluate_dossier_fatality(
            env={"TRYONYOU_CAPITAL_450K_CONFIRMED": "1"},
            now=tuesday,
        )
        self.assertEqual(decision.status, "PENDING_VALIDATION")
        self.assertNotIn("outside_tuesday_0800_europe_paris", decision.reasons)
        self.assertIn("missing_evidence_path", decision.reasons)

    def test_activates_only_with_window_flag_and_eur_reference(self) -> None:
        tuesday = datetime(2026, 9, 29, 8, 0, tzinfo=PARIS)
        evidence = Path("/tmp/tryonyou-fatality-evidence.json")
        evidence.write_text(
            json.dumps(
                {
                    "amount_eur": "450000",
                    "currency": "EUR",
                    "reference": "QONTO-TEST-REF",
                    "source": "unit-test",
                }
            ),
            encoding="utf-8",
        )
        decision = evaluate_dossier_fatality(
            env={
                "TRYONYOU_CAPITAL_450K_CONFIRMED": "yes",
                "DOSSIER_FATALITY_EVIDENCE_PATH": str(evidence),
            },
            now=tuesday,
        )
        self.assertEqual(decision.status, "DOSSIER_FATALITY_ACTIVE")
        self.assertTrue(decision.active)
        self.assertEqual(decision.evidence_summary["amount_cents"], 45_000_000)
        self.assertEqual(decision.evidence_summary["currency"], "EUR")


if __name__ == "__main__":
    unittest.main()
