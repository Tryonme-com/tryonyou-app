from __future__ import annotations

import io
import os
import unittest
from contextlib import redirect_stdout
from unittest.mock import Mock, patch

import requests

import bunker_status


class TestBunkerStatus(unittest.TestCase):
    def test_returns_none_when_system_token_missing(self) -> None:
        old = os.environ.pop("SYSTEM_TOKEN", None)
        try:
            with io.StringIO() as buf, redirect_stdout(buf):
                result = bunker_status.get_bunker_status()
                output = buf.getvalue()
            self.assertIsNone(result)
            self.assertIn("SYSTEM_TOKEN no configurado", output)
        finally:
            if old is not None:
                os.environ["SYSTEM_TOKEN"] = old

    @patch("bunker_status.requests.get")
    def test_successful_bunker_status_fetch(self, mock_get: Mock) -> None:
        old = os.environ.get("SYSTEM_TOKEN")
        os.environ["SYSTEM_TOKEN"] = "token-ok"
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "status": "ACTIVE",
            "pending_amount": 27500,
            "e2e_reference": "E2E-123",
        }
        mock_get.return_value = mock_response
        try:
            with io.StringIO() as buf, redirect_stdout(buf):
                result = bunker_status.get_bunker_status()
                output = buf.getvalue()
            self.assertIsInstance(result, dict)
            self.assertEqual(result["status"], "ACTIVE")
            self.assertIn("ESTADO BANCARIO: ACTIVE", output)
            self.assertIn("SALDO EN TRÁNSITO: 27500 EUR", output)
            self.assertIn("REFERENCIA E2E: E2E-123", output)
            mock_get.assert_called_once()
            self.assertIn("timeout", mock_get.call_args.kwargs)
        finally:
            if old is None:
                os.environ.pop("SYSTEM_TOKEN", None)
            else:
                os.environ["SYSTEM_TOKEN"] = old

    @patch("bunker_status.requests.get")
    def test_request_exception_returns_none(self, mock_get: Mock) -> None:
        old = os.environ.get("SYSTEM_TOKEN")
        os.environ["SYSTEM_TOKEN"] = "token-ok"
        mock_get.side_effect = requests.RequestException("boom")
        try:
            with io.StringIO() as buf, redirect_stdout(buf):
                result = bunker_status.get_bunker_status()
                output = buf.getvalue()
            self.assertIsNone(result)
            self.assertIn("Error de sincronización:", output)
            self.assertIn("boom", output)
        finally:
            if old is None:
                os.environ.pop("SYSTEM_TOKEN", None)
            else:
                os.environ["SYSTEM_TOKEN"] = old

    @patch("bunker_status.requests.get")
    def test_non_dict_json_returns_none(self, mock_get: Mock) -> None:
        old = os.environ.get("SYSTEM_TOKEN")
        os.environ["SYSTEM_TOKEN"] = "token-ok"
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = ["not-a-dict"]
        mock_get.return_value = mock_response
        try:
            with io.StringIO() as buf, redirect_stdout(buf):
                result = bunker_status.get_bunker_status()
                output = buf.getvalue()
            self.assertIsNone(result)
            self.assertIn("Error de sincronización:", output)
            self.assertIn("non-dictionary", output)
        finally:
            if old is None:
                os.environ.pop("SYSTEM_TOKEN", None)
            else:
                os.environ["SYSTEM_TOKEN"] = old

    @patch("bunker_status.requests.get")
    def test_invalid_timeout_env_uses_default(self, mock_get: Mock) -> None:
        old_token = os.environ.get("SYSTEM_TOKEN")
        old_timeout = os.environ.get("BUNKER_STATUS_TIMEOUT_SECONDS")
        os.environ["SYSTEM_TOKEN"] = "token-ok"
        os.environ["BUNKER_STATUS_TIMEOUT_SECONDS"] = "invalid"
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "status": "ACTIVE",
            "pending_amount": 1,
            "e2e_reference": "E2E",
        }
        mock_get.return_value = mock_response
        try:
            with io.StringIO() as buf, redirect_stdout(buf):
                result = bunker_status.get_bunker_status()
                output = buf.getvalue()
            self.assertIsInstance(result, dict)
            self.assertIn("BUNKER_STATUS_TIMEOUT_SECONDS inválido", output)
            self.assertEqual(
                mock_get.call_args.kwargs.get("timeout"),
                bunker_status.DEFAULT_TIMEOUT_SECONDS,
            )
        finally:
            if old_token is None:
                os.environ.pop("SYSTEM_TOKEN", None)
            else:
                os.environ["SYSTEM_TOKEN"] = old_token
            if old_timeout is None:
                os.environ.pop("BUNKER_STATUS_TIMEOUT_SECONDS", None)
            else:
                os.environ["BUNKER_STATUS_TIMEOUT_SECONDS"] = old_timeout


if __name__ == "__main__":
    unittest.main()
