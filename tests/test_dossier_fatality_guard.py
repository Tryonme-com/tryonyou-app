"""Tests para dossier_fatality_guard.py."""

from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from dossier_fatality_guard import (
    EXPECTED_AMOUNT_EUR,
    find_confirmed_inflow,
    is_tuesday_0800_or_later,
    run_guard,
)


class TestScheduleWindow(unittest.TestCase):
    def test_tuesday_after_0800_is_valid(self) -> None:
        self.assertTrue(is_tuesday_0800_or_later(datetime(2026, 4, 14, 8, 0)))
        self.assertTrue(is_tuesday_0800_or_later(datetime(2026, 4, 14, 9, 15)))

    def test_non_tuesday_or_early_is_invalid(self) -> None:
        self.assertFalse(is_tuesday_0800_or_later(datetime(2026, 4, 13, 8, 0)))  # Monday
        self.assertFalse(is_tuesday_0800_or_later(datetime(2026, 4, 14, 7, 59)))


class TestLedgerEvidence(unittest.TestCase):
    def test_find_confirmed_inflow_match(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            ledger = Path(td) / "ledger.json"
            ledger.write_text(
                json.dumps(
                    {
                        "entries": [
                            {"amount": 120000, "currency": "EUR", "status": "pending"},
                            {"amount": 450000, "currency": "EUR", "status": "confirmed"},
                        ]
                    }
                ),
                encoding="utf-8",
            )
            evidence = find_confirmed_inflow(ledger, EXPECTED_AMOUNT_EUR)
            self.assertIsNotNone(evidence)
            self.assertEqual(evidence.get("amount"), 450000)

    def test_find_confirmed_inflow_no_match(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            ledger = Path(td) / "ledger.json"
            ledger.write_text(
                json.dumps([{"amount": 449999.99, "currency": "EUR", "status": "confirmed"}]),
                encoding="utf-8",
            )
            evidence = find_confirmed_inflow(ledger, EXPECTED_AMOUNT_EUR)
            self.assertIsNone(evidence)


class TestGuardExecution(unittest.TestCase):
    def test_run_guard_activates_with_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            ledger = root / "ledger.json"
            dossier = root / "dossier_fatality.json"
            state = root / "logs" / "dossier_fatality_state.json"
            ledger.write_text(
                json.dumps(
                    {
                        "transactions": [
                            {"importe": "450.000,00 €", "moneda": "EUR", "estado": "settled"}
                        ]
                    }
                ),
                encoding="utf-8",
            )
            dossier.write_text('{"estrategia":"DOSSIER FATALITY V10"}\n', encoding="utf-8")

            result = run_guard(
                now=datetime(2026, 4, 14, 8, 0),
                ledger_path=ledger,
                dossier_path=dossier,
                state_path=state,
                expected_amount=EXPECTED_AMOUNT_EUR,
            )
            self.assertTrue(result.activated)
            self.assertTrue(state.exists())
            payload = json.loads(state.read_text(encoding="utf-8"))
            self.assertTrue(payload.get("fatality_active"))
            self.assertIn("evidence", payload)

    def test_run_guard_does_not_activate_without_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            ledger = root / "ledger.json"
            dossier = root / "dossier_fatality.json"
            state = root / "logs" / "dossier_fatality_state.json"
            ledger.write_text("[]", encoding="utf-8")
            dossier.write_text('{"estrategia":"DOSSIER FATALITY V10"}\n', encoding="utf-8")

            result = run_guard(
                now=datetime(2026, 4, 14, 8, 0),
                ledger_path=ledger,
                dossier_path=dossier,
                state_path=state,
                expected_amount=EXPECTED_AMOUNT_EUR,
            )
            self.assertFalse(result.activated)
            self.assertFalse(state.exists())


if __name__ == "__main__":
    unittest.main()
