"""Tests for ejecucion_total_equipo_51.py"""

import os
import sys
import unittest
from unittest.mock import patch, mock_open, MagicMock

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import ejecucion_total_equipo_51
from ejecucion_total_equipo_51 import _run, ejecucion_total_equipo_51 as execute

class TestEjecucionTotalEquipo51(unittest.TestCase):
    @patch("subprocess.run")
    def test_run_success(self, mock_sub_run):
        mock_sub_run.return_value = MagicMock(returncode=0)
        self.assertTrue(_run(["test"]))
        mock_sub_run.assert_called_once()

    @patch("subprocess.run")
    def test_run_fail(self, mock_sub_run):
        mock_sub_run.return_value = MagicMock(returncode=1)
        self.assertFalse(_run(["test"]))

    @patch("subprocess.run")
    def test_run_oserror(self, mock_sub_run):
        mock_sub_run.side_effect = OSError("test error")
        self.assertFalse(_run(["test"]))

    @patch("os.makedirs")
    @patch("os.chdir")
    @patch("os.path.isfile")
    @patch("builtins.open", new_callable=mock_open, read_data='{}')
    @patch("os.environ.get")
    @patch("sys.exit")
    def test_no_package_no_git(self, mock_exit, mock_env_get, mock_file, mock_isfile, mock_chdir, mock_makedirs):
        mock_isfile.return_value = False
        mock_env_get.return_value = "" # No git push

        with patch("ejecucion_total_equipo_51.ROOT", "/mock/root"):
            execute()

        mock_makedirs.assert_called_with("/mock/root", exist_ok=True)
        mock_chdir.assert_called_with("/mock/root")
        mock_exit.assert_not_called()

    @patch("os.makedirs")
    @patch("os.chdir")
    @patch("os.path.isfile")
    @patch("builtins.open", new_callable=mock_open, read_data='{}')
    @patch("os.environ.get")
    @patch("ejecucion_total_equipo_51._run")
    @patch("sys.exit")
    def test_with_package_npm_fails(self, mock_exit, mock_run, mock_env_get, mock_file, mock_isfile, mock_chdir, mock_makedirs):
        mock_isfile.return_value = True
        mock_run.return_value = False # npm install fails

        with patch("ejecucion_total_equipo_51.ROOT", "/mock/root"):
            execute()

        mock_exit.assert_called_with(1)

    @patch("os.makedirs")
    @patch("os.chdir")
    @patch("os.path.isfile")
    @patch("builtins.open", new_callable=mock_open, read_data='{}')
    @patch("os.environ.get")
    @patch("ejecucion_total_equipo_51._run")
    @patch("sys.exit")
    def test_with_package_npm_success_no_git(self, mock_exit, mock_run, mock_env_get, mock_file, mock_isfile, mock_chdir, mock_makedirs):
        mock_isfile.return_value = True
        mock_run.return_value = True # npm install succeeds
        mock_env_get.return_value = "0"

        with patch("ejecucion_total_equipo_51.ROOT", "/mock/root"):
            execute()

        mock_exit.assert_not_called()
        mock_run.assert_called_with(["npm", "install", "--package-lock-only"])

    @patch("os.makedirs")
    @patch("os.chdir")
    @patch("os.path.isfile")
    @patch("builtins.open", new_callable=mock_open, read_data='{}')
    @patch("os.environ.get")
    @patch("sys.exit")
    @patch("os.path.exists")
    @patch("subprocess.run")
    def test_git_push_no_trackable(self, mock_sub_run, mock_exists, mock_exit, mock_env_get, mock_file, mock_isfile, mock_chdir, mock_makedirs):
        mock_isfile.return_value = False
        mock_env_get.return_value = "1"
        mock_exists.return_value = False # No trackable files
        mock_sub_run.return_value = MagicMock(returncode=0)

        with patch("ejecucion_total_equipo_51.ROOT", "/mock/root"):
            execute()

        mock_exit.assert_called_with(1)

    @patch("os.makedirs")
    @patch("os.chdir")
    @patch("os.path.isfile")
    @patch("builtins.open", new_callable=mock_open, read_data='{}')
    @patch("os.environ.get")
    @patch("ejecucion_total_equipo_51._run")
    @patch("sys.exit")
    @patch("os.path.exists")
    @patch("subprocess.run")
    def test_git_push_add_fails(self, mock_sub_run, mock_exists, mock_exit, mock_run, mock_env_get, mock_file, mock_isfile, mock_chdir, mock_makedirs):
        mock_isfile.return_value = False
        mock_env_get.return_value = "1"
        mock_exists.return_value = True # files exist
        mock_run.return_value = False # git add fails
        mock_sub_run.return_value = MagicMock(returncode=0)

        with patch("ejecucion_total_equipo_51.ROOT", "/mock/root"):
            execute()

        mock_exit.assert_called_with(1)

    @patch("os.makedirs")
    @patch("os.chdir")
    @patch("os.path.isfile")
    @patch("builtins.open", new_callable=mock_open, read_data='{}')
    @patch("os.environ.get")
    @patch("ejecucion_total_equipo_51._run")
    @patch("sys.exit")
    @patch("os.path.exists")
    @patch("subprocess.run")
    def test_git_push_commit_fails(self, mock_sub_run, mock_exists, mock_exit, mock_run, mock_env_get, mock_file, mock_isfile, mock_chdir, mock_makedirs):
        mock_isfile.return_value = False
        mock_env_get.return_value = "1"
        mock_exists.return_value = True
        mock_run.return_value = True # git add succeeds
        mock_sub_run.return_value = MagicMock(returncode=2) # commit fails

        with patch("ejecucion_total_equipo_51.ROOT", "/mock/root"):
            execute()

        mock_exit.assert_called_with(1)

    @patch("os.makedirs")
    @patch("os.chdir")
    @patch("os.path.isfile")
    @patch("builtins.open", new_callable=mock_open, read_data='{}')
    @patch("os.environ.get")
    @patch("ejecucion_total_equipo_51._run")
    @patch("sys.exit")
    @patch("os.path.exists")
    @patch("subprocess.run")
    def test_git_push_fails(self, mock_sub_run, mock_exists, mock_exit, mock_run, mock_env_get, mock_file, mock_isfile, mock_chdir, mock_makedirs):
        mock_isfile.return_value = False
        mock_env_get.return_value = "1"
        mock_exists.return_value = True
        mock_run.side_effect = [True, False] # git add succeeds, git push fails
        mock_sub_run.return_value = MagicMock(returncode=0) # commit succeeds

        with patch("ejecucion_total_equipo_51.ROOT", "/mock/root"):
            execute()

        mock_exit.assert_called_with(1)

    @patch("os.makedirs")
    @patch("os.chdir")
    @patch("os.path.isfile")
    @patch("builtins.open", new_callable=mock_open, read_data='{}')
    @patch("os.environ.get")
    @patch("ejecucion_total_equipo_51._run")
    @patch("sys.exit")
    @patch("os.path.exists")
    @patch("subprocess.run")
    def test_full_success(self, mock_sub_run, mock_exists, mock_exit, mock_run, mock_env_get, mock_file, mock_isfile, mock_chdir, mock_makedirs):
        mock_isfile.return_value = False
        mock_env_get.return_value = "1"
        mock_exists.return_value = True
        mock_run.side_effect = [True, True] # git add succeeds, git push succeeds
        mock_sub_run.return_value = MagicMock(returncode=0) # commit succeeds

        with patch("ejecucion_total_equipo_51.ROOT", "/mock/root"):
            execute()

        mock_exit.assert_not_called()

if __name__ == "__main__":
    unittest.main()
