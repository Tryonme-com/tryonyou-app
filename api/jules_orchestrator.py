from __future__ import annotations

import base64
import json
import os
import random
import re
import time
from datetime import datetime
from email.mime.text import MIMEText
from typing import Any

import gspread
import requests
from google.oauth2.credentials import Credentials as UserCredentials
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

PENNYLANE_API_URL = "https://api.pennylane.com/v1"
PENNYLANE_API_KEY = os.environ.get("PENNYLANE_API_KEY")
SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")
GEMINI_API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.5-pro:generateContent"
)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

CUENTAS_AUTORIZADAS = [
    "admin@tryonyou.app",
    "ruben.espinard.10@icloud.com",
    "rubensanzburo@gmail.com",
]
SEO_MAX_ENVIOS_DIARIOS = 4


def get_google_sheet_client() -> gspread.Client:
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    service_account_raw = (os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON") or "").strip()
    if not service_account_raw:
        raise RuntimeError("Missing required env: GOOGLE_SERVICE_ACCOUNT_JSON")
    service_account_info = json.loads(service_account_raw)
    credentials = Credentials.from_service_account_info(
        service_account_info, scopes=scopes
    )
    return gspread.authorize(credentials)


def get_gmail_service() -> Any:
    token_infra = {
        "token": None,
        "refresh_token": os.environ.get("GMAIL_REFRESH_TOKEN"),
        "client_id": os.environ.get("GMAIL_CLIENT_ID"),
        "client_secret": os.environ.get("GMAIL_CLIENT_SECRET"),
        "token_uri": "https://oauth2.googleapis.com/token",
    }
    creds = UserCredentials.from_authorized_user_info(token_infra)
    return build("gmail", "v1", credentials=creds, cache_discovery=False)


class ExcelenciaContableJules:
    def __init__(self, tva_rate_default: float = 0.20):
        self.tva_default = tva_rate_default

    def verificar_calculo_tva(
        self, total: float, base_imponible: float, tva_declarada: float
    ) -> dict[str, Any]:
        total = float(total)
        base_imponible = float(base_imponible)
        tva_declarada = float(tva_declarada)
        tva_teorica = round(base_imponible * self.tva_default, 2)
        total_teorico = round(base_imponible + tva_teorica, 2)
        if abs(tva_teorica - tva_declarada) > 0.02 or abs(total_teorico - total) > 0.02:
            return {
                "valido": False,
                "error": (
                    f"Discrepancia fiscal. IVA teórico: {tva_teorica}€, "
                    f"Declarado: {tva_declarada}€."
                ),
            }
        return {"valido": True, "error": None}

    def escanear_importes_en_texto(self, texto: str) -> list[float]:
        patron = r"(\d{1,3}(?:\s\d{3})*(?:[.,]\d+)?|\d+(?:[.,]\d+)?)\s*(?:€|EUR|euros)"
        coincidencias = re.findall(patron, texto)
        importes: list[float] = []
        for coincidencia in coincidencias:
            try:
                importes.append(float(coincidencia.replace(" ", "").replace(",", ".")))
            except ValueError:
                continue
        return importes

    def obtener_alertas_calendario_fiscal(self) -> list[str]:
        hoy = datetime.now()
        dia, mes = hoy.day, hoy.month
        alertas: list[str] = []
        if 1 <= dia <= 19:
            alertas.append("Window de declaración de TVA del mes anterior activa (Límite: 19-24).")
        if dia >= 25 or dia <= 5:
            alertas.append("Revisar cálculo de cotizaciones de autónomos y URSSAF.")
        if mes in [1, 4, 7, 10] and dia <= 15:
            alertas.append("Cierre de trimestre fiscal en curso. Recopilar facturas intracomunitarias.")
        return alertas


def sync_pennylane_to_sheets() -> None:
    if not PENNYLANE_API_KEY or not SPREADSHEET_ID:
        print("[Jules] Pennylane sync omitido por configuración incompleta.")
        return

    print("[Jules] Sincronizando registros financieros desde Pennylane...")
    headers = {
        "Authorization": f"Bearer {PENNYLANE_API_KEY}",
        "Content-Type": "application/json",
    }
    res = requests.get(
        f"{PENNYLANE_API_URL}/bank_transactions",
        headers=headers,
        timeout=45,
    )
    if res.status_code != 200:
        print(f"[Pennylane Error] Fallo de API: {res.text[:500]}")
        return

    transactions = res.json().get("bank_transactions", [])
    client = get_google_sheet_client()
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1
    existing_ids = set(sheet.col_values(1)[1:])

    new_rows = []
    for tx in transactions:
        tx_id = str(tx.get("id"))
        if not tx_id or tx_id in existing_ids:
            continue

        date_str = str(tx.get("date", ""))
        label = str(tx.get("label", "Sin concepto"))
        amount = float(tx.get("amount", 0.0))
        matched = bool(tx.get("matched", False))

        tva_rate = 0.20 if amount < 0 else 0.0
        vat_amount = round(amount * (tva_rate / (1 + tva_rate)), 2) if amount < 0 else 0.0
        base_imponible = round(amount - vat_amount, 2)
        status = "Conciliado" if matched else "Pendiente Justificante"

        new_rows.append(
            [
                tx_id,
                date_str,
                label,
                amount,
                base_imponible,
                vat_amount,
                status,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ]
        )

    if new_rows:
        sheet.append_rows(new_rows, value_input_option="USER_ENTERED")
        print(f"[Jules] {len(new_rows)} transacciones añadidas sin duplicados.")
    else:
        print("[Jules] El balance ya se encuentra actualizado.")


def _decode_b64(value: str) -> str:
    padded = value + "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(padded.encode("utf-8")).decode("utf-8", errors="replace")


def extraer_cuerpo_mensaje(payload: dict[str, Any]) -> str:
    body = ""
    if "parts" in payload:
        for part in payload["parts"]:
            if part.get("mimeType") == "text/plain" and "data" in part.get("body", {}):
                body += _decode_b64(part["body"]["data"])
            elif "parts" in part:
                body += extraer_cuerpo_mensaje(part)
    elif "body" in payload and "data" in payload["body"]:
        body = _decode_b64(payload["body"]["data"])
    return body


def process_jules_inboxes() -> None:
    if not GEMINI_API_KEY:
        print("[Jules] Gemini no configurado; se omite process_jules_inboxes.")
        return

    service = get_gmail_service()
    auditor = ExcelenciaContableJules()

    emails_filter = " OR ".join([f"to:{email}" for email in CUENTAS_AUTORIZADAS])
    query = f"is:unread ({emails_filter})"
    resultados = service.users().messages().list(userId="me", q=query, maxResults=10).execute()
    messages = resultados.get("messages", [])

    if not messages:
        print("[Jules] No hay correos entrantes en cola de gestión.")
        return

    for msg in messages:
        msg_id = msg["id"]
        thread_id = msg["threadId"]
        details = service.users().messages().get(userId="me", id=msg_id, format="full").execute()
        headers = details.get("payload", {}).get("headers", [])

        subject = next((h["value"] for h in headers if h["name"].lower() == "subject"), "Sin Asunto")
        sender = next((h["value"] for h in headers if h["name"].lower() == "from"), "")
        message_id_header = next((h["value"] for h in headers if h["name"].lower() == "message-id"), "")
        delivered_to = next((h["value"] for h in headers if h["name"].lower() == "to"), "")
        recipient_target = next(
            (email for email in CUENTAS_AUTORIZADAS if email in delivered_to.lower()),
            CUENTAS_AUTORIZADAS[0],
        )

        body = extraer_cuerpo_mensaje(details.get("payload", {}))
        importes = auditor.escanear_importes_en_texto(body)
        alertas = auditor.obtener_alertas_calendario_fiscal()
        contexto_rol = (
            "Jules, agente de operaciones de TRYONYOU"
            if "tryonyou.app" in recipient_target
            else "Jules, asistente contable personal de Rubén"
        )
        system_instruction = (
            f"Eres {contexto_rol}. Responde de forma directa, analítica y basada estrictamente en datos contables reales. "
            f"Prohibido inventar precios, tratos o situaciones ficticias. Plazos fiscales activos: {alertas}. "
            f"Cifras detectadas en consulta: {importes}. Usa respuestas limpias, cortas y profesionales."
        )

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": (
                                f"Para: {recipient_target}\nDe: {sender}\nAsunto: {subject}\n\nCuerpo:\n{body[:12000]}"
                            )
                        }
                    ]
                }
            ],
            "systemInstruction": {"parts": [{"text": system_instruction}]},
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 800},
        }
        gemini_res = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=45,
        )
        if gemini_res.status_code != 200:
            continue

        candidates = gemini_res.json().get("candidates", [])
        parts = candidates[0].get("content", {}).get("parts", []) if candidates else []
        reply_text = parts[0].get("text", "") if parts else ""
        if not reply_text:
            continue

        reply = MIMEText(reply_text, "plain", "utf-8")
        reply["To"] = sender
        reply["From"] = recipient_target
        reply["Subject"] = subject if subject.startswith("Re:") else f"Re: {subject}"
        if message_id_header:
            reply["In-Reply-To"] = message_id_header
            reply["References"] = message_id_header

        raw_message = base64.urlsafe_b64encode(reply.as_bytes()).decode("utf-8")
        service.users().messages().send(
            userId="me", body={"raw": raw_message, "threadId": thread_id}
        ).execute()
        service.users().messages().batchModify(
            userId="me", body={"ids": [msg_id], "removeLabelIds": ["UNREAD"]}
        ).execute()
        print(f"[Jules] Consulta de {sender} resuelta y archivada desde {recipient_target}.")


