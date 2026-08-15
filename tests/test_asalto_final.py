import unittest
import os
from unittest.mock import patch

from asalto_final import _on

class TestAsaltoFinal(unittest.TestCase):
    def test_on(self):
        with patch.dict(os.environ, {"TEST_VAR_TRUE": "1", "TEST_VAR_FALSE": "0", "TEST_VAR_YES": "yes", "TEST_VAR_NO": "no", "TEST_VAR_TRUE_UPPER": "TRUE", "TEST_VAR_ON": "on", "TEST_VAR_OFF": "off"}, clear=True):
            self.assertTrue(_on("TEST_VAR_TRUE"))
            self.assertTrue(_on("TEST_VAR_YES"))
            self.assertTrue(_on("TEST_VAR_TRUE_UPPER"))
            self.assertTrue(_on("TEST_VAR_ON"))
            self.assertFalse(_on("TEST_VAR_FALSE"))
            self.assertFalse(_on("TEST_VAR_NO"))
            self.assertFalse(_on("TEST_VAR_OFF"))
            self.assertFalse(_on("MISSING_VAR"))

if __name__ == '__main__':
    unittest.main()
