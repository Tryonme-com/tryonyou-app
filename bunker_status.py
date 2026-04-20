"""BÚNKER CONTROL: consulta de estado financiero remoto."""

from __future__ import annotations

import os
from typing import Any

import requests

DEFAULT_API_URL = "https://api.tryonyou.app/v1/compliance/status"
DEFAULT_TIMEOUT_SECONDS = 10.0
MIN_TIMEOUT_SECONDS = 0.1


def _env_stripped(key: str, default: str = "") -> str:
    return (os.getenv(key) or default).strip()


def _build_headers(system_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {system_token}"}


def get_bunker_status() -> dict[str, Any] | None:
    api_url = _env_stripped("BUNKER_STATUS_API_URL", DEFAULT_API_URL)
    token = _env_stripped("SYSTEM_TOKEN")
    timeout_raw = _env_stripped("BUNKER_STATUS_TIMEOUT_SECONDS")

    if not token:
        print("Error de sincronización: SYSTEM_TOKEN no configurado.")
        return None

    timeout = DEFAULT_TIMEOUT_SECONDS
    if timeout_raw:
        try:
            timeout = float(timeout_raw)
        except ValueError:
            print(
                "Error de sincronización: BUNKER_STATUS_TIMEOUT_SECONDS inválido, usando valor por defecto."
            )

    try:
        response = requests.get(
            api_url,
            headers=_build_headers(token),
            timeout=max(timeout, MIN_TIMEOUT_SECONDS),
        )
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict):
            raise ValueError("API returned non-dictionary JSON response")
        print(f"ESTADO BANCARIO: {data.get('status')}")
        print(f"SALDO EN TRÁNSITO: {data.get('pending_amount')} EUR")
        print(f"REFERENCIA E2E: {data.get('e2e_reference')}")
        return data
    except (requests.RequestException, ValueError) as exc:
        print(f"Error de sincronización: {exc}")
        return None


def main() -> int:
    return 0 if get_bunker_status() is not None else 1


if __name__ == "__main__":
    raise SystemExit(main())
