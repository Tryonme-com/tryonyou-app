import unittest
from unittest.mock import patch, call
from maza_final_v10 import sellar_bunker_git, PATENTE

class TestMazaFinalV10(unittest.TestCase):
    @patch("maza_final_v10.os.chdir")
    @patch("maza_final_v10.subprocess.run")
    def test_sellar_bunker_git_no_shell(self, mock_subprocess_run, mock_chdir):
        sellar_bunker_git()

        msg = f"V10.4 OMEGA: Bunker 75005 Blindado - Patente {PATENTE}"

        expected_calls = [
            call(["git", "add", "."]),
            call(["git", "commit", "-m", msg]),
            call(["git", "push", "origin", "main", "--force"])
        ]

        mock_subprocess_run.assert_has_calls(expected_calls)
        self.assertEqual(mock_subprocess_run.call_count, 3)

        # Verify shell=True is not in any of the kwargs for the calls
        for mock_call in mock_subprocess_run.call_args_list:
            _, kwargs = mock_call
            self.assertNotIn("shell", kwargs)
            self.assertFalse(kwargs.get("shell", False))

if __name__ == "__main__":
    unittest.main()
