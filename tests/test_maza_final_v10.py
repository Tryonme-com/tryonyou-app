import unittest
from unittest.mock import patch
import sys
from unittest.mock import MagicMock

# Mock stripe before importing the module
sys.modules['stripe'] = MagicMock()

import maza_final_v10

class TestMazaFinalV10(unittest.TestCase):
    @patch("maza_final_v10.subprocess.run")
    @patch("maza_final_v10.os.chdir")
    def test_sellar_bunker_git(self, mock_chdir, mock_run):
        # Call the function
        maza_final_v10.sellar_bunker_git()

        # Verify chdir was called
        mock_chdir.assert_called_once_with(maza_final_v10.PROJECT_ROOT)

        # Verify subprocess.run calls
        self.assertEqual(mock_run.call_count, 3)

        # First call: git add .
        call1 = mock_run.call_args_list[0]
        self.assertEqual(call1[0][0], ["git", "add", "."])
        self.assertNotIn("shell", call1[1]) # ensure shell is not True

        # Second call: git commit -m msg
        call2 = mock_run.call_args_list[1]
        self.assertEqual(call2[0][0], ["git", "commit", "-m", f"V10.4 OMEGA: Bunker 75005 Blindado - Patente {maza_final_v10.PATENTE}"])
        self.assertNotIn("shell", call2[1])

        # Third call: git push origin main --force
        call3 = mock_run.call_args_list[2]
        self.assertEqual(call3[0][0], ["git", "push", "origin", "main", "--force"])
        self.assertNotIn("shell", call3[1])

if __name__ == '__main__':
    unittest.main()
