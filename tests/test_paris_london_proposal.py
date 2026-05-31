"""Tests for the Paris-London proposal generator (OP_CASH_PARIS_LONDON)."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
_API = os.path.join(_ROOT, "api")
for _p in (_ROOT, _API):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from paris_london_proposal import (
    IDENTITY,
    TARGETS,
    build_london_proposal,
    build_paris_proposal,
    generate_proposals,
)


class TestIdentity(unittest.TestCase):
    def test_brand_name(self) -> None:
        self.assertEqual(IDENTITY["brand"], "TryOnYou (Trae y Yo)")

    def test_patent(self) -> None:
        self.assertEqual(IDENTITY["patent"], "PCT/EP2025/067317")

    def test_precision(self) -> None:
        self.assertEqual(IDENTITY["precision"], "0.08mm")

    def test_price(self) -> None:
        self.assertEqual(IDENTITY["price"], "250€ / £210")

    def test_stripe_link_is_make_webhook(self) -> None:
        self.assertIn("hook.eu2.make.com", IDENTITY["stripe_link"])


class TestTargets(unittest.TestCase):
    def test_paris_key_present(self) -> None:
        self.assertIn("PARIS", TARGETS)

    def test_london_key_present(self) -> None:
        self.assertIn("LONDON", TARGETS)

    def test_paris_brands_count(self) -> None:
        self.assertEqual(len(TARGETS["PARIS"]), 6)

    def test_london_brands_count(self) -> None:
        self.assertEqual(len(TARGETS["LONDON"]), 6)

    def test_jacquemus_in_paris(self) -> None:
        self.assertIn("Jacquemus", TARGETS["PARIS"])

    def test_corteiz_in_london(self) -> None:
        self.assertIn("Corteiz", TARGETS["LONDON"])


class TestBuildParisProposal(unittest.TestCase):
    def setUp(self) -> None:
        self.text = build_paris_proposal()

    def test_contains_precision(self) -> None:
        self.assertIn("0.08mm", self.text)

    def test_contains_patent(self) -> None:
        self.assertIn("PCT/EP2025/067317", self.text)

    def test_contains_price(self) -> None:
        self.assertIn("250€", self.text)

    def test_contains_stripe_link(self) -> None:
        self.assertIn(IDENTITY["stripe_link"], self.text)

    def test_subject_in_french(self) -> None:
        self.assertIn("OBJET", self.text)

    def test_returns_string(self) -> None:
        self.assertIsInstance(self.text, str)


class TestBuildLondonProposal(unittest.TestCase):
    def setUp(self) -> None:
        self.text = build_london_proposal()

    def test_contains_precision(self) -> None:
        self.assertIn("0.08mm", self.text)

    def test_contains_patent(self) -> None:
        self.assertIn("PCT/EP2025/067317", self.text)

    def test_contains_price(self) -> None:
        self.assertIn("£210", self.text)

    def test_contains_stripe_link(self) -> None:
        self.assertIn(IDENTITY["stripe_link"], self.text)

    def test_subject_in_english(self) -> None:
        self.assertIn("SUBJECT", self.text)

    def test_returns_string(self) -> None:
        self.assertIsInstance(self.text, str)


class TestGenerateProposals(unittest.TestCase):
    def test_creates_output_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            generate_proposals(output_dir=tmp)
            self.assertTrue(os.path.exists(os.path.join(tmp, "FR_Paris_Audit.md")))
            self.assertTrue(os.path.exists(os.path.join(tmp, "UK_London_Audit.md")))

    def test_paris_file_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            generate_proposals(output_dir=tmp)
            with open(os.path.join(tmp, "FR_Paris_Audit.md"), encoding="utf-8") as fh:
                content = fh.read()
            self.assertIn("OBJET", content)
            self.assertIn("PCT/EP2025/067317", content)

    def test_london_file_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            generate_proposals(output_dir=tmp)
            with open(os.path.join(tmp, "UK_London_Audit.md"), encoding="utf-8") as fh:
                content = fh.read()
            self.assertIn("SUBJECT", content)
            self.assertIn("PCT/EP2025/067317", content)

    def test_idempotent_second_call(self) -> None:
        """Calling generate_proposals twice must not raise."""
        with tempfile.TemporaryDirectory() as tmp:
            generate_proposals(output_dir=tmp)
            generate_proposals(output_dir=tmp)
            self.assertTrue(os.path.exists(os.path.join(tmp, "FR_Paris_Audit.md")))


if __name__ == "__main__":
    unittest.main()
