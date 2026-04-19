from __future__ import annotations

import os
import sys
import unittest

_API = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "api"))
if _API not in sys.path:
    sys.path.insert(0, _API)

from pau_agent import PauAgent


class TestPauAgent(unittest.TestCase):
    def setUp(self) -> None:
        self.agent = PauAgent()

    def test_defaults(self) -> None:
        self.assertEqual(self.agent.name, "Pau")
        self.assertEqual(self.agent.persona, "Eric Lafayette")
        self.assertEqual(self.agent.status, "ACTIVE")

    def test_check_sovereign_protocol_allows_non_restricted_account(self) -> None:
        allowed = self.agent.check_sovereign_protocol({"id": "123", "status_402": False})
        self.assertTrue(allowed)
        self.assertEqual(self.agent.status, "ACTIVE")

    def test_check_sovereign_protocol_blocks_restricted_account(self) -> None:
        allowed = self.agent.check_sovereign_protocol({"id": "123", "status_402": True})
        self.assertFalse(allowed)
        self.assertEqual(self.agent.status, "RESTRICTED")

    def test_check_sovereign_protocol_restores_active_status(self) -> None:
        self.assertFalse(self.agent.check_sovereign_protocol({"id": "123", "status_402": True}))
        self.assertEqual(self.agent.status, "RESTRICTED")
        self.assertTrue(self.agent.check_sovereign_protocol({"id": "123", "status_402": False}))
        self.assertEqual(self.agent.status, "ACTIVE")

    def test_generate_response_returns_protocol_message_when_restricted(self) -> None:
        response = self.agent.generate_response(
            "¿Qué look me recomiendas hoy?",
            {"id": "123", "status_402": True},
        )
        self.assertIn("protocolo soberano", response.lower())
        self.assertIn("ajuste técnico", response.lower())
        self.assertEqual(self.agent.status, "RESTRICTED")

    def test_generate_response_returns_persona_message_when_active(self) -> None:
        user_input = "¿Qué look me recomiendas hoy?"
        response = self.agent.generate_response(
            user_input,
            {"id": "123", "status_402": False},
        )
        self.assertIn("Yves Saint Laurent", response)
        self.assertIn(user_input, response)

    def test_generate_response_escapes_user_input(self) -> None:
        response = self.agent.generate_response(
            "<b>look</b>",
            {"id": "123", "status_402": False},
        )
        self.assertIn("&lt;b&gt;look&lt;/b&gt;", response)


if __name__ == "__main__":
    unittest.main()
