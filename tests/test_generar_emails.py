"""Tests for generar_emails.py."""

from __future__ import annotations

import csv
import os
import sys
import tempfile
import unittest
from pathlib import Path

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from generar_emails import BRIDGE_TEXT, EMAILS, generar_secuencia, main


class TestConstants(unittest.TestCase):
    def test_emails_is_list(self) -> None:
        self.assertIsInstance(EMAILS, list)

    def test_emails_not_empty(self) -> None:
        self.assertGreater(len(EMAILS), 0)

    def test_each_email_has_asunto_and_cuerpo(self) -> None:
        for email in EMAILS:
            self.assertIn("Asunto", email)
            self.assertIn("Cuerpo", email)

    def test_bridge_text_is_string(self) -> None:
        self.assertIsInstance(BRIDGE_TEXT, str)

    def test_bridge_text_not_empty(self) -> None:
        self.assertTrue(BRIDGE_TEXT.strip())

    def test_emails_contain_bridge_text(self) -> None:
        for email in EMAILS:
            self.assertIn(BRIDGE_TEXT, email["Cuerpo"])


class TestGenerarSecuencia(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.output = Path(self._tmpdir.name) / "test_emails.csv"

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_returns_path(self) -> None:
        result = generar_secuencia(self.output)
        self.assertIsInstance(result, Path)

    def test_file_created(self) -> None:
        generar_secuencia(self.output)
        self.assertTrue(self.output.exists())

    def test_csv_has_header(self) -> None:
        generar_secuencia(self.output)
        with open(self.output, encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            self.assertIn("Asunto", reader.fieldnames or [])
            self.assertIn("Cuerpo", reader.fieldnames or [])

    def test_csv_row_count_matches_emails(self) -> None:
        generar_secuencia(self.output)
        with open(self.output, encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        self.assertEqual(len(rows), len(EMAILS))

    def test_csv_first_row_asunto(self) -> None:
        generar_secuencia(self.output)
        with open(self.output, encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        self.assertEqual(rows[0]["Asunto"], EMAILS[0]["Asunto"])

    def test_csv_first_row_cuerpo(self) -> None:
        generar_secuencia(self.output)
        with open(self.output, encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        self.assertEqual(rows[0]["Cuerpo"], EMAILS[0]["Cuerpo"])

    def test_csv_encoded_utf8(self) -> None:
        generar_secuencia(self.output)
        raw = self.output.read_bytes()
        # Should decode cleanly as UTF-8
        raw.decode("utf-8")

    def test_returns_same_path_as_argument(self) -> None:
        result = generar_secuencia(self.output)
        self.assertEqual(result, self.output)


class TestMain(unittest.TestCase):
    def test_main_returns_zero(self) -> None:
        # Override OUTPUT_PATH for this test to avoid writing to /tmp in CI
        import generar_emails as mod

        original = mod.OUTPUT_PATH
        with tempfile.TemporaryDirectory() as tmpdir:
            mod.OUTPUT_PATH = Path(tmpdir) / "ci_emails.csv"
            try:
                result = main()
            finally:
                mod.OUTPUT_PATH = original
        self.assertEqual(result, 0)


if __name__ == "__main__":
    unittest.main()