def ejecutar_goteo_seo_diario() -> None:
    if not SPREADSHEET_ID:
        print("[SEO Warning] SPREADSHEET_ID ausente. Saltando módulo SEO.")
        return

    client = get_google_sheet_client()
    try:
        sheet = client.open_by_key(SPREADSHEET_ID).worksheet("SEO_Prospects")
    except gspread.exceptions.WorksheetNotFound:
        print("[SEO Warning] Pestaña 'SEO_Prospects' ausente en Drive. Saltando módulo.")
        return

    prospectos = [
        r for r in sheet.get_all_records() if str(r.get("Estado", "")).strip() == "Pendiente"
    ][:SEO_MAX_ENVIOS_DIARIOS]
    if not prospectos:
        return

    service = get_gmail_service()
    plantilla_asunto = "Propuesta de contenido técnico / Recurso de innovación para {{sitio_nombre}}"
    plantilla_cuerpo = (
        "Bonjour,\n\nJe vous contacte concernant votre section dédiée à l'innovation technologique sur {{sitio_nombre}}.\n"
        "Nous avons développé une infrastructure d'essayage virtuel de haute précision et zéro-donnée qui pourrait intéresser vos lecteurs.\n"
        "Vous pouvez consulter notre matériel publicitaire sur notre plateforme officielle.\n\nCordialement,\nJules - TRYONYOU"
    )

    for p in prospectos:
        email = str(p.get("Email_Contacto", "")).strip()
        nombre = str(p.get("Nombre_Sitio", "sitio")).strip() or "sitio"
        url = str(p.get("URL", "")).strip()
        if not email:
            continue

        asunto = plantilla_asunto.replace("{{sitio_nombre}}", nombre)
        cuerpo = plantilla_cuerpo.replace("{{sitio_nombre}}", nombre)

        mensaje = MIMEText(cuerpo, "plain", "utf-8")
        mensaje["To"] = email
        mensaje["From"] = "admin@tryonyou.app"
        mensaje["Subject"] = asunto

        raw_msg = base64.urlsafe_b64encode(mensaje.as_bytes()).decode("utf-8")
        try:
            service.users().messages().send(userId="me", body={"raw": raw_msg}).execute()
            if url:
                celda = sheet.find(url)
                sheet.update_cell(celda.row, 4, "Enviado")
                sheet.update_cell(celda.row, 5, datetime.now().strftime("%Y-%m-%d"))
            print(f"[Jules SEO] Enlace estratégico enviado a {nombre}.")
            time.sleep(random.uniform(3.0, 7.0))
        except Exception as exc:
            print(f"[SEO Error] No se pudo enviar a {nombre}: {exc}")


def main_cron_handler() -> None:
    try:
        print(f"--- INICIO DE CICLO OPERATIVO JULES: {datetime.now()} ---")
        sync_pennylane_to_sheets()
        process_jules_inboxes()
        ejecutar_goteo_seo_diario()
        print("--- FIN DE CICLO OPERATIVO: SISTEMA COMPLETO CONSOLIDADO ---")
    except Exception as exc:
        print(f"[CRÍTICO ERROR] Caída general del pipeline de control: {exc}")


if __name__ == "__main__":
    main_cron_handler()
