import unittest
import io
from unittest.mock import patch

from fix_environment import _run

class TestFixEnvironmentRun(unittest.TestCase):
    def test_run_success(self):
        """Test that a successful command returns 0."""
        self.assertEqual(_run(["true"], cwd="."), 0)

    def test_run_command_fails(self):
        """Test that a failing command returns a non-zero code."""
        self.assertNotEqual(_run(["false"], cwd="."), 0)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_run_oserror(self, mock_stdout):
        """Test that an OSError is caught, prints to stdout, and returns 1."""
        # Use a clearly nonexistent executable.
        result = _run(["/this/command/does/not/exist_12345"], cwd=".")
        self.assertEqual(result, 1)
        self.assertIn("No such file or directory", mock_stdout.getvalue())

if __name__ == '__main__':
    unittest.main()
