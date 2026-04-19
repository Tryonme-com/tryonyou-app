"""
Punto de entrada único de consolidación — Lafayette, Le Bon Marché y canales asociados.

Ejecución recomendada (entorno del proyecto): ``.venv/bin/python master_fatality.py``
(``httpx`` instalado en ``.venv``; si usas otro Python, ``pip install httpx`` en ese entorno).

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""

# Directiva maestra para agentes (Cursor): leer antes de tocar infra, contratos o pagos.
AGENTE_CONSOLIDACION_DIRECTIVA = """
Actúa como agente técnico. El archivo master_fatality.py concentra el marco operativo
(Lafayette, Le Bon Marché y canales listados en CONTACTOS_CLAVE). Todo lo que hagamos
debe poder contrastarse con este script: si añades una entrada nueva al dossier y aparece
un contacto o sede nuevo, incorpóralo en CONTACTOS_CLAVE. Con Qonto o Stripe, usa únicamente
las funciones de verificación de este módulo (variables de entorno; nunca claves en código).
Es la fuente de archivo operativa para esta capa de infraestructura.

Consolidación: un solo punto de entrada; CONTACTOS_CLAVE escala con nuevos retail
(p. ej. Mango, El Corte Inglés) como diccionarios adicionales. Al consolidar, ejecuta
python master_fatality.py y registra saldo/capital y si los metadatos de Stripe sugieren
documento o contrato (véase stripe_payment_intents_metadata_probe).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

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
]


STRIPE_API_BASE = "https://api.stripe.com/v1"
# Metadatos que sugieren documento / contrato en objetos Stripe (ajustar a tu convención)
DOCUMENT_METADATA_KEYS = (
    "contract_id",
    "document_id",
    "contrat",
    "dossier_ref",
    "invoice_pdf",
)


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
    return {
        "patent": "PCT/EP2025/067317",
        "contactos_clave": CONTACTOS_CLAVE,
        "dossier": DOSSIER_FATALITY,
        "qonto_y_deuda": verify_qonto(),
        "stripe_balance": verify_stripe_balance_httpx(),
        "stripe_metadata_probe": stripe_payment_intents_metadata_probe(),
    }


def main() -> None:
    print(json.dumps(consolidate_report(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
