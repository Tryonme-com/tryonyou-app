
import os
import sys
import unittest
from unittest.mock import patch, mock_open, call, MagicMock
import io
import json

from ejecucion_total_equipo_51 import ejecucion_total_equipo_51, _run, ROOT

class TestEjecucionTotalEquipo51(unittest.TestCase):

    def setUp(self):
        # Base environment without E50_GIT_PUSH
        self.env_patcher = patch.dict(os.environ, {"E50_PROJECT_ROOT": "/mock/root"}, clear=True)
        self.env_patcher.start()

        self.mock_makedirs = patch("os.makedirs").start()
        self.mock_chdir = patch("os.chdir").start()

        self.mock_sys_exit = patch("sys.exit").start()
        self.mock_sys_exit.side_effect = SystemExit("Mocked Exit")

        # Mock stdout to keep test output clean
        self.mock_stdout = patch('sys.stdout', new_callable=io.StringIO).start()

    def tearDown(self):
        patch.stopall()

    @patch("ejecucion_total_equipo_51._run")
    @patch("subprocess.run")
    @patch("os.path.exists")
    @patch("os.path.isfile")
    @patch("builtins.open", new_callable=mock_open, read_data='{"name": "test"}')
    def test_happy_path_no_git(self, mock_file, mock_isfile, mock_exists, mock_subprocess, mock_run):
        # mock_isfile returns True for package.json
        mock_isfile.return_value = True
        mock_run.return_value = True

        ejecucion_total_equipo_51()

        self.mock_makedirs.assert_called_once_with(ROOT, exist_ok=True)
        self.mock_chdir.assert_called_once_with(ROOT)

        # Verify package.json engines update
        mock_file.assert_any_call(os.path.join(ROOT, "package.json"), encoding="utf-8")
        mock_file.assert_any_call(os.path.join(ROOT, "package.json"), "w", encoding="utf-8")

        # Verify MISSION_CONTROL.json write
        mock_file.assert_any_call(os.path.join(ROOT, "MISSION_CONTROL.json"), "w", encoding="utf-8")

        # Verify npm install called
        mock_run.assert_called_once_with(["npm", "install", "--package-lock-only"])

        # Verify sys.exit was not called
        self.mock_sys_exit.assert_not_called()

        # Verify git push was not attempted
        mock_subprocess.assert_not_called()


    @patch("ejecucion_total_equipo_51._run")
    @patch("subprocess.run")
    @patch("os.path.exists")
    @patch("os.path.isfile")
    @patch("builtins.open", new_callable=mock_open, read_data='{"name": "test"}')
    def test_happy_path_with_git(self, mock_file, mock_isfile, mock_exists, mock_subprocess, mock_run):
        mock_isfile.return_value = True
        mock_exists.return_value = True  # Make all paths exist for git add
        mock_run.return_value = True

        # Mock git commit subprocess return code
        mock_commit_result = MagicMock()
        mock_commit_result.returncode = 0
        mock_subprocess.return_value = mock_commit_result

        with patch.dict(os.environ, {"E50_GIT_PUSH": "1"}, clear=True):
            ejecucion_total_equipo_51()

        # npm install called
        mock_run.assert_any_call(["npm", "install", "--package-lock-only"])

        # git add called
        add_args = ["git", "add",
                    os.path.join(ROOT, "package.json"),
                    os.path.join(ROOT, "package-lock.json"),
                    os.path.join(ROOT, "MISSION_CONTROL.json"),
                    os.path.join(ROOT, ".gitignore"),
                    os.path.join(ROOT, "src")]
        mock_run.assert_any_call(add_args)

        # git commit called
        mock_subprocess.assert_called_once_with(
            ["git", "commit", "-m", "EQUIPO 51: Ejecución Total Jules/70/Manus - Studio Build"],
            cwd=ROOT,
            check=False
        )

        # git push called
        mock_run.assert_any_call(["git", "push", "origin", "main", "--force"])

        self.mock_sys_exit.assert_not_called()

    @patch("ejecucion_total_equipo_51._run")
    @patch("subprocess.run")
    @patch("os.path.exists")
    @patch("os.path.isfile")
    @patch("builtins.open", new_callable=mock_open)
    def test_missing_package_json(self, mock_file, mock_isfile, mock_exists, mock_subprocess, mock_run):
        mock_isfile.return_value = False

        ejecucion_total_equipo_51()

        # package.json was not opened
        call_args_list = [c.args[0] for c in mock_file.call_args_list if c.args]
        self.assertNotIn(os.path.join(ROOT, "package.json"), call_args_list)

        # npm install was not called
        mock_run.assert_not_called()
        self.mock_sys_exit.assert_not_called()

    @patch("ejecucion_total_equipo_51._run")
    @patch("subprocess.run")
    @patch("os.path.exists")
    @patch("os.path.isfile")
    @patch("builtins.open", new_callable=mock_open, read_data='{"name": "test"}')
    def test_npm_install_failure(self, mock_file, mock_isfile, mock_exists, mock_subprocess, mock_run):
        mock_isfile.return_value = True
        mock_run.return_value = False  # npm install fails

        with self.assertRaises(SystemExit):
            ejecucion_total_equipo_51()

        mock_run.assert_called_once_with(["npm", "install", "--package-lock-only"])
        self.mock_sys_exit.assert_called_once_with(1)

    @patch("ejecucion_total_equipo_51._run")
    @patch("subprocess.run")
    @patch("os.path.exists")
    @patch("os.path.isfile")
    @patch("builtins.open", new_callable=mock_open, read_data='{"name": "test"}')
    def test_empty_trackable_paths(self, mock_file, mock_isfile, mock_exists, mock_subprocess, mock_run):
        mock_isfile.return_value = True
        mock_exists.return_value = False  # No paths exist for git add

        # mock_run for npm install succeeds
        def mock_run_side_effect(args):
            if args[0] == "npm":
                return True
            return False
        mock_run.side_effect = mock_run_side_effect

        with patch.dict(os.environ, {"E50_GIT_PUSH": "1"}, clear=True):
            with self.assertRaises(SystemExit):
                ejecucion_total_equipo_51()

        self.mock_sys_exit.assert_called_once_with(1)
        mock_subprocess.assert_not_called()

    @patch("ejecucion_total_equipo_51._run")
    @patch("subprocess.run")
    @patch("os.path.exists")
    @patch("os.path.isfile")
    @patch("builtins.open", new_callable=mock_open, read_data='{"name": "test"}')
    def test_git_add_failure(self, mock_file, mock_isfile, mock_exists, mock_subprocess, mock_run):
        mock_isfile.return_value = True
        mock_exists.return_value = True

        def mock_run_side_effect(args):
            if args[0] == "npm":
                return True
            if args[0] == "git" and args[1] == "add":
                return False # git add fails
            return True
        mock_run.side_effect = mock_run_side_effect

        with patch.dict(os.environ, {"E50_GIT_PUSH": "1"}, clear=True):
            with self.assertRaises(SystemExit):
                ejecucion_total_equipo_51()

        self.mock_sys_exit.assert_called_once_with(1)
        mock_subprocess.assert_not_called()

    @patch("ejecucion_total_equipo_51._run")
    @patch("subprocess.run")
    @patch("os.path.exists")
    @patch("os.path.isfile")
    @patch("builtins.open", new_callable=mock_open, read_data='{"name": "test"}')
    def test_git_commit_failure(self, mock_file, mock_isfile, mock_exists, mock_subprocess, mock_run):
        mock_isfile.return_value = True
        mock_exists.return_value = True
        mock_run.return_value = True

        mock_commit_result = MagicMock()
        mock_commit_result.returncode = 2 # git commit fails (not 0 or 1)
        mock_subprocess.return_value = mock_commit_result

        with patch.dict(os.environ, {"E50_GIT_PUSH": "1"}, clear=True):
            with self.assertRaises(SystemExit):
                ejecucion_total_equipo_51()

        self.mock_sys_exit.assert_called_once_with(1)

    @patch("ejecucion_total_equipo_51._run")
    @patch("subprocess.run")
    @patch("os.path.exists")
    @patch("os.path.isfile")
    @patch("builtins.open", new_callable=mock_open, read_data='{"name": "test"}')
    def test_git_push_failure(self, mock_file, mock_isfile, mock_exists, mock_subprocess, mock_run):
        mock_isfile.return_value = True
        mock_exists.return_value = True

        def mock_run_side_effect(args):
            if args[0] == "git" and args[1] == "push":
                return False # git push fails
            return True
        mock_run.side_effect = mock_run_side_effect

        mock_commit_result = MagicMock()
        mock_commit_result.returncode = 0
        mock_subprocess.return_value = mock_commit_result

        with patch.dict(os.environ, {"E50_GIT_PUSH": "1"}, clear=True):
            with self.assertRaises(SystemExit):
                ejecucion_total_equipo_51()

        self.mock_sys_exit.assert_called_once_with(1)

    @patch("subprocess.run")
    def test_private_run_success(self, mock_subprocess):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result

        result = _run(["echo", "test"])
        self.assertTrue(result)
        mock_subprocess.assert_called_once_with(["echo", "test"], cwd=ROOT, check=False)

    @patch("subprocess.run")
    def test_private_run_oserror(self, mock_subprocess):
        mock_subprocess.side_effect = OSError("Mocked Error")

        result = _run(["invalid_cmd"])
        self.assertFalse(result)

if __name__ == "__main__":
    unittest.main()
