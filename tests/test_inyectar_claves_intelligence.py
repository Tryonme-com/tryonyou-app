import unittest
import os
import tempfile
import json
from unittest.mock import patch

from inyectar_claves_intelligence import inyectar_claves_intelligence, ROOT

class TestInyectarClavesIntelligence(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = self.temp_dir.name
        self.env_patcher = patch.dict(os.environ, {"E50_PROJECT_ROOT": self.root}, clear=True)
        self.env_patcher.start()

        # We need to mock ROOT in the module since it was already evaluated
        self.root_patcher = patch("inyectar_claves_intelligence.ROOT", self.root)
        self.root_patcher.start()

    def tearDown(self):
        self.root_patcher.stop()
        self.env_patcher.stop()
        self.temp_dir.cleanup()

    @patch("inyectar_claves_intelligence._git_on", return_value=False)
    @patch("inyectar_claves_intelligence._force_push_on", return_value=False)
    def test_inyectar_claves_intelligence(self, mock_force, mock_git):
        # Setup env variables that the script looks for
        os.environ["INJECT_VITE_STRIPE_PUBLIC_KEY"] = "pk_test_123"
        os.environ["INJECT_STRIPE_SECRET_KEY"] = "sk_test_456"

        # Create an initial .env
        env_file = os.path.join(self.root, ".env")
        with open(env_file, "w") as f:
            f.write("EXISTING_KEY=existing_val\n")

        # Run function
        result = inyectar_claves_intelligence()

        self.assertEqual(result, 0)

        # Check .env was updated
        with open(env_file, "r") as f:
            env_content = f.read()

        self.assertIn("EXISTING_KEY=existing_val", env_content)
        self.assertIn("VITE_STRIPE_PUBLIC_KEY=pk_test_123", env_content)
        self.assertIn("STRIPE_SECRET_KEY=sk_test_456", env_content)

        # Check INTELLIGENCE_SYNC.json was created
        sync_file = os.path.join(self.root, "INTELLIGENCE_SYNC.json")
        self.assertTrue(os.path.exists(sync_file))

        with open(sync_file, "r") as f:
            sync_data = json.load(f)

        self.assertEqual(sync_data["status"], "LINKED")
        self.assertIn("VITE_STRIPE_PUBLIC_KEY", sync_data["keys_injected"])
        self.assertIn("STRIPE_SECRET_KEY", sync_data["keys_injected"])

    @patch("inyectar_claves_intelligence._git_on", return_value=False)
    def test_inyectar_claves_empty_env(self, mock_git):
        # Run function without any environment variables
        result = inyectar_claves_intelligence()
        self.assertEqual(result, 0)

        # Check INTELLIGENCE_SYNC.json was created with PENDING_ENV
        sync_file = os.path.join(self.root, "INTELLIGENCE_SYNC.json")
        self.assertTrue(os.path.exists(sync_file))

        with open(sync_file, "r") as f:
            sync_data = json.load(f)

        self.assertEqual(sync_data["status"], "PENDING_ENV")
        self.assertEqual(len(sync_data["keys_injected"]), 0)

    @patch("inyectar_claves_intelligence._git_on", return_value=True)
    @patch("inyectar_claves_intelligence._run", return_value=0)
    def test_inyectar_claves_git_execution(self, mock_run, mock_git):
        # Ensure .git directory exists to pass git check
        os.makedirs(os.path.join(self.root, ".git"), exist_ok=True)

        result = inyectar_claves_intelligence()
        self.assertEqual(result, 0)

        # Check that git commands were executed
        self.assertTrue(mock_run.called)

        # The exact number of calls depends on git add, commit, push
        # Here we just check that git was called
        calls = mock_run.call_args_list
        self.assertTrue(any(call[0][0][0] == "git" for call in calls))

    @patch("inyectar_claves_intelligence._git_on", return_value=False)
    def test_ensure_env_example_updated(self, mock_git):
        # Create an initial empty .env.example
        example_file = os.path.join(self.root, ".env.example")
        with open(example_file, "w") as f:
            f.write("SOME_VAR=foo\n")

        # Run function
        result = inyectar_claves_intelligence()
        self.assertEqual(result, 0)

        # Check that .env.example contains the Stripe plan block
        with open(example_file, "r") as f:
            content = f.read()

        self.assertIn("VITE_PLAN_100_ID=TU_PRICE_ID_STRIPE", content)
        self.assertIn("STRIPE_SECRET_KEY=TU_STRIPE_SECRET_KEY", content)

if __name__ == "__main__":
    unittest.main()
