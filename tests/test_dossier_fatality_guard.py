from __future__ import annotations

from datetime import datetime
import unittest
from zoneinfo import ZoneInfo

from dossier_fatality_guard import evaluate_fatality_guard


PARIS = ZoneInfo("Europe/Paris")


class TestDossierFatalityGuard(unittest.TestCase):
    def test_pending_without_bank_evidence(self) -> None:
        decision = evaluate_fatality_guard(
            now=datetime(2026, 5, 5, 8, 0, tzinfo=PARIS),
            env={"DOSSIER_FATALITY_ARM": "1"},
        )

        self.assertFalse(decision.ready)
        self.assertEqual(decision.status, "PENDING_VALIDATION")
        self.assertIn("amount_below_450000_eur", decision.reasons)
        self.assertIn("missing_bank_reference", decision.reasons)

    def test_pending_outside_tuesday_0800_paris(self) -> None:
        decision = evaluate_fatality_guard(
            now=datetime(2026, 5, 6, 8, 0, tzinfo=PARIS),
            env={
                "DOSSIER_FATALITY_ARM": "1",
                "DOSSIER_FATALITY_EVIDENCE_JSON": (
                    '{"amount_cents":45000000,"currency":"EUR",'
                    '"reference":"QONTO-OK","source":"qonto"}'
                ),
            },
        )

        self.assertFalse(decision.ready)
        self.assertIn("outside_tuesday_0800_paris", decision.reasons)

    def test_ready_only_with_window_arm_and_verified_450k_eur(self) -> None:
        decision = evaluate_fatality_guard(
            now=datetime(2026, 5, 5, 8, 0, tzinfo=PARIS),
            env={
                "DOSSIER_FATALITY_ARM": "1",
                "DOSSIER_FATALITY_EVIDENCE_JSON": (
                    '{"amount_cents":45000000,"currency":"EUR",'
                    '"reference":"QONTO-450K","source":"qonto"}'
                ),
            },
        )

        self.assertTrue(decision.ready)
        self.assertEqual(decision.status, "DOSSIER_FATALITY_READY")


if __name__ == "__main__":
    unittest.main()
