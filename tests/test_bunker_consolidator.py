import unittest
from unittest.mock import patch, MagicMock
from bunker_consolidator import main

class TestBunkerConsolidatorMain(unittest.TestCase):
    @patch('bunker_consolidator.BunkerConsolidator')
    def test_main_success(self, mock_class):
        # Setup mock instance
        mock_instance = MagicMock()
        mock_class.return_value = mock_instance
        mock_instance.run_build.return_value = True

        # Run
        result = main()

        # Assert
        self.assertEqual(result, 0)
        mock_instance.clean_legacy_code.assert_called_once()
        mock_instance.verify_env_variables.assert_called_once()
        mock_instance.run_build.assert_called_once()
        mock_instance.final_check.assert_called_once()

    @patch('bunker_consolidator.BunkerConsolidator')
    def test_main_failure(self, mock_class):
        # Setup mock instance
        mock_instance = MagicMock()
        mock_class.return_value = mock_instance
        mock_instance.run_build.return_value = False

        # Run
        result = main()

        # Assert
        self.assertEqual(result, 1)
        mock_instance.clean_legacy_code.assert_called_once()
        mock_instance.verify_env_variables.assert_called_once()
        mock_instance.run_build.assert_called_once()
        mock_instance.final_check.assert_not_called()

if __name__ == '__main__':
    unittest.main()
