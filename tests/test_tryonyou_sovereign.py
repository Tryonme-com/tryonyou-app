"""
Tests para TryOnYouSovereign:
  - __init__: atributos de versión, assets y configuración
  - autenticar_bunker: formato y consistencia de la firma
  - ejecutar_flujo_piloto: estructura y contenido del lead
  - reporte_financiero_total: cálculo del total de activos
"""

from __future__ import annotations

import os
import sys
import unittest

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
_API = os.path.join(_ROOT, "api")
for _p in (_ROOT, _API):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from tryonyou_sovereign import TryOnYouSovereign


# ---------------------------------------------------------------------------
# TryOnYouSovereign.__init__
# ---------------------------------------------------------------------------

class TestTryOnYouSovereignInit(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = TryOnYouSovereign()

    def test_version(self) -> None:
        self.assertEqual(self.engine.version, "10.9")

    def test_kernel(self) -> None:
        self.assertEqual(self.engine.kernel, "2.31.0")

    def test_latency(self) -> None:
        self.assertEqual(self.engine.latency, "24ms")

    def test_google_sheets_db(self) -> None:
        self.assertEqual(self.engine.google_sheets_db, "Divineo_Leads_DB")

    def test_auth_active(self) -> None:
        self.assertTrue(self.engine.auth_active)

    def test_assets_is_dict(self) -> None:
        self.assertIsInstance(self.engine.assets, dict)

    def test_assets_keys(self) -> None:
        expected_keys = {
            "Licencia_Lafayette",
            "Licencia_Bon_Marche",
            "VIP_Friends_Program",
            "Stripe_Pipeline",
        }
        self.assertEqual(set(self.engine.assets.keys()), expected_keys)

    def test_assets_total_exceeds_37000(self) -> None:
        self.assertGreater(sum(self.engine.assets.values()), 37000)

    def test_licencia_lafayette_value(self) -> None:
        self.assertAlmostEqual(self.engine.assets["Licencia_Lafayette"], 12500.00)

    def test_licencia_bon_marche_value(self) -> None:
        self.assertAlmostEqual(self.engine.assets["Licencia_Bon_Marche"], 15000.00)

    def test_vip_friends_program_value(self) -> None:
        self.assertAlmostEqual(self.engine.assets["VIP_Friends_Program"], 8400.00)

    def test_stripe_pipeline_value(self) -> None:
        self.assertAlmostEqual(self.engine.assets["Stripe_Pipeline"], 1988.00)


# ---------------------------------------------------------------------------
# autenticar_bunker
# ---------------------------------------------------------------------------

class TestAutenticarBunker(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = TryOnYouSovereign()

    def test_returns_string(self) -> None:
        result = self.engine.autenticar_bunker("TEST_TOKEN")
        self.assertIsInstance(result, str)

    def test_prefix_auth_ok(self) -> None:
        result = self.engine.autenticar_bunker("TEST_TOKEN")
        self.assertTrue(result.startswith("AUTH_OK_"))

    def test_signature_length(self) -> None:
        # "AUTH_OK_" (8 chars) + 8-char signature = 16 total
        result = self.engine.autenticar_bunker("TEST_TOKEN")
        self.assertEqual(len(result), 16)

    def test_signature_uppercase(self) -> None:
        result = self.engine.autenticar_bunker("abc123")
        suffix = result[len("AUTH_OK_"):]
        self.assertEqual(suffix, suffix.upper())

    def test_deterministic(self) -> None:
        r1 = self.engine.autenticar_bunker("SAME_TOKEN")
        r2 = self.engine.autenticar_bunker("SAME_TOKEN")
        self.assertEqual(r1, r2)

    def test_different_tokens_different_signatures(self) -> None:
        r1 = self.engine.autenticar_bunker("TOKEN_A")
        r2 = self.engine.autenticar_bunker("TOKEN_B")
        self.assertNotEqual(r1, r2)

    def test_empty_token(self) -> None:
        result = self.engine.autenticar_bunker("")
        self.assertTrue(result.startswith("AUTH_OK_"))


# ---------------------------------------------------------------------------
# ejecutar_flujo_piloto
# ---------------------------------------------------------------------------

class TestEjecutarFlujoPiloto(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = TryOnYouSovereign()
        self.lead = self.engine.ejecutar_flujo_piloto(
            "Client_Sovereign_Paris", "vip.contact@luxury.fr", brand="Valentino"
        )

    def test_returns_dict(self) -> None:
        self.assertIsInstance(self.lead, dict)

    def test_all_keys_present(self) -> None:
        for key in ("ID", "Timestamp", "Cliente", "Email", "Interés", "Status", "Jules_V7_Action"):
            self.assertIn(key, self.lead)

    def test_client_name(self) -> None:
        self.assertEqual(self.lead["Cliente"], "Client_Sovereign_Paris")

    def test_email(self) -> None:
        self.assertEqual(self.lead["Email"], "vip.contact@luxury.fr")

    def test_look_contains_brand(self) -> None:
        self.assertIn("Valentino", self.lead["Interés"])

    def test_look_contains_v10(self) -> None:
        self.assertIn("V10", self.lead["Interés"])

    def test_status_rich_people_tendency(self) -> None:
        self.assertEqual(self.lead["Status"], "Rich_People_Tendency")

    def test_jules_action(self) -> None:
        self.assertEqual(self.lead["Jules_V7_Action"], "Email_QR_Sent")

    def test_scan_id_length(self) -> None:
        self.assertEqual(len(self.lead["ID"]), 6)

    def test_default_brand_balmain(self) -> None:
        lead = self.engine.ejecutar_flujo_piloto("Test", "test@test.com")
        self.assertIn("Balmain", lead["Interés"])

    def test_timestamp_format(self) -> None:
        import re
        pattern = r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$"
        self.assertRegex(self.lead["Timestamp"], pattern)


# ---------------------------------------------------------------------------
# reporte_financiero_total
# ---------------------------------------------------------------------------

class TestReporteFinancieroTotal(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = TryOnYouSovereign()

    def test_returns_float(self) -> None:
        result = self.engine.reporte_financiero_total()
        self.assertIsInstance(result, float)

    def test_total_correct(self) -> None:
        expected = sum(self.engine.assets.values())
        result = self.engine.reporte_financiero_total()
        self.assertAlmostEqual(result, expected, places=2)

    def test_total_value(self) -> None:
        result = self.engine.reporte_financiero_total()
        self.assertAlmostEqual(result, 37888.00, places=2)

    def test_total_exceeds_37000(self) -> None:
        result = self.engine.reporte_financiero_total()
        self.assertGreater(result, 37000)

    def test_modified_assets_reflected(self) -> None:
        self.engine.assets["Stripe_Pipeline"] = 5000.00
        result = self.engine.reporte_financiero_total()
        expected = (
            self.engine.assets["Licencia_Lafayette"]
            + self.engine.assets["Licencia_Bon_Marche"]
            + self.engine.assets["VIP_Friends_Program"]
            + 5000.00
        )
        self.assertAlmostEqual(result, expected, places=2)


if __name__ == "__main__":
    unittest.main()
