"""Tests for AbvetosTaskRunner — Firebase integrity check and task-sync flow."""

from __future__ import annotations

import os
import sys
import unittest
from io import StringIO
from unittest.mock import patch

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from abvetos_task_runner import SIREN, TASK_ID, AbvetosTaskRunner


class TestAbvetosTaskRunnerInit(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = AbvetosTaskRunner()

    def test_task_id_value(self) -> None:
        self.assertEqual(self.runner.task_id, TASK_ID)

    def test_siren_value(self) -> None:
        self.assertEqual(self.runner.siren, SIREN)

    def test_api_url_contains_task_id(self) -> None:
        self.assertIn(TASK_ID, self.runner.api_url)

    def test_api_url_targets_abvetos_repo(self) -> None:
        self.assertIn("TRYONME-TRYONYOU-ABVETOS--INTELLIGENCE--SYSTEM", self.runner.api_url)


class TestVerifyFirebaseIntegrity(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = AbvetosTaskRunner()
        for key in ("VITE_FIREBASE_API_KEY", "FIREBASE_API_KEY"):
            os.environ.pop(key, None)

    def tearDown(self) -> None:
        for key in ("VITE_FIREBASE_API_KEY", "FIREBASE_API_KEY"):
            os.environ.pop(key, None)

    def test_missing_key_returns_error(self) -> None:
        result = self.runner.verify_firebase_integrity()
        self.assertIn("❌", result)
        self.assertIn("ausente", result)

    def test_invalid_format_returns_error(self) -> None:
        os.environ["VITE_FIREBASE_API_KEY"] = "INVALID_KEY_FORMAT"
        result = self.runner.verify_firebase_integrity()
        self.assertIn("❌", result)
        self.assertIn("AIza", result)

    def test_valid_vite_key_returns_ok(self) -> None:
        os.environ["VITE_FIREBASE_API_KEY"] = "AIzaSyBtest12345"
        result = self.runner.verify_firebase_integrity()
        self.assertIn("✅", result)

    def test_valid_firebase_key_returns_ok(self) -> None:
        os.environ["FIREBASE_API_KEY"] = "AIzaSyBtest12345"
        result = self.runner.verify_firebase_integrity()
        self.assertIn("✅", result)

    def test_vite_key_has_priority_over_firebase_key(self) -> None:
        os.environ["VITE_FIREBASE_API_KEY"] = "INVALID"
        os.environ["FIREBASE_API_KEY"] = "AIzaSyBvalid"
        result = self.runner.verify_firebase_integrity()
        self.assertIn("❌", result)

    def test_result_is_string(self) -> None:
        result = self.runner.verify_firebase_integrity()
        self.assertIsInstance(result, str)

    def test_valid_key_message(self) -> None:
        os.environ["VITE_FIREBASE_API_KEY"] = "AIzaSyBtest12345"
        result = self.runner.verify_firebase_integrity()
        self.assertIn("Validada", result)


class TestSyncTaskStatus(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = AbvetosTaskRunner()
        for key in ("VITE_FIREBASE_API_KEY", "FIREBASE_API_KEY"):
            os.environ.pop(key, None)

    def tearDown(self) -> None:
        for key in ("VITE_FIREBASE_API_KEY", "FIREBASE_API_KEY"):
            os.environ.pop(key, None)

    def test_prints_task_id(self) -> None:
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.runner.sync_task_status()
            output = mock_stdout.getvalue()
        self.assertIn(TASK_ID, output)

    def test_prints_blocked_warning_when_key_missing(self) -> None:
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.runner.sync_task_status()
            output = mock_stdout.getvalue()
        self.assertIn("Bloqueo", output)

    def test_prints_supercommit_when_key_valid(self) -> None:
        os.environ["VITE_FIREBASE_API_KEY"] = "AIzaSyBtest12345"
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.runner.sync_task_status()
            output = mock_stdout.getvalue()
        self.assertIn("SUPERCOMMIT", output)

    def test_prints_integrity_status(self) -> None:
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            self.runner.sync_task_status()
            output = mock_stdout.getvalue()
        self.assertIn("❌", output)

    def test_returns_none(self) -> None:
        result = self.runner.sync_task_status()
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
