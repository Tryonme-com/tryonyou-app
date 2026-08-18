import os
import unittest
from unittest.mock import patch

from asalto_final import _on

class TestAsaltoFinal(unittest.TestCase):
    def test_on_truthy_values(self):
        truthy_values = ["1", "true", "yes", "on", " 1 ", " TRUE ", "YeS"]
        for val in truthy_values:
            with patch.dict(os.environ, {"TEST_VAR": val}, clear=True):
                self.assertTrue(_on("TEST_VAR"), f"Expected True for value: '{val}'")

    def test_on_falsy_values(self):
        falsy_values = ["0", "false", "no", "off", " random ", ""]
        for val in falsy_values:
            with patch.dict(os.environ, {"TEST_VAR": val}, clear=True):
                self.assertFalse(_on("TEST_VAR"), f"Expected False for value: '{val}'")

    def test_on_unset_value(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(_on("UNSET_VAR"), "Expected False when env var is unset")

if __name__ == '__main__':
    unittest.main()
