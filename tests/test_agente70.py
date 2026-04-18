import unittest
from unittest.mock import Mock, patch

import requests

from agente70 import Agente70


class TestAgente70(unittest.TestCase):
    @patch("agente70.requests.get")
    def test_validate_sovereign_status_restricts_on_402(self, mock_get: Mock) -> None:
        mock_get.return_value = Mock(status_code=402)
        agent = Agente70()

        self.assertFalse(agent.validate_sovereign_status())
        self.assertEqual(agent.status, "RESTRICTED")

    @patch("agente70.requests.get")
    def test_validate_sovereign_status_allows_200_when_payload_is_not_json(self, mock_get: Mock) -> None:
        mock_response = Mock(status_code=200)
        mock_response.json.side_effect = ValueError("not json")
        mock_get.return_value = mock_response
        agent = Agente70()

        self.assertTrue(agent.validate_sovereign_status())
        self.assertEqual(agent.status, "OPERATIONAL")

    @patch("agente70.requests.get")
    def test_validate_sovereign_status_handles_request_error(self, mock_get: Mock) -> None:
        mock_get.side_effect = requests.RequestException("network down")
        agent = Agente70()

        self.assertFalse(agent.validate_sovereign_status())
        self.assertEqual(agent.status, "DEGRADED")

    @patch("agente70.requests.get")
    def test_validate_sovereign_status_restricts_on_403(self, mock_get: Mock) -> None:
        mock_get.return_value = Mock(status_code=403)
        agent = Agente70()

        self.assertFalse(agent.validate_sovereign_status())
        self.assertEqual(agent.status, "RESTRICTED")

    @patch("agente70.requests.get")
    def test_validate_sovereign_status_degrades_on_500(self, mock_get: Mock) -> None:
        mock_get.return_value = Mock(status_code=500)
        agent = Agente70()

        self.assertFalse(agent.validate_sovereign_status())
        self.assertEqual(agent.status, "DEGRADED")

    @patch("agente70.requests.get")
    def test_validate_sovereign_status_restricts_when_payload_marks_inactive(self, mock_get: Mock) -> None:
        mock_response = Mock(status_code=200)
        mock_response.json.return_value = {"subscription_active": False}
        mock_get.return_value = mock_response
        agent = Agente70()

        self.assertFalse(agent.validate_sovereign_status())
        self.assertEqual(agent.status, "RESTRICTED")

    @patch("agente70.requests.get")
    def test_validate_sovereign_status_degrades_on_ambiguous_payload_shape(self, mock_get: Mock) -> None:
        mock_response = Mock(status_code=200)
        mock_response.json.return_value = ["unexpected", "list"]
        mock_get.return_value = mock_response
        agent = Agente70()

        self.assertFalse(agent.validate_sovereign_status())
        self.assertEqual(agent.status, "DEGRADED")

    def test_process_request_returns_restriction_message_when_validation_fails(self) -> None:
        agent = Agente70()
        with (
            patch.object(agent, "validate_sovereign_status", return_value=False),
            patch.object(agent, "sync_with_drive") as sync_mock,
        ):
            result = agent.process_request("hola")

        self.assertIn("espera refinada", result)
        sync_mock.assert_not_called()

    def test_process_request_syncs_and_returns_success_message_when_validation_passes(self) -> None:
        agent = Agente70()
        with (
            patch.object(agent, "validate_sovereign_status", return_value=True),
            patch.object(agent, "sync_with_drive", return_value={"synced": True}) as sync_mock,
        ):
            result = agent.process_request("mensaje")

        sync_mock.assert_called_once_with("mensaje")
        self.assertIn("He procesado tu petición", result)
        self.assertIn("mensaje", result)

    def test_process_request_handles_sync_exceptions(self) -> None:
        agent = Agente70()
        with (
            patch.object(agent, "validate_sovereign_status", return_value=True),
            patch.object(agent, "sync_with_drive", side_effect=RuntimeError("drive down")),
        ):
            result = agent.process_request("mensaje")

        self.assertIn("contingencia", result)
        self.assertEqual(agent.status, "DEGRADED")

    def test_process_request_coerces_non_string_input(self) -> None:
        agent = Agente70()
        with (
            patch.object(agent, "validate_sovereign_status", return_value=True),
            patch.object(agent, "sync_with_drive") as sync_mock,
        ):
            result = agent.process_request({"payload": "ok"})  # type: ignore[arg-type]

        sync_mock.assert_called_once_with("{'payload': 'ok'}")
        self.assertIn("{'payload': 'ok'}", result)


if __name__ == "__main__":
    unittest.main()
