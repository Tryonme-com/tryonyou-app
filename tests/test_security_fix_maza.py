import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Mock stripe before importing maza_final_v10
sys.modules['stripe'] = MagicMock()

import maza_final_v10

class TestSecurityFixMaza(unittest.TestCase):
    @patch("maza_final_v10.subprocess.run")
    @patch("maza_final_v10.os.chdir")
    def test_sellar_bunker_git_secure_calls(self, mock_chdir, mock_run):
        maza_final_v10.sellar_bunker_git()

        # Check calls to subprocess.run
        self.assertEqual(mock_run.call_count, 3)

        # Check first call: git add .
        args1, kwargs1 = mock_run.call_args_list[0]
        self.assertEqual(args1[0], ["git", "add", "."])
        self.assertFalse(kwargs1.get("shell", False))

        # Check second call: git commit -m "..."
        args2, kwargs2 = mock_run.call_args_list[1]
        msg = f"V10.4 OMEGA: Bunker 75005 Blindado - Patente {maza_final_v10.PATENTE}"
        self.assertEqual(args2[0], ["git", "commit", "-m", msg])
        self.assertFalse(kwargs2.get("shell", False))

        # Check third call: git push origin main --force
        args3, kwargs3 = mock_run.call_args_list[2]
        self.assertEqual(args3[0], ["git", "push", "origin", "main", "--force"])
        self.assertFalse(kwargs3.get("shell", False))

if __name__ == "__main__":
    unittest.main()
