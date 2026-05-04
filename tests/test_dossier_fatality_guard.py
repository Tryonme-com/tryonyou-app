import json
import os
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import dossier_fatality_guard as guard


class DossierFatalityGuardTest(unittest.TestCase):
    def setUp(self) -> None:
        self._old_env = os.environ.copy()

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._old_env)

    def _write_evidence(self, payload: dict) -> str:
        tmp = tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8")
        with tmp:
            json.dump(payload, tmp)
        self.addCleanup(lambda: Path(tmp.name).unlink(missing_ok=True))
        return tmp.name

    def test_rejects_outside_tuesday_0800_window(self) -> None:
        evidence = self._write_evidence({"amount_cents": 45_000_000})
        os.environ["TRYONYOU_CAPITAL_450K_CONFIRMED"] = "1"
        result = guard.evaluate(
            now=datetime(2026, 5, 4, 8, 0, tzinfo=timezone.utc),
            evidence_path=Path(evidence),
        )
        self.assertEqual(result["status"], "PENDING_VALIDATION")
        self.assertEqual(result["reason"], "outside_tuesday_0800_window")

    def test_requires_explicit_confirmation_flag(self) -> None:
        evidence = self._write_evidence({"amount_cents": 45_000_000})
        result = guard.evaluate(
            now=datetime(2026, 5, 5, 8, 0, tzinfo=timezone.utc),
            evidence_path=Path(evidence),
        )
        self.assertEqual(result["status"], "PENDING_VALIDATION")
        self.assertEqual(result["reason"], "missing_confirmation_flag")

    def test_requires_local_evidence_amount(self) -> None:
        evidence = self._write_evidence({"amount_cents": 44_999_999})
        os.environ["TRYONYOU_CAPITAL_450K_CONFIRMED"] = "1"
        result = guard.evaluate(
            now=datetime(2026, 5, 5, 8, 0, tzinfo=timezone.utc),
            evidence_path=Path(evidence),
        )
        self.assertEqual(result["status"], "PENDING_VALIDATION")
        self.assertEqual(result["reason"], "insufficient_evidence_amount")

    def test_activates_only_with_window_flag_and_evidence(self) -> None:
        evidence = self._write_evidence({"amount_cents": 45_000_000, "source": "qonto_export"})
        os.environ["TRYONYOU_CAPITAL_450K_CONFIRMED"] = "1"
        result = guard.evaluate(
            now=datetime(2026, 5, 5, 8, 0, tzinfo=timezone.utc),
            evidence_path=Path(evidence),
        )
        self.assertEqual(result["status"], "DOSSIER_FATALITY_ARMED")
        self.assertEqual(result["amount_cents"], 45_000_000)


if __name__ == "__main__":
    unittest.main()
