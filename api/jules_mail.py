from __future__ import annotations

import base64
import csv
import mimetypes
import os
import re
from datetime import datetime
from email.mime.text import MIMEText
from email.utils import parseaddr
from typing import Any

import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

GEMINI_API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.5-pro:generateContent"
)
AUDIT_LOG_FILENAME = "logs_contabilidad.csv"
CUENTAS_AUTORIZADAS = [
    "admin@tryonyou.app",
    "ruben.espinard.10@icloud.com",
    "rubensanzburo@gmail.com",
]


class ExcelenciaContableJules:
    def __init__(self, tva_rate_default: float = 0.20) -> None:
        self.tva_default = tva_rate_default

    def verificar_calculo_tva(
        self, total: float, base_imponible: float, tva_declarada: float
    ) -> dict[str, Any]:
        total = float(total)
        base_imponible = float(base_imponible)
        tva_declarada = float(tva_declarada)

        tva_teorica = round(base_imponible * self.tva_default, 2)
        total_teorico = round(base_imponible + tva_teorica, 2)

        descuadre_tva = abs(tva_teorica - tva_declarada)
        descuadre_total = abs(total_teorico - total)

        if descuadre_tva > 0.02 or descuadre_total > 0.02:
            return {
                "valido": False,
                "error": (
                    f"Discrepancia fiscal. IVA teórico: {tva_teorica}€, "
                    f"Declarado: {tva_declarada}€. Total teórico: {total_teorico}€, "
                    f"Declarado: {total}€."
                ),
            }
        return {"valido": True, "error": None}

    def escanear_importes_en_texto(self, texto: str) -> list[float]:
        patron = r"(\d+(?:[\s.,]\d+)?)\s*(?:€|EUR|euros)"
        coincidencias = re.findall(patron, texto)

        importes: list[float] = []
        for coincidencia in coincidencias:
            try:
                num_str = coincidencia.replace(" ", "").replace(",", ".")
                importes.append(float(num_str))
            except ValueError:
                continue
        return importes

    def generar_instruccion_sistema_avanzada(
        self, contexto_bancario_actual: str = ""
    ) -> str:
        return (
            "Eres Jules, el controlador financiero y contable de más alto nivel para TRYONYOU. "
            "Tus respuestas son estrictamente analíticas, basadas en datos confirmados y leyes fiscales vigentes "
            "(Francia/Unión Europea). Reglas de oro:\n"
            "1. Si Lconta o un proveedor pregunta por un descuadre, revisa los datos adjuntos y desglosa la Base "
            "Imponible y la TVA (20%).\n"
            "2. Nunca asumas un pago como realizado si no figura en el extracto bancario sincronizado.\n"
            "3. Usa terminología financiera precisa (NIF, IVA/TVA, Invoice, Bilan, Conciliación).\n"
            "4. Respuestas concisas, cortas, directas y sin rodeos corporativos innecesarios.\n"
            "5. Si te piden un justificante que no está en el sistema, indica que se está procesando en Pennylane.\n"
            f"Contexto de caja actual del sistema:\n{contexto_bancario_actual}"
        )


class CalendarioFiscalFrances:
    @staticmethod
    def obtener_alertas_del_mes() -> list[str]:
        hoy = datetime.now()
        dia = hoy.day
        mes = hoy.month

        alertas: list[str] = []
        if 1 <= dia <= 19:
            alertas.append(
                "CRÍTICO: Ventana de declaración de TVA del mes anterior en curso. Límite aproximado: día 19-24."
            )
        if dia >= 25 or dia <= 5:
            alertas.append(
                "RECORDATORIO: Revisar cálculo de cotizaciones de autónomos/URSSAF para el cierre de ciclo."
            )
        if mes in [1, 4, 7, 10] and dia <= 15:
            alertas.append(
                "ATENCIÓN: Cierre de trimestre fiscal en curso. Recopilar facturas intracomunitarias."
            )
        return alertas


