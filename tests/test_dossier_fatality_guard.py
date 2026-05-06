from __future__ import annotations

import json
import os
import unittest
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
import sys

if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from dossier_fatality_guard import evaluate_fatality_guard


PARIS = ZoneInfo("Europe/Paris")


class TestDossierFatalityGuard(unittest.TestCase):
    def setUp(self) -> None:
        self._old_env = os.environ.copy()

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._old_env)

    def _ready_env(self) -> None:
        os.environ["DOSSIER_FATALITY_ARM"] = "1"
        os.environ["DOSSIER_FATALITY_EVIDENCE_JSON"] = json.dumps(
            {
                "amount_cents": 45_000_000,
                "currency": "EUR",
                "reference": "QONTO-450K",
                "status": "completed",
            }
        )

    def test_pending_outside_tuesday_window(self) -> None:
        self._ready_env()
        result = evaluate_fatality_guard(now=datetime(2026, 5, 6, 8, 0, tzinfo=PARIS))
        self.assertEqual(result.status, "PENDING_VALIDATION")
        self.assertEqual(result.reason, "outside_tuesday_0800_paris")

    def test_pending_without_explicit_arm(self) -> None:
        os.environ["DOSSIER_FATALITY_EVIDENCE_JSON"] = json.dumps(
            {
                "amount_cents": 45_000_000,
                "currency": "EUR",
                "reference": "QONTO-450K",
            }
        )
        result = evaluate_fatality_guard(now=datetime(2026, 5, 5, 8, 0, tzinfo=PARIS))
        self.assertEqual(result.status, "PENDING_VALIDATION")
        self.assertEqual(result.reason, "fatality_not_armed")

    def test_ready_with_evidence_on_window(self) -> None:
        self._ready_env()
        result = evaluate_fatality_guard(now=datetime(2026, 5, 5, 8, 0, tzinfo=PARIS))
        self.assertEqual(result.status, "DOSSIER_FATALITY_READY")
        self.assertEqual(result.amount_cents, 45_000_000)
        self.assertTrue(result.active)

    def test_reads_evidence_path(self) -> None:
        tmp = Path(os.environ.get("TMPDIR") or "/tmp") / "tryonyou_fatality_evidence.json"
        tmp.write_text(
            json.dumps(
                {
                    "amount_cents": 45_000_000,
                    "currency": "EUR",
                    "reference": "QONTO-PATH",
                }
            ),
            encoding="utf-8",
        )
        self.addCleanup(lambda: tmp.unlink(missing_ok=True))
        os.environ["DOSSIER_FATALITY_ARM"] = "1"
        os.environ["DOSSIER_FATALITY_EVIDENCE_PATH"] = str(tmp)

        result = evaluate_fatality_guard(now=datetime(2026, 5, 5, 8, 0, tzinfo=PARIS))

        self.assertEqual(result.status, "DOSSIER_FATALITY_READY")
        self.assertEqual(result.reference, "QONTO-PATH")


if __name__ == "__main__":
    unittest.main()
