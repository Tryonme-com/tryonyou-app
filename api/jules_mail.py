from __future__ import annotations

import base64
import os
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


def analyze_and_draft_response(email_body: str, sender_email: str) -> str:
    gemini_api_key = _get_required_env("GEMINI_API_KEY")
    system_instruction = (
        "Eres Jules, asistente técnico de operaciones y contabilidad. Responde consultas "
        "de contables o gestores de forma directa, objetiva y basada estrictamente en "
        "datos reales. Si te piden un justificante que no está en el sistema, indica "
        "que se está procesando en Pennylane. No inventes números ni transacciones. "
        "Usa un tono profesional, claro y refinado."
    )
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

            reply_body = analyze_and_draft_response(body, sender_email)
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
