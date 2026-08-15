import unittest
from unittest.mock import patch, MagicMock
import io

from inyectar_claves_intelligence import _run

class TestRunFunction(unittest.TestCase):
    @patch('subprocess.run')
    def test_run_success(self, mock_run):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = _run(['echo', 'test'], cwd='/tmp')
        self.assertEqual(result, 0)
        mock_run.assert_called_once_with(['echo', 'test'], cwd='/tmp', check=False)

    @patch('subprocess.run')
    def test_run_failure(self, mock_run):
        mock_result = MagicMock()
        mock_result.returncode = 2
        mock_run.return_value = mock_result

        result = _run(['ls', '/nonexistent'], cwd='/tmp')
        self.assertEqual(result, 2)
        mock_run.assert_called_once_with(['ls', '/nonexistent'], cwd='/tmp', check=False)

    @patch('subprocess.run')
    @patch('sys.stdout', new_callable=io.StringIO)
    def test_run_oserror(self, mock_stdout, mock_run):
        mock_run.side_effect = OSError("Command not found")

        result = _run(['nonexistent_command'], cwd='/tmp')
        self.assertEqual(result, 1)
        mock_run.assert_called_once_with(['nonexistent_command'], cwd='/tmp', check=False)
        self.assertIn("❌ Command not found", mock_stdout.getvalue())

if __name__ == '__main__':
    unittest.main()
