from __future__ import annotations

import base64
import os
import re
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
DEFAULT_QUERY = "is:unread (lconta OR comptabilité OR factura OR taxes)"
CUENTAS_AUTORIZADAS = [
    "admin@tryonyou.app",
    "ruben.espinar.10@icloud.com",
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


def _get_required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required env: {name}")
    return value


def get_gmail_service() -> Any:
    creds = Credentials(
        token=None,
        refresh_token=_get_required_env("GMAIL_REFRESH_TOKEN"),
        client_id=_get_required_env("GMAIL_CLIENT_ID"),
        client_secret=_get_required_env("GMAIL_CLIENT_SECRET"),
        token_uri="https://oauth2.googleapis.com/token",
    )
    return build("gmail", "v1", credentials=creds, cache_discovery=False)


def read_unseen_accounting_emails(service: Any) -> list[dict[str, str]]:
    query = os.environ.get("JULES_MAIL_QUERY", DEFAULT_QUERY).strip() or DEFAULT_QUERY
    max_results = int(os.environ.get("JULES_MAIL_MAX_RESULTS", "10"))
    results = (
        service.users()
        .messages()
        .list(userId="me", q=query, maxResults=max_results)
        .execute()
    )
    return results.get("messages", [])


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


def _extract_plain_text(payload: dict[str, Any]) -> str:
    mime_type = payload.get("mimeType", "")
    if mime_type == "text/plain":
        data = payload.get("body", {}).get("data", "")
        return _decode_base64_content(data)

    for part in payload.get("parts", []) or []:
        text = _extract_plain_text(part)
        if text.strip():
            return text

    data = payload.get("body", {}).get("data", "")
    return _decode_base64_content(data)


def _header_value(headers: list[dict[str, str]], name: str) -> str:
    for header in headers:
        if header.get("name", "").lower() == name.lower():
            return header.get("value", "")
    return ""


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
        service = get_gmail_service()
        profile = service.users().getProfile(userId="me").execute()
        mailbox = str(profile.get("emailAddress", "")).strip().lower()
        if mailbox not in {c.lower() for c in CUENTAS_AUTORIZADAS}:
            return {
                "ok": False,
                "status": "skipped",
                "message": (
                    "Mail agent skipped: mailbox not authorized. "
                    f"Authorized: {', '.join(CUENTAS_AUTORIZADAS)}"
                ),
                "processed": 0,
                "replied": 0,
                "failed": 0,
            }
    except Exception as exc:
        return {
            "ok": False,
            "status": "skipped",
            "message": f"Mail agent skipped: {exc}",
            "processed": 0,
            "replied": 0,
            "failed": 0,
        }

    messages = read_unseen_accounting_emails(service)
    if not messages:
        return {
            "ok": True,
            "status": "success",
            "message": "No unread accounting messages.",
            "processed": 0,
            "replied": 0,
            "failed": 0,
        }

    replied = 0
    failed = 0
    auditor = ExcelenciaContableJules()
    for msg in messages:
        msg_id = msg.get("id", "")
        thread_id = msg.get("threadId", "")
        if not msg_id:
            failed += 1
            continue

        try:
            details = (
                service.users()
                .messages()
                .get(userId="me", id=msg_id, format="full")
                .execute()
            )
            payload = details.get("payload", {})
            headers = payload.get("headers", []) or []

            subject = _header_value(headers, "Subject") or "(sin asunto)"
            sender = _header_value(headers, "From")
            message_id_header = _header_value(headers, "Message-ID")
            sender_email = parseaddr(sender)[1].strip() or sender.strip()
            if not sender_email:
                raise RuntimeError("Missing sender email")

            body = _extract_plain_text(payload)
            if not body.strip():
                body = "(correo sin cuerpo de texto plano)"

            importes_mencionados = auditor.escanear_importes_en_texto(body)
            contexto_adicional = ""
            if importes_mencionados:
                contexto_adicional = (
                    "El remitente menciona los siguientes importes en su consulta: "
                    f"{importes_mencionados}. Verifica si requieren validación."
                )
                if len(importes_mencionados) >= 3:
                    revision_tva = auditor.verificar_calculo_tva(
                        total=importes_mencionados[0],
                        base_imponible=importes_mencionados[1],
                        tva_declarada=importes_mencionados[2],
                    )
                    contexto_adicional = (
                        f"{contexto_adicional}\nResultado de auditoría TVA preliminar: {revision_tva}"
                    )

            system_instruction = auditor.generar_instruccion_sistema_avanzada(
                contexto_adicional
            )
            reply_body = analyze_and_draft_response(body, sender_email, system_instruction)
            send_reply(service, sender_email, subject, reply_body, thread_id, message_id_header)
            mark_as_read(service, msg_id)
            replied += 1
        except Exception:
            failed += 1

    processed = len(messages)
    return {
        "ok": failed == 0,
        "status": "success" if failed == 0 else "partial_error",
        "message": "Mail run completed" if failed == 0 else "Mail run completed with errors",
        "processed": processed,
        "replied": replied,
        "failed": failed,
    }
