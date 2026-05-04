from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

import dossier_fatality_guard as guard


class TestDossierFatalityGuard(unittest.TestCase):
    def tearDown(self) -> None:
        for key in guard.CONFIRMATION_ENV_KEYS:
            os.environ.pop(key, None)
        os.environ.pop("DOSSIER_FATALITY_ACTIVE", None)

    def _write_evidence(self, payload: dict) -> Path:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w", encoding="utf-8")
        json.dump(payload, tmp)
        tmp.close()
        return Path(tmp.name)

    def test_outside_tuesday_window_stays_pending(self) -> None:
        evidence = self._write_evidence(
            {
                "source": "qonto",
                "reference": "QONTO-450K",
                "currency": "EUR",
                "amount_cents": guard.MIN_AMOUNT_CENTS,
            }
        )
        os.environ["TRYONYOU_CAPITAL_450K_CONFIRMED"] = "1"

        result = guard.evaluate_dossier_fatality(
            now="2026-05-04T08:00:00+02:00",
            evidence_path=evidence,
        )

        self.assertFalse(result.activated)
        self.assertEqual(result.reason, "outside_tuesday_0800_window")

    def test_missing_confirmation_flag_stays_pending(self) -> None:
        evidence = self._write_evidence(
            {
                "source": "bank",
                "reference": "BANK-450K",
                "currency": "EUR",
                "amount_eur": 450000,
            }
        )

        result = guard.evaluate_dossier_fatality(
            now="2026-05-05T08:00:00+02:00",
            evidence_path=evidence,
        )

        self.assertFalse(result.activated)
        self.assertEqual(result.reason, "missing_explicit_capital_confirmation")

    def test_invalid_evidence_stays_pending(self) -> None:
        evidence = self._write_evidence(
            {
                "source": "spreadsheet",
                "reference": "UNVERIFIED",
                "currency": "EUR",
                "amount_eur": 450000,
            }
        )
        os.environ["TRYONYOU_CAPITAL_450K_CONFIRMED"] = "1"

        result = guard.evaluate_dossier_fatality(
            now="2026-05-05T08:00:00+02:00",
            evidence_path=evidence,
        )

        self.assertFalse(result.activated)
        self.assertEqual(result.reason, "missing_or_invalid_banking_evidence")

    def test_valid_gates_activate_dossier_fatality(self) -> None:
        evidence = self._write_evidence(
            {
                "source": "qonto",
                "reference": "QONTO-450K-SETTLED",
                "currency": "EUR",
                "amount_cents": guard.MIN_AMOUNT_CENTS,
            }
        )
        os.environ["TRYONYOU_CAPITAL_450K_CONFIRMED"] = "1"

        result = guard.evaluate_dossier_fatality(
            now="2026-05-05T08:00:00+02:00",
            evidence_path=evidence,
        )

        self.assertTrue(result.activated)
        self.assertEqual(result.status, "DOSSIER_FATALITY_ACTIVE")
        self.assertEqual(os.environ["DOSSIER_FATALITY_ACTIVE"], "1")


if __name__ == "__main__":
    unittest.main()
