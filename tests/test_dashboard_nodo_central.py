"""Tests para el Dashboard Vivo 75001 — Monitor de liquidez (dashboard_nodo_central).

Cubre:
  1. get_revolut_balance: éxito, fallback por error de red, fallback sin token.
  2. get_paypal_balance: éxito, fallback sin credenciales, error en OAuth, error en saldo.
  3. publicar_en_slack: mensaje correcto, fallo sin credenciales, error de Slack API.
  4. run_once: integración mínima con mocks.
"""

from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Añadir el directorio raíz al path para importar el módulo
_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import dashboard_nodo_central as dnc


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_VALID_ENV = {
    "SLACK_TOKEN": "xoxb-test-token",
    "SLACK_CHANNEL": "C08MB3Z7B12",
    "ACTIVOS_FIJOS_EUR": "65000.00",
    "REVOLUT_TOKEN": "revolut-test-token",
    "REVOLUT_API_URL": "https://b2b.revolut.com/api/1.0",
    "REVOLUT_FALLBACK_EUR": "32800.00",
    "PAYPAL_CLIENT_ID": "paypal-client-id",
    "PAYPAL_SECRET": "paypal-secret",
}


def _make_response(json_data: object, status_code: int = 200) -> MagicMock:
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = json_data
    mock.raise_for_status = MagicMock()
    if status_code >= 400:
        import requests

        mock.raise_for_status.side_effect = requests.HTTPError(response=mock)
    return mock


# ---------------------------------------------------------------------------
# 1. get_revolut_balance
# ---------------------------------------------------------------------------


class TestGetRevolutBalance(unittest.TestCase):
    def test_retorna_suma_cuentas_eur(self) -> None:
        accounts = [
            {"currency": "EUR", "balance": "10000.50"},
            {"currency": "EUR", "balance": "5000.00"},
            {"currency": "USD", "balance": "9999.99"},
        ]
        with patch.dict(os.environ, _VALID_ENV, clear=False):
            with patch("requests.get", return_value=_make_response(accounts)):
                result = dnc.get_revolut_balance()
        self.assertAlmostEqual(result, 15000.50)

    def test_solo_suma_cuentas_eur(self) -> None:
        accounts = [{"currency": "GBP", "balance": "500.00"}]
        with patch.dict(os.environ, _VALID_ENV, clear=False):
            with patch("requests.get", return_value=_make_response(accounts)):
                result = dnc.get_revolut_balance()
        self.assertAlmostEqual(result, 0.00)

    def test_fallback_sin_token(self) -> None:
        env = {**_VALID_ENV, "REVOLUT_TOKEN": ""}
        with patch.dict(os.environ, env, clear=False):
            result = dnc.get_revolut_balance()
        self.assertAlmostEqual(result, 32800.00)

    def test_fallback_ante_error_de_red(self) -> None:
        import requests as req_module

        with patch.dict(os.environ, _VALID_ENV, clear=False):
            with patch(
                "requests.get",
                side_effect=req_module.ConnectionError("timeout"),
            ):
                result = dnc.get_revolut_balance()
        self.assertAlmostEqual(result, 32800.00)

    def test_fallback_personalizado(self) -> None:
        import requests as req_module

        env = {**_VALID_ENV, "REVOLUT_FALLBACK_EUR": "12345.00"}
        with patch.dict(os.environ, env, clear=False):
            with patch(
                "requests.get",
                side_effect=req_module.ConnectionError("err"),
            ):
                result = dnc.get_revolut_balance()
        self.assertAlmostEqual(result, 12345.00)

    def test_fallback_ante_http_error(self) -> None:
        with patch.dict(os.environ, _VALID_ENV, clear=False):
            with patch(
                "requests.get",
                return_value=_make_response({}, status_code=401),
            ):
                result = dnc.get_revolut_balance()
        self.assertAlmostEqual(result, 32800.00)


# ---------------------------------------------------------------------------
# 2. get_paypal_balance
# ---------------------------------------------------------------------------


