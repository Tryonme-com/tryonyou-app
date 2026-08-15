import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import json
import tempfile
import io

# Import the module to be tested
import ejecucion_total_equipo_51

class TestEjecucionTotalEquipo51(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = self.temp_dir.name

        self.patcher_root = patch('ejecucion_total_equipo_51.ROOT', self.root)
        self.patcher_root.start()

        self.patcher_stdout = patch('sys.stdout', new_callable=io.StringIO)
        self.mock_stdout = self.patcher_stdout.start()

    def tearDown(self):
        self.patcher_root.stop()
        self.patcher_stdout.stop()
        self.temp_dir.cleanup()

    @patch.dict('os.environ', {}, clear=True)
    @patch('ejecucion_total_equipo_51._run')
    def test_no_package_json_no_git_push(self, mock_run):
        ejecucion_total_equipo_51.ejecucion_total_equipo_51()

        mission_path = os.path.join(self.root, "MISSION_CONTROL.json")
        self.assertTrue(os.path.exists(mission_path))
        with open(mission_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertEqual(data["ejecutor"], "Jules")
            self.assertEqual(data["litis_status"], "TOTAL_WAR_READY")

        mock_run.assert_not_called()

    @patch.dict('os.environ', {}, clear=True)
    @patch('ejecucion_total_equipo_51._run')
    def test_with_package_json_no_git_push(self, mock_run):
        mock_run.return_value = True

        pkg_path = os.path.join(self.root, "package.json")
        with open(pkg_path, "w", encoding="utf-8") as f:
            json.dump({"name": "test-app"}, f)

        ejecucion_total_equipo_51.ejecucion_total_equipo_51()

        with open(pkg_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertEqual(data["engines"]["node"], ">=20.0.0")

        mock_run.assert_called_once_with(["npm", "install", "--package-lock-only"])

    @patch.dict('os.environ', {}, clear=True)
    @patch('ejecucion_total_equipo_51._run')
    def test_npm_install_fails(self, mock_run):
        mock_run.return_value = False

        pkg_path = os.path.join(self.root, "package.json")
        with open(pkg_path, "w", encoding="utf-8") as f:
            json.dump({"name": "test-app"}, f)

        with self.assertRaises(SystemExit) as cm:
            ejecucion_total_equipo_51.ejecucion_total_equipo_51()

        self.assertEqual(cm.exception.code, 1)

    @patch.dict('os.environ', {"E50_GIT_PUSH": "1"}, clear=True)
    @patch('subprocess.run')
    @patch('ejecucion_total_equipo_51._run')
    def test_with_git_push_success(self, mock_run, mock_subprocess_run):
        mock_run.side_effect = [True, True, True]

        mock_commit_result = MagicMock()
        mock_commit_result.returncode = 0
        mock_subprocess_run.return_value = mock_commit_result

        pkg_path = os.path.join(self.root, "package.json")
        with open(pkg_path, "w", encoding="utf-8") as f:
            json.dump({"name": "test-app"}, f)

        ejecucion_total_equipo_51.ejecucion_total_equipo_51()

        self.assertEqual(mock_run.call_count, 3)
        mock_run.assert_any_call(["npm", "install", "--package-lock-only"])
        add_call_args = mock_run.call_args_list[1][0][0]
        self.assertEqual(add_call_args[0], "git")
        self.assertEqual(add_call_args[1], "add")

        mock_run.assert_any_call(["git", "push", "origin", "main", "--force"])

        mock_subprocess_run.assert_called_once()
        commit_call_args = mock_subprocess_run.call_args[0][0]
        self.assertEqual(commit_call_args[0], "git")
        self.assertEqual(commit_call_args[1], "commit")

    @patch.dict('os.environ', {"E50_GIT_PUSH": "1"}, clear=True)
    def test_git_push_no_trackable_files(self):
        original_exists = os.path.exists
        def mock_exists(path):
            if "MISSION_CONTROL.json" in path: return False
            return original_exists(path)

        with patch('os.path.exists', side_effect=mock_exists):
            with self.assertRaises(SystemExit) as cm:
                ejecucion_total_equipo_51.ejecucion_total_equipo_51()
            self.assertEqual(cm.exception.code, 1)

    @patch.dict('os.environ', {"E50_GIT_PUSH": "1"}, clear=True)
    @patch('ejecucion_total_equipo_51._run')
    def test_git_add_fails(self, mock_run):
        mock_run.return_value = False
        with self.assertRaises(SystemExit) as cm:
            ejecucion_total_equipo_51.ejecucion_total_equipo_51()
        self.assertEqual(cm.exception.code, 1)

    @patch.dict('os.environ', {"E50_GIT_PUSH": "1"}, clear=True)
    @patch('subprocess.run')
    @patch('ejecucion_total_equipo_51._run')
    def test_git_commit_fails(self, mock_run, mock_subprocess_run):
        mock_run.side_effect = [True] # git add

        mock_commit_result = MagicMock()
        mock_commit_result.returncode = 2
        mock_subprocess_run.return_value = mock_commit_result

        with self.assertRaises(SystemExit) as cm:
            ejecucion_total_equipo_51.ejecucion_total_equipo_51()
        self.assertEqual(cm.exception.code, 1)

    @patch.dict('os.environ', {"E50_GIT_PUSH": "1"}, clear=True)
    @patch('subprocess.run')
    @patch('ejecucion_total_equipo_51._run')
    def test_git_push_fails(self, mock_run, mock_subprocess_run):
        mock_run.side_effect = [True, False] # git add -> True, git push -> False

        mock_commit_result = MagicMock()
        mock_commit_result.returncode = 0
        mock_subprocess_run.return_value = mock_commit_result

        with self.assertRaises(SystemExit) as cm:
            ejecucion_total_equipo_51.ejecucion_total_equipo_51()
        self.assertEqual(cm.exception.code, 1)

    @patch('subprocess.run')
    def test_run_helper(self, mock_subprocess_run):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_subprocess_run.return_value = mock_result

        self.assertTrue(ejecucion_total_equipo_51._run(["echo", "test"]))

        mock_result.returncode = 1
        self.assertFalse(ejecucion_total_equipo_51._run(["echo", "test"]))

        mock_subprocess_run.side_effect = OSError("mock error")
        self.assertFalse(ejecucion_total_equipo_51._run(["echo", "test"]))

if __name__ == '__main__':
    unittest.main()
