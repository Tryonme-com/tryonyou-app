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


def _shopify_admin_host() -> str:
    """
    Host exclusivo Admin API (*.myshopify.com).
    Si storefront usa dominio público, define SHOPIFY_MYSHOPIFY_HOST=tienda.myshopify.com
    """
    raw = os.environ.get("SHOPIFY_MYSHOPIFY_HOST", "").strip()
    if raw:
        return raw.replace("https://", "").replace("http://", "").split("/")[0]
    h = _shopify_host()
    return h


def admin_draft_order_invoice_url(lead_id: int, fabric_sensation: str) -> str | None:
    """POST /admin/api/{ver}/draft_orders.json → invoice_url si credenciales válidas."""
    token = os.environ.get("SHOPIFY_ADMIN_ACCESS_TOKEN", "").strip()
    host = _shopify_admin_host()
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
        f"ajustage Zero-Size · ANTI-ACCUMULATION (qty=1, single_size) · QC 27 Rue Argenteuil 75001 · "
        f"{sensation}"
    )
    body = {
        "draft_order": {
            "line_items": [{"variant_id": int(variant_raw), "quantity": 1}],
            "note": note,
            "tags": (
                "TryOnYou,ZeroSize,PCT_EP2025_067317,Divineo,"
                "AntiAccumulation,SingleSizeCertitude"
            ),
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


class ShopifyBridge:
    """
    Puente de integración Robert Engine → Shopify para el flujo de venta soberana.

    Sincroniza los datos de Fit calculados por el motor Robert con la orden
    correspondiente en Shopify (draft order o checkout storefront).
    """

    def sync_robert_to_shopify(
        self, fabric_key: str, fit_data: dict
    ) -> dict:
        """
        Prepara y registra una orden Shopify a partir del Fit del motor Robert.

        Args:
            fabric_key: Identificador de la prenda/tejido.
            fit_data:   Datos de Fit producidos por RobertEngine
                        (debe incluir al menos «fitScore»).

        Returns:
            Diccionario con el estado de la orden:
              - status       : «DRAFT_CREATED» | «CHECKOUT_URL» | «PENDING»
              - fabric_key   : clave de prenda enviada
              - fit_score    : puntuación de ajuste recibida
              - shopify_ref  : invoice_url o checkout URL (o None si no disponible)
              - legal        : sello legal / patente
        """
        fit_score = float((fit_data or {}).get("fitScore", 0))
        lead_id = abs(hash(str(fabric_key))) % 10_000_000

        # Prioridad 1: draft invoice (Admin API) → DRAFT_CREATED
        # Prioridad 2: storefront checkout URL → CHECKOUT_URL
        # Sin credenciales configuradas → PENDING
        shopify_ref = admin_draft_order_invoice_url(lead_id, str(fabric_key)[:120])
        if shopify_ref:
            status = "DRAFT_CREATED"
        else:
            shopify_ref = build_shopify_perfect_selection_url(lead_id, str(fabric_key)[:120])
            status = "CHECKOUT_URL" if shopify_ref else "PENDING"

        return {
            "status": status,
            "fabric_key": fabric_key,
            "fit_score": fit_score,
            "shopify_ref": shopify_ref,
            "legal": f"SIREN {SIREN_SELL} · {PATENTE}",
        }
