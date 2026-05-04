from __future__ import annotations

import json
import os
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from dossier_fatality_guard import (
    ACTIVE_STATUS,
    MIN_CAPITAL_CENTS,
    PENDING_STATUS,
    evaluate_guard,
)


class TestDossierFatalityGuard(unittest.TestCase):
    def setUp(self) -> None:
        self._old_env = {
            key: os.environ.pop(key, None)
            for key in (
                "TRYONYOU_CAPITAL_450K_CONFIRMED",
                "TRYONYOU_CAPITAL_450K_EVIDENCE",
                "DOSSIER_FATALITY_TIMEZONE",
            )
        }

    def tearDown(self) -> None:
        for key, value in self._old_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def _write_evidence(self, payload: dict[str, object]) -> str:
        tmp = tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False)
        self.addCleanup(lambda: Path(tmp.name).unlink(missing_ok=True))
        with tmp:
            json.dump(payload, tmp)
        return tmp.name

    def test_pending_outside_tuesday_0800(self) -> None:
        evidence = self._write_evidence(
            {
                "source": "qonto",
                "amount_cents": MIN_CAPITAL_CENTS,
                "currency": "EUR",
                "reference": "QONTO-OK",
                "confirmed_at": "2026-05-05T08:00:00Z",
            },
        )

        result = evaluate_guard(
            datetime(2026, 5, 4, 8, 0, tzinfo=timezone.utc),
            evidence_path=evidence,
            env={"TRYONYOU_CAPITAL_450K_CONFIRMED": "1"},
        )

        self.assertEqual(result.status, PENDING_STATUS)
        self.assertEqual(result.reason, "outside_tuesday_0800_utc_window")

    def test_pending_without_explicit_confirmation_flag(self) -> None:
        evidence = self._write_evidence(
            {
                "source": "bank",
                "amount_cents": MIN_CAPITAL_CENTS,
                "currency": "EUR",
                "reference": "BANK-OK",
                "confirmed_at": "2026-05-05T08:00:00Z",
            },
        )

        result = evaluate_guard(
            datetime(2026, 5, 5, 8, 0, tzinfo=timezone.utc),
            evidence_path=evidence,
            env={},
        )

        self.assertEqual(result.status, PENDING_STATUS)
        self.assertIn("TRYONYOU_CAPITAL_450K_CONFIRMED", result.reason)

    def test_pending_with_insufficient_amount(self) -> None:
        evidence = self._write_evidence(
            {
                "source": "qonto",
                "amount_cents": MIN_CAPITAL_CENTS - 1,
                "currency": "EUR",
                "reference": "QONTO-LOW",
                "confirmed_at": "2026-05-05T08:00:00Z",
            },
        )

        result = evaluate_guard(
            datetime(2026, 5, 5, 8, 0, tzinfo=timezone.utc),
            evidence_path=evidence,
            env={"TRYONYOU_CAPITAL_450K_CONFIRMED": "1"},
        )

        self.assertEqual(result.status, PENDING_STATUS)
        self.assertEqual(result.reason, "amount_below_required_450k")

    def test_activates_with_valid_window_flag_and_evidence(self) -> None:
        evidence = self._write_evidence(
            {
                "source": "Qonto",
                "amount_cents": MIN_CAPITAL_CENTS,
                "currency": "EUR",
                "reference": "QONTO-450K-SETTLED",
                "confirmed_at": "2026-05-05T08:00:00Z",
            },
        )

        result = evaluate_guard(
            datetime(2026, 5, 5, 8, 0, tzinfo=timezone.utc),
            evidence_path=evidence,
            env={"TRYONYOU_CAPITAL_450K_CONFIRMED": "1"},
        )

        self.assertEqual(result.status, ACTIVE_STATUS)
        self.assertEqual(result.reason, "verified_capital_evidence_present")


if __name__ == "__main__":
    unittest.main()
