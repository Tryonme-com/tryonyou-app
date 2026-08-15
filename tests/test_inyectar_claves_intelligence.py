import os
import sys
import tempfile
import unittest

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from inyectar_claves_intelligence import _merge_dotenv

class TestMergeDotenv(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.env_path = os.path.join(self.temp_dir.name, ".env")

    def tearDown(self):
        self.temp_dir.cleanup()

    def read_env(self):
        with open(self.env_path, encoding="utf-8") as f:
            return f.read()

    def test_merge_dotenv_new_file(self):
        updates = {"KEY1": "val1", "KEY2": "val2"}
        _merge_dotenv(self.env_path, updates)

        content = self.read_env()
        self.assertIn("KEY1=val1", content)
        self.assertIn("KEY2=val2", content)
        self.assertIn("# Jules / Intelligence merge (KEY1)", content)

    def test_merge_dotenv_existing_file_replace(self):
        with open(self.env_path, "w", encoding="utf-8") as f:
            f.write("KEY1=old_val1\nOTHER_KEY=keep_me\n")

        updates = {"KEY1": "new_val1", "NEW_KEY": "new_val"}
        _merge_dotenv(self.env_path, updates)

        content = self.read_env()
        self.assertIn("KEY1=new_val1", content)
        self.assertNotIn("KEY1=old_val1", content)
        self.assertIn("OTHER_KEY=keep_me", content)
        self.assertIn("NEW_KEY=new_val", content)

    def test_merge_dotenv_preserves_comments(self):
        initial = "# A comment\nKEY1=val1\n\n# Another comment\n"
        with open(self.env_path, "w", encoding="utf-8") as f:
            f.write(initial)

        updates = {"KEY1": "val2"}
        _merge_dotenv(self.env_path, updates)

        content = self.read_env()
        self.assertIn("# A comment", content)
        self.assertIn("KEY1=val2", content)
        self.assertIn("# Another comment", content)

    def test_merge_dotenv_empty_values_and_equals_in_value(self):
        updates = {"KEY1": "", "KEY2": "val2=xyz"}
        _merge_dotenv(self.env_path, updates)

        content = self.read_env()
        self.assertIn("KEY1=\n", content)
        self.assertIn("KEY2=val2=xyz\n", content)

if __name__ == "__main__":
    unittest.main()
