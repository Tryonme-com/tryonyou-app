from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import io

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from inyectar_claves_intelligence import _run

class TestInyectarClavesIntelligenceRun(unittest.TestCase):
    @patch("inyectar_claves_intelligence.subprocess.run")
    def test_run_success(self, mock_run: MagicMock) -> None:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = _run(["echo", "hello"], cwd="/tmp")

        self.assertEqual(result, 0)
        mock_run.assert_called_once_with(["echo", "hello"], cwd="/tmp", check=False)

    @patch("inyectar_claves_intelligence.subprocess.run")
    def test_run_failure(self, mock_run: MagicMock) -> None:
        mock_result = MagicMock()
        mock_result.returncode = 2
        mock_run.return_value = mock_result

        result = _run(["false"], cwd="/tmp")

        self.assertEqual(result, 2)
        mock_run.assert_called_once_with(["false"], cwd="/tmp", check=False)

    @patch("sys.stdout", new_callable=io.StringIO)
    @patch("inyectar_claves_intelligence.subprocess.run")
    def test_run_oserror(self, mock_run: MagicMock, mock_stdout: io.StringIO) -> None:
        mock_run.side_effect = OSError("No such file or directory")

        result = _run(["nonexistent_command"], cwd="/tmp")

        self.assertEqual(result, 1)
        mock_run.assert_called_once_with(["nonexistent_command"], cwd="/tmp", check=False)
        self.assertIn("❌ No such file or directory", mock_stdout.getvalue())

if __name__ == "__main__":
    unittest.main()
