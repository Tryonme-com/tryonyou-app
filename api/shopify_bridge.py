"""
Shopify Bridge — Agente 26 (Admin API + storefront Zero-Size).

Integración bunker: consumido por api/index.py (handler serverless Vercel).
Contrato tipo «servicio FastAPI» sin uvicorn: funciones puras invocadas desde el orquestador HTTP.

1) Borrador de pedido (Admin REST): crea draft_order con variante piloto única
   (sin tallas en payload ni nota visible al comprador más allá del sello Divineo).
   Requiere: SHOPIFY_ADMIN_ACCESS_TOKEN, SHOPIFY_STORE_DOMAIN (*.myshopify.com),
   SHOPIFY_ZERO_SIZE_VARIANT_ID (numérico).

2) Fallback: URL de producto / checkout configurada (SHOPIFY_PERFECT_CHECKOUT_URL o dominio + path).

Variables de entorno: ver docstring en build + resolve al final.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request

SIREN_SELL = "943 610 196"
PATENTE = "PCT/EP2025/067317"


def _shopify_host() -> str:
    raw = os.environ.get("SHOPIFY_STORE_DOMAIN", "").strip()
    raw = raw.replace("https://", "").replace("http://", "").split("/")[0]
    return raw


def admin_draft_order_invoice_url(lead_id: int, fabric_sensation: str) -> str | None:
    """POST /admin/api/{ver}/draft_orders.json → invoice_url si credenciales válidas."""
    token = os.environ.get("SHOPIFY_ADMIN_ACCESS_TOKEN", "").strip()
    host = _shopify_host()
    variant_raw = os.environ.get("SHOPIFY_ZERO_SIZE_VARIANT_ID", "").strip()
    if not token or not host or not variant_raw.isdigit():
        return None
    if ".myshopify.com" not in host:
        # Admin API oficial exige host myshopify; si usas dominio custom, define el myshopify en env.
        return None
    ver = os.environ.get("SHOPIFY_ADMIN_API_VERSION", "2024-10").strip() or "2024-10"
    url = f"https://{host}/admin/api/{ver}/draft_orders.json"
    sensation = (fabric_sensation or "").strip()[:120]
    note = (
        f"Divineo V10 · lead #{lead_id} · SIREN {SIREN_SELL} · {PATENTE} · "
        f"ajustage Zero-Size · {sensation}"
    )
    body = {
        "draft_order": {
            "line_items": [{"variant_id": int(variant_raw), "quantity": 1}],
            "note": note,
            "tags": "TryOnYou,ZeroSize,PCT_EP2025_067317,Divineo",
        }
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": token,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError, ValueError):
        return None
    inv = data.get("draft_order", {}).get("invoice_url")
    return inv if isinstance(inv, str) and inv.startswith("http") else None


def build_shopify_perfect_selection_url(lead_id: int, fabric_sensation: str) -> str | None:
    """URL storefront / carrito piloto con atributos de sello (sin tallas)."""
    sensation = (fabric_sensation or "").strip()[:160]
    direct = os.environ.get("SHOPIFY_PERFECT_CHECKOUT_URL", "").strip()
    if direct:
        attrs = urllib.parse.urlencode(
            {
                "attributes[tryonyou_lead]": str(lead_id),
                "attributes[fit_sensation]": sensation[:80],
                "attributes[siren]": SIREN_SELL.replace(" ", ""),
                "attributes[patente]": PATENTE,
            }
        )
        sep = "&" if "?" in direct else "?"
        return f"{direct}{sep}{attrs}"

    domain = os.environ.get("SHOPIFY_STORE_DOMAIN", "").strip().rstrip("/")
    path = os.environ.get("SHOPIFY_PERFECT_PRODUCT_PATH", "/products/tryonyou-perfect-snap")
    path = path if path.startswith("/") else f"/{path}"
    if not domain:
        return None
    host = domain if domain.startswith("http") else f"https://{domain}"
    base = f"{host}{path}"
    q = urllib.parse.urlencode(
        {
            "utm_source": "tryonyou_v10",
            "utm_medium": "biometric_zero_size",
            "utm_campaign": f"lead_{lead_id}",
            "utm_content": PATENTE.replace("/", "_"),
        }
    )
    return f"{base}?{q}"


def resolve_shopify_checkout_url(lead_id: int, fabric_sensation: str) -> str | None:
    """Prioriza facturación Admin (draft invoice); si falla, URL storefront configurada."""
    inv = admin_draft_order_invoice_url(lead_id, fabric_sensation)
    if inv:
        return inv
    return build_shopify_perfect_selection_url(lead_id, fabric_sensation)
