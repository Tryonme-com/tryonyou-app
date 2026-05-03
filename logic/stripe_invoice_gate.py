"""
Consulta el estado de una factura Stripe para gatear despliegue (p. ej. Jules).

La API de Stripe identifica facturas con `in_...`, no con números tipo
`INV-2026-0001` (eso puede existir como metadata o en tu ERP, pero no sirve
como `id` en GET /v1/invoices/{id}).

Patente PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import os
import sys
from typing import Any

import requests

_STRIPE_INVOICE_URL = "https://api.stripe.com/v1/invoices/{invoice_id}"


def _stripe_secret_key() -> str:
    return (
        os.getenv("STRIPE_SECRET_KEY_FR", "").strip()
        or os.getenv("STRIPE_SECRET_KEY", "").strip()
        or os.getenv("E50_STRIPE_SECRET_KEY", "").strip()
        or os.getenv("INJECT_STRIPE_SECRET_KEY_FR", "").strip()
        or os.getenv("INJECT_STRIPE_SECRET_KEY", "").strip()
    )


def _shop_url_for_log() -> str:
    host = (
        os.getenv("SHOPIFY_MYSHOPIFY_HOST", "").strip()
        or os.getenv("SHOPIFY_STORE_DOMAIN", "").strip()
        or os.getenv("VITE_SHOP_DOMAIN", "").strip()
    )
    if not host:
        return "(configura SHOPIFY_MYSHOPIFY_HOST / SHOPIFY_STORE_DOMAIN / VITE_SHOP_DOMAIN)"
    if host.startswith("http"):
        return host
    return f"https://{host}"


def check_invoice_status(invoice_id: str) -> bool:
    """
    Devuelve True si la factura Stripe está `paid`.

    Requiere clave secreta en entorno (misma cadena que v10_terminal.validar_stripe).
    """
    key = _stripe_secret_key()
    if not key:
        print("Stripe: sin clave en entorno; no se consulta la factura.")
        return False

    if not invoice_id or not str(invoice_id).strip():
        print("Stripe: invoice_id vacío.")
        return False

    url = _STRIPE_INVOICE_URL.format(invoice_id=str(invoice_id).strip())
    try:
        r = requests.get(url, auth=(key, ""), timeout=25)
    except requests.RequestException as e:
        print(f"Stripe: error de red al leer factura — {e}")
        return False

    if r.status_code != 200:
        print(
            f"Factura {invoice_id}: HTTP {r.status_code}. "
            f"Comprueba que el id sea el de Stripe (`in_...`), no un número interno."
        )
        return False

    data: dict[str, Any] = r.json()
    status = str(data.get("status", "")).lower()
    shop = _shop_url_for_log()

    if status == "paid":
        print(f"Factura {invoice_id} pagada. Gate OK. Contexto tienda: {shop}")
        return True

    print(f"Factura {invoice_id} estado={status!r}. Esperando fondos… ({shop})")
    return False


if __name__ == "__main__":
    iid = (sys.argv[1] if len(sys.argv) > 1 else "").strip()
    if not iid:
        print(
            "Uso: python3 -m logic.stripe_invoice_gate <invoice_id_stripe>\n"
            "Ejemplo de id válido en API: in_1AbCdEfGhIjKlMnO"
        )
        sys.exit(2)
    sys.exit(0 if check_invoice_status(iid) else 1)
