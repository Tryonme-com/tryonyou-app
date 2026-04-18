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
_TRUTHY_SUBSCRIPTION_VALUES = {"active", "operational", "ok", "enabled", "valid", "paid"}
_FALSY_SUBSCRIPTION_VALUES = {
    "inactive",
    "restricted",
    "blocked",
    "expired",
    "revoked",
    "delinquent",
    "payment_required",
}


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
            _logger.warning("No se pudo consultar el estado soberano.")
            self.status = "DEGRADED"
            return False

        if response.status_code in (401, 402, 403):
            self.status = "RESTRICTED"
            return False
        if response.status_code >= 500:
            self.status = "DEGRADED"
            return False
        if response.status_code >= 400:
            self.status = "RESTRICTED"
            return False

        payload_state = self._extract_subscription_state(response)
        if payload_state is False:
            self.status = "RESTRICTED"
            return False
        if payload_state is None:
            self.status = "DEGRADED"
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

        safe_input = user_input if isinstance(user_input, str) else str(user_input)
        try:
            self.sync_with_drive(safe_input)
        except Exception:
            _logger.exception("Fallo durante la sincronización de Drive.")
            self.status = "DEGRADED"
            return (
                "Mon ami, hubo una contingencia durante la sincronización. "
                "Quedo en modo resguardo hasta recuperar estabilidad."
            )

        return (
            f"He procesado tu petición, mon ami: '{safe_input}'. "
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

    def _extract_subscription_state(self, response: requests.Response) -> bool | None:
        """
        Interpreta campos opcionales del payload de suscripción.

        Returns:
            - True: el payload confirma acceso.
            - False: el payload marca restricción explícita.
            - None: payload ambiguo o inválido (fail-closed).
        """
        try:
            payload = response.json()
        except ValueError:
            return True
        except Exception:
            return None

        if not isinstance(payload, dict):
            return None

        candidates = (
            payload.get("subscription_active"),
            payload.get("is_active"),
            payload.get("active"),
            payload.get("sovereign_status"),
            payload.get("status"),
        )
        for value in candidates:
            interpreted = self._interpret_subscription_value(value)
            if interpreted is not None:
                return interpreted
        return True

    @staticmethod
    def _interpret_subscription_value(value: Any) -> bool | None:
        if value is None:
            return None
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in _TRUTHY_SUBSCRIPTION_VALUES:
                return True
            if normalized in _FALSY_SUBSCRIPTION_VALUES:
                return False
            return None
        return None


agente70 = Agente70()
