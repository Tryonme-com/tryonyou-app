import json
import os
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import dossier_fatality_guard as guard


class DossierFatalityGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self._old = os.environ.get("TRYONYOU_CAPITAL_450K_CONFIRMED")
        os.environ.pop("TRYONYOU_CAPITAL_450K_CONFIRMED", None)

    def tearDown(self) -> None:
        if self._old is None:
            os.environ.pop("TRYONYOU_CAPITAL_450K_CONFIRMED", None)
        else:
            os.environ["TRYONYOU_CAPITAL_450K_CONFIRMED"] = self._old

    def _evidence(self, payload: dict) -> Path:
        tmp = tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False)
        with tmp:
            json.dump(payload, tmp)
        return Path(tmp.name)

    def test_pending_without_explicit_confirmation(self) -> None:
        evidence = self._evidence({"amount_cents": guard.MIN_AMOUNT_CENTS})
        status = guard.evaluate_guard(
            now=datetime(2026, 5, 5, 8, 0, tzinfo=timezone.utc),
            evidence_path=evidence,
        )
        self.assertEqual(status["status"], "PENDING_VALIDATION")
        self.assertIn("falta_TRYONYOU_CAPITAL_450K_CONFIRMED=1", status["reasons"])

    def test_pending_outside_tuesday_0800(self) -> None:
        os.environ["TRYONYOU_CAPITAL_450K_CONFIRMED"] = "1"
        evidence = self._evidence({"amount_cents": guard.MIN_AMOUNT_CENTS})
        status = guard.evaluate_guard(
            now=datetime(2026, 5, 4, 8, 0, tzinfo=timezone.utc),
            evidence_path=evidence,
        )
        self.assertEqual(status["status"], "PENDING_VALIDATION")
        self.assertIn("fuera_de_ventana_martes_0800", status["reasons"])

    def test_pending_without_sufficient_evidence(self) -> None:
        os.environ["TRYONYOU_CAPITAL_450K_CONFIRMED"] = "1"
        evidence = self._evidence({"amount_cents": guard.MIN_AMOUNT_CENTS - 1})
        status = guard.evaluate_guard(
            now=datetime(2026, 5, 5, 8, 0, tzinfo=timezone.utc),
            evidence_path=evidence,
        )
        self.assertEqual(status["status"], "PENDING_VALIDATION")
        self.assertIn("evidencia_qonto_450k_ausente_o_insuficiente", status["reasons"])

    def test_activated_with_window_confirmation_and_evidence(self) -> None:
        os.environ["TRYONYOU_CAPITAL_450K_CONFIRMED"] = "1"
        evidence = self._evidence({"confirmed_amount_eur": "450000.00"})
        status = guard.evaluate_guard(
            now=datetime(2026, 5, 5, 8, 0, tzinfo=timezone.utc),
            evidence_path=evidence,
        )
        self.assertEqual(status["status"], "ACTIVATED")
        self.assertEqual(status["reasons"], [])


if __name__ == "__main__":
    unittest.main()
