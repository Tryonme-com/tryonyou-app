from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

import dossier_fatality_guard as guard


class TestDossierFatalityGuard(unittest.TestCase):
    def setUp(self) -> None:
        self._old_env = os.environ.copy()
        self.tmpdir = tempfile.TemporaryDirectory()
        self.evidence = Path(self.tmpdir.name) / "capital_450k_evidence.json"
        os.environ["TRYONYOU_CAPITAL_450K_EVIDENCE"] = str(self.evidence)

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._old_env)
        self.tmpdir.cleanup()

    def _write_evidence(self, **overrides: object) -> None:
        payload: dict[str, object] = {
            "source": "qonto",
            "reference": "TRYO-450K-TEST",
            "amount_cents": 45_000_000,
            "currency": "EUR",
            "confirmed_at": "2026-05-05T07:59:59+00:00",
        }
        payload.update(overrides)
        self.evidence.write_text(json.dumps(payload), encoding="utf-8")

    def test_outside_tuesday_0800_is_pending(self) -> None:
        os.environ["TRYONYOU_CAPITAL_450K_CONFIRMED"] = "1"
        self._write_evidence()

        result = guard.evaluate_guard(now="2026-05-04T08:00:00+00:00").as_dict()

        self.assertEqual(result["status"], "PENDING_VALIDATION")
        self.assertEqual(result["reason"], "outside_tuesday_0800_window")

    def test_requires_confirmation_flag(self) -> None:
        self._write_evidence()

        result = guard.evaluate_guard(now="2026-05-05T08:00:00+00:00").as_dict()

        self.assertEqual(result["status"], "PENDING_VALIDATION")
        self.assertEqual(result["reason"], "capital_confirmation_flag_missing")

    def test_requires_valid_evidence(self) -> None:
        os.environ["TRYONYOU_CAPITAL_450K_CONFIRMED"] = "1"

        result = guard.evaluate_guard(now="2026-05-05T08:00:00+00:00").as_dict()

        self.assertEqual(result["status"], "PENDING_VALIDATION")
        self.assertEqual(result["reason"], "missing_evidence")

    def test_rejects_under_minimum_amount(self) -> None:
        os.environ["TRYONYOU_CAPITAL_450K_CONFIRMED"] = "1"
        self._write_evidence(amount_cents=44_999_999)

        result = guard.evaluate_guard(now="2026-05-05T08:00:00+00:00").as_dict()

        self.assertEqual(result["status"], "PENDING_VALIDATION")
        self.assertEqual(result["reason"], "evidence_amount_below_450k")

    def test_activates_with_flag_window_and_valid_evidence(self) -> None:
        os.environ["TRYONYOU_CAPITAL_450K_CONFIRMED"] = "1"
        self._write_evidence()

        result = guard.evaluate_guard(now="2026-05-05T08:00:00+00:00").as_dict()

        self.assertEqual(result["status"], "DOSSIER_FATALITY_ACTIVE")
        self.assertTrue(result["active"])
        self.assertEqual(result["required_amount_cents"], 45_000_000)


if __name__ == "__main__":
    unittest.main()
