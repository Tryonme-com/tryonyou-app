import os
import tempfile
import unittest

from inyectar_claves_intelligence import _ensure_env_example, EXAMPLE_MARK

class TestEnsureEnvExample(unittest.TestCase):

    def test_ensure_env_example_missing_file(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "non_existent.env")
            _ensure_env_example(path)
            self.assertFalse(os.path.exists(path))

    def test_ensure_env_example_appends_block(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, ".env.example")
            with open(path, "w", encoding="utf-8") as f:
                f.write("EXISTING_VAR=1\n")

            _ensure_env_example(path)

            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            self.assertIn("EXISTING_VAR=1\n", content)
            self.assertIn(EXAMPLE_MARK, content)
            self.assertIn("VITE_PLAN_100_ID=TU_PRICE_ID_STRIPE", content)
            self.assertIn("STRIPE_SECRET_KEY=TU_STRIPE_SECRET_KEY", content)

    def test_ensure_env_example_already_present(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, ".env.example")
            initial_content = f"EXISTING_VAR=1\n\n{EXAMPLE_MARK}VITE_PLAN_100_ID=TU_PRICE_ID_STRIPE\nSTRIPE_SECRET_KEY=TU_STRIPE_SECRET_KEY\n"
            with open(path, "w", encoding="utf-8") as f:
                f.write(initial_content)

            _ensure_env_example(path)

            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            self.assertEqual(content, initial_content)

if __name__ == '__main__':
    unittest.main()
