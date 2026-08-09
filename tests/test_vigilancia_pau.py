import os
import subprocess
from unittest import mock
import pytest

from vigilancia_pau import disparar_sincronizacion_bunker

class TestVigilanciaPau:
    @mock.patch.dict(os.environ, {"BUNKER_SYNC_CMD": "python v10_terminal.py --sync"})
    @mock.patch("vigilancia_pau.subprocess.run")
    def test_disparar_sincronizacion_bunker_valid_cmd(self, mock_run):
        disparar_sincronizacion_bunker()
        mock_run.assert_called_once_with(["python", "v10_terminal.py", "--sync"], shell=False, check=False)

    @mock.patch.dict(os.environ, {"BUNKER_SYNC_CMD": "   "})
    @mock.patch("vigilancia_pau.subprocess.run")
    def test_disparar_sincronizacion_bunker_empty_cmd(self, mock_run):
        disparar_sincronizacion_bunker()
        mock_run.assert_not_called()

    @mock.patch.dict(os.environ, {}, clear=True)
    @mock.patch("vigilancia_pau.subprocess.run")
    def test_disparar_sincronizacion_bunker_no_env_var(self, mock_run):
        disparar_sincronizacion_bunker()
        mock_run.assert_not_called()

    @mock.patch.dict(os.environ, {"BUNKER_SYNC_CMD": 'echo "hello"'})
    @mock.patch("vigilancia_pau.subprocess.run")
    def test_disparar_sincronizacion_bunker_quotes(self, mock_run):
        disparar_sincronizacion_bunker()
        mock_run.assert_called_once_with(["echo", "hello"], shell=False, check=False)

    @mock.patch.dict(os.environ, {"BUNKER_SYNC_CMD": 'echo "unclosed quote'})
    @mock.patch("vigilancia_pau.subprocess.run")
    def test_disparar_sincronizacion_bunker_invalid_shlex(self, mock_run, capsys):
        disparar_sincronizacion_bunker()
        mock_run.assert_not_called()
        captured = capsys.readouterr()
        assert "Error al parsear BUNKER_SYNC_CMD" in captured.out
