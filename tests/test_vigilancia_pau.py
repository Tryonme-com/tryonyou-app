import os
import sys
from unittest.mock import patch

# add root to sys.path to import vigilancia_pau
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import vigilancia_pau

@patch('subprocess.run')
def test_disparar_sincronizacion_bunker(mock_run):
    os.environ["BUNKER_SYNC_CMD"] = "echo 'hello world'"
    vigilancia_pau.disparar_sincronizacion_bunker()
    mock_run.assert_called_once_with(['echo', 'hello world'], shell=False, check=False)

    mock_run.reset_mock()

    os.environ["BUNKER_SYNC_CMD"] = ""
    vigilancia_pau.disparar_sincronizacion_bunker()
    mock_run.assert_not_called()
