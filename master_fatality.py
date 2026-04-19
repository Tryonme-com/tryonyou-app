"""
Punto de entrada único de consolidación — Lafayette, Le Bon Marché y canales asociados.

Instrucción para el agente (Cursor): este script es la fuente operativa a contrastar antes
de cambiar infraestructura, contratos o pagos. Nueva entrada de dossier → actualizar
CONTACTOS_CLAVE si implica un contacto o sede nuevo. Qonto y Stripe: usar solo las
funciones de verificación de este módulo (env; nunca claves en código).

Ejecución: ``python3 master_fatality.py`` — imprime estado Qonto (FinancialGuard), saldo
Stripe (httpx) y si hay metadatos tipo documento en los últimos PaymentIntents.

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import httpx

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from stripe_fr_resolve import resolve_stripe_secret_fr

# --- Red / tiendas (escalable: añadir clave = nuevo diccionario) ---
CONTACTOS_CLAVE: dict[str, dict[str, str]] = {
    "galeries_lafayette_pilot": {
        "label": "Galeries Lafayette (piloto TryOnYou / espejo)",
        "ciudad": "París",
        "rol": "Retail soberano / vitrina",
        "notas": "Alineado con production_manifest y FinancialGuard (espejo 402 si impago).",
    },
    "le_bon_marche": {
        "label": "Le Bon Marché",
        "ciudad": "París",
        "rol": "Canal de referencia luxury (expansión)",
        "notas": "Misma matriz de contacto que Lafayette; añadir aquí personas/nodos reales.",
    },
    "mango": {
        "label": "Mango (placeholder)",
        "ciudad": "",
        "rol": "Canal futuro",
        "notas": "Rellenar cuando exista acuerdo; no operativo hasta entrada en dossier.",
    },
    "el_corte_ingles": {
        "label": "El Corte Inglés (placeholder)",
        "ciudad": "",
        "rol": "Canal futuro",
        "notas": "Rellenar cuando exista acuerdo; no operativo hasta entrada en dossier.",
    },
}

# --- Dossier de operaciones (añadir entradas; si hay contacto nuevo, duplicar clave en CONTACTOS_CLAVE) ---
DOSSIER_FATALITY: list[dict[str, Any]] = [
    {
        "id": "op-001",
        "titulo": "Matriz Lafayette — consolidación soberana",
        "estado": "activo",
        "notas": "Contratos y capital: verificar vía Qonto + Stripe; metadatos en PI/charges.",
    },
    {
        "id": "op-450k-shield",
        "titulo": "Blindaje de capital 450.000€",
        "estado": "armado",
        "notas": (
            "Martes 08:00 (Europa/París): confirmar entrada de 450.000€ y activar "
            "Dossier Fatality."
        ),
    },
]


STRIPE_API_BASE = "https://api.stripe.com/v1"
PARIS_TZ = ZoneInfo("Europe/Paris")
TARGET_CAPITAL_ENTRY_EUR = 450_000.0
CAPITAL_ENTRY_EPSILON_EUR = 0.01
# Metadatos que sugieren documento / contrato en objetos Stripe (ajustar a tu convención)
DOCUMENT_METADATA_KEYS = (
    "contract_id",
    "document_id",
    "contrat",
    "dossier_ref",
    "invoice_pdf",
)


def _parse_amount_eur(raw: str) -> float | None:
    value = (raw or "").strip().replace("€", "").replace(" ", "")
    if not value:
        return None
    if "," in value and "." in value:
        if value.rfind(",") > value.rfind("."):
            value = value.replace(".", "").replace(",", ".")
        else:
            value = value.replace(",", "")
    elif "," in value:
        value = value.replace(".", "").replace(",", ".")
    try:
        return float(value)
    except ValueError:
        return None


def _env_truthy(name: str) -> bool:
    return (os.environ.get(name) or "").strip().lower() in ("1", "true", "yes", "on")


def _next_tuesday_0800(reference: datetime) -> datetime:
    local_ref = reference.astimezone(PARIS_TZ)
    days_ahead = (1 - local_ref.weekday()) % 7
    slot = (local_ref + timedelta(days=days_ahead)).replace(
        hour=8, minute=0, second=0, microsecond=0
    )
    if slot < local_ref:
        slot += timedelta(days=7)
    return slot


def dossier_fatality_security_status(now: datetime | None = None) -> dict[str, Any]:
    """
    Corte de seguridad para el hito de tesorería:
    - martes 08:00 (Europa/París),
    - entrada objetivo de 450.000 €,
    - activación de Dossier Fatality para blindaje de capital.
    """
    local_now = (now or datetime.now(tz=PARIS_TZ)).astimezone(PARIS_TZ)
    next_slot = _next_tuesday_0800(local_now)
    slot_is_now = local_now.weekday() == 1 and local_now.hour >= 8

    raw_entry = (
        os.environ.get("FATALITY_CAPITAL_ENTRY_EUR", "").strip()
        or os.environ.get("QONTO_LAST_ENTRY_EUR", "").strip()
    )
    capital_entry_eur = _parse_amount_eur(raw_entry) if raw_entry else None
    manual_confirmed = _env_truthy("FATALITY_CAPITAL_CONFIRMED") or _env_truthy(
        "QONTO_PAGO_CONFIRMADO"
    )
    entry_confirmed = manual_confirmed or (
        capital_entry_eur is not None
        and capital_entry_eur + CAPITAL_ENTRY_EPSILON_EUR >= TARGET_CAPITAL_ENTRY_EUR
    )
    dossier_activated = bool(slot_is_now and entry_confirmed)

    status = "scheduled"
    if slot_is_now and entry_confirmed:
        status = "active"
    elif slot_is_now and not entry_confirmed:
        status = "awaiting_capital_confirmation"

    return {
        "timezone": "Europe/Paris",
        "target_amount_eur": TARGET_CAPITAL_ENTRY_EUR,
        "checkpoint_rule": "Tuesday 08:00",
        "now_local": local_now.isoformat(),
        "next_checkpoint_local": next_slot.isoformat(),
        "checkpoint_window_open": slot_is_now,
        "manual_confirmed": manual_confirmed,
        "capital_entry_detected_eur": capital_entry_eur,
        "entry_confirmed": entry_confirmed,
        "dossier_fatality_activated": dossier_activated,
        "status": status,
    }


def _dossier_with_security_state(status: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for entry in DOSSIER_FATALITY:
        row = dict(entry)
        if row.get("id") == "op-450k-shield":
            row["estado"] = "activo" if status["dossier_fatality_activated"] else "armado"
            row["checkpoint_status"] = status["status"]
        rows.append(row)
    return rows


def verify_qonto() -> dict[str, Any]:
    """Estado Qonto / deuda según FinancialGuard (solo lectura env)."""
    from api.financial_guard import sovereignty_status

    return sovereignty_status()


def _stripe_headers() -> dict[str, str]:
    sk = resolve_stripe_secret_fr()
    if not sk:
        return {}
    return {"Authorization": f"Bearer {sk}"}


def verify_stripe_balance_httpx() -> dict[str, Any]:
    """Saldo Stripe cuenta FR vía httpx (sin volcar secretos)."""
    headers = _stripe_headers()
    if not headers:
        return {
            "ok": False,
            "error": "missing_stripe_secret",
            "hint": "Definir STRIPE_SECRET_KEY_FR (u otras resueltas por stripe_fr_resolve).",
        }
    try:
        with httpx.Client(timeout=30.0) as client:
            r = client.get(f"{STRIPE_API_BASE}/balance", headers=headers)
    except httpx.HTTPError as e:
        return {"ok": False, "error": str(e)}
    if r.status_code != 200:
        return {"ok": False, "status_code": r.status_code, "body_preview": r.text[:200]}
    data = r.json()
    available = data.get("available") or []
    pending = data.get("pending") or []
    return {
        "ok": True,
        "available": available,
        "pending": pending,
        "livemode": data.get("livemode"),
    }


def stripe_payment_intents_metadata_probe(limit: int = 8) -> dict[str, Any]:
    """
    Últimos PaymentIntents: indica si hay metadatos que parecen documento/contrato.
    """
    headers = _stripe_headers()
    if not headers:
        return {"ok": False, "error": "missing_stripe_secret"}
    params = {"limit": str(max(1, min(limit, 100)))}
    try:
        with httpx.Client(timeout=30.0) as client:
            r = client.get(
                f"{STRIPE_API_BASE}/payment_intents",
                headers=headers,
                params=params,
            )
    except httpx.HTTPError as e:
        return {"ok": False, "error": str(e)}
    if r.status_code != 200:
        return {"ok": False, "status_code": r.status_code, "body_preview": r.text[:200]}
    data = r.json()
    rows: list[dict[str, Any]] = []
    for pi in data.get("data") or []:
        meta = pi.get("metadata") or {}
        keys = [k for k in meta if k.lower() in {m.lower() for m in DOCUMENT_METADATA_KEYS}]
        any_doc_hint = bool(keys) or any(
            "pdf" in str(v).lower() or "contr" in str(v).lower() for v in meta.values()
        )
        rows.append(
            {
                "id": pi.get("id"),
                "amount": pi.get("amount"),
                "currency": pi.get("currency"),
                "metadata_keys": list(meta.keys()),
                "document_like_metadata": bool(keys or any_doc_hint),
            }
        )
    return {"ok": True, "payment_intents": rows}


def consolidate_report() -> dict[str, Any]:
    """Informe único: Qonto/FinancialGuard + Stripe (capital + huella de documentos en metadatos)."""
    security_status = dossier_fatality_security_status()
    return {
        "patent": "PCT/EP2025/067317",
        "contactos_clave": CONTACTOS_CLAVE,
        "dossier": _dossier_with_security_state(security_status),
        "fatality_security": security_status,
        "qonto_y_deuda": verify_qonto(),
        "stripe_balance": verify_stripe_balance_httpx(),
        "stripe_metadata_probe": stripe_payment_intents_metadata_probe(),
    }


def main() -> None:
    print(json.dumps(consolidate_report(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
