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
        self.tmp = tempfile.TemporaryDirectory()
        self.evidence_path = Path(self.tmp.name) / "evidence.json"

    def tearDown(self) -> None:
        self.tmp.cleanup()
        self._env_patch.stop()

    def write_evidence(self, **overrides: object) -> None:
        payload: dict[str, object] = {
            "source": "qonto",
            "reference": "txn-450k",
            "amount_cents": 45_000_000,
            "currency": "EUR",
        }
        payload.update(overrides)
        self.evidence_path.write_text(json.dumps(payload), encoding="utf-8")

    def test_outside_window_never_activates(self) -> None:
        self.write_evidence()
        os.environ["TRYONYOU_CAPITAL_450K_CONFIRMED"] = "1"
        result = guard.evaluate_guard(
            now=datetime(2026, 5, 4, 8, 0, tzinfo=timezone.utc),
            evidence_path=self.evidence_path,
        )

        self.assertEqual(result["status"], "PENDING_VALIDATION")
        self.assertFalse(result["activated"])
        self.assertIn("outside_tuesday_0800", result["reasons"])

    def test_missing_flag_blocks_activation(self) -> None:
        self.write_evidence()
        result = guard.evaluate_guard(
            now=datetime(2026, 5, 5, 8, 0, tzinfo=timezone.utc),
            evidence_path=self.evidence_path,
        )

        self.assertEqual(result["status"], "PENDING_VALIDATION")
        self.assertFalse(result["activated"])
        self.assertIn("missing_confirmed_flag", result["reasons"])

    def test_invalid_amount_blocks_activation(self) -> None:
        self.write_evidence(amount_cents=44_999_999)
        os.environ["TRYONYOU_CAPITAL_450K_CONFIRMED"] = "1"
        result = guard.evaluate_guard(
            now=datetime(2026, 5, 5, 8, 0, tzinfo=timezone.utc),
            evidence_path=self.evidence_path,
        )

        self.assertEqual(result["status"], "PENDING_VALIDATION")
        self.assertFalse(result["activated"])
        self.assertIn("invalid_evidence_amount", result["reasons"])

    def test_valid_window_flag_and_evidence_activate(self) -> None:
        self.write_evidence()
        os.environ["TRYONYOU_CAPITAL_450K_CONFIRMED"] = "1"
        result = guard.evaluate_guard(
            now=datetime(2026, 5, 5, 8, 0, tzinfo=timezone.utc),
            evidence_path=self.evidence_path,
        )

        self.assertEqual(result["status"], "DOSSIER_FATALITY_ACTIVE")
        self.assertTrue(result["activated"])
        self.assertEqual(result["reasons"], [])

    def test_parse_now_accepts_z_suffix(self) -> None:
        parsed = guard.parse_now("2026-05-05T08:00:00Z")

        self.assertEqual(parsed, datetime(2026, 5, 5, 8, 0, tzinfo=timezone.utc))


if __name__ == "__main__":
    unittest.main()
