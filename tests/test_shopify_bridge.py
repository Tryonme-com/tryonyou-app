"""Tests de validación de venta ABVETOS en Shopify.

Objetivo: confirmar que el flujo desde el escaneo en el espejo digital hasta
la asignación del VARIANT_ID cierra la transacción sin fricciones.

Cubre:
  1. Construcción de URL storefront con atributos biométricos (Zero-Size).
  2. Fallback a URL directa configurada (SHOPIFY_PERFECT_CHECKOUT_URL).
  3. Creación de draft order vía Admin API (mock HTTP).
  4. Flujo completo resolve_shopify_checkout_url: Admin primero, storefront segundo.
  5. Casos de error: credenciales ausentes, VARIANT_ID inválido, fallo de red.
"""

from __future__ import annotations

import io
import json
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Añadir el directorio api al path para importar el módulo
_API = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "api"))
if _API not in sys.path:
    sys.path.insert(0, _API)

from shopify_bridge import (
    PATENTE,
    SIREN_SELL,
    admin_draft_order_invoice_url,
    build_shopify_perfect_selection_url,
    resolve_shopify_checkout_url,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_VALID_ENV = {
    "SHOPIFY_ADMIN_ACCESS_TOKEN": "shpat_testtoken123",
    "SHOPIFY_STORE_DOMAIN": "tienda-prueba.myshopify.com",
    "SHOPIFY_MYSHOPIFY_HOST": "tienda-prueba.myshopify.com",
    "SHOPIFY_ZERO_SIZE_VARIANT_ID": "987654321",
    "SHOPIFY_ADMIN_API_VERSION": "2024-10",
    "SHOPIFY_PERFECT_CHECKOUT_URL": "",
    "SHOPIFY_PERFECT_PRODUCT_PATH": "",
}


def _mock_urlopen(invoice_url: str = "https://tienda-prueba.myshopify.com/invoices/abc123"):
    """Devuelve un context-manager que simula urllib.request.urlopen con éxito."""
    response_body = json.dumps({"draft_order": {"invoice_url": invoice_url}}).encode()
    mock_resp = MagicMock()
    mock_resp.read.return_value = response_body
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    return mock_resp


# ---------------------------------------------------------------------------
# 1. Storefront URL — flujo biométrico Zero-Size
# ---------------------------------------------------------------------------


class TestBuildShopifyPerfectSelectionUrl(unittest.TestCase):
    """Valida que la URL storefront incluye los atributos del escaneo del espejo digital."""

    def test_url_con_dominio_incluye_lead_y_sensacion(self) -> None:
        env = {
            **_VALID_ENV,
            "SHOPIFY_STORE_DOMAIN": "tienda-prueba.myshopify.com",
            "SHOPIFY_PERFECT_CHECKOUT_URL": "",
        }
        with patch.dict(os.environ, env, clear=False):
            url = build_shopify_perfect_selection_url(
                lead_id=42,
                fabric_sensation="seda_alpaca",
                biometric_hash="hash_biometrico_abc",
            )
        self.assertIsNotNone(url)
        self.assertIn("lead_42", url)
        self.assertIn("tryonyou_v10", url)
        self.assertIn(PATENTE.replace("/", "_"), url)

    def test_url_directa_incluye_atributos_biometricos(self) -> None:
        import urllib.parse

        env = {
            **_VALID_ENV,
            "SHOPIFY_PERFECT_CHECKOUT_URL": "https://tienda-prueba.myshopify.com/cart/987654321:1",
        }
        with patch.dict(os.environ, env, clear=False):
            url = build_shopify_perfect_selection_url(
                lead_id=7,
                fabric_sensation="cachemira",
                biometric_hash="hash_soberano_xyz",
            )
        self.assertIsNotNone(url)
        assert url is not None
        decoded = urllib.parse.unquote(url)
        self.assertIn("tryonyou_lead", decoded)
        self.assertIn("fit_sensation", decoded)
        self.assertIn(SIREN_SELL.replace(" ", ""), decoded)
        self.assertIn(PATENTE, decoded)
        self.assertIn("hash_soberano_xyz", decoded)

    def test_sin_dominio_retorna_none(self) -> None:
        env = {
            "SHOPIFY_STORE_DOMAIN": "",
            "SHOPIFY_PERFECT_CHECKOUT_URL": "",
        }
        with patch.dict(os.environ, env, clear=False):
            url = build_shopify_perfect_selection_url(1, "lino")
        self.assertIsNone(url)

    def test_url_directa_sin_hash_biometrico(self) -> None:
        env = {
            **_VALID_ENV,
            "SHOPIFY_PERFECT_CHECKOUT_URL": "https://tienda-prueba.myshopify.com/cart/987654321:1",
        }
        with patch.dict(os.environ, env, clear=False):
            url = build_shopify_perfect_selection_url(lead_id=3, fabric_sensation="lino")
        self.assertIsNotNone(url)
        assert url is not None
        self.assertNotIn("_Sovereignty_ID", url)

    def test_sensacion_larga_es_truncada(self) -> None:
        larga = "x" * 200
        env = {
            **_VALID_ENV,
            "SHOPIFY_PERFECT_CHECKOUT_URL": "https://tienda-prueba.myshopify.com/cart/987654321:1",
        }
        with patch.dict(os.environ, env, clear=False):
            url = build_shopify_perfect_selection_url(1, larga)
        self.assertIsNotNone(url)


# ---------------------------------------------------------------------------
# 2. Admin API — draft order con VARIANT_ID
# ---------------------------------------------------------------------------


class TestAdminDraftOrderInvoiceUrl(unittest.TestCase):
    """Valida la asignación del VARIANT_ID y la creación del draft order."""

    def test_retorna_invoice_url_con_credenciales_validas(self) -> None:
        expected = "https://tienda-prueba.myshopify.com/invoices/abc123"
        with patch.dict(os.environ, _VALID_ENV, clear=False):
            with patch("urllib.request.urlopen", return_value=_mock_urlopen(expected)):
                url = admin_draft_order_invoice_url(
                    lead_id=1,
                    fabric_sensation="seda",
                    biometric_hash="hash_abc",
                )
        self.assertEqual(url, expected)

    def test_payload_incluye_variant_id_correcto(self) -> None:
        """El VARIANT_ID del entorno debe aparecer en el body enviado a Shopify."""
        captured_request = {}

        def fake_urlopen(req, **_kwargs):
            captured_request["data"] = json.loads(req.data.decode("utf-8"))
            return _mock_urlopen()

        with patch.dict(os.environ, _VALID_ENV, clear=False):
            with patch("urllib.request.urlopen", side_effect=fake_urlopen):
                admin_draft_order_invoice_url(1, "algodón", "hash_soberano")

        line_items = captured_request["data"]["draft_order"]["line_items"]
        self.assertEqual(len(line_items), 1)
        self.assertEqual(line_items[0]["variant_id"], 987654321)
        self.assertEqual(line_items[0]["quantity"], 1)

    def test_payload_incluye_hash_biometrico_como_propiedad(self) -> None:
        """El hash biométrico del escaneo debe registrarse como _Sovereignty_ID."""
        captured_request = {}

        def fake_urlopen(req, **_kwargs):
            captured_request["data"] = json.loads(req.data.decode("utf-8"))
            return _mock_urlopen()

        biometric = "escaneo_espejo_digital_001"
        with patch.dict(os.environ, _VALID_ENV, clear=False):
            with patch("urllib.request.urlopen", side_effect=fake_urlopen):
                admin_draft_order_invoice_url(1, "seda", biometric)

        props = captured_request["data"]["draft_order"]["line_items"][0]["properties"]
        names = [p["name"] for p in props]
        self.assertIn("_Sovereignty_ID", names)
        sovereignty_prop = next(p for p in props if p["name"] == "_Sovereignty_ID")
        self.assertEqual(sovereignty_prop["value"], biometric)

    def test_sin_hash_biometrico_no_incluye_sovereignty_id(self) -> None:
        captured_request = {}

        def fake_urlopen(req, **_kwargs):
            captured_request["data"] = json.loads(req.data.decode("utf-8"))
            return _mock_urlopen()

        with patch.dict(os.environ, _VALID_ENV, clear=False):
            with patch("urllib.request.urlopen", side_effect=fake_urlopen):
                admin_draft_order_invoice_url(1, "lino")

        props = captured_request["data"]["draft_order"]["line_items"][0]["properties"]
        names = [p["name"] for p in props]
        self.assertNotIn("_Sovereignty_ID", names)
        self.assertIn("_Patent", names)

    def test_retorna_none_sin_token(self) -> None:
        env = {**_VALID_ENV, "SHOPIFY_ADMIN_ACCESS_TOKEN": ""}
        with patch.dict(os.environ, env, clear=False):
            url = admin_draft_order_invoice_url(1, "lino")
        self.assertIsNone(url)

    def test_retorna_none_sin_variant_id(self) -> None:
        env = {**_VALID_ENV, "SHOPIFY_ZERO_SIZE_VARIANT_ID": ""}
        with patch.dict(os.environ, env, clear=False):
            url = admin_draft_order_invoice_url(1, "lino")
        self.assertIsNone(url)

    def test_retorna_none_con_variant_id_no_numerico(self) -> None:
        env = {**_VALID_ENV, "SHOPIFY_ZERO_SIZE_VARIANT_ID": "no-es-numero"}
        with patch.dict(os.environ, env, clear=False):
            url = admin_draft_order_invoice_url(1, "lino")
        self.assertIsNone(url)

    def test_retorna_none_si_host_no_es_myshopify(self) -> None:
        env = {
            **_VALID_ENV,
            "SHOPIFY_MYSHOPIFY_HOST": "tienda-personalizada.com",
        }
        with patch.dict(os.environ, env, clear=False):
            url = admin_draft_order_invoice_url(1, "lino")
        self.assertIsNone(url)

    def test_retorna_none_ante_fallo_de_red(self) -> None:
        import urllib.error

        with patch.dict(os.environ, _VALID_ENV, clear=False):
            with patch(
                "urllib.request.urlopen",
                side_effect=urllib.error.URLError("connection refused"),
            ):
                url = admin_draft_order_invoice_url(1, "seda")
        self.assertIsNone(url)

    def test_retorna_none_si_invoice_url_ausente_en_respuesta(self) -> None:
        response_body = json.dumps({"draft_order": {}}).encode()
        mock_resp = MagicMock()
        mock_resp.read.return_value = response_body
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch.dict(os.environ, _VALID_ENV, clear=False):
            with patch("urllib.request.urlopen", return_value=mock_resp):
                url = admin_draft_order_invoice_url(1, "lino")
        self.assertIsNone(url)

    def test_note_incluye_lead_y_patente(self) -> None:
        captured_request = {}

        def fake_urlopen(req, **_kwargs):
            captured_request["data"] = json.loads(req.data.decode("utf-8"))
            return _mock_urlopen()

        with patch.dict(os.environ, _VALID_ENV, clear=False):
            with patch("urllib.request.urlopen", side_effect=fake_urlopen):
                admin_draft_order_invoice_url(99, "terciopelo")

        note = captured_request["data"]["draft_order"]["note"]
        self.assertIn("lead #99", note)
        self.assertIn(PATENTE, note)
        self.assertIn(SIREN_SELL, note)


# ---------------------------------------------------------------------------
# 3. Flujo completo — resolve_shopify_checkout_url
# ---------------------------------------------------------------------------


class TestResolveShopifyCheckoutUrl(unittest.TestCase):
    """Valida el flujo end-to-end: espejo digital → VARIANT_ID → cierre sin fricciones."""

    def test_prioriza_admin_cuando_credenciales_disponibles(self) -> None:
        expected = "https://tienda-prueba.myshopify.com/invoices/xyz"
        with patch.dict(os.environ, _VALID_ENV, clear=False):
            with patch("urllib.request.urlopen", return_value=_mock_urlopen(expected)):
                url = resolve_shopify_checkout_url(
                    lead_id=5,
                    fabric_sensation="seda",
                    biometric_hash="escaneo_123",
                )
        self.assertEqual(url, expected)

    def test_fallback_a_storefront_si_admin_falla(self) -> None:
        import urllib.error

        env = {
            **_VALID_ENV,
            "SHOPIFY_PERFECT_CHECKOUT_URL": "",
        }
        with patch.dict(os.environ, env, clear=False):
            with patch(
                "urllib.request.urlopen",
                side_effect=urllib.error.URLError("timeout"),
            ):
                url = resolve_shopify_checkout_url(
                    lead_id=10,
                    fabric_sensation="cachemira",
                    biometric_hash="hash_fallback",
                )
        # El fallback storefront requiere al menos el dominio
        self.assertIsNotNone(url)
        assert url is not None
        self.assertIn("lead_10", url)

    def test_retorna_none_sin_ninguna_configuracion(self) -> None:
        env = {
            "SHOPIFY_ADMIN_ACCESS_TOKEN": "",
            "SHOPIFY_STORE_DOMAIN": "",
            "SHOPIFY_MYSHOPIFY_HOST": "",
            "SHOPIFY_ZERO_SIZE_VARIANT_ID": "",
            "SHOPIFY_PERFECT_CHECKOUT_URL": "",
        }
        with patch.dict(os.environ, env, clear=False):
            url = resolve_shopify_checkout_url(1, "lino")
        self.assertIsNone(url)

    def test_flujo_sin_hash_biometrico(self) -> None:
        """El flujo debe funcionar incluso sin hash biométrico (escaneo opcional)."""
        expected = "https://tienda-prueba.myshopify.com/invoices/noHash"
        with patch.dict(os.environ, _VALID_ENV, clear=False):
            with patch("urllib.request.urlopen", return_value=_mock_urlopen(expected)):
                url = resolve_shopify_checkout_url(lead_id=2, fabric_sensation="lino")
        self.assertEqual(url, expected)


if __name__ == "__main__":
    unittest.main()
