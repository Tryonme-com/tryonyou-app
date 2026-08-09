import unittest
from unittest.mock import patch
import sys
import subprocess

from unificar_v10 import _free_port_5173, VITE_PORT

class TestUnificarV10(unittest.TestCase):
    @patch('unificar_v10.sys')
    @patch('unificar_v10.subprocess.run')
    def test_free_port_darwin(self, mock_run, mock_sys):
        mock_sys.platform = 'darwin'
        _free_port_5173()
        mock_run.assert_called_once_with(
            f"lsof -ti:{VITE_PORT} | xargs kill -9 2>/dev/null || true",
            shell=True,
            stderr=subprocess.DEVNULL,
        )

    @patch('unificar_v10.sys')
    @patch('unificar_v10.subprocess.run')
    def test_free_port_linux(self, mock_run, mock_sys):
        mock_sys.platform = 'linux'
        _free_port_5173()
        mock_run.assert_called_once_with(
            f"lsof -ti:{VITE_PORT} | xargs kill -9 2>/dev/null || true",
            shell=True,
            stderr=subprocess.DEVNULL,
        )

    @patch('unificar_v10.os')
    @patch('unificar_v10.sys')
    @patch('unificar_v10.subprocess.run')
    def test_free_port_windows(self, mock_run, mock_sys, mock_os):
        mock_sys.platform = 'win32'
        mock_os.name = 'nt'
        _free_port_5173()
        ps = (
            "Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue "
            "| ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"
        )
        mock_run.assert_called_once_with(
            ["powershell", "-NoProfile", "-Command", ps],
            stderr=subprocess.DEVNULL,
        )

if __name__ == '__main__':
    unittest.main()