class TestGetPaypalBalance(unittest.TestCase):
    def _mock_post_and_get(
        self,
        token: str = "access_token_abc",
        balance_value: str = "7500.00",
    ):
        auth_resp = _make_response({"access_token": token})
        balance_resp = _make_response(
            {
                "balances": [
                    {
                        "total_balance": {
                            "currency_code": "EUR",
                            "value": balance_value,
                        }
                    }
                ]
            }
        )
        return auth_resp, balance_resp

    def test_retorna_saldo_eur(self) -> None:
        auth_resp, balance_resp = self._mock_post_and_get(balance_value="7500.00")
        with patch.dict(os.environ, _VALID_ENV, clear=False):
            with patch("requests.post", return_value=auth_resp):
                with patch("requests.get", return_value=balance_resp):
                    result = dnc.get_paypal_balance()
        self.assertAlmostEqual(result, 7500.00)

    def test_cero_sin_credenciales(self) -> None:
        env = {**_VALID_ENV, "PAYPAL_CLIENT_ID": "", "PAYPAL_SECRET": ""}
        with patch.dict(os.environ, env, clear=False):
            result = dnc.get_paypal_balance()
        self.assertAlmostEqual(result, 0.00)

    def test_cero_sin_client_id(self) -> None:
        env = {**_VALID_ENV, "PAYPAL_CLIENT_ID": ""}
        with patch.dict(os.environ, env, clear=False):
            result = dnc.get_paypal_balance()
        self.assertAlmostEqual(result, 0.00)

    def test_cero_si_oauth_falla(self) -> None:
        import requests as req_module

        with patch.dict(os.environ, _VALID_ENV, clear=False):
            with patch(
                "requests.post",
                side_effect=req_module.ConnectionError("no connection"),
            ):
                result = dnc.get_paypal_balance()
        self.assertAlmostEqual(result, 0.00)

    def test_cero_si_access_token_ausente_en_respuesta(self) -> None:
        auth_resp = _make_response({})
        with patch.dict(os.environ, _VALID_ENV, clear=False):
            with patch("requests.post", return_value=auth_resp):
                result = dnc.get_paypal_balance()
        self.assertAlmostEqual(result, 0.00)

    def test_cero_si_balances_vacio(self) -> None:
        auth_resp = _make_response({"access_token": "tok"})
        balance_resp = _make_response({"balances": []})
        with patch.dict(os.environ, _VALID_ENV, clear=False):
            with patch("requests.post", return_value=auth_resp):
                with patch("requests.get", return_value=balance_resp):
                    result = dnc.get_paypal_balance()
        self.assertAlmostEqual(result, 0.00)

    def test_cero_si_get_saldo_falla(self) -> None:
        import requests as req_module

        auth_resp = _make_response({"access_token": "tok"})
        with patch.dict(os.environ, _VALID_ENV, clear=False):
            with patch("requests.post", return_value=auth_resp):
                with patch(
                    "requests.get",
                    side_effect=req_module.ConnectionError("err"),
                ):
                    result = dnc.get_paypal_balance()
        self.assertAlmostEqual(result, 0.00)


# ---------------------------------------------------------------------------
# 3. publicar_en_slack
# ---------------------------------------------------------------------------


