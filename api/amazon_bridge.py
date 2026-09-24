"""
Amazon Bridge — Agente 27 (GL-M/GL-F → ASIN + capa SP-API LWA, Zero-Size).

- AMAZON_GL_CATALOG_MAP_JSON: catálogo Lafayette interno → ASIN (sin tallas al cliente).

- LWA (Login with Amazon): SP_API_LWA_CLIENT_ID, SP_API_LWA_CLIENT_SECRET,
  SP_API_REFRESH_TOKEN. Si hay access_token válido y AMAZON_SP_API_RESOLVED_ASIN
  está definido (sync/batch con firma AWS fuera del runtime mínimo), se prioriza.

- Las llamadas Catalog Items firmadas (SigV4) no están en este módulo serverless
  mínimo; el mapa JSON + ASIN piloto cubre producción inmediata.

No exponer pesos, tallas (S/M/L) ni medidas en query pública: solo lead_id,
sello SIREN/patente y sensación corta emocional.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request

SIREN_SELL = "943 610 196"
PATENTE = "PCT/EP2025/067317"


def _catalog_map() -> dict[str, str]:
    raw = os.environ.get("AMAZON_GL_CATALOG_MAP_JSON", "").strip()
    if not raw:
        return {}
    try:
        m = json.loads(raw)
        return m if isinstance(m, dict) else {}
    except json.JSONDecodeError:
        return {}


def sp_api_lwa_access_token() -> str | None:
    """Intercambio refresh_token → access_token (capa SP-API)."""
    cid = os.environ.get("SP_API_LWA_CLIENT_ID", "").strip()
    secret = os.environ.get("SP_API_LWA_CLIENT_SECRET", "").strip()
    refresh = os.environ.get("SP_API_REFRESH_TOKEN", "").strip()
    if not cid or not secret or not refresh:
        return None
    body = urllib.parse.urlencode(
        {
            "grant_type": "refresh_token",
            "refresh_token": refresh,
            "client_id": cid,
            "client_secret": secret,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        "https://api.amazon.com/auth/o2/token",
        data=body,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        tok = data.get("access_token")
        return str(tok).strip() if tok else None
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError, ValueError):
        return None


def resolve_lafayette_asin(fabric_sensation: str) -> str:
    """Silhouette V10 → ASIN real (mapa GL / capa SP opcional / piloto)."""
    forced = os.environ.get("AMAZON_SP_API_RESOLVED_ASIN", "").strip()
    if forced and os.environ.get("SP_API_REFRESH_TOKEN", "").strip():
        if sp_api_lwa_access_token():
            return forced

    sensation = (fabric_sensation or "").strip().lower()
    m = _catalog_map()
    default = (m.get("default") or m.get("unisex") or "").strip()
    gl_m = (m.get("GL_M") or m.get("mens") or m.get("homme") or "").strip()
    gl_f = (m.get("GL_F") or m.get("womens") or m.get("femme") or "").strip()

    if any(k in sensation for k in ("homme", "mens", "gl-m", "gl_m")) and gl_m:
        return gl_m
    if any(k in sensation for k in ("femme", "womens", "gl-f", "gl_f")) and gl_f:
        return gl_f
    if default:
        return default
    return os.environ.get("AMAZON_PERFECT_ASIN", "").strip()


def build_amazon_offering_url(lead_id: int, fabric_sensation: str) -> str | None:
    asin = resolve_lafayette_asin(fabric_sensation)
    if not asin:
        return None
    host = os.environ.get("AMAZON_MARKETPLACE_DOMAIN", "www.amazon.fr").strip().lstrip(".")
    if "://" in host:
        host = host.split("://", 1)[-1].split("/")[0]
    tag = os.environ.get("AMAZON_ASSOCIATE_TAG", "").strip()
    params = {
        "siren": SIREN_SELL.replace(" ", ""),
        "patente": PATENTE,
        "lead_id": str(lead_id),
        "fit": fabric_sensation[:48].strip(),
    }
    if tag:
        params["tag"] = tag
    q = urllib.parse.urlencode(params)
    return f"https://{host}/dp/{asin}/?{q}"


def resolve_amazon_checkout_url(lead_id: int, fabric_sensation: str) -> str | None:
    return build_amazon_offering_url(lead_id, fabric_sensation)
