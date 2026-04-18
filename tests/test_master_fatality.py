from __future__ import annotations

import asyncio
import os
import sys
import unittest
from unittest.mock import patch

import httpx

_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import master_fatality


class _FakeResponse:
    def __init__(self, payload: object, *, status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code
        self.request = httpx.Request("GET", "https://api.stripe.com")

    def json(self) -> object:
        return self._payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                "error",
                request=self.request,
                response=httpx.Response(self.status_code, request=self.request),
            )


class _FakeClient:
    def __init__(self, responses: list[_FakeResponse]) -> None:
        self._responses = responses
        self.closed = False

    async def get(self, _: str) -> _FakeResponse:
        return self._responses.pop(0)

    async def aclose(self) -> None:
        self.closed = True


class TestFatalitySystem(unittest.TestCase):
    def test_init_requires_key(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(EnvironmentError):
                master_fatality.FatalitySystem()

    def test_verificar_estado_financiero(self) -> None:
        fake_client = _FakeClient([_FakeResponse({"available": [{"amount": 12500, "currency": "eur"}]})])
        with self.assertLogs("master_fatality", level="INFO") as logs:
            system = master_fatality.FatalitySystem(api_key="sk_test_dummy", client=fake_client)
            amount = asyncio.run(system.verificar_estado_financiero())
        self.assertEqual(amount, 125.0)
        self.assertIn("Fondos actuales: 125.00 EUR", "\n".join(logs.output))

    def test_check_documentacion(self) -> None:
        fake_client = _FakeClient(
            [
                _FakeResponse(
                    {
                        "data": [
                            {"id": "pi_1", "metadata": {"contrato": "DOC-01"}},
                            {"id": "pi_2", "metadata": {}},
                        ]
                    }
                )
            ]
        )
        with self.assertLogs("master_fatality", level="INFO") as logs:
            system = master_fatality.FatalitySystem(api_key="sk_test_dummy", client=fake_client)
            docs = asyncio.run(system.check_documentacion())
        self.assertEqual(docs, ["DOC-01"])
        output = "\n".join(logs.output)
        self.assertIn("DOCUMENTO ENCONTRADO en pago pi_1: DOC-01", output)
        self.assertIn("Transacción pi_2: Pendiente de documentación.", output)

    def test_main_returns_1_without_env_key(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(master_fatality.main(), 1)


if __name__ == "__main__":
    unittest.main()
