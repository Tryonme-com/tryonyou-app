import io
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from asalto_final import _run

class TestAsaltoFinalRun(unittest.TestCase):
    @patch("asalto_final.subprocess.run")
    def test_run_success(self, mock_run):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = _run(["git", "status"], cwd="/tmp")

        self.assertEqual(result, 0)
        mock_run.assert_called_once_with(["git", "status"], cwd="/tmp", check=False)

    @patch("asalto_final.subprocess.run")
    def test_run_failure(self, mock_run):
        mock_result = MagicMock()
        mock_result.returncode = 128
        mock_run.return_value = mock_result

        result = _run(["git", "push"], cwd="/tmp")

        self.assertEqual(result, 128)
        mock_run.assert_called_once_with(["git", "push"], cwd="/tmp", check=False)

    @patch("asalto_final.subprocess.run")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_run_os_error(self, mock_stdout, mock_run):
        mock_run.side_effect = OSError("No such file or directory")

        result = _run(["nonexistent_command"], cwd="/tmp")

        self.assertEqual(result, 1)
        mock_run.assert_called_once_with(["nonexistent_command"], cwd="/tmp", check=False)
        self.assertIn("No such file or directory", mock_stdout.getvalue())

if __name__ == "__main__":
    unittest.main()
