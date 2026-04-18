from __future__ import annotations

import os
import tempfile
import unittest
from datetime import datetime

from zoneinfo import ZoneInfo

import supercommit_max_autonomia as sma


class TestAmountParsing(unittest.TestCase):
    def test_parse_amount_supports_dot_thousands(self) -> None:
        self.assertEqual(sma._parse_amount("450.000"), 450000.0)

    def test_parse_amount_supports_eu_decimal(self) -> None:
        self.assertEqual(sma._parse_amount("450.000,00"), 450000.0)

    def test_parse_amount_supports_us_decimal(self) -> None:
        self.assertEqual(sma._parse_amount("450,000.00"), 450000.0)


class TestSecurityWindow(unittest.TestCase):
    def test_is_tuesday_0800(self) -> None:
        paris = ZoneInfo("Europe/Paris")
        dt = datetime(2026, 4, 21, 8, 0, tzinfo=paris)  # Tuesday
        self.assertTrue(sma._is_tuesday_0800(dt))

    def test_not_tuesday_0800(self) -> None:
        paris = ZoneInfo("Europe/Paris")
        dt = datetime(2026, 4, 21, 9, 0, tzinfo=paris)
        self.assertFalse(sma._is_tuesday_0800(dt))


class TestDossierActivation(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.root = sma.ROOT
        self.dossier_file = sma.DOSSIER_FILE
        self.dossier_log = sma.DOSSIER_LOG
        self.memory_file = sma.MEMORY_NOTES_FILE

        sma.ROOT = sma.Path(self.tmpdir.name)
        sma.DOSSIER_FILE = sma.ROOT / "dossier_fatality_activation.json"
        sma.DOSSIER_LOG = sma.ROOT / "dossier_fatality_activation_log.json"
        sma.MEMORY_NOTES_FILE = sma.ROOT / "bunker_sovereignty.ma"

        self._old_env = os.environ.copy()
        for key in (
            "TRYONYOU_CAPITAL_CONFIRMED",
            "TRYONYOU_CAPITAL_INFLOW_EUR",
            "TRYONYOU_CAPITAL_EVIDENCE_FILE",
        ):
            os.environ.pop(key, None)

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self._old_env)
        sma.ROOT = self.root
        sma.DOSSIER_FILE = self.dossier_file
        sma.DOSSIER_LOG = self.dossier_log
        sma.MEMORY_NOTES_FILE = self.memory_file
        self.tmpdir.cleanup()

    def test_dossier_activation_requires_confirmation(self) -> None:
        os.environ["TRYONYOU_CAPITAL_INFLOW_EUR"] = "450000"
        os.environ["TRYONYOU_CAPITAL_EVIDENCE_FILE"] = "evidence.txt"
        result = sma.evaluate_security(force_now=True)
        self.assertFalse(result.activated)
        self.assertIn("no confirmado", result.reason.lower())

    def test_dossier_activation_success(self) -> None:
        evidence = sma.ROOT / "evidence.txt"
        evidence.write_text("bank proof", encoding="utf-8")
        os.environ["TRYONYOU_CAPITAL_CONFIRMED"] = "true"
        os.environ["TRYONYOU_CAPITAL_INFLOW_EUR"] = "450.000,00"
        os.environ["TRYONYOU_CAPITAL_EVIDENCE_FILE"] = str(evidence)

        result = sma.evaluate_security(force_now=True)
        self.assertTrue(result.activated)
        self.assertTrue(sma.DOSSIER_FILE.exists())
        self.assertTrue(sma.DOSSIER_LOG.exists())

    def test_memory_notes_created(self) -> None:
        sec = sma.SecurityResult(
            checked=True,
            scheduled_window=True,
            confirmed=True,
            amount_eur=450000.0,
            activated=True,
            reason="ok",
        )
        sma.update_memory_notes(summary="sync ok", security=sec)
        self.assertTrue(sma.MEMORY_NOTES_FILE.exists())
        content = sma.MEMORY_NOTES_FILE.read_text(encoding="utf-8")
        self.assertIn("bunker sovereignty notes".lower(), content.lower())


if __name__ == "__main__":
    unittest.main()
