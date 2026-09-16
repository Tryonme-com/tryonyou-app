import unittest
from unittest.mock import patch

from terminar_web_ahora import _run

class TestTerminarWebAhora(unittest.TestCase):

    @patch('terminar_web_ahora.subprocess.run')
    def test_run_oserror(self, mock_run):
        mock_run.side_effect = OSError("Mocked OS error")
        result = _run(["mock", "command"])
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
