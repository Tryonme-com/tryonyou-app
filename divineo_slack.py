"""Notificaciones TryOnYou vía Slack Incoming Webhook (sin SMTP/Gmail)."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


def slack_post(text: str, *, timeout_s: float = 8.0) -> bool:
    url = os.environ.get("SLACK_WEBHOOK_URL", "").strip()
    if not url:
        return False
    payload = json.dumps({"text": str(text)[:3500]}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as r:
            del r
        return True
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def _resolve_sovereignty_webhook_url() -> str:
    """Prioriza webhook dedicado y usa fallback al webhook global."""
    return (
        os.environ.get("SOVEREIGNTY_SLACK_WEBHOOK_URL", "").strip()
        or os.environ.get("SLACK_WEBHOOK_URL", "").strip()
    )


def _status_indicates_block(status: str) -> bool:
    normalized = str(status).casefold()
    return any(
        token in normalized
        for token in ("bloque", "block", "bloqueado", "blocked", "lockdown")
    )


def build_sovereignty_payload(amount: float, status: str) -> dict[str, Any]:
    return {
        "text": "🚨 *PROTOCOLO DE SOBERANÍA V11 ACTUALIZADO*",
        "attachments": [
            {
                "color": "#FF3B30" if _status_indicates_block(status) else "#34C759",
                "fields": [
                    {
                        "title": "Objetivo",
                        "value": "Lafayette + Marais (LVMH)",
                        "short": True,
                    },
                    {"title": "Estado", "value": str(status), "short": True},
                    {
                        "title": "Umbral de Apertura",
                        "value": f"{float(amount):.2f} € TTC",
                        "short": False,
                    },
                    {
                        "title": "Oferta Flash 15%",
                        "value": "Activa (Expira en 7 días)",
                        "short": False,
                    },
                ],
                "footer": "Arquitecto V11 - El silencio es poder.",
            }
        ],
    }


def notify_sovereignty_status(
    amount: float,
    status: str,
    *,
    timeout_s: float = 8.0,
) -> bool:
    """
    Envía una alerta de estado soberano por Slack.

    Requiere `SOVEREIGNTY_SLACK_WEBHOOK_URL` o, en su defecto, `SLACK_WEBHOOK_URL`.
    """
    url = _resolve_sovereignty_webhook_url()
    if not url:
        return False
    payload = json.dumps(build_sovereignty_payload(amount, status)).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as r:
            del r
        return True
    except (urllib.error.URLError, TimeoutError, OSError):
        return False
