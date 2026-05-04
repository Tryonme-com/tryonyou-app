"""Tests for Dossier Fatality guard."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from dossier_fatality_guard import MIN_CAPITAL_CENTS, evaluate_guard, load_evidence


class TestDossierFatalityGuard(unittest.TestCase):
    def setUp(self) -> None:
        self.now = datetime(2026, 5, 5, 8, 0, tzinfo=ZoneInfo("Europe/Paris"))
        self.evidence = {
            "amount_cents": MIN_CAPITAL_CENTS,
            "currency": "EUR",
            "source": "qonto",
            "reference": "txn_450k",
        }

    def tearDown(self) -> None:
        for key in (
            "TRYONYOU_CAPITAL_450K_CONFIRMED",
            "DOSSIER_FATALITY_ACTIVE",
            "DOSSIER_FATALITY_EVIDENCE_JSON",
            "DOSSIER_FATALITY_EVIDENCE_PATH",
        ):
            os.environ.pop(key, None)

    def test_pending_without_confirmation_flag(self) -> None:
        result = evaluate_guard(evidence=self.evidence, now=self.now)
        self.assertEqual(result.status, "PENDING_VALIDATION")
        self.assertIn("flag", result.reason)
        self.assertNotIn("DOSSIER_FATALITY_ACTIVE", os.environ)

    def test_pending_outside_tuesday_0800_window(self) -> None:
        os.environ["TRYONYOU_CAPITAL_450K_CONFIRMED"] = "1"
        monday = datetime(2026, 5, 4, 8, 0, tzinfo=ZoneInfo("Europe/Paris"))
        result = evaluate_guard(evidence=self.evidence, now=monday)
        self.assertEqual(result.status, "PENDING_WINDOW")
        self.assertIn("martes a las 08:00", result.reason)

    def test_pending_with_insufficient_amount(self) -> None:
        os.environ["TRYONYOU_CAPITAL_450K_CONFIRMED"] = "1"
        evidence = dict(self.evidence, amount_cents=MIN_CAPITAL_CENTS - 1)
        result = evaluate_guard(evidence=evidence, now=self.now)
        self.assertEqual(result.status, "PENDING_EVIDENCE")
        self.assertIn(">=450.000 EUR", result.reason)

    def test_activates_with_valid_window_flag_and_evidence(self) -> None:
        os.environ["TRYONYOU_CAPITAL_450K_CONFIRMED"] = "1"
        result = evaluate_guard(evidence=self.evidence, now=self.now)
        self.assertEqual(result.status, "DOSSIER_FATALITY_ACTIVE")
        self.assertTrue(result.active)
        self.assertEqual(os.environ["DOSSIER_FATALITY_ACTIVE"], "1")

    def test_loads_evidence_from_json_env(self) -> None:
        os.environ["DOSSIER_FATALITY_EVIDENCE_JSON"] = json.dumps(self.evidence)
        loaded = load_evidence()
        self.assertEqual(loaded["reference"], "txn_450k")

    def test_loads_evidence_from_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "evidence.json"
            path.write_text(json.dumps(self.evidence), encoding="utf-8")
            os.environ["DOSSIER_FATALITY_EVIDENCE_PATH"] = str(path)
            loaded = load_evidence()
        self.assertEqual(loaded["source"], "qonto")


if __name__ == "__main__":
    unittest.main()
