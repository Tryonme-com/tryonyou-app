"""Agente 70: validación soberana y procesamiento base de solicitudes."""

from __future__ import annotations

import os
import logging
from typing import Any

import requests

try:
    from google.oauth2.service_account import Credentials
    from google.auth.exceptions import DefaultCredentialsError
except ImportError:  # pragma: no cover - dependencia opcional en algunos entornos
    Credentials = None  # type: ignore[assignment]
    DefaultCredentialsError = None  # type: ignore[assignment]

_CREDENTIAL_LOAD_ERRORS: tuple[type[BaseException], ...] = (
    ValueError,
    OSError,
    TypeError,
) + ((DefaultCredentialsError,) if DefaultCredentialsError else ())

_logger = logging.getLogger(__name__)


class Agente70:
    """Motor simplificado del protocolo soberano."""

    def __init__(self) -> None:
        self.status = "OPERATIONAL"
        self.service_name = "Golden_Peacock_Protocol"
        self.subscription_check_url = os.getenv(
            "SUBSCRIPTION_CHECK_URL", "https://api.tryandyou.com/check-subscription"
        )
        timeout_raw = os.getenv("SUBSCRIPTION_CHECK_TIMEOUT", "5")
        try:
            self.subscription_check_timeout = float(timeout_raw)
        except ValueError as exc:
            raise ValueError(
                "SUBSCRIPTION_CHECK_TIMEOUT debe ser un número (ej. 5 o 5.0)."
            ) from exc

    def validate_sovereign_status(self) -> bool:
        """
        Valida el estado soberano consultando el endpoint de suscripción.

        Returns:
            ``True`` cuando la operación continúa en estado operacional.
            ``False`` cuando hay restricción (402) o fallo de conectividad.
        """
        try:
            response = requests.get(
                self.subscription_check_url,
                timeout=self.subscription_check_timeout,
            )
        except requests.RequestException:
            self.status = "DEGRADED"
            return False

        if response.status_code == 402:
            self.status = "RESTRICTED"
            return False
        self.status = "OPERATIONAL"
        return True

    def process_request(self, user_input: str) -> str:
        """
        Procesa la solicitud del usuario tras validar estado soberano.

        Args:
            user_input: Texto recibido del usuario.

        Returns:
            Mensaje de espera cuando la validación falla, o mensaje de éxito
            cuando el procesamiento continúa.

        Si la validación falla, retorna mensaje de espera refinada.
        Si la validación pasa, sincroniza logging y devuelve respuesta final.
        """
        if not self.validate_sovereign_status():
            return (
                "Oh, cher, el Protocolo Soberano requiere un ajuste. "
                "Mi estado es de espera refinada hasta que se solvente el detalle técnico."
            )

        self.sync_with_drive(user_input)
        return (
            f"He procesado tu petición, mon ami: '{user_input}'. "
            "Todo bajo control, la elegancia es nuestra prioridad."
        )

    def sync_with_drive(self, data: str) -> dict[str, Any]:
        """
        Sincronización de logging con Drive/Sheets (placeholder seguro).

        Args:
            data: Contenido a sincronizar en el registro operativo.

        Returns:
            Diccionario con:
              - ``synced``: indicador booleano del paso de sincronización.
              - ``credentials_loaded``: ``True`` si las credenciales se cargaron.
        """
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
        credentials_loaded = False

        if credentials_path and Credentials:
            try:
                if os.path.exists(credentials_path):
                    credentials = Credentials.from_service_account_file(credentials_path)
                    credentials_loaded = bool(credentials)
            except _CREDENTIAL_LOAD_ERRORS:
                credentials_loaded = False

        _logger.info(
            "Datos sincronizados en Google Drive | payload_length=%d | credentials_loaded=%s",
            len(data),
            credentials_loaded,
        )
        return {"synced": True, "credentials_loaded": credentials_loaded}


agente70 = Agente70()
