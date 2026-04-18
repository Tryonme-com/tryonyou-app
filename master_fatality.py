from __future__ import annotations

import asyncio
import logging
import os
from typing import Any

import httpx

from stripe_verify_secret_env import resolve_stripe_secret

LOGGER = logging.getLogger(__name__)

CONTACTOS_CLAVE = [
    {
        "nombre": "Nicolas T.",
        "empresa": "Galeries Lafayette",
        "email": "nicolas.t@galerieslafayette.com",
    },
    {"nombre": "Julien M.", "empresa": "Bpifrance", "email": "julien.m@bpifrance.fr"},
]


class FatalitySystem:
    def __init__(
        self,
        *,
        api_key: str | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        token = (api_key or resolve_stripe_secret() or "").strip()
        if not token:
            raise EnvironmentError(
                "Define STRIPE_SECRET_KEY_FR o STRIPE_SECRET_KEY_NUEVA / STRIPE_SECRET_KEY."
            )
        self.client = client or httpx.AsyncClient(
            headers={"Authorization": f"Bearer {token}"},
            timeout=20.0,
        )
        self._owns_client = client is None

    async def __aenter__(self) -> FatalitySystem:
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()

    async def close(self) -> None:
        if self._owns_client:
            await self.client.aclose()

    @staticmethod
    def _response_json(response: httpx.Response) -> dict[str, Any]:
        try:
            payload = response.json()
        except ValueError:
            return {}
        return payload if isinstance(payload, dict) else {}

    async def verificar_estado_financiero(self) -> float:
        response = await self.client.get("https://api.stripe.com/v1/balance")
        response.raise_for_status()
        data = self._response_json(response)
        available = data.get("available")
        amount_cents = 0
        currency = "eur"
        if isinstance(available, list) and available:
            first = available[0]
            if isinstance(first, dict):
                amount_cents = int(first.get("amount", 0) or 0)
                currency = str(first.get("currency", "eur") or "eur").upper()
        amount = amount_cents / 100
        LOGGER.info("Fondos actuales: %.2f %s", amount, currency)
        return amount

    async def check_documentacion(self) -> list[str]:
        response = await self.client.get("https://api.stripe.com/v1/payment_intents")
        response.raise_for_status()
        data = self._response_json(response)
        found_docs: list[str] = []
        for payment in data.get("data", []):
            if not isinstance(payment, dict):
                continue
            payment_id = str(payment.get("id", "desconocido"))
            metadata = payment.get("metadata")
            if isinstance(metadata, dict) and metadata.get("contrato"):
                contract = str(metadata["contrato"])
                found_docs.append(contract)
                LOGGER.info("DOCUMENTO ENCONTRADO en pago %s: %s", payment_id, contract)
                continue
            LOGGER.info("Transacción %s: Pendiente de documentación.", payment_id)
        return found_docs

    async def ejecutar_fatality(self) -> None:
        LOGGER.info("--- INICIANDO PROTOCOLO FATALITY ---")
        await self.verificar_estado_financiero()
        await self.check_documentacion()
        LOGGER.info("--- PROTOCOLO FINALIZADO ---")


async def _run() -> None:
    async with FatalitySystem() as system:
        await system.ejecutar_fatality()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
    try:
        asyncio.run(_run())
    except (EnvironmentError, httpx.HTTPError) as exc:
        LOGGER.error("FATALITY abortado: %s", exc)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
