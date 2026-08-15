import os
import unittest
from unittest.mock import patch

from fix_environment import _deep_clean_on


class TestFixEnvironment(unittest.TestCase):
    def test_deep_clean_on_truthy(self):
        truthy_values = ["1", "true", "yes", "on", " 1 ", " TrUe ", "  YES  ", "oN"]
        for val in truthy_values:
            with self.subTest(val=val):
                with patch.dict(os.environ, {"E50_DEEP_CLEAN": val}, clear=True):
                    self.assertTrue(_deep_clean_on())

    def test_deep_clean_on_falsy(self):
        falsy_values = ["0", "false", "no", "off", "", " ", "something_else"]
        for val in falsy_values:
            with self.subTest(val=val):
                with patch.dict(os.environ, {"E50_DEEP_CLEAN": val}, clear=True):
                    self.assertFalse(_deep_clean_on())

    def test_deep_clean_on_unset(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(_deep_clean_on())


if __name__ == "__main__":
    unittest.main()
