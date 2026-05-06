from __future__ import annotations

import os
import unittest
from datetime import datetime
from unittest.mock import patch
from zoneinfo import ZoneInfo

from dossier_fatality_guard import (
    TARGET_AMOUNT_CENTS,
    activation_report,
    evaluate_dossier_fatality_window,
    is_activation_window,
    load_evidence,
    parse_now,
)


PARIS_TUESDAY_0800 = datetime(2026, 5, 5, 8, 15, tzinfo=ZoneInfo("Europe/Paris"))
PARIS_MONDAY_0800 = datetime(2026, 5, 4, 8, 15, tzinfo=ZoneInfo("Europe/Paris"))


class TestDossierFatalityGuard(unittest.TestCase):
    def test_parse_now_iso(self) -> None:
        dt = parse_now("2026-05-05T08:00:00+02:00")
        self.assertEqual(dt.hour, 8)

    def test_activation_window_only_tuesday_at_0800(self) -> None:
        self.assertTrue(is_activation_window(PARIS_TUESDAY_0800, "Europe/Paris"))
        self.assertFalse(is_activation_window(PARIS_MONDAY_0800, "Europe/Paris"))

    def test_pending_outside_window_even_with_valid_evidence(self) -> None:
        with patch.dict(
            os.environ,
            {
                "DOSSIER_FATALITY_ARM": "1",
                "DOSSIER_FATALITY_AMOUNT_EUR": "450000",
                "DOSSIER_FATALITY_REFERENCE": "qonto-450k",
            },
            clear=False,
        ):
            report = activation_report(now=PARIS_MONDAY_0800)

        self.assertEqual(report["status"], "PENDING_VALIDATION")
        self.assertEqual(report["reason"], "outside_tuesday_0800_window")

    def test_pending_without_arm_flag(self) -> None:
        with patch.dict(
            os.environ,
            {
                "DOSSIER_FATALITY_ARM": "",
                "DOSSIER_FATALITY_AMOUNT_CENTS": str(TARGET_AMOUNT_CENTS),
                "DOSSIER_FATALITY_REFERENCE": "qonto-450k",
            },
            clear=False,
        ):
            report = activation_report(now=PARIS_TUESDAY_0800)

        self.assertEqual(report["status"], "PENDING_VALIDATION")
        self.assertEqual(report["reason"], "fatality_not_armed")

    def test_ready_requires_arm_window_and_450k_evidence(self) -> None:
        with patch.dict(
            os.environ,
            {
                "DOSSIER_FATALITY_ARM": "1",
                "DOSSIER_FATALITY_AMOUNT_EUR": "450000",
                "DOSSIER_FATALITY_CURRENCY": "EUR",
                "DOSSIER_FATALITY_REFERENCE": "qonto-450k",
            },
            clear=False,
        ):
            report = activation_report(now=PARIS_TUESDAY_0800)

        self.assertEqual(report["status"], "DOSSIER_FATALITY_READY")
        self.assertEqual(report["evidence"]["amount_cents"], TARGET_AMOUNT_CENTS)
        self.assertTrue(report["evidence"]["reference_present"])

    def test_invalid_currency_stays_pending(self) -> None:
        with patch.dict(
            os.environ,
            {
                "DOSSIER_FATALITY_ARM": "1",
                "DOSSIER_FATALITY_AMOUNT_CENTS": str(TARGET_AMOUNT_CENTS),
                "DOSSIER_FATALITY_CURRENCY": "USD",
                "DOSSIER_FATALITY_REFERENCE": "wire-450k",
            },
            clear=False,
        ):
            report = activation_report(now=PARIS_TUESDAY_0800)

        self.assertEqual(report["status"], "PENDING_VALIDATION")
        self.assertEqual(report["reason"], "missing_or_invalid_450k_evidence")

    def test_json_evidence_env_parses_amount_eur_as_euros(self) -> None:
        with patch.dict(
            os.environ,
            {
                "DOSSIER_FATALITY_EVIDENCE_JSON": (
                    '{"amount_eur": "450000", "currency": "EUR", "reference": "bank-ref"}'
                )
            },
            clear=False,
        ):
            evidence = load_evidence()

        self.assertEqual(evidence.amount_cents, TARGET_AMOUNT_CENTS)
        self.assertTrue(evidence.valid)

    def test_compatibility_api_does_not_allow_without_evidence(self) -> None:
        outcome = evaluate_dossier_fatality_window(
            now_dt=PARIS_TUESDAY_0800,
            capital_confirmed=True,
        )
        self.assertEqual(outcome["status"], "PENDING_VALIDATION")
        self.assertFalse(outcome["activation_allowed"])


if __name__ == "__main__":
    unittest.main()
