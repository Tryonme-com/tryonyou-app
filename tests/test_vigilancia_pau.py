import unittest
from unittest.mock import patch, MagicMock
import os
import vigilancia_pau

class TestVigilanciaPau(unittest.TestCase):

    @patch('vigilancia_pau.subprocess.run')
    @patch.dict(os.environ, {"BUNKER_SYNC_CMD": "python script.py arg1 arg2"}, clear=True)
    def test_disparar_sincronizacion_bunker_shell_false(self, mock_run):
        vigilancia_pau.disparar_sincronizacion_bunker()

        mock_run.assert_called_once_with(
            ['python', 'script.py', 'arg1', 'arg2'],
            shell=False,
            check=False
        )

    @patch('vigilancia_pau.subprocess.run')
    @patch.dict(os.environ, {}, clear=True)
    def test_disparar_sincronizacion_bunker_no_cmd(self, mock_run):
        vigilancia_pau.disparar_sincronizacion_bunker()
        mock_run.assert_not_called()

if __name__ == '__main__':
    unittest.main()
