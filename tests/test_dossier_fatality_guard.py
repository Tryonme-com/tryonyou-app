"""Tests for the safe Dossier Fatality capital guard."""

from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from dossier_fatality_guard import (
    CONFIRM_ENV,
    EVIDENCE_ENV,
    STATUS_ACTIVE,
    STATUS_PENDING,
    evaluate_guard,
)


class TestDossierFatalityGuard(unittest.TestCase):
    def test_pending_outside_tuesday_0800_window(self) -> None:
        result = evaluate_guard(
            now=datetime(2026, 5, 4, 8, 0, tzinfo=timezone.utc),
            env={CONFIRM_ENV: "1"},
        )

        self.assertEqual(result.status, STATUS_PENDING)
        self.assertFalse(result.active)
        self.assertEqual(result.reason, "outside_tuesday_0800_utc_window")

    def test_pending_without_explicit_confirmation_flag(self) -> None:
        result = evaluate_guard(now=datetime(2026, 5, 5, 8, 0, tzinfo=timezone.utc), env={})

        self.assertEqual(result.status, STATUS_PENDING)
        self.assertFalse(result.active)
        self.assertEqual(result.reason, "missing_explicit_capital_confirmation_flag")

    def test_pending_without_valid_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evidence = Path(tmp) / "capital_450k_evidence.json"
            evidence.write_text(
                json.dumps(
                    {
                        "amount_cents": 44_999_999,
                        "currency": "EUR",
                        "source": "qonto",
                        "reference": "QONTO-REF",
                    }
                ),
                encoding="utf-8",
            )

            result = evaluate_guard(
                now=datetime(2026, 5, 5, 8, 0, tzinfo=timezone.utc),
                evidence_path=evidence,
                env={CONFIRM_ENV: "1"},
            )

        self.assertEqual(result.status, STATUS_PENDING)
        self.assertFalse(result.active)
        self.assertEqual(result.reason, "missing_or_invalid_450k_evidence")

    def test_active_with_window_flag_and_bank_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evidence = Path(tmp) / "capital_450k_evidence.json"
            evidence.write_text(
                json.dumps(
                    {
                        "amount_cents": 45_000_000,
                        "currency": "EUR",
                        "source": "Qonto bank transfer",
                        "reference": "QONTO-450K-OK",
                    }
                ),
                encoding="utf-8",
            )

            result = evaluate_guard(
                now=datetime(2026, 5, 5, 8, 0, tzinfo=timezone.utc),
                evidence_path=evidence,
                env={CONFIRM_ENV: "1"},
            )

        self.assertEqual(result.status, STATUS_ACTIVE)
        self.assertTrue(result.active)
        self.assertEqual(result.reason, "verified_window_flag_and_local_evidence")

    def test_can_resolve_evidence_path_from_environment(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evidence = Path(tmp) / "capital_450k_evidence.json"
            evidence.write_text(
                json.dumps(
                    {
                        "amount_cents": 45_000_000,
                        "currency": "EUR",
                        "source": "banque qonto",
                        "reference": "ENV-QONTO-450K",
                    }
                ),
                encoding="utf-8",
            )

            result = evaluate_guard(
                now=datetime(2026, 5, 5, 8, 0, tzinfo=timezone.utc),
                env={CONFIRM_ENV: "1", EVIDENCE_ENV: str(evidence)},
            )

        self.assertEqual(result.status, STATUS_ACTIVE)
        self.assertTrue(result.active)


if __name__ == "__main__":
    unittest.main()
