import sys
import unittest
from unittest.mock import patch, MagicMock
import os
import tempfile
import shutil
import json

import ejecucion_total_equipo_51 as et

class TestEjecucionTotalEquipo51(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()

        # Patch ROOT
        self.patcher_root = patch('ejecucion_total_equipo_51.ROOT', self.test_dir)
        self.mock_root = self.patcher_root.start()

        # Patch sys.exit
        self.patcher_exit = patch('sys.exit')
        self.mock_exit = self.patcher_exit.start()

        # Patch os.environ
        self.patcher_env = patch.dict(os.environ, {}, clear=True)
        self.patcher_env.start()

        # Patch subprocess.run
        self.patcher_sub = patch('subprocess.run')
        self.mock_sub = self.patcher_sub.start()
        self.mock_sub.return_value = MagicMock(returncode=0)

    def tearDown(self):
        os.chdir(self.original_cwd)
        patch.stopall()
        shutil.rmtree(self.test_dir)

    def test_run_success(self):
        self.assertTrue(et._run(["ls"]))
        self.mock_sub.assert_called_with(["ls"], cwd=self.test_dir, check=False)

    def test_run_failure(self):
        self.mock_sub.return_value = MagicMock(returncode=1)
        self.assertFalse(et._run(["ls"]))

    def test_run_oserror(self):
        self.mock_sub.side_effect = OSError("mock error")
        self.assertFalse(et._run(["ls"]))

    def test_no_package_json_and_no_git(self):
        et.ejecucion_total_equipo_51()

        mission_path = os.path.join(self.test_dir, "MISSION_CONTROL.json")
        self.assertTrue(os.path.isfile(mission_path))
        with open(mission_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertEqual(data["ejecutor"], "Jules")

        self.mock_sub.assert_not_called()
        self.mock_exit.assert_not_called()

    def test_with_package_json_and_no_git(self):
        pkg_path = os.path.join(self.test_dir, "package.json")
        with open(pkg_path, "w", encoding="utf-8") as f:
            json.dump({"name": "test"}, f)

        et.ejecucion_total_equipo_51()

        with open(pkg_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertEqual(data["engines"]["node"], ">=20.0.0")

        self.mock_sub.assert_called_once_with(["npm", "install", "--package-lock-only"], cwd=self.test_dir, check=False)
        self.mock_exit.assert_not_called()

    @patch.dict(os.environ, {"E50_GIT_PUSH": "1"})
    def test_git_push_flow_success(self):
        pkg_path = os.path.join(self.test_dir, "package.json")
        with open(pkg_path, "w", encoding="utf-8") as f:
            json.dump({"name": "test"}, f)

        et.ejecucion_total_equipo_51()

        self.assertEqual(self.mock_sub.call_count, 4)
        calls = self.mock_sub.call_args_list
        self.assertEqual(calls[0][0][0], ["npm", "install", "--package-lock-only"])
        self.assertEqual(calls[1][0][0][0:2], ["git", "add"])
        self.assertEqual(calls[2][0][0][0:2], ["git", "commit"])
        self.assertEqual(calls[3][0][0], ["git", "push", "origin", "main", "--force"])

        self.mock_exit.assert_not_called()

    @patch.dict(os.environ, {"E50_GIT_PUSH": "1"})
    def test_npm_install_fails(self):
        pkg_path = os.path.join(self.test_dir, "package.json")
        with open(pkg_path, "w", encoding="utf-8") as f:
            json.dump({"name": "test"}, f)

        # Mock _run to return False when npm is called
        original_run = et._run
        def side_effect(args):
            if args[0] == "npm":
                return False
            return original_run(args)

        with patch('ejecucion_total_equipo_51._run', side_effect=side_effect):
            et.ejecucion_total_equipo_51()

        self.mock_exit.assert_called_once_with(1)

    @patch.dict(os.environ, {"E50_GIT_PUSH": "1"})
    def test_git_add_no_files(self):
        original_exists = os.path.exists
        def fake_exists(path):
            if path.startswith(self.test_dir):
                return False
            return original_exists(path)

        with patch('os.path.exists', side_effect=fake_exists):
            et.ejecucion_total_equipo_51()

        self.mock_exit.assert_called_once_with(1)

    @patch.dict(os.environ, {"E50_GIT_PUSH": "1"})
    def test_git_add_fails(self):
        original_run = et._run
        def side_effect(args):
            if args[0] == "git" and args[1] == "add":
                return False
            return True

        with patch('ejecucion_total_equipo_51._run', side_effect=side_effect):
            et.ejecucion_total_equipo_51()

        self.mock_exit.assert_called_once_with(1)

    @patch.dict(os.environ, {"E50_GIT_PUSH": "1"})
    def test_git_commit_fails(self):
        def side_effect(args, **kwargs):
            if args[0] == "git" and args[1] == "commit":
                return MagicMock(returncode=2)
            return MagicMock(returncode=0)
        self.mock_sub.side_effect = side_effect

        et.ejecucion_total_equipo_51()
        self.mock_exit.assert_called_once_with(1)

    @patch.dict(os.environ, {"E50_GIT_PUSH": "1"})
    def test_git_push_fails(self):
        original_run = et._run
        def side_effect(args):
            if args[0] == "git" and args[1] == "push":
                return False
            return True

        with patch('ejecucion_total_equipo_51._run', side_effect=side_effect):
            et.ejecucion_total_equipo_51()

        self.mock_exit.assert_called_once_with(1)

if __name__ == "__main__":
    unittest.main()