class AuditoriaContableJules:
    def __init__(self, ruta_log: str = f"api/{AUDIT_LOG_FILENAME}") -> None:
        self.ruta_log = os.environ.get("JULES_AUDIT_LOG_PATH", ruta_log)
        self._inicializar_archivo()

    def _abrir_para_append(self, mode: str):
        try:
            os.makedirs(os.path.dirname(self.ruta_log), exist_ok=True)
            return open(self.ruta_log, mode=mode, newline="", encoding="utf-8")
        except OSError:
            tmp_path = os.path.join(os.environ.get("TMPDIR", "/tmp"), AUDIT_LOG_FILENAME)
            os.makedirs(os.path.dirname(tmp_path), exist_ok=True)
            self.ruta_log = tmp_path
            return open(self.ruta_log, mode=mode, newline="", encoding="utf-8")

    def _inicializar_archivo(self) -> None:
        try:
            if not os.path.exists(self.ruta_log):
                with self._abrir_para_append("w") as file:
                    writer = csv.writer(file)
                    writer.writerow(
                        [
                            "Timestamp",
                            "Cuenta_Destino",
                            "Remitente",
                            "Asunto",
                            "Accion_Jules",
                            "Importe_Detectado",
                        ]
                    )
        except OSError:
            return

    def registrar_accion(
        self,
        cuenta: str,
        remitente: str,
        asunto: str,
        accion: str,
        importe: float = 0.0,
    ) -> None:
        try:
            with self._abrir_para_append("a") as file:
                writer = csv.writer(file)
                writer.writerow(
                    [
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        cuenta,
                        remitente,
                        asunto,
                        accion,
                        f"{importe:.2f}€",
                    ]
                )
        except OSError:
            return


def _get_required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required env: {name}")
    return value


def _decode_base64_content(value: str) -> str:
    if not value:
        return ""
    padded = value + "=" * (-len(value) % 4)
    try:
        return base64.urlsafe_b64decode(padded.encode("utf-8")).decode(
            "utf-8", errors="replace"
        )
    except Exception:
        return ""


def obtener_servicio_gmail() -> Any:
    token_infra = {
        "token": None,
        "refresh_token": _get_required_env("GMAIL_REFRESH_TOKEN"),
        "client_id": _get_required_env("GMAIL_CLIENT_ID"),
        "client_secret": _get_required_env("GMAIL_CLIENT_SECRET"),
        "token_uri": "https://oauth2.googleapis.com/token",
    }
    creds = Credentials.from_authorized_user_info(token_infra)
    return build("gmail", "v1", credentials=creds, cache_discovery=False)


def get_gmail_service() -> Any:
    return obtener_servicio_gmail()


def extraer_cuerpo_mensaje(payload: dict[str, Any]) -> str:
    body = ""
    if "parts" in payload:
        for part in payload.get("parts", []):
            if part.get("mimeType") == "text/plain" and part.get("body", {}).get("data"):
                body += _decode_base64_content(part["body"]["data"])
            elif "parts" in part:
                body += extraer_cuerpo_mensaje(part)
    elif payload.get("body", {}).get("data"):
        body = _decode_base64_content(payload["body"]["data"])
    return body


def _header_value(headers: list[dict[str, str]], name: str) -> str:
    for header in headers:
        if header.get("name", "").lower() == name.lower():
            return header.get("value", "")
    return ""


def descargar_correos_bandeja(service: Any | None = None) -> list[dict[str, Any]]:
    service = service or obtener_servicio_gmail()
    filtro_busqueda = " OR ".join([f"to:{email}" for email in CUENTAS_AUTORIZADAS])
    query = f"is:unread ({filtro_busqueda})"
    max_results = int(os.environ.get("JULES_MAIL_MAX_RESULTS", "10"))

    resultados = service.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
    mensajes_pendientes = resultados.get("messages", [])

    correos_procesados: list[dict[str, Any]] = []
    for msg in mensajes_pendientes:
        detalle = service.users().messages().get(userId="me", id=msg["id"], format="full").execute()
        headers = detalle.get("payload", {}).get("headers", [])

        asunto = _header_value(headers, "subject") or "Sin Asunto"
        remitente = _header_value(headers, "from") or "Desconocido"
        destinatario_original = _header_value(headers, "to")
        mensaje_id = _header_value(headers, "message-id")

        cuenta_destino = next(
            (
                email
                for email in CUENTAS_AUTORIZADAS
                if email in destinatario_original.lower()
            ),
            CUENTAS_AUTORIZADAS[0],
        )

        cuerpo_texto = extraer_cuerpo_mensaje(detalle.get("payload", {}))
        correos_procesados.append(
            {
                "id": msg.get("id", ""),
                "threadId": msg.get("threadId", ""),
                "message_id_header": mensaje_id,
                "cuenta_destino": cuenta_destino,
                "remitente": remitente,
                "asunto": asunto,
                "cuerpo": cuerpo_texto,
            }
        )
    return correos_procesados


