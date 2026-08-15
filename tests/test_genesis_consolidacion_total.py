import unittest
from unittest.mock import patch
import runpy

import genesis_consolidacion_total

class TestGenesisConsolidacionTotal(unittest.TestCase):

    @patch('genesis_consolidacion_total.genesis_consolidacion_total_safe')
    def test_genesis_consolidacion_total_returns_safe_value(self, mock_safe):
        # Arrange
        mock_safe.return_value = 42

        # Act
        result = genesis_consolidacion_total.genesis_consolidacion_total()

        # Assert
        mock_safe.assert_called_once()
        self.assertEqual(result, 42)

    @patch('sys.exit')
    @patch('genesis_consolidacion_total_safe.genesis_consolidacion_total_safe')
    def test_run_module_as_main(self, mock_safe, mock_exit):
        # Arrange
        mock_safe.return_value = 99

        # Act
        try:
            runpy.run_path('genesis_consolidacion_total.py', run_name='__main__')
        except SystemExit:
            pass

        # Assert
        mock_safe.assert_called_once()
        mock_exit.assert_called_once_with(99)

if __name__ == '__main__':
    unittest.main()
