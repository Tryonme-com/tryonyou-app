"""Tests for inyectar_claves_intelligence."""

import os
import sys
import unittest
from unittest.mock import patch

# Allow importing from project root
_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from inyectar_claves_intelligence import _force_push_on

class TestInyectarClavesIntelligence(unittest.TestCase):
    """Test suite for inyectar_claves_intelligence.py."""

    def test_force_push_on_true_values(self):
        """Test that _force_push_on returns True for valid true strings."""
        true_values = ["1", "true", "yes", "on", " 1 ", " TrUe ", "YES"]
        for val in true_values:
            with self.subTest(val=val):
                with patch.dict(os.environ, {"E50_FORCE_PUSH": val}, clear=True):
                    self.assertTrue(_force_push_on())

    def test_force_push_on_false_values(self):
        """Test that _force_push_on returns False for invalid or false strings."""
        false_values = ["0", "false", "no", "off", " ", "invalid", ""]
        for val in false_values:
            with self.subTest(val=val):
                with patch.dict(os.environ, {"E50_FORCE_PUSH": val}, clear=True):
                    self.assertFalse(_force_push_on())

    def test_force_push_on_unset(self):
        """Test that _force_push_on returns False when the environment variable is not set."""
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(_force_push_on())

if __name__ == "__main__":
    unittest.main()
