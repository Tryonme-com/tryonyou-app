"""
Final Commit — Módulo de registro y selección Divineo V10 (La Niña Perfecta).

Ciclo completo de selección y registro de prendas:
  1. commit_final               : registra acciones en la base de datos (Google Sheets).
  2. la_nina_perfecta_selection : selección IA de prendas mediante Agente 70 + Jules.
  3. final_snap                 : activación de evento de marca Divineo.
  4. send_final_qr              : envío de QR de acceso al cliente por correo electrónico.

Las dependencias externas (Google Sheets, modelos IA, servicio de correo) se inyectan
en el constructor de ``FinalCommitModule`` para permitir pruebas unitarias sin
conexiones reales a la red.

Patente: PCT/EP2025/067317
SIREN: 943 610 196
"""

from __future__ import annotations

import base64
import json
import os
from datetime import datetime
from email.mime.text import MIMEText
from typing import Any, Protocol, runtime_checkable

PATENTE = "PCT/EP2025/067317"
SIREN = "943 610 196"

# Marcas de lujo integradas en el protocolo Divineo
DIVINEO_LUXURY_BRANDS: frozenset[str] = frozenset({"Balmain", "Chanel", "Dior"})

# URL base del portal QR (SAC Museum)
QR_BASE_URL = os.environ.get("DIVINEO_QR_BASE_URL", "https://sacmuseum.app/qr/")

# Nombre de la hoja de cálculo (configurable mediante variable de entorno)
DB_NAME = os.environ.get("DIVINEO_DB_NAME", "Divineo_Leads_DB")


# ---------------------------------------------------------------------------
# Protocolos de dependencia inyectable
# ---------------------------------------------------------------------------


@runtime_checkable
class SheetsBackend(Protocol):
    """Protocolo mínimo para un backend de registro tabular (Google Sheets u otro)."""

    def append_row(self, row: list[Any]) -> None:
        """Añade una fila al final de la hoja activa."""
        ...


@runtime_checkable
class AIAgent(Protocol):
    """Protocolo mínimo para un agente generativo (Gemini u otro)."""

    def generate(self, prompt: str, *, response_json: bool = False) -> str:
        """Genera texto a partir de un prompt; si response_json=True, devuelve JSON."""
        ...


@runtime_checkable
class MailService(Protocol):
    """Protocolo mínimo para envío de correo (Gmail API u otro)."""

    def send_raw(self, raw_b64: str, sender: str = "me") -> None:
        """Envía un mensaje codificado en base64-URL."""
        ...


# ---------------------------------------------------------------------------
# Módulo principal
# ---------------------------------------------------------------------------


