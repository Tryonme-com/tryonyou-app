"""Tests for launcher.py — TRYONYOU_ACTION_NOW kit generator."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from launcher import (
    _EMAIL_FILENAME,
    _FR_EMAIL,
    _OUTPUT_DIRNAME,
    generate_action_kit,
    main,
)


class TestGenerateActionKit(unittest.TestCase):
    def test_creates_output_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dest = generate_action_kit(output_dir=tmp)
            self.assertTrue(dest.is_dir())

    def test_creates_email_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dest = generate_action_kit(output_dir=tmp)
            email_path = dest / _EMAIL_FILENAME
            self.assertTrue(email_path.is_file())

    def test_email_content_contains_objet(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dest = generate_action_kit(output_dir=tmp)
            content = (dest / _EMAIL_FILENAME).read_text(encoding="utf-8")
            self.assertIn("Objet :", content)

    def test_email_content_contains_pilote(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dest = generate_action_kit(output_dir=tmp)
            content = (dest / _EMAIL_FILENAME).read_text(encoding="utf-8")
            self.assertIn("pilote", content)

    def test_email_content_is_fr_email(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dest = generate_action_kit(output_dir=tmp)
            content = (dest / _EMAIL_FILENAME).read_text(encoding="utf-8")
            self.assertEqual(content, _FR_EMAIL)

    def test_idempotent_second_call(self) -> None:
        """Calling generate_action_kit twice must not raise."""
        with tempfile.TemporaryDirectory() as tmp:
            generate_action_kit(output_dir=tmp)
            generate_action_kit(output_dir=tmp)
            self.assertTrue((Path(tmp) / _EMAIL_FILENAME).is_file())

    def test_returns_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dest = generate_action_kit(output_dir=tmp)
            self.assertIsInstance(dest, Path)

    def test_custom_output_dir_nested(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            nested = os.path.join(tmp, "sub", "dir")
            dest = generate_action_kit(output_dir=nested)
            self.assertTrue(dest.is_dir())
            self.assertTrue((dest / _EMAIL_FILENAME).is_file())


class TestMain(unittest.TestCase):
    def test_main_returns_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            code = main(["--output-dir", tmp])
            self.assertEqual(code, 0)

    def test_main_creates_email_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            main(["--output-dir", tmp])
            self.assertTrue((Path(tmp) / _EMAIL_FILENAME).is_file())


if __name__ == "__main__":
    unittest.main()