class TestPublicarEnSlack(unittest.TestCase):
    def test_envia_mensaje_y_retorna_true(self) -> None:
        mock_client = MagicMock()
        mock_client.chat_postMessage.return_value = {"ok": True}

        with patch.dict(os.environ, _VALID_ENV, clear=False):
            with patch("dashboard_nodo_central.WebClient", return_value=mock_client):
                result = dnc.publicar_en_slack(32800.00)

        self.assertTrue(result)
        mock_client.chat_postMessage.assert_called_once()
        call_kwargs = mock_client.chat_postMessage.call_args
        self.assertEqual(call_kwargs.kwargs.get("channel"), "C08MB3Z7B12")

    def test_mensaje_contiene_total_imperio(self) -> None:
        captured = {}
        mock_client = MagicMock()

        def fake_post(**kwargs):
            captured["text"] = kwargs.get("text", "")
            return {"ok": True}

        mock_client.chat_postMessage.side_effect = fake_post

        env = {**_VALID_ENV, "ACTIVOS_FIJOS_EUR": "65000.00"}
        with patch.dict(os.environ, env, clear=False):
            with patch("dashboard_nodo_central.WebClient", return_value=mock_client):
                dnc.publicar_en_slack(32800.00)

        text = captured["text"]
        # 32800 + 65000 = 97800
        self.assertIn("97,800.00", text)
        self.assertIn("DASHBOARD VIVO 75001", text)
        self.assertIn("Liquidez Real", text)
        self.assertIn("TOTAL IMPERIO", text)

    def test_retorna_false_sin_token(self) -> None:
        env = {**_VALID_ENV, "SLACK_TOKEN": ""}
        with patch.dict(os.environ, env, clear=False):
            result = dnc.publicar_en_slack(1000.00)
        self.assertFalse(result)

    def test_retorna_false_sin_channel(self) -> None:
        env = {**_VALID_ENV, "SLACK_CHANNEL": ""}
        with patch.dict(os.environ, env, clear=False):
            result = dnc.publicar_en_slack(1000.00)
        self.assertFalse(result)

    def test_retorna_false_ante_slack_api_error(self) -> None:
        from slack_sdk.errors import SlackApiError

        mock_client = MagicMock()
        mock_client.chat_postMessage.side_effect = SlackApiError(
            "channel_not_found",
            {"error": "channel_not_found"},
        )

        with patch.dict(os.environ, _VALID_ENV, clear=False):
            with patch("dashboard_nodo_central.WebClient", return_value=mock_client):
                result = dnc.publicar_en_slack(1000.00)
        self.assertFalse(result)

    def test_activos_fijos_por_defecto(self) -> None:
        captured = {}
        mock_client = MagicMock()

        def fake_post(**kwargs):
            captured["text"] = kwargs.get("text", "")
            return {"ok": True}

        mock_client.chat_postMessage.side_effect = fake_post

        # No ACTIVOS_FIJOS_EUR → usa 65000.00 por defecto
        env = {k: v for k, v in _VALID_ENV.items() if k != "ACTIVOS_FIJOS_EUR"}
        with patch.dict(os.environ, env, clear=False):
            # Asegurar que no existe en el entorno
            with patch.dict(os.environ, {"ACTIVOS_FIJOS_EUR": ""}, clear=False):
                with patch("dashboard_nodo_central.WebClient", return_value=mock_client):
                    dnc.publicar_en_slack(0.00)

        text = captured["text"]
        self.assertIn("65,000.00", text)


# ---------------------------------------------------------------------------
# 4. run_once
# ---------------------------------------------------------------------------


class TestRunOnce(unittest.TestCase):
    def test_run_once_llama_a_publicar(self) -> None:
        with patch.dict(os.environ, _VALID_ENV, clear=False):
            with patch.object(dnc, "get_revolut_balance", return_value=10000.00):
                with patch.object(dnc, "get_paypal_balance", return_value=5000.00):
                    with patch.object(
                        dnc, "publicar_en_slack", return_value=True
                    ) as mock_pub:
                        dnc.run_once()

        mock_pub.assert_called_once_with(15000.00)

    def test_run_once_suma_saldos_correctamente(self) -> None:
        captured = {}

        def fake_pub(total):
            captured["total"] = total
            return True

        with patch.dict(os.environ, _VALID_ENV, clear=False):
            with patch.object(dnc, "get_revolut_balance", return_value=32800.00):
                with patch.object(dnc, "get_paypal_balance", return_value=1200.50):
                    with patch.object(dnc, "publicar_en_slack", side_effect=fake_pub):
                        dnc.run_once()

        self.assertAlmostEqual(captured["total"], 34000.50)


if __name__ == "__main__":
    unittest.main()
