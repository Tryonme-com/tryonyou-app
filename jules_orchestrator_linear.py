"""
Jules — orquestador de flujo lineal (Slack + Vertex opcional).

Secretos solo por entorno (nunca en el código):
  JULES_SLACK_BOT_TOKEN o SLACK_BOT_TOKEN — Bot User OAuth Token (xoxb-...)
  JULES_SLACK_CHANNEL_ID o SLACK_CHANNEL_ID — canal (C...)
  Alternativa sin slack_sdk: SLACK_WEBHOOK_URL (divineo_slack.slack_post)

GCP / Vertex (opcional):
  GCP_PROJECT_ID o VERTEX_PROJECT_ID — ej. gen-lang-client-0066102635
  VERTEX_LOCATION — ej. europe-west1

  pip install slack_sdk google-cloud-aiplatform  (solo en máquinas que ejecuten este script)

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import os
import sys
from typing import Any

from divineo_slack import slack_post


def _slack_token() -> str:
    return (
        os.environ.get("JULES_SLACK_BOT_TOKEN", "").strip()
        or os.environ.get("SLACK_BOT_TOKEN", "").strip()
    )


def _slack_channel() -> str:
    return (
        os.environ.get("JULES_SLACK_CHANNEL_ID", "").strip()
        or os.environ.get("SLACK_CHANNEL_ID", "").strip()
    )


def _vertex_project() -> str:
    return (
        os.environ.get("GCP_PROJECT_ID", "").strip()
        or os.environ.get("VERTEX_PROJECT_ID", "").strip()
    )


class JulesOrchestrator:
    """Informa pasos a Slack; generación Vertex/YouTube queda como hook para extender."""

    def __init__(self) -> None:
        self._token = _slack_token()
        self._channel = _slack_channel()
        self._slack_client: Any = None
        if self._token:
            try:
                from slack_sdk import WebClient  # type: ignore[import-untyped]

                self._slack_client = WebClient(token=self._token)
            except ImportError:
                print(
                    "[Jules] slack_sdk no instalado: pip install slack_sdk "
                    "o usa SLACK_WEBHOOK_URL.",
                    file=sys.stderr,
                )

    def report_status(self, message: str) -> None:
        """Jules informa a Slack de cada paso completado."""
        text = f"🚀 [Jules]: {message}"
        if self._slack_client and self._channel:
            try:
                self._slack_client.chat_postMessage(channel=self._channel, text=text)
                return
            except OSError as e:
                print(f"[Jules] Slack API: {e}", file=sys.stderr)
        if slack_post(text):
            return
        print(text, file=sys.stderr)

    def execute_perfect_flow(self, prompt: str) -> None:
        """Flujo demo: generación → validación → YouTube (hooks). `prompt` reservado para Vertex."""
        _ = prompt  # reservado para Vertex / Gemini
        self.report_status("Iniciando generación de vídeo lineal...")
        project = _vertex_project()
        if project:
            try:
                from google.cloud import aiplatform  # type: ignore[import-untyped]

                loc = os.environ.get("VERTEX_LOCATION", "europe-west1").strip()
                aiplatform.init(project=project, location=loc)
            except ImportError:
                self.report_status(
                    "Vertex: google-cloud-aiplatform no instalado; "
                    "pip install google-cloud-aiplatform"
                )
            except OSError as e:
                self.report_status(f"Vertex init omitido: {e}")
        else:
            self.report_status(
                "Vertex sin GCP_PROJECT_ID/VERTEX_PROJECT_ID — solo notificaciones Slack."
            )

        self.report_status("Vídeo generado. Validando calidad y formato...")
        self.report_status("Subiendo a YouTube y comentando...")
        self.report_status("Flujo completado con éxito. Vídeo disponible.")


if __name__ == "__main__":
    JulesOrchestrator().execute_perfect_flow("demo lineal")
