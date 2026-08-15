import unittest
from unittest.mock import patch, call
from maza_final_v10 import sellar_bunker_git, PATENTE

class TestMazaFinalV10(unittest.TestCase):

    @patch('maza_final_v10.subprocess.run')
    @patch('maza_final_v10.os.chdir')
    def test_sellar_bunker_git_no_shell(self, mock_chdir, mock_run):
        sellar_bunker_git()

        msg = f"V10.4 OMEGA: Bunker 75005 Blindado - Patente {PATENTE}"
        expected_calls = [
            call(["git", "add", "."]),
            call(["git", "commit", "-m", msg]),
            call(["git", "push", "origin", "main", "--force"])
        ]

        mock_run.assert_has_calls(expected_calls)

        # Verify no shell=True was used
        for _, kwargs in mock_run.call_args_list:
            self.assertNotIn('shell', kwargs)
            self.assertFalse(kwargs.get('shell', False))

if __name__ == '__main__':
    unittest.main()
