from __future__ import annotations

import json
import os
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from dossier_fatality_guard import evaluate_guard


WINDOW = datetime(2026, 5, 5, 6, 0, tzinfo=timezone.utc)


def _write_evidence(path: Path, amount_cents: int = 45_000_000, source: str = "qonto") -> None:
    path.write_text(
        json.dumps(
            {
                "amount_cents": amount_cents,
                "currency": "EUR",
                "source": source,
                "reference": "QONTO-450K-VERIFIED",
            }
        ),
        encoding="utf-8",
    )


class TestDossierFatalityGuard(unittest.TestCase):
    def test_pending_outside_tuesday_0800_window(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evidence = Path(tmp) / "capital.json"
            _write_evidence(evidence)
            with patch.dict(
                os.environ,
                {
                    "TRYONYOU_CAPITAL_450K_CONFIRMED": "1",
                    "DOSSIER_FATALITY_EVIDENCE_PATH": str(evidence),
                },
                clear=False,
            ):
                result = evaluate_guard(datetime(2026, 5, 4, 6, 0, tzinfo=timezone.utc))

        self.assertEqual(result.status, "PENDING_VALIDATION")
        self.assertEqual(result.reason, "outside_tuesday_0800_europe_paris")

    def test_pending_without_explicit_confirmation_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evidence = Path(tmp) / "capital.json"
            _write_evidence(evidence)
            with patch.dict(
                os.environ,
                {
                    "TRYONYOU_CAPITAL_450K_CONFIRMED": "",
                    "DOSSIER_FATALITY_EVIDENCE_PATH": str(evidence),
                },
                clear=False,
            ):
                result = evaluate_guard(WINDOW)

        self.assertEqual(result.status, "PENDING_VALIDATION")
        self.assertEqual(result.reason, "confirmation_flag_missing")

    def test_pending_with_insufficient_evidence_amount(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evidence = Path(tmp) / "capital.json"
            _write_evidence(evidence, amount_cents=44_999_999)
            with patch.dict(
                os.environ,
                {
                    "TRYONYOU_CAPITAL_450K_CONFIRMED": "1",
                    "DOSSIER_FATALITY_EVIDENCE_PATH": str(evidence),
                },
                clear=False,
            ):
                result = evaluate_guard(WINDOW)

        self.assertEqual(result.status, "PENDING_VALIDATION")
        self.assertEqual(result.reason, "amount_below_450k_eur")

    def test_pending_with_untrusted_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evidence = Path(tmp) / "capital.json"
            _write_evidence(evidence, source="stripe_balance_scan")
            with patch.dict(
                os.environ,
                {
                    "TRYONYOU_CAPITAL_450K_CONFIRMED": "1",
                    "DOSSIER_FATALITY_EVIDENCE_PATH": str(evidence),
                },
                clear=False,
            ):
                result = evaluate_guard(WINDOW)

        self.assertEqual(result.status, "PENDING_VALIDATION")
        self.assertEqual(result.reason, "source_not_bank_or_qonto")

    def test_active_with_window_flag_and_bank_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evidence = Path(tmp) / "capital.json"
            _write_evidence(evidence)
            with patch.dict(
                os.environ,
                {
                    "TRYONYOU_CAPITAL_450K_CONFIRMED": "1",
                    "DOSSIER_FATALITY_EVIDENCE_PATH": str(evidence),
                },
                clear=False,
            ):
                result = evaluate_guard(WINDOW)

        self.assertEqual(result.status, "DOSSIER_FATALITY_ACTIVE")
        self.assertEqual(result.amount_cents, 45_000_000)


if __name__ == "__main__":
    unittest.main()
