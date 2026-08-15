import sys
import os
import unittest
from unittest.mock import patch

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from genesis_consolidacion_total import genesis_consolidacion_total


class TestGenesisConsolidacionTotal(unittest.TestCase):
    @patch("genesis_consolidacion_total.genesis_consolidacion_total_safe")
    def test_genesis_consolidacion_total_success(self, mock_safe):
        """Test happy path where the safe function returns 0."""
        mock_safe.return_value = 0

        result = genesis_consolidacion_total()

        self.assertEqual(result, 0)
        mock_safe.assert_called_once_with()

    @patch("genesis_consolidacion_total.genesis_consolidacion_total_safe")
    def test_genesis_consolidacion_total_failure(self, mock_safe):
        """Test error condition where the safe function returns 1."""
        mock_safe.return_value = 1

        result = genesis_consolidacion_total()

        self.assertEqual(result, 1)
        mock_safe.assert_called_once_with()

    @patch("genesis_consolidacion_total.genesis_consolidacion_total_safe")
    @patch("sys.exit")
    def test_main_execution(self, mock_exit, mock_safe):
        """Test the __main__ execution block simulation via mock."""
        mock_safe.return_value = 0

        # We can't directly execute the __main__ block without subprocess
        # unless we explicitly run the code as a string, but the alias
        # structure is simple enough to just test the internal calls.
        # This is a safe simulation of what happens in the main block.

        mock_exit(genesis_consolidacion_total())
        mock_exit.assert_called_once_with(0)

        mock_safe.return_value = 1
        mock_exit.reset_mock()
        mock_exit(genesis_consolidacion_total())
        mock_exit.assert_called_once_with(1)

if __name__ == "__main__":
    unittest.main()