def _collect_parts(parts: list[dict[str, Any]], out: list[dict[str, Any]]) -> None:
    for part in parts:
        out.append(part)
        nested = part.get("parts", [])
        if nested:
            _collect_parts(nested, out)


def descargar_y_clasificar_adjuntos(
    service: Any, message_id: str, cuenta_origen: str
) -> list[dict[str, Any]]:
    message = service.users().messages().get(userId="me", id=message_id, format="full").execute()
    payload = message.get("payload", {})
    parts = payload.get("parts", [])

    all_parts: list[dict[str, Any]] = []
    _collect_parts(parts, all_parts)
    documentos_recuperados: list[dict[str, Any]] = []

    for part in all_parts:
        if part.get("filename") and part.get("body", {}).get("attachmentId"):
            attachment_id = part["body"]["attachmentId"]
            filename = part["filename"]

            attachment = (
                service.users()
                .messages()
                .attachments()
                .get(userId="me", messageId=message_id, id=attachment_id)
                .execute()
            )

            data = attachment.get("data", "")
            file_data = base64.urlsafe_b64decode((data + "=" * (-len(data) % 4)).encode("utf-8"))

            ext = os.path.splitext(filename)[1].lower()
            tipo_documento = "Otros"
            if ext in [".pdf", ".doc", ".docx"]:
                tipo_documento = "Facturas_Justificantes"
            elif ext in [".xls", ".xlsx", ".csv"]:
                tipo_documento = "Extractos_Modelos"

            tipo_mime = part.get("mimeType") or mimetypes.guess_type(filename)[0] or "application/octet-stream"
            documentos_recuperados.append(
                {
                    "nombre": filename,
                    "datos": file_data,
                    "categoria_sugerida": tipo_documento,
                    "cuenta_origen": cuenta_origen,
                    "tipo_mime": tipo_mime,
                }
            )

    return documentos_recuperados


def analyze_and_draft_response(
    email_body: str, sender_email: str, system_instruction: str
) -> str:
    gemini_api_key = _get_required_env("GEMINI_API_KEY")
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": f"Consulta recibida de {sender_email}:\n\n{email_body[:12000]}"
                    }
                ]
            }
        ],
        "systemInstruction": {"parts": [{"text": system_instruction}]},
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 800},
    }
    response = requests.post(
        f"{GEMINI_API_URL}?key={gemini_api_key}",
        headers={"Content-Type": "application/json"},
        json=payload,
        timeout=45,
    )
    if response.status_code != 200:
        raise RuntimeError(f"Gemini API error {response.status_code}: {response.text[:500]}")

    body = response.json()
    candidates = body.get("candidates", [])
    if not candidates:
        raise RuntimeError("Gemini response has no candidates")
    parts = candidates[0].get("content", {}).get("parts", [])
    if not parts:
        raise RuntimeError("Gemini response has no content parts")
    text = parts[0].get("text", "").strip()
    if not text:
        raise RuntimeError("Gemini returned an empty reply")
    return text


def send_reply(
    service: Any, to_email: str, subject: str, body: str, thread_id: str, message_id: str
) -> None:
    reply = MIMEText(body, "plain", "utf-8")
    reply["To"] = to_email
    reply["Subject"] = subject if subject.lower().startswith("re:") else f"Re: {subject}"
    if message_id:
        reply["In-Reply-To"] = message_id
        reply["References"] = message_id

    raw_message = base64.urlsafe_b64encode(reply.as_bytes()).decode("utf-8")
    service.users().messages().send(
        userId="me",
        body={"raw": raw_message, "threadId": thread_id},
    ).execute()


def mark_as_read(service: Any, message_id: str) -> None:
    service.users().messages().batchModify(
        userId="me",
        body={"ids": [message_id], "removeLabelIds": ["UNREAD"]},
    ).execute()


