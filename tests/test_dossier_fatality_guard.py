from __future__ import annotations

import json
import os
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import dossier_fatality_guard as guard


class DossierFatalityGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env_patch = patch.dict(os.environ, {}, clear=True)
        self._env_patch.start()
        self.addCleanup(self._env_patch.stop)

    def test_requires_tuesday_0800_window(self) -> None:
        result = guard.evaluate_guard(
            now=datetime(2026, 5, 4, 8, 0, tzinfo=timezone.utc),
        )

        self.assertEqual(result.status, "PENDING_VALIDATION")
        self.assertEqual(result.reason, "outside_tuesday_0800_utc_window")
        self.assertFalse(result.activated)

    def test_requires_explicit_confirmation_flag(self) -> None:
        result = guard.evaluate_guard(
            now=datetime(2026, 5, 5, 8, 0, tzinfo=timezone.utc),
        )

        self.assertEqual(result.reason, "missing_TRYONYOU_CAPITAL_450K_CONFIRMED")
        self.assertFalse(result.activated)

    def test_requires_local_evidence_file(self) -> None:
        os.environ["TRYONYOU_CAPITAL_450K_CONFIRMED"] = "1"

        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "missing.json"
            result = guard.evaluate_guard(
            now=datetime(2026, 5, 5, 8, 0, tzinfo=timezone.utc),
                evidence_path=missing,
            )

        self.assertEqual(result.reason, "missing_evidence_file")
        self.assertFalse(result.activated)

    def test_rejects_insufficient_evidence_amount(self) -> None:
        os.environ["TRYONYOU_CAPITAL_450K_CONFIRMED"] = "1"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "evidence.json"
            path.write_text(json.dumps({"amount_cents": 44_999_999}), encoding="utf-8")

            result = guard.evaluate_guard(
                now=datetime(2026, 5, 5, 8, 0, tzinfo=timezone.utc),
                evidence_path=path,
            )

        self.assertEqual(result.reason, "amount_below_450000_eur")
        self.assertFalse(result.activated)

    def test_activates_with_window_flag_and_evidence(self) -> None:
        os.environ["TRYONYOU_CAPITAL_450K_CONFIRMED"] = "1"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "evidence.json"
            path.write_text(
                json.dumps({"amount_cents": 45_000_000, "source": "qonto", "reference": "tr_123"}),
                encoding="utf-8",
            )

            result = guard.evaluate_guard(
                now=datetime(2026, 5, 5, 8, 0, tzinfo=timezone.utc),
                evidence_path=path,
            )

        self.assertEqual(result.status, "DOSSIER_FATALITY_ACTIVE")
        self.assertTrue(result.activated)
        self.assertEqual(result.reason, "verified_qonto_evidence")


if __name__ == "__main__":
    unittest.main()
