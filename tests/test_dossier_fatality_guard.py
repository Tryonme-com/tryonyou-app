from __future__ import annotations

import json
import os
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from dossier_fatality_guard import (
    CONFIRMATION_ENV,
    REQUIRED_AMOUNT_CENTS,
    evaluate_fatality_guard,
    load_evidence,
)


class TestDossierFatalityGuard(unittest.TestCase):
    def setUp(self) -> None:
        self._old_env = {
            key: os.environ.pop(key, None)
            for key in (
                CONFIRMATION_ENV,
                "TRYONYOU_CAPITAL_EVIDENCE_JSON",
            )
        }

    def tearDown(self) -> None:
        for key, value in self._old_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def test_blocks_outside_tuesday_0800_window(self) -> None:
        result = evaluate_fatality_guard(
            now=datetime(2026, 5, 4, 8, 0, tzinfo=timezone.utc),
            confirmed_env="1",
        )

        self.assertEqual(result.status, "PENDING_VALIDATION")
        self.assertEqual(result.reason, "outside_tuesday_0800_utc_window")
        self.assertFalse(result.activated)

    def test_blocks_without_confirmation_env(self) -> None:
        result = evaluate_fatality_guard(
            now=datetime(2026, 5, 5, 8, 0, tzinfo=timezone.utc),
        )

        self.assertEqual(result.status, "PENDING_QONTO_VERIFICATION")
        self.assertEqual(result.reason, f"{CONFIRMATION_ENV}_not_set")
        self.assertFalse(result.activated)

    def test_blocks_without_sufficient_evidence(self) -> None:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as handle:
            json.dump({"amount_cents": 44_999_999, "reference": "partial"}, handle)
            path = Path(handle.name)

        try:
            result = evaluate_fatality_guard(
                now=datetime(2026, 5, 5, 8, 0, tzinfo=timezone.utc),
                confirmed_env="1",
                evidence_path=path,
            )
        finally:
            path.unlink()

        self.assertEqual(result.status, "PENDING_EVIDENCE")
        self.assertEqual(result.reason, "missing_or_insufficient_capital_evidence")
        self.assertEqual(result.observed_amount_cents, 44_999_999)

    def test_activates_only_with_window_confirmation_and_evidence(self) -> None:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as handle:
            json.dump({"amount_cents": REQUIRED_AMOUNT_CENTS, "reference": "qonto-ok"}, handle)
            path = Path(handle.name)

        try:
            result = evaluate_fatality_guard(
                now=datetime(2026, 5, 5, 8, 0, tzinfo=timezone.utc),
                confirmed_env="1",
                evidence_path=path,
            )
        finally:
            path.unlink()

        self.assertEqual(result.status, "DOSSIER_FATALITY_ACTIVE")
        self.assertEqual(result.observed_amount_cents, REQUIRED_AMOUNT_CENTS)
        self.assertTrue(result.activated)

    def test_load_evidence_from_json_file(self) -> None:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as handle:
            json.dump({"amount_cents": REQUIRED_AMOUNT_CENTS, "reference": "qonto-ref"}, handle)
            path = Path(handle.name)

        try:
            evidence = load_evidence(path)
        finally:
            path.unlink()

        self.assertEqual(evidence["amount_cents"], REQUIRED_AMOUNT_CENTS)
        self.assertEqual(evidence["reference"], "qonto-ref")


if __name__ == "__main__":
    unittest.main()