def jules_mail_agent_execution() -> dict[str, Any]:
    try:
        service = obtener_servicio_gmail()
        profile = service.users().getProfile(userId="me").execute()
        mailbox = str(profile.get("emailAddress", "")).strip().lower()
        if mailbox not in {c.lower() for c in CUENTAS_AUTORIZADAS}:
            return {
                "ok": False,
                "status": "skipped",
                "message": "Mail agent skipped: mailbox not authorized.",
                "processed": 0,
                "replied": 0,
                "failed": 0,
            }
    except Exception as exc:
        return {
            "ok": False,
            "status": "skipped",
            "message": "Mail agent skipped: Gmail configuration or auth is invalid.",
            "processed": 0,
            "replied": 0,
            "failed": 0,
        }

    correos = descargar_correos_bandeja(service)
    if not correos:
        return {
            "ok": True,
            "status": "success",
            "message": "No unread accounting messages.",
            "processed": 0,
            "replied": 0,
            "failed": 0,
            "attachments": 0,
        }

    replied = 0
    failed = 0
    total_adjuntos = 0
    auditor = ExcelenciaContableJules()
    auditoria = AuditoriaContableJules()
    alertas_fiscales = CalendarioFiscalFrances.obtener_alertas_del_mes()

    for correo in correos:
        msg_id = str(correo.get("id", ""))
        thread_id = str(correo.get("threadId", ""))
        if not msg_id:
            failed += 1
            continue

        try:
            remitente = str(correo.get("remitente", "Desconocido"))
            asunto = str(correo.get("asunto", "Sin Asunto"))
            cuenta_destino = str(correo.get("cuenta_destino", CUENTAS_AUTORIZADAS[0]))
            message_id_header = str(correo.get("message_id_header", ""))
            body = str(correo.get("cuerpo", "")).strip() or "(correo sin cuerpo de texto plano)"
            sender_email = parseaddr(remitente)[1].strip() or remitente.strip()
            if not sender_email:
                raise RuntimeError("Missing sender email")

            importes_mencionados = auditor.escanear_importes_en_texto(body)
            contexto_adicional = ""
            if importes_mencionados:
                contexto_adicional = (
                    "El remitente menciona los siguientes importes en su consulta: "
                    f"{importes_mencionados}. Verifica si requieren validación."
                )

            if len(importes_mencionados) >= 3:
                # Heurística: usamos los tres primeros importes detectados como
                # total, base imponible y TVA declarada para un chequeo preliminar.
                revision_tva = auditor.verificar_calculo_tva(
                    total=importes_mencionados[0],
                    base_imponible=importes_mencionados[1],
                    tva_declarada=importes_mencionados[2],
                )
                contexto_adicional = (
                    f"{contexto_adicional} Resultado de auditoría TVA preliminar: {revision_tva}"
                ).strip()

            adjuntos = descargar_y_clasificar_adjuntos(service, msg_id, cuenta_destino)
            total_adjuntos += len(adjuntos)
            if adjuntos:
                categorias = sorted({a.get("categoria_sugerida", "Otros") for a in adjuntos})
                contexto_adicional = (
                    f"{contexto_adicional} Adjuntos detectados: {categorias}."
                ).strip()

            if alertas_fiscales:
                contexto_adicional = (
                    f"{contexto_adicional} Alertas fiscales del mes: {alertas_fiscales}."
                ).strip()

            system_instruction = auditor.generar_instruccion_sistema_avanzada(contexto_adicional)
            reply_body = analyze_and_draft_response(body, sender_email, system_instruction)
            send_reply(service, sender_email, asunto, reply_body, thread_id, message_id_header)
            mark_as_read(service, msg_id)
            replied += 1
            auditoria.registrar_accion(
                cuenta=cuenta_destino,
                remitente=remitente,
                asunto=asunto,
                accion="RESPUESTA_ENVIADA",
                importe=importes_mencionados[0] if importes_mencionados else 0.0,
            )
        except Exception:
            failed += 1
            auditoria.registrar_accion(
                cuenta=str(correo.get("cuenta_destino", CUENTAS_AUTORIZADAS[0])),
                remitente=str(correo.get("remitente", "Desconocido")),
                asunto=str(correo.get("asunto", "Sin Asunto")),
                accion="ERROR_PROCESANDO_CORREO",
                importe=0.0,
            )

    processed = len(correos)
    return {
        "ok": failed == 0,
        "status": "success" if failed == 0 else "partial_error",
        "message": "Mail run completed" if failed == 0 else "Mail run completed with errors",
        "processed": processed,
        "replied": replied,
        "failed": failed,
        "attachments": total_adjuntos,
    }
