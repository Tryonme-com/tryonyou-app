# -*- coding: utf-8 -*-
import os
import sys
import json
import base64
import asyncio
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
import google.generativeai as genai

# Configuración de Infraestructura Confirmada
SPREADSHEET_ID = "Divineo_Leads_DB"
SHEET_NAME = "Startup Follow-Up"
TARGET_EMAILS = ["admin@tryonyou.app", "ruben.espinar.10@icloud.com", "rubensanzburo@gmail.com"]

SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/spreadsheets"
]

def obtener_credenciales():
    for archivo in ["jules-agent-key.json", "service_account.json"]:
        if os.path.exists(archivo):
            return service_account.Credentials.from_service_account_file(archivo, scopes=SCOPES)
    raise FileNotFoundError("Error crítico: Falta el archivo de credenciales de la cuenta de servicio.")

def registrar_rastro_sheets(sheets_service, cuenta, remitente, asunto, estado, detalles):
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    body = {"values": [[ahora, cuenta, remitente, asunto, estado, detalles]]}
    try:
        sheets_service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID, range="Historial_Acciones!A:F",
            valueInputOption="USER_ENTERED", insertDataOption="INSERT_ROWS", body=body
        ).execute()
    except Exception as e:
        print(f"Error histórico Sheets: {e}", file=sys.stderr)

def obtener_contexto_empresa(sheets_service):
    try:
        res = sheets_service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID, range=f"{SHEET_NAME}!A:Z"
        ).execute()
        rows = res.get("values", [])
        if not rows:
            return "DATOS CONFIRMADOS Y REALES:\nBase de datos corporativa vacía."

        ctx = "DATOS CONFIRMADOS Y REALES:\n"
        headers = rows[0]
        for r in rows[1:]:
            linea = ", ".join([f"{headers[i]}: {r[i]}" for i in range(min(len(headers), len(r)))])
            ctx += f"- {linea}\n"
        return ctx
    except Exception as e:
        return f"Error lectura base de datos: {e}"

async def consultar_gemini_async(contexto, remitente, asunto, cuerpo):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("La variable de entorno GEMINI_API_KEY no está configurada.")

    genai.configure(api_key=api_key)
    inst = (
        "Eres el agente de operaciones de TryOnYou. Responde basándote EXCLUSIVAMENTE en datos reales provistos. "
        "PROHIBIDO INVENTAR DATOS O SITUACIONES FICTICIAS. Si no sabes, dilo de forma clara y sincera."
    )
    req = f"{inst}\n\n{contexto}\n\nDe: {remitente}\nAsunto: {asunto}\nCuerpo: {cuerpo}\n\nRespuesta:"

    model = genai.GenerativeModel('gemini-1.5-flash')
    loop = asyncio.get_event_loop()
    res = await loop.run_in_executor(
        None,
        lambda: model.generate_content(contents=req, generation_config={"temperature": 0.0})
    )
    return res.text

def enviar_respuesta_gmail(gmail_service, msg_id, thread_id, original_to, remitente, asunto, texto_respuesta):
    from email.mime.text import MIMEText
    mensaje = MIMEText(texto_respuesta)
    mensaje['to'] = remitente
    mensaje['from'] = original_to
    mensaje['subject'] = f"Re: {asunto}" if not asunto.lower().startswith("re:") else asunto
    mensaje['In-Reply-To'] = msg_id
    mensaje['References'] = msg_id

    raw = base64.urlsafe_b64encode(mensaje.as_bytes()).decode('utf-8')
    gmail_service.users().messages().send(userId='me', body={'raw': raw, 'threadId': thread_id}).execute()

async def procesar_cuenta(gmail_service, sheets_service, ctx, em):
    loop = asyncio.get_event_loop()
    try:
        results = await loop.run_in_executor(
            None, lambda: gmail_service.users().messages().list(userId='me', q=f"to:{em} is:unread").execute()
        )
        messages = results.get('messages', [])
        if not messages:
            return

        for msg in messages:
            m_id = msg['id']
            det = await loop.run_in_executor(
                None, lambda: gmail_service.users().messages().get(userId='me', id=m_id).execute()
            )

            headers = det["payload"].get("headers", [])
            rem = next((h["value"] for h in headers if h["name"].lower() == "from"), "Desconocido")
            asu = next((h["value"] for h in headers if h["name"].lower() == "subject"), "Sin Asunto")

            body = ""
            if "parts" in det["payload"]:
                for p in det["payload"]["parts"]:
                    if p["mimeType"] == "text/plain" and "data" in p["body"]:
                        body = base64.urlsafe_b64decode(p["body"]["data"]).decode("utf-8")
                        break
            elif "body" in det["payload"] and "data" in det["payload"]["body"]:
                body = base64.urlsafe_b64decode(det["payload"]["body"]["data"]).decode("utf-8")

            try:
                txt = await consultar_gemini_async(ctx, rem, asu, body)
                await loop.run_in_executor(
                    None, lambda: enviar_respuesta_gmail(gmail_service, m_id, det["threadId"], em, rem, asu, txt)
                )
                await loop.run_in_executor(
                    None, lambda: gmail_service.users().messages().batchModify(
                        userId="me", body={"ids": [m_id], "removeLabelIds": ["UNREAD"]}
                    ).execute()
                )
                registrar_rastro_sheets(sheets_service, em, rem, asu, "PROCESADO", "Sincronización v100 finalizada.")
            except Exception as ex:
                registrar_rastro_sheets(sheets_service, em, rem, asu, "ERROR", str(ex))
    except Exception as e:
        print(f"Error procesando cuenta {em}: {e}", file=sys.stderr)

async def main():
    try:
        creds = obtener_credenciales()
        sheets_service = build('sheets', 'v4', credentials=creds)
        gmail_service = build('gmail', 'v1', credentials=creds)
        ctx = obtener_contexto_empresa(sheets_service)

        tareas = [procesar_cuenta(gmail_service, sheets_service, ctx, em) for em in TARGET_EMAILS]
        await asyncio.gather(*tareas)
    except Exception as e:
        print(f"Error general en pipeline: {e}", file=sys.stderr)

if __name__ == "__main__":
    asyncio.run(main())
