import unittest
import os
from unittest.mock import patch
from inyectar_claves_intelligence import _git_on

class TestInyectarClavesIntelligence(unittest.TestCase):
    def test_git_on_true_cases(self):
        for val in ["1", "true", "yes", "on", " 1 ", "TrUe "]:
            with patch.dict(os.environ, {"E50_GIT_PUSH": val}, clear=True):
                self.assertTrue(_git_on())

    def test_git_on_false_cases(self):
        for val in ["0", "false", "no", "off", ""]:
            with patch.dict(os.environ, {"E50_GIT_PUSH": val}, clear=True):
                self.assertFalse(_git_on())

    def test_git_on_missing_env(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(_git_on())

if __name__ == '__main__':
    unittest.main()
