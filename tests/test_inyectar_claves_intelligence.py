import unittest
import os
import json
import tempfile
import io
from unittest.mock import patch

from inyectar_claves_intelligence import inyectar_claves_intelligence, _run

class TestInyectarClavesIntelligence(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root_patcher = patch("inyectar_claves_intelligence.ROOT", self.temp_dir.name)
        self.root = self.root_patcher.start()

        # Save original cwd
        self.original_cwd = os.getcwd()

    def tearDown(self):
        os.chdir(self.original_cwd)
        self.root_patcher.stop()
        self.temp_dir.cleanup()

    @patch("inyectar_claves_intelligence._run")
    @patch.dict(os.environ, {}, clear=True)
    def test_no_keys_no_git(self, mock_run):
        # Create a mock .env.example file so _ensure_env_example modifies it
        example_path = os.path.join(self.temp_dir.name, ".env.example")
        with open(example_path, "w") as f:
            f.write("")

        # Default behavior: no env keys, no git
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            result = inyectar_claves_intelligence()

        self.assertEqual(result, 0)
        self.assertEqual(mock_run.call_count, 0)

        # Check that .env is not created
        env_path = os.path.join(self.temp_dir.name, ".env")
        self.assertFalse(os.path.exists(env_path))

        # Check that sync json is pending
        sync_path = os.path.join(self.temp_dir.name, "INTELLIGENCE_SYNC.json")
        self.assertTrue(os.path.exists(sync_path))
        with open(sync_path, "r", encoding="utf-8") as f:
            sync_data = json.load(f)
            self.assertEqual(sync_data["status"], "PENDING_ENV")
            self.assertEqual(sync_data["keys_injected"], [])

        # Check .env.example contains example mark
        self.assertTrue(os.path.exists(example_path))
        with open(example_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("# --- Intelligence / Stripe (inyectar_claves_intelligence) ---", content)

    @patch("inyectar_claves_intelligence._run")
    @patch.dict(os.environ, {"INJECT_VITE_STRIPE_PUBLIC_KEY": "pk_test_123"}, clear=True)
    def test_keys_in_env_no_git(self, mock_run):
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            result = inyectar_claves_intelligence()

        self.assertEqual(result, 0)
        self.assertEqual(mock_run.call_count, 0)

        env_path = os.path.join(self.temp_dir.name, ".env")
        self.assertTrue(os.path.exists(env_path))
        with open(env_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("VITE_STRIPE_PUBLIC_KEY=pk_test_123", content)

        sync_path = os.path.join(self.temp_dir.name, "INTELLIGENCE_SYNC.json")
        with open(sync_path, "r", encoding="utf-8") as f:
            sync_data = json.load(f)
            self.assertEqual(sync_data["status"], "LINKED")
            self.assertIn("VITE_STRIPE_PUBLIC_KEY", sync_data["keys_injected"])

    @patch("inyectar_claves_intelligence._run")
    @patch.dict(os.environ, {"E50_GIT_PUSH": "1"}, clear=True)
    def test_git_push_no_git_dir(self, mock_run):
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            result = inyectar_claves_intelligence()

        self.assertEqual(result, 0)
        self.assertEqual(mock_run.call_count, 0)

    @patch("inyectar_claves_intelligence._run")
    @patch.dict(os.environ, {"E50_GIT_PUSH": "1"}, clear=True)
    def test_git_push_with_git_dir_success(self, mock_run):
        os.makedirs(os.path.join(self.temp_dir.name, ".git"))
        mock_run.return_value = 0

        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            result = inyectar_claves_intelligence()

        self.assertEqual(result, 0)
        self.assertEqual(mock_run.call_count, 3)
        calls = mock_run.call_args_list
        self.assertEqual(calls[0][0][0][0], "git")
        self.assertEqual(calls[0][0][0][1], "add")
        self.assertEqual(calls[1][0][0][:2], ["git", "commit"])
        self.assertEqual(calls[2][0][0][:3], ["git", "push", "origin"])

    @patch("inyectar_claves_intelligence._run")
    @patch.dict(os.environ, {"E50_GIT_PUSH": "1", "E50_FORCE_PUSH": "1"}, clear=True)
    def test_git_force_push(self, mock_run):
        os.makedirs(os.path.join(self.temp_dir.name, ".git"))
        mock_run.return_value = 0

        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            result = inyectar_claves_intelligence()

        self.assertEqual(result, 0)
        self.assertEqual(mock_run.call_count, 3)
        calls = mock_run.call_args_list
        # check that push includes --force
        self.assertEqual(calls[2][0][0], ["git", "push", "origin", "main", "--force"])

    @patch("inyectar_claves_intelligence._run")
    @patch.dict(os.environ, {"E50_GIT_PUSH": "1"}, clear=True)
    def test_git_add_fails(self, mock_run):
        os.makedirs(os.path.join(self.temp_dir.name, ".git"))
        mock_run.return_value = 1

        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            result = inyectar_claves_intelligence()

        self.assertEqual(result, 1)
        self.assertEqual(mock_run.call_count, 1)
        self.assertEqual(mock_run.call_args[0][0][:2], ["git", "add"])

    @patch("inyectar_claves_intelligence._run")
    @patch.dict(os.environ, {"E50_GIT_PUSH": "1"}, clear=True)
    def test_git_commit_fails(self, mock_run):
        os.makedirs(os.path.join(self.temp_dir.name, ".git"))
        def mock_run_side_effect(args, **kwargs):
            if args[1] == "commit":
                return 2
            return 0
        mock_run.side_effect = mock_run_side_effect

        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            result = inyectar_claves_intelligence()

        self.assertEqual(result, 1)
        self.assertEqual(mock_run.call_count, 2)

    @patch("inyectar_claves_intelligence._run")
    @patch.dict(os.environ, {"E50_GIT_PUSH": "1"}, clear=True)
    def test_git_push_fails(self, mock_run):
        os.makedirs(os.path.join(self.temp_dir.name, ".git"))
        def mock_run_side_effect(args, **kwargs):
            if args[1] == "push":
                return 1
            return 0
        mock_run.side_effect = mock_run_side_effect

        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            result = inyectar_claves_intelligence()

        self.assertEqual(result, 1)
        self.assertEqual(mock_run.call_count, 3)

if __name__ == "__main__":
    unittest.main()
