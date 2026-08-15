import unittest
from unittest.mock import patch, call
from maza_final_v10 import sellar_bunker_git, PATENTE

class TestMazaFinalV10(unittest.TestCase):
    @patch('maza_final_v10.os.chdir')
    @patch('maza_final_v10.subprocess.run')
    def test_sellar_bunker_git_no_shell(self, mock_run, mock_chdir):
        sellar_bunker_git()

        msg = f"V10.4 OMEGA: Bunker 75005 Blindado - Patente {PATENTE}"

        expected_calls = [
            call(["git", "add", "."]),
            call(["git", "commit", "-m", msg]),
            call(["git", "push", "origin", "main", "--force"])
        ]

        mock_run.assert_has_calls(expected_calls)

        for mock_call in mock_run.call_args_list:
            args, kwargs = mock_call
            self.assertNotIn('shell', kwargs, "shell=True should not be used")
            self.assertFalse(kwargs.get('shell', False), "shell must be False or absent")
            self.assertIsInstance(args[0], list, "Arguments should be passed as a list")

if __name__ == '__main__':
    unittest.main()
