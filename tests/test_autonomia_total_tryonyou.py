"""Tests para autonomia_total_tryonyou.py (orquestación segura)."""

from __future__ import annotations

import argparse
import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

import autonomia_total_tryonyou as att


class TestAmountParsing(unittest.TestCase):
    def test_parse_integer(self) -> None:
        self.assertEqual(att.parse_eur_amount(450000), 450000)

    def test_parse_european_format(self) -> None:
        self.assertEqual(att.parse_eur_amount("450.000,00€"), 450000)

    def test_parse_us_format(self) -> None:
        self.assertEqual(att.parse_eur_amount("450,000.00"), 450000)

    def test_parse_plain_string(self) -> None:
        self.assertEqual(att.parse_eur_amount("450000"), 450000)

    def test_parse_invalid_raises(self) -> None:
        with self.assertRaises(ValueError):
            att.parse_eur_amount("no-es-importe")


class TestSchedule(unittest.TestCase):
    def test_tuesday_at_0800_true(self) -> None:
        # Martes 14/04/2026 08:00
        now = datetime(2026, 4, 14, 8, 0, 0)
        self.assertTrue(att.should_run_tuesday_0800(now))

    def test_tuesday_wrong_minute_false(self) -> None:
        now = datetime(2026, 4, 14, 8, 1, 0)
        self.assertFalse(att.should_run_tuesday_0800(now))

    def test_sunday_0800_false(self) -> None:
        now = datetime(2026, 4, 12, 8, 0, 0)
        self.assertFalse(att.should_run_tuesday_0800(now))


class TestEvidenceEvaluation(unittest.TestCase):
    def test_valid_evidence_ok(self) -> None:
        result = att.evaluate_capital_evidence(
            {"confirmed": True, "status": "received", "amount_eur": "450.000€"}
        )
        self.assertTrue(result.ok)
        self.assertIn("450000", result.message)

    def test_missing_confirmation_not_ok(self) -> None:
        result = att.evaluate_capital_evidence(
            {"confirmed": False, "status": "received", "amount_eur": 450000}
        )
        self.assertFalse(result.ok)

    def test_wrong_amount_not_ok(self) -> None:
        result = att.evaluate_capital_evidence(
            {"confirmed": True, "status": "received", "amount_eur": 451000}
        )
        self.assertFalse(result.ok)


class TestOrchestration(unittest.TestCase):
    def test_run_without_security_check_returns_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            memory = Path(tmp) / "bunker_sovereignty.ma"
            evidence = Path(tmp) / "capital_entry_evidence.json"
            args = argparse.Namespace(
                memory_file=str(memory),
                capital_evidence=str(evidence),
                skip_supercommit=True,
                full_supercommit=False,
                force_security_check=False,
                strict_notify=False,
            )
            rc = att.run_orchestration(args, now=datetime(2026, 4, 12, 10, 0, 0))
            self.assertEqual(rc, 0)
            self.assertTrue(memory.exists())

    def test_force_security_check_without_evidence_returns_two(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            memory = Path(tmp) / "bunker_sovereignty.ma"
            evidence = Path(tmp) / "capital_entry_evidence.json"
            args = argparse.Namespace(
                memory_file=str(memory),
                capital_evidence=str(evidence),
                skip_supercommit=True,
                full_supercommit=False,
                force_security_check=True,
                strict_notify=False,
            )
            rc = att.run_orchestration(args, now=datetime(2026, 4, 12, 10, 0, 0))
            self.assertEqual(rc, 2)

    def test_force_security_check_with_valid_evidence_creates_log(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            memory = Path(tmp) / "bunker_sovereignty.ma"
            evidence = Path(tmp) / "capital_entry_evidence.json"
            logs_dir = Path(tmp) / "logs"
            log_file = logs_dir / "dossier_fatality_activation.json"
            evidence.write_text(
                json.dumps(
                    {"confirmed": True, "status": "received", "amount_eur": "450000"}
                ),
                encoding="utf-8",
            )

            previous_log_path = att.DOSSIER_LOG_FILE
            att.DOSSIER_LOG_FILE = log_file
            try:
                args = argparse.Namespace(
                    memory_file=str(memory),
                    capital_evidence=str(evidence),
                    skip_supercommit=True,
                    full_supercommit=False,
                    force_security_check=True,
                    strict_notify=False,
                )
                rc = att.run_orchestration(args, now=datetime(2026, 4, 14, 8, 0, 0))
                self.assertEqual(rc, 0)
                self.assertTrue(log_file.exists())
                payload = json.loads(log_file.read_text(encoding="utf-8"))
                self.assertEqual(payload["mode"], "GUARD_ONLY")
                self.assertEqual(payload["amount_expected_eur"], 450000)
            finally:
                att.DOSSIER_LOG_FILE = previous_log_path


if __name__ == "__main__":
    unittest.main()
