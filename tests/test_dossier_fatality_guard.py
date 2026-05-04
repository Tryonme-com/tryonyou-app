"""Tests del guard Dossier Fatality 450k."""

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

from dossier_fatality_guard import evaluate_guard, load_evidence


class TestDossierFatalityGuard(unittest.TestCase):
    def setUp(self) -> None:
        self.keys = (
            "TRYONYOU_CAPITAL_450K_CONFIRMED",
            "DOSSIER_FATALITY_ENABLE",
            "DOSSIER_FATALITY_EVIDENCE_JSON",
            "DOSSIER_FATALITY_TARGET_CENTS",
        )
        self.old = {k: os.environ.pop(k, None) for k in self.keys}
        self.valid_time = datetime(2026, 5, 5, 8, 0, tzinfo=ZoneInfo("Europe/Paris"))

    def tearDown(self) -> None:
        for k, v in self.old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def _evidence_file(self, payload: dict) -> str:
        tmp = tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False)
        with tmp:
            json.dump(payload, tmp)
        self.addCleanup(lambda: Path(tmp.name).unlink(missing_ok=True))
        return tmp.name

    def test_pending_without_flags(self) -> None:
        result = evaluate_guard(now=self.valid_time)
        self.assertEqual(result["status"], "PENDING_VALIDATION")
        self.assertIn("confirmation_flag_missing", result["checks"]["failures"])
        self.assertIn("evidence_missing", result["checks"]["failures"])

    def test_pending_before_tuesday_0800(self) -> None:
        os.environ["TRYONYOU_CAPITAL_450K_CONFIRMED"] = "1"
        os.environ["DOSSIER_FATALITY_ENABLE"] = "1"
        os.environ["DOSSIER_FATALITY_EVIDENCE_JSON"] = self._evidence_file(
            {"amount_cents": 45000000, "currency": "EUR", "source": "qonto", "reference": "txn_1"}
        )
        early = datetime(2026, 5, 5, 7, 59, tzinfo=ZoneInfo("Europe/Paris"))
        result = evaluate_guard(now=early)
        self.assertEqual(result["status"], "PENDING_VALIDATION")
        self.assertIn("window_not_reached", result["checks"]["failures"])

    def test_activates_with_valid_flags_window_and_evidence(self) -> None:
        os.environ["TRYONYOU_CAPITAL_450K_CONFIRMED"] = "1"
        os.environ["DOSSIER_FATALITY_ENABLE"] = "1"
        os.environ["DOSSIER_FATALITY_EVIDENCE_JSON"] = self._evidence_file(
            {"amount_cents": 45000000, "currency": "EUR", "source": "qonto", "reference": "txn_450k"}
        )
        result = evaluate_guard(now=self.valid_time)
        self.assertEqual(result["status"], "DOSSIER_FATALITY_ACTIVE")
        self.assertEqual(result["capital_target_cents"], 45000000)
        self.assertEqual(result["evidence"]["reference"], "txn_450k")

    def test_rejects_underfunded_evidence(self) -> None:
        os.environ["TRYONYOU_CAPITAL_450K_CONFIRMED"] = "1"
        os.environ["DOSSIER_FATALITY_ENABLE"] = "1"
        os.environ["DOSSIER_FATALITY_EVIDENCE_JSON"] = self._evidence_file(
            {"amount_cents": 44999999, "currency": "EUR", "source": "qonto", "reference": "txn_low"}
        )
        result = evaluate_guard(now=self.valid_time)
        self.assertEqual(result["status"], "PENDING_VALIDATION")
        self.assertIn("amount_below_target", result["checks"]["failures"])

    def test_load_evidence_accepts_json_string(self) -> None:
        os.environ["DOSSIER_FATALITY_EVIDENCE_JSON"] = json.dumps(
            {"amount_cents": 45000000, "currency": "EUR", "source": "stripe", "reference": "po_1"}
        )
        evidence = load_evidence()
        self.assertEqual(evidence["source"], "stripe")


if __name__ == "__main__":
    unittest.main()
