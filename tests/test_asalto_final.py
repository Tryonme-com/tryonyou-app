import unittest
import os
from unittest.mock import patch

from asalto_final import _on

class TestAsaltoFinal(unittest.TestCase):
    def test_on_truthy_values(self):
        """Test that _on returns True for various truthy values, including different casings and whitespaces."""
        truthy_values = ["1", "true", "yes", "on", "  True  ", "YES", "On", " 1 "]
        for val in truthy_values:
            with self.subTest(val=val):
                with patch.dict(os.environ, {"TEST_ENV_VAR": val}, clear=True):
                    self.assertTrue(_on("TEST_ENV_VAR"))

    def test_on_falsy_values(self):
        """Test that _on returns False for various falsy values."""
        falsy_values = ["0", "false", "no", "off", "anything_else", ""]
        for val in falsy_values:
            with self.subTest(val=val):
                with patch.dict(os.environ, {"TEST_ENV_VAR": val}, clear=True):
                    self.assertFalse(_on("TEST_ENV_VAR"))

    def test_on_missing_value(self):
        """Test that _on returns False when the environment variable is not present."""
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(_on("MISSING_ENV_VAR"))

if __name__ == '__main__':
    unittest.main()
