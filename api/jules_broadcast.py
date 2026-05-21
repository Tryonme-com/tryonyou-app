from __future__ import annotations

import base64
import os
import random
import time
from email.mime.text import MIMEText
from typing import Any

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

CUENTAS_AUTORIZADAS = [
    "admin@tryonyou.app",
    "ruben.espinard.10@icloud.com",
    "rubensanzburo@gmail.com",
]


def _get_required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required env: {name}")
    return value


def get_gmail_service() -> Any:
    token_infra = {
        "token": None,
        "refresh_token": _get_required_env("GMAIL_REFRESH_TOKEN"),
        "client_id": _get_required_env("GMAIL_CLIENT_ID"),
        "client_secret": _get_required_env("GMAIL_CLIENT_SECRET"),
        "token_uri": "https://oauth2.googleapis.com/token",
    }
    creds = Credentials.from_authorized_user_info(token_infra)
    return build("gmail", "v1", credentials=creds, cache_discovery=False)


def enviar_correo_individual(
    service: Any,
    desde_cuenta: str,
    para_email: str,
    asunto: str,
    cuerpo_texto: str,
) -> bool:
    if desde_cuenta.lower() not in {c.lower() for c in CUENTAS_AUTORIZADAS}:
        print(f"[Jules Error] Remitente no autorizado: {desde_cuenta}")
        return False

    mensaje = MIMEText(cuerpo_texto, "html", "utf-8")
    mensaje["To"] = para_email
    mensaje["From"] = desde_cuenta
    mensaje["Subject"] = asunto
    raw_message = base64.urlsafe_b64encode(mensaje.as_bytes()).decode("utf-8")

    try:
        service.users().messages().send(userId="me", body={"raw": raw_message}).execute()
        return True
    except Exception as exc:
        print(f"[Jules Error] No se pudo enviar a {para_email}: {exc}")
        return False


def ejecutar_envio_masivo(
    remitente_autorizado: str,
    plantilla_asunto: str,
    plantilla_cuerpo: str,
    lista_destinatarios: list[dict[str, str]],
) -> int:
    if remitente_autorizado.lower() not in {c.lower() for c in CUENTAS_AUTORIZADAS}:
        raise RuntimeError("remitente_autorizado no está en CUENTAS_AUTORIZADAS")

    service = get_gmail_service()
    total_enviados = 0

    print(f"[Jules Broadcast] Iniciando envío masivo desde: {remitente_autorizado}")
    print(f"[Jules Broadcast] Total de destinatarios en cola: {len(lista_destinatarios)}")

    for index, contacto in enumerate(lista_destinatarios):
        email_destino = (contacto.get("email") or "").strip()
        if not email_destino:
            continue
        nombre_destino = (contacto.get("nombre") or "Cliente").strip() or "Cliente"
        empresa_destino = (contacto.get("empresa") or "Empresa").strip() or "Empresa"

        asunto_personalizado = (
            plantilla_asunto.replace("{{nombre}}", nombre_destino).replace(
                "{{empresa}}", empresa_destino
            )
        )
        cuerpo_personalizado = (
            plantilla_cuerpo.replace("{{nombre}}", nombre_destino).replace(
                "{{empresa}}", empresa_destino
            )
        )

        exito = enviar_correo_individual(
            service,
            remitente_autorizado,
            email_destino,
            asunto_personalizado,
            cuerpo_personalizado,
        )
        if exito:
            total_enviados += 1
            print(f"[Jules] Correo entregado con éxito a: {email_destino}")

        if index < len(lista_destinatarios) - 1:
            time.sleep(random.uniform(2.0, 5.0))

    print(
        f"[Jules Broadcast] Proceso terminado. Envíos exitosos: {total_enviados}/{len(lista_destinatarios)}"
    )
    return total_enviados
