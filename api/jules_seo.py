from __future__ import annotations

import base64
import json
import os
import random
import time
from datetime import datetime
from email.mime.text import MIMEText
from typing import Any

import gspread
from gspread.exceptions import CellNotFound
from google.oauth2.credentials import Credentials as UserCredentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from googleapiclient.discovery import build

MAX_ENVIOS_DIARIOS = 4
CUENTA_ENVIO_CORPORATIVA = "admin@tryonyou.app"
SHEET_TAB = "SEO_Prospects"
SEO_HEADERS = ["Nombre_Sitio", "URL", "Email_Contacto", "Estado", "Fecha_Envio", "Msg_ID"]


def get_google_sheet_client() -> gspread.Client:
    service_account_json = (os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON") or "").strip()
    if not service_account_json:
        raise RuntimeError("Missing required env: GOOGLE_SERVICE_ACCOUNT_JSON")
    service_account_info = json.loads(service_account_json)
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials = ServiceAccountCredentials.from_service_account_info(
        service_account_info, scopes=scopes
    )
    return gspread.authorize(credentials)


def _sheet() -> gspread.Worksheet:
    spreadsheet_id = (os.environ.get("SPREADSHEET_ID") or "").strip()
    if not spreadsheet_id:
        raise RuntimeError("Missing required env: SPREADSHEET_ID")
    client = get_google_sheet_client()
    spreadsheet = client.open_by_key(spreadsheet_id)
    try:
        sheet = spreadsheet.worksheet(SHEET_TAB)
    except gspread.exceptions.WorksheetNotFound:
        sheet = spreadsheet.add_worksheet(title=SHEET_TAB, rows=1000, cols=10)
        sheet.append_row(SEO_HEADERS, value_input_option="USER_ENTERED")
        return sheet

    first_row = sheet.row_values(1)
    if not first_row:
        sheet.append_row(SEO_HEADERS, value_input_option="USER_ENTERED")
    return sheet


def obtener_sitios_seo_pendientes() -> list[dict[str, Any]]:
    sheet = _sheet()
    todos_los_registros = sheet.get_all_records()
    pendientes = [r for r in todos_los_registros if str(r.get("Estado", "")).strip() == "Pendiente"]
    limit = int(os.environ.get("MAX_ENVIOS_DIARIOS", str(MAX_ENVIOS_DIARIOS)))
    return pendientes[:limit]


def actualizar_estado_seo_sheet(sitio_url: str, msg_id: str) -> None:
    sheet = _sheet()
    try:
        celda_url = sheet.find(sitio_url)
    except CellNotFound:
        print(f"[Jules SEO] URL no encontrada en hoja: {sitio_url}")
        return
    fila = celda_url.row
    sheet.update_cell(fila, 4, "Enviado")
    sheet.update_cell(fila, 5, datetime.now().strftime("%Y-%m-%d"))
    if msg_id:
        sheet.update_cell(fila, 6, msg_id)


def _gmail_service() -> Any:
    token_infra = {
        "token": None,
        "refresh_token": os.environ.get("GMAIL_REFRESH_TOKEN"),
        "client_id": os.environ.get("GMAIL_CLIENT_ID"),
        "client_secret": os.environ.get("GMAIL_CLIENT_SECRET"),
        "token_uri": "https://oauth2.googleapis.com/token",
    }
    creds = UserCredentials.from_authorized_user_info(token_infra)
    return build("gmail", "v1", credentials=creds, cache_discovery=False)


def enviar_propuesta_seo(
    service: Any, desde_cuenta: str, para_email: str, asunto: str, cuerpo: str
) -> str | None:
    mensaje = MIMEText(cuerpo, "html", "utf-8")
    mensaje["To"] = para_email
    mensaje["From"] = desde_cuenta
    mensaje["Subject"] = asunto
    raw_message = base64.urlsafe_b64encode(mensaje.as_bytes()).decode("utf-8")
    try:
        res = (
            service.users()
            .messages()
            .send(userId="me", body={"raw": raw_message})
            .execute()
        )
        return res.get("id")
    except Exception as exc:
        print(f"[Jules SEO Error] No se pudo enviar propuesta a {para_email}: {exc}")
        return None


def ejecutar_goteo_seo_diario() -> dict[str, Any]:
    service = _gmail_service()
    prospectos = obtener_sitios_seo_pendientes()
    if not prospectos:
        return {"ok": True, "status": "skipped", "sent": 0, "message": "No hay objetivos pendientes."}

    plantilla_asunto = (
        "Propuesta de contenido técnico / Recurso de innovación para {{sitio_nombre}}"
    )
    plantilla_cuerpo = """
    <p>Bonjour,</p>
    <p>Je vous contacte concernant votre section dédiée à l'innovation technologique sur {{sitio_nombre}}.</p>
    <p>Nous avons développé une infrastructure d'essayage virtuel de haute précision et zéro-donnée qui pourrait intéresser vos lecteurs ou être intégrée dans vos listes de ressources d'architecture logicielle.</p>
    <p>Vous pouvez consulter notre matériel publicitaire et documentation technique sur notre plateforme officielle.</p>
    <p>Cordialement,<br>Jules<br>Département Technique - TRYONYOU</p>
    """

    sent = 0
    for index, prospecto in enumerate(prospectos):
        email_contacto = (prospecto.get("Email_Contacto") or "").strip()
        nombre_sitio = (prospecto.get("Nombre_Sitio") or "sitio").strip() or "sitio"
        url_sitio = (prospecto.get("URL") or "").strip()
        if not email_contacto:
            continue

        asunto_listo = plantilla_asunto.replace("{{sitio_nombre}}", nombre_sitio)
        cuerpo_listo = plantilla_cuerpo.replace("{{sitio_nombre}}", nombre_sitio)

        msg_id = enviar_propuesta_seo(
            service, CUENTA_ENVIO_CORPORATIVA, email_contacto, asunto_listo, cuerpo_listo
        )
        if msg_id:
            sent += 1
            if url_sitio:
                actualizar_estado_seo_sheet(url_sitio, msg_id)

        if index < len(prospectos) - 1:
            time.sleep(random.uniform(5.0, 10.0))

    return {
        "ok": True,
        "status": "success",
        "sent": sent,
        "processed": len(prospectos),
        "message": f"Lote SEO completado: {sent}/{len(prospectos)} enviados.",
    }


if __name__ == "__main__":
    print(ejecutar_goteo_seo_diario())