class FinalCommitModule:
    """
    Módulo de registro definitivo del ciclo Divineo V10.

    Todas las dependencias externas son opcionales en el constructor: si no se
    proporcionan, los métodos que las requieren lanzarán ``RuntimeError`` con un
    mensaje descriptivo, lo que facilita el uso en tests sin necesidad de
    instanciar credenciales reales.
    """

    def __init__(
        self,
        sheets: SheetsBackend | None = None,
        agent_70: AIAgent | None = None,
        jules: AIAgent | None = None,
        mail: MailService | None = None,
    ) -> None:
        self._sheets = sheets
        self._agent_70 = agent_70
        self._jules = jules
        self._mail = mail

    # ------------------------------------------------------------------
    # commit_final
    # ------------------------------------------------------------------

    def commit_final(self, user_id: str, action: str, result: Any) -> dict[str, Any]:
        """
        Registra definitivamente una acción en la base de datos Divineo.

        Args:
            user_id: Identificador del usuario (e-mail u otro).
            action:  Código de la acción ejecutada (p.ej. ``"LA_NINA_PERFECTA_EXEC"``).
            result:  Resultado de la acción (serializable a JSON).

        Returns:
            Diccionario con los campos registrados y el campo ``"status": "COMMITTED"``.

        Raises:
            RuntimeError: Si no se inyectó ningún ``SheetsBackend``.
        """
        if self._sheets is None:
            raise RuntimeError(
                "commit_final requiere un SheetsBackend inyectado. "
                "Instancia FinalCommitModule con sheets=<cliente_hojas>."
            )
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result_json = json.dumps(result, ensure_ascii=False)
        row = [timestamp, str(user_id), str(action), result_json, "COMMITTED"]
        self._sheets.append_row(row)
        return {
            "timestamp": timestamp,
            "user_id": user_id,
            "action": action,
            "result": result,
            "status": "COMMITTED",
        }

    # ------------------------------------------------------------------
    # la_nina_perfecta_selection
    # ------------------------------------------------------------------

    def la_nina_perfecta_selection(
        self, metrics: dict[str, Any], brand: str
    ) -> dict[str, Any]:
        """
        Selección definitiva de prendas «La Niña Perfecta».

        El Agente 70 realiza la selección técnica y Jules elabora la presentación
        al cliente.  El resultado se registra con :meth:`commit_final`.

        Args:
            metrics: Métricas corporales del usuario (debe incluir ``"email"``).
            brand:   Nombre de la marca para la selección.

        Returns:
            Diccionario con:
              - ``selection_raw`` : resultado JSON del Agente 70 (str).
              - ``manifesto``     : texto de presentación de Jules.
              - ``commit``        : registro de la operación (ver :meth:`commit_final`).

        Raises:
            RuntimeError: Si no se inyectaron los agentes IA o el backend de hojas.
        """
        if self._agent_70 is None or self._jules is None:
            raise RuntimeError(
                "la_nina_perfecta_selection requiere agent_70 y jules inyectados."
            )
        if self._sheets is None:
            raise RuntimeError(
                "la_nina_perfecta_selection requiere un SheetsBackend inyectado."
            )

        prompt_70 = (
            f"Métricas reales: {json.dumps(metrics, ensure_ascii=False)}. "
            f"Marca: {brand}. Selección 5 prendas 'Niña Perfecta'."
        )
        selection_raw = self._agent_70.generate(prompt_70, response_json=True)

        prompt_jules = f"Presenta la Niña Perfecta a la clienta: {selection_raw}. París 2026."
        manifesto = self._jules.generate(prompt_jules)

        user_id = str(metrics.get("email", "anonymous"))
        commit = self.commit_final(user_id, "LA_NINA_PERFECTA_EXEC", selection_raw)

        return {
            "selection_raw": selection_raw,
            "manifesto": manifesto,
            "commit": commit,
        }

    # ------------------------------------------------------------------
    # final_snap
    # ------------------------------------------------------------------

    def final_snap(self, brand: str, user_id: str) -> dict[str, Any]:
        """
        Activa el evento de transformación de marca en el protocolo Divineo.

        Solo las marcas integradas en ``DIVINEO_LUXURY_BRANDS`` desencadenan
        la transformación; el resto devuelven estado ``"BRAND_NOT_INTEGRATED"``.

        Args:
            brand:   Nombre de la marca.
            user_id: Identificador del usuario.

        Returns:
            Diccionario con:
              - ``status``  : ``"LA_NINA_PERFECTA"`` o ``"BRAND_NOT_INTEGRATED"``.
              - ``brand``   : nombre de la marca.
              - ``message`` : mensaje descriptivo de resultado.
              - ``commit``  : registro de la operación (solo para marcas integradas).
        """
        if brand in DIVINEO_LUXURY_BRANDS:
            snap_result: dict[str, Any] = {
                "event": "TRANSFORMACION_TOTAL",
                "brand": brand,
                "status": "LA_NINA_PERFECTA",
            }
            commit: dict[str, Any] | None = None
            if self._sheets is not None:
                commit = self.commit_final(user_id, "FINAL_SNAP", snap_result)
            return {
                "status": "LA_NINA_PERFECTA",
                "brand": brand,
                "message": f"Bienvenida a su nueva realidad en {brand}. Lo+eres tú.",
                "commit": commit,
                "legal": f"{PATENTE} · SIREN {SIREN}",
            }

        return {
            "status": "BRAND_NOT_INTEGRATED",
            "brand": brand,
            "message": "Marca no integrada.",
            "commit": None,
            "legal": f"{PATENTE} · SIREN {SIREN}",
        }

    # ------------------------------------------------------------------
    # send_final_qr
    # ------------------------------------------------------------------

    def send_final_qr(self, email: str, name: str, look_id: str) -> dict[str, Any]:
        """
        Envía el QR de acceso definitivo al cliente por correo electrónico.

        Args:
            email:   Dirección de correo electrónico del destinatario.
            name:    Nombre del destinatario.
            look_id: Identificador del look seleccionado.

        Returns:
            Diccionario con:
              - ``status``  : ``"QR_SENT"``.
              - ``email``   : destinatario.
              - ``look_id`` : identificador del look.
              - ``qr_url``  : URL de acceso al QR.
              - ``commit``  : registro de la operación.

        Raises:
            RuntimeError: Si no se inyectó ningún ``MailService``.
        """
        if self._mail is None:
            raise RuntimeError(
                "send_final_qr requiere un MailService inyectado. "
                "Instancia FinalCommitModule con mail=<servicio_correo>."
            )

        qr_url = f"{QR_BASE_URL.rstrip('/')}/{look_id}"
        body = (
            f"Estimada {name},\n\n"
            f"La Niña Perfecta ha hablado. Su selección {look_id} es su piel en París 2026. "
            f"El fin de las tallas ha llegado.\n\n"
            f"Acceso QR: {qr_url}\n\n"
            f"Jules.\n\n{PATENTE} · SIREN {SIREN}"
        )
        msg = MIMEText(body)
        msg["to"] = email
        msg["subject"] = "Divineo: El Fin de las Devoluciones"
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        self._mail.send_raw(raw)

        commit: dict[str, Any] | None = None
        if self._sheets is not None:
            commit = self.commit_final(email, "QR_FINAL_SENT", look_id)

        return {
            "status": "QR_SENT",
            "email": email,
            "look_id": look_id,
            "qr_url": qr_url,
            "commit": commit,
        }
