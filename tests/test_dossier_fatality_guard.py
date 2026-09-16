from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from dossier_fatality_guard import evaluate_dossier_fatality


PARIS = ZoneInfo("Europe/Paris")


class TestDossierFatalityGuard(unittest.TestCase):
    def _evidence(self, root: Path, payload: dict) -> str:
        path = root / "qonto_evidence.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return str(path)

    def test_pending_outside_tuesday_0800_even_with_valid_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evidence = self._evidence(
                Path(tmp),
                {
                    "amount_cents": 45_000_000,
                    "currency": "EUR",
                    "reference": "QONTO-OK-450K",
                    "source": "qonto",
                },
            )
            decision = evaluate_dossier_fatality(
                {
                    "TRYONYOU_CAPITAL_450K_CONFIRMED": "1",
                    "DOSSIER_FATALITY_EVIDENCE_PATH": evidence,
                },
                now=datetime(2026, 5, 7, 8, 0, tzinfo=PARIS),
            )

        self.assertFalse(decision.active)
        self.assertEqual(decision.status, "PENDING_VALIDATION")
        self.assertIn("outside_tuesday_0800_europe_paris", decision.reasons)

    def test_active_only_with_exact_window_flag_and_bank_reference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evidence = self._evidence(
                Path(tmp),
                {
                    "amount_eur": "450000.00",
                    "currency": "EUR",
                    "qonto_transaction_id": "QONTO-TX-450K",
                    "provider": "Qonto",
                },
            )
            decision = evaluate_dossier_fatality(
                {
                    "TRYONYOU_CAPITAL_450K_CONFIRMED": "confirmed",
                    "DOSSIER_FATALITY_EVIDENCE_PATH": evidence,
                },
                now=datetime(2026, 5, 5, 8, 0, tzinfo=PARIS),
            )

        self.assertTrue(decision.active)
        self.assertEqual(decision.status, "DOSSIER_FATALITY_ACTIVE")
        self.assertEqual(decision.reasons, [])
        self.assertEqual(decision.evidence_summary["amount_cents"], 45_000_000)

    def test_rejects_missing_reference_or_underfunded_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evidence = self._evidence(
                Path(tmp),
                {"amount_cents": 44_999_999, "currency": "EUR", "source": "qonto"},
            )
            decision = evaluate_dossier_fatality(
                {
                    "TRYONYOU_CAPITAL_450K_CONFIRMED": "1",
                    "DOSSIER_FATALITY_EVIDENCE_PATH": evidence,
                },
                now=datetime(2026, 5, 5, 8, 0, tzinfo=PARIS),
            )

        self.assertFalse(decision.active)
        self.assertIn("evidence_amount_below_450k_eur", decision.reasons)
        self.assertIn("missing_bank_or_qonto_reference", decision.reasons)


if __name__ == "__main__":
    unittest.main()
