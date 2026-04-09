"""Tests para JulesAgentV7 — Registro VIP en Divineo_Leads_DB."""

from __future__ import annotations

import os
import sys
import unittest

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
_API = os.path.join(_ROOT, "api")
for _p in (_ROOT, _API):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from jules_agent_v7 import JulesAgentV7


class TestJulesAgentV7Init(unittest.TestCase):
    def setUp(self) -> None:
        self.agent = JulesAgentV7()

    def test_database_name(self) -> None:
        self.assertEqual(self.agent.database, "Divineo_Leads_DB")

    def test_status_active(self) -> None:
        self.assertEqual(self.agent.status, "ACTIVO - Tendencia Alta")


class TestProcesarVipLead(unittest.TestCase):
    def setUp(self) -> None:
        self.agent = JulesAgentV7()

    def test_returns_dict(self) -> None:
        result = self.agent.procesar_vip_lead(
            "Sovereign_Client", "vip@paris.com", "Rouge Valentino"
        )
        self.assertIsInstance(result, dict)

    def test_email_status_sent_gmail(self) -> None:
        result = self.agent.procesar_vip_lead(
            "Sovereign_Client", "vip@paris.com", "Rouge Valentino"
        )
        self.assertEqual(result["email_status"], "SENT_GMAIL")

    def test_db_status_recorded(self) -> None:
        result = self.agent.procesar_vip_lead(
            "Sovereign_Client", "vip@paris.com", "Rouge Valentino"
        )
        self.assertEqual(result["db_status"], "RECORDED")

    def test_message_contains_nombre(self) -> None:
        result = self.agent.procesar_vip_lead(
            "Sovereign_Client", "vip@paris.com", "Rouge Valentino"
        )
        self.assertIn("Sovereign_Client", result["message"])

    def test_message_contains_audrey_hepburn_quote(self) -> None:
        result = self.agent.procesar_vip_lead(
            "Sovereign_Client", "vip@paris.com", "Rouge Valentino"
        )
        self.assertIn("Audrey Hepburn", result["message"])

    def test_message_contains_silueta(self) -> None:
        result = self.agent.procesar_vip_lead(
            "Sovereign_Client", "vip@paris.com", "Rouge Valentino"
        )
        self.assertIn("silueta", result["message"])

    def test_all_keys_present(self) -> None:
        result = self.agent.procesar_vip_lead(
            "Sovereign_Client", "vip@paris.com", "Rouge Valentino"
        )
        for key in ("email_status", "db_status", "message"):
            self.assertIn(key, result)

    def test_different_client_name_in_message(self) -> None:
        result = self.agent.procesar_vip_lead(
            "Marie Curie", "marie@paris.com", "Noir Chanel"
        )
        self.assertIn("Marie Curie", result["message"])
        self.assertNotIn("Sovereign_Client", result["message"])


if __name__ == "__main__":
    unittest.main()
