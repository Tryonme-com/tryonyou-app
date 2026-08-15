import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import io

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from ejecucion_total_equipo_51 import _run


class TestRunFunction(unittest.TestCase):
    @patch("subprocess.run")
    def test_run_success(self, mock_run) -> None:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        self.assertTrue(_run(["git", "status"]))
        mock_run.assert_called_once()
        self.assertEqual(mock_run.call_args[0][0], ["git", "status"])
        self.assertFalse(mock_run.call_args[1].get("check", True))

    @patch("subprocess.run")
    def test_run_failure(self, mock_run) -> None:
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_run.return_value = mock_result

        self.assertFalse(_run(["git", "invalid"]))
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_run_oserror(self, mock_run) -> None:
        mock_run.side_effect = OSError("Command not found")

        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            result = _run(["non_existent_command"])

            self.assertFalse(result)
            self.assertIn("❌ Command not found", mock_stdout.getvalue())

        mock_run.assert_called_once()


if __name__ == "__main__":
    unittest.main()
