import unittest
from unittest.mock import patch
from genesis_consolidacion_total import genesis_consolidacion_total


class TestGenesisConsolidacionTotal(unittest.TestCase):
    @patch("genesis_consolidacion_total.genesis_consolidacion_total_safe")
    def test_genesis_consolidacion_total_calls_safe_and_returns_result(self, mock_safe):
        # Arrange
        mock_safe.return_value = 42

        # Act
        result = genesis_consolidacion_total()

        # Assert
        mock_safe.assert_called_once()
        self.assertEqual(result, 42)


if __name__ == "__main__":
    unittest.main()
