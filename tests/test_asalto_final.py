import unittest
from unittest.mock import patch
import os
import io

from asalto_final import asalto_final, ROOT

class TestAsaltoFinal(unittest.TestCase):

    @patch("asalto_final.os.makedirs")
    @patch("asalto_final.os.chdir")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_missing_git_push_env_var(self, mock_stdout, mock_chdir, mock_makedirs):
        with patch.dict(os.environ, clear=True):
            result = asalto_final()
            self.assertEqual(result, 0)
            mock_makedirs.assert_called_once_with(ROOT, exist_ok=True)
            mock_chdir.assert_called_once_with(ROOT)
            self.assertIn("E50_GIT_PUSH=1 para ejecutar push.", mock_stdout.getvalue())

    @patch("asalto_final.os.makedirs")
    @patch("asalto_final.os.chdir")
    @patch("asalto_final.os.path.isdir")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_missing_git_dir(self, mock_stdout, mock_isdir, mock_chdir, mock_makedirs):
        with patch.dict(os.environ, {"E50_GIT_PUSH": "1"}, clear=True):
            mock_isdir.return_value = False
            result = asalto_final()
            self.assertEqual(result, 1)
            mock_isdir.assert_called_once_with(os.path.join(ROOT, ".git"))
            self.assertIn(f"❌ Sin .git en {ROOT}", mock_stdout.getvalue())

    @patch("asalto_final.os.makedirs")
    @patch("asalto_final.os.chdir")
    @patch("asalto_final.os.path.isdir")
    @patch("asalto_final._run")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_successful_normal_push(self, mock_stdout, mock_run, mock_isdir, mock_chdir, mock_makedirs):
        with patch.dict(os.environ, {"E50_GIT_PUSH": "1"}, clear=True):
            mock_isdir.return_value = True
            mock_run.return_value = 0

            result = asalto_final()
            self.assertEqual(result, 0)
            mock_run.assert_called_once_with(["git", "push", "origin", "main"], cwd=ROOT)
            self.assertIn("🔥 Push completado.", mock_stdout.getvalue())

    @patch("asalto_final.os.makedirs")
    @patch("asalto_final.os.chdir")
    @patch("asalto_final.os.path.isdir")
    @patch("asalto_final._run")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_successful_force_push(self, mock_stdout, mock_run, mock_isdir, mock_chdir, mock_makedirs):
        with patch.dict(os.environ, {"E50_GIT_PUSH": "1", "E50_FORCE_PUSH": "1"}, clear=True):
            mock_isdir.return_value = True
            mock_run.return_value = 0

            result = asalto_final()
            self.assertEqual(result, 0)
            mock_run.assert_called_once_with(["git", "push", "origin", "main", "--force"], cwd=ROOT)
            self.assertIn("🔥 Push completado.", mock_stdout.getvalue())

    @patch("asalto_final.os.makedirs")
    @patch("asalto_final.os.chdir")
    @patch("asalto_final.os.path.isdir")
    @patch("asalto_final._run")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_push_failure(self, mock_stdout, mock_run, mock_isdir, mock_chdir, mock_makedirs):
        with patch.dict(os.environ, {"E50_GIT_PUSH": "1"}, clear=True):
            mock_isdir.return_value = True
            mock_run.return_value = 1

            result = asalto_final()
            self.assertEqual(result, 1)
            mock_run.assert_called_once_with(["git", "push", "origin", "main"], cwd=ROOT)
            self.assertIn("❌ git push falló", mock_stdout.getvalue())

if __name__ == '__main__':
    unittest.main()
