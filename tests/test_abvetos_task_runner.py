"""Tests for AbvetosTaskRunner.verify_firebase_integrity and sync_task_status."""

from __future__ import annotations

import io
import os
import sys
import unittest
from unittest.mock import patch

_API = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "api"))
if _API not in sys.path:
    sys.path.insert(0, _API)

from abvetos_task_runner import AbvetosTaskRunner


class TestVerifyFirebaseIntegrity(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = AbvetosTaskRunner()

    def test_missing_key_returns_error(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            # Remove both key names if present
            env = {k: v for k, v in os.environ.items()
                   if k not in ("VITE_FIREBASE_API_KEY", "FIREBASE_API_KEY")}
            with patch.dict(os.environ, env, clear=True):
                result = self.runner.verify_firebase_integrity()
        self.assertIn("❌", result)
        self.assertIn("ausente", result)

    def test_invalid_format_returns_error(self) -> None:
        with patch.dict(os.environ, {"VITE_FIREBASE_API_KEY": "BADFORMAT123"}, clear=False):
            result = self.runner.verify_firebase_integrity()
        self.assertIn("❌", result)
        self.assertIn("AIza", result)

    def test_valid_key_vite_prefix(self) -> None:
        with patch.dict(os.environ, {"VITE_FIREBASE_API_KEY": "AIzaSyTestKey123"}, clear=False):
            result = self.runner.verify_firebase_integrity()
        self.assertIn("✅", result)
        self.assertIn("Validada", result)

    def test_valid_key_firebase_fallback(self) -> None:
        env = {k: v for k, v in os.environ.items() if k != "VITE_FIREBASE_API_KEY"}
        env["FIREBASE_API_KEY"] = "AIzaSyFallbackKey"
        with patch.dict(os.environ, env, clear=True):
            result = self.runner.verify_firebase_integrity()
        self.assertIn("✅", result)

    def test_vite_key_takes_precedence_over_firebase_key(self) -> None:
        with patch.dict(os.environ, {
            "VITE_FIREBASE_API_KEY": "AIzaViteKey",
            "FIREBASE_API_KEY": "AIzaFallback",
        }, clear=False):
            result = self.runner.verify_firebase_integrity()
        self.assertIn("✅", result)

    def test_empty_vite_key_falls_back_to_firebase_key(self) -> None:
        with patch.dict(os.environ, {
            "VITE_FIREBASE_API_KEY": "",
            "FIREBASE_API_KEY": "AIzaFallback",
        }, clear=False):
            result = self.runner.verify_firebase_integrity()
        self.assertIn("✅", result)

    def test_returns_string(self) -> None:
        with patch.dict(os.environ, {"VITE_FIREBASE_API_KEY": "AIzaTest"}, clear=False):
            result = self.runner.verify_firebase_integrity()
        self.assertIsInstance(result, str)


class TestSyncTaskStatus(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = AbvetosTaskRunner()

    def test_sync_prints_task_id(self) -> None:
        with patch.dict(os.environ, {"VITE_FIREBASE_API_KEY": "AIzaTest"}, clear=False):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
                self.runner.sync_task_status()
                output = mock_out.getvalue()
        self.assertIn(AbvetosTaskRunner.TASK_ID, output)

    def test_sync_valid_key_prints_supercommit(self) -> None:
        with patch.dict(os.environ, {"VITE_FIREBASE_API_KEY": "AIzaTest"}, clear=False):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
                self.runner.sync_task_status()
                output = mock_out.getvalue()
        self.assertIn("SUPERCOMMIT", output)

    def test_sync_missing_key_prints_bloqueo(self) -> None:
        env = {k: v for k, v in os.environ.items()
               if k not in ("VITE_FIREBASE_API_KEY", "FIREBASE_API_KEY")}
        with patch.dict(os.environ, env, clear=True):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
                self.runner.sync_task_status()
                output = mock_out.getvalue()
        self.assertIn("Bloqueo", output)


class TestAbvetosTaskRunnerConstants(unittest.TestCase):
    def test_task_id(self) -> None:
        self.assertEqual(AbvetosTaskRunner.TASK_ID, "1b0d7405-aff9-465a-b680-92133b499ba8")

    def test_siren(self) -> None:
        self.assertEqual(AbvetosTaskRunner.SIREN, "943610196")


if __name__ == "__main__":
    unittest.main()
