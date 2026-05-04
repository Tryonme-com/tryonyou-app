from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from dossier_fatality_guard import (
    REQUIRED_AMOUNT_CENTS,
    STATUS_ACTIVE,
    STATUS_PENDING,
    evaluate_dossier_fatality,
)


class TestDossierFatalityGuard(unittest.TestCase):
    def _evidence_file(self, payload: dict[str, object]) -> str:
        temp = tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False)
        self.addCleanup(lambda: Path(temp.name).unlink(missing_ok=True))
        json.dump(payload, temp)
        temp.close()
        return temp.name

    def test_outside_tuesday_window_is_pending(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            result = evaluate_dossier_fatality(now_iso="2026-05-04T08:00:00+00:00")

        self.assertEqual(result["status"], STATUS_PENDING)
        self.assertIn("martes", result["reason"])

    def test_missing_flag_blocks_even_with_evidence(self) -> None:
        evidence = self._evidence_file(
            {
                "source": "qonto",
                "reference": "bank-ref-450k",
                "amount_cents": REQUIRED_AMOUNT_CENTS,
                "currency": "EUR",
            }
        )
        with patch.dict(os.environ, {"TRYONYOU_CAPITAL_450K_EVIDENCE_PATH": evidence}, clear=True):
            result = evaluate_dossier_fatality(now_iso="2026-05-05T08:00:00+00:00")

        self.assertEqual(result["status"], STATUS_PENDING)
        self.assertIn("TRYONYOU_CAPITAL_450K_CONFIRMED", result["reason"])

    def test_requires_bank_or_qonto_evidence(self) -> None:
        evidence = self._evidence_file(
            {
                "source": "stripe",
                "reference": "stripe-balance",
                "amount_cents": REQUIRED_AMOUNT_CENTS,
                "currency": "EUR",
            }
        )
        with patch.dict(
            os.environ,
            {
                "TRYONYOU_CAPITAL_450K_CONFIRMED": "1",
                "TRYONYOU_CAPITAL_450K_EVIDENCE_PATH": evidence,
            },
            clear=True,
        ):
            result = evaluate_dossier_fatality(now_iso="2026-05-05T08:00:00+00:00")

        self.assertEqual(result["status"], STATUS_PENDING)
        self.assertIn("evidencia", result["reason"])

    def test_activates_with_confirmed_qonto_evidence(self) -> None:
        evidence = self._evidence_file(
            {
                "source": "Qonto",
                "reference": "qonto-confirmed-450k",
                "amount_cents": REQUIRED_AMOUNT_CENTS,
                "currency": "EUR",
            }
        )
        with patch.dict(
            os.environ,
            {
                "TRYONYOU_CAPITAL_450K_CONFIRMED": "1",
                "TRYONYOU_CAPITAL_450K_EVIDENCE_PATH": evidence,
            },
            clear=True,
        ):
            result = evaluate_dossier_fatality(now_iso="2026-05-05T08:00:00+00:00")

        self.assertEqual(result["status"], STATUS_ACTIVE)
        self.assertIn("Dossier Fatality activo", result["reason"])


if __name__ == "__main__":
    unittest.main()
