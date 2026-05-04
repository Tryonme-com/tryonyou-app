from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from dossier_fatality_guard import (  # noqa: E402
    ACTIVE_STATUS,
    MINIMUM_AMOUNT_CENTS,
    PENDING_STATUS,
    evaluate_fatality_guard,
)


class DossierFatalityGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.previous_flag = os.environ.get("TRYONYOU_CAPITAL_450K_CONFIRMED")
        os.environ.pop("TRYONYOU_CAPITAL_450K_CONFIRMED", None)
        self.tuesday_0800 = datetime(2026, 5, 5, 8, 0, tzinfo=timezone.utc)

    def tearDown(self) -> None:
        if self.previous_flag is None:
            os.environ.pop("TRYONYOU_CAPITAL_450K_CONFIRMED", None)
        else:
            os.environ["TRYONYOU_CAPITAL_450K_CONFIRMED"] = self.previous_flag

    def write_evidence(self, payload: dict[str, object]) -> Path:
        temp = tempfile.NamedTemporaryFile("w", delete=False, suffix=".json", encoding="utf-8")
        with temp:
            json.dump(payload, temp)
        return Path(temp.name)

    def test_pending_outside_tuesday_0800_window(self) -> None:
        os.environ["TRYONYOU_CAPITAL_450K_CONFIRMED"] = "1"
        evidence = self.write_evidence(
            {
                "source": "qonto",
                "reference": "bank-ref-450k",
                "amount_cents": MINIMUM_AMOUNT_CENTS,
                "currency": "EUR",
            }
        )

        result = evaluate_fatality_guard(
            now=datetime(2026, 5, 4, 8, 0, tzinfo=timezone.utc),
            evidence_path=evidence,
        )

        self.assertEqual(result.status, PENDING_STATUS)
        self.assertFalse(result.active)
        self.assertEqual(result.reason, "outside_tuesday_0800_window")

    def test_pending_without_confirmation_flag(self) -> None:
        evidence = self.write_evidence(
            {
                "source": "qonto",
                "reference": "bank-ref-450k",
                "amount_cents": MINIMUM_AMOUNT_CENTS,
                "currency": "EUR",
            }
        )

        result = evaluate_fatality_guard(now=self.tuesday_0800, evidence_path=evidence)

        self.assertEqual(result.status, PENDING_STATUS)
        self.assertFalse(result.active)
        self.assertEqual(result.reason, "missing_explicit_capital_confirmation")

    def test_pending_without_bank_evidence(self) -> None:
        os.environ["TRYONYOU_CAPITAL_450K_CONFIRMED"] = "1"

        result = evaluate_fatality_guard(
            now=self.tuesday_0800,
            evidence_path=Path("/tmp/tryonyou-missing-evidence.json"),
        )

        self.assertEqual(result.status, PENDING_STATUS)
        self.assertFalse(result.active)
        self.assertEqual(result.reason, "evidence_amount_below_450000_eur")

    def test_pending_when_amount_is_below_450k(self) -> None:
        os.environ["TRYONYOU_CAPITAL_450K_CONFIRMED"] = "1"
        evidence = self.write_evidence(
            {
                "source": "qonto",
                "reference": "bank-ref-low",
                "amount_cents": MINIMUM_AMOUNT_CENTS - 1,
                "currency": "EUR",
            }
        )

        result = evaluate_fatality_guard(now=self.tuesday_0800, evidence_path=evidence)

        self.assertEqual(result.status, PENDING_STATUS)
        self.assertFalse(result.active)
        self.assertEqual(result.reason, "evidence_amount_below_450000_eur")

    def test_activates_with_tuesday_flag_and_valid_evidence(self) -> None:
        os.environ["TRYONYOU_CAPITAL_450K_CONFIRMED"] = "1"
        evidence = self.write_evidence(
            {
                "source": "qonto",
                "reference": "bank-ref-450k",
                "amount_cents": MINIMUM_AMOUNT_CENTS,
                "currency": "EUR",
            }
        )

        result = evaluate_fatality_guard(now=self.tuesday_0800, evidence_path=evidence)

        self.assertEqual(result.status, ACTIVE_STATUS)
        self.assertTrue(result.active)
        self.assertEqual(result.reason, "capital_verified_and_guard_window_valid")


if __name__ == "__main__":
    unittest.main()
