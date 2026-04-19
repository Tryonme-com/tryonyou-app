"""
Consolidación de red TryOnYou — alineación dominio / API / front.

Este script es la «prueba de salud» entre:

- ``src/services/paymentService.ts`` — POST ``/api/stripe_inauguration_checkout`` (vía
  ``VITE_STRIPE_CHECKOUT_API_ORIGIN`` o mismo origen que el despliegue).
- ``master_fatality.py`` — lectura Stripe/Qonto local (opcional, requiere env).

Prompt maestro (pegar en chat Cursor al consolidar infra)
----------------------------------------------------------
Actúa como ingeniero senior de infraestructura. Misión: alinear extensión Cursor,
despliegue (p. ej. Vercel) y dominio ``tryonyou.app``. Tareas: (1) sincronizar URLs de
pago con este repo y comprobar CORS en rutas API; (2) auditar ``.env`` / ``.env.example``
sin volcar secretos — Stripe vía ``STRIPE_SECRET_KEY_FR``, webhooks
``STRIPE_WEBHOOK_SECRET_FR``, Google Studio vía ``GOOGLE_STUDIO_API_KEY``; (3) que los
agentes externos envíen ``Origin`` / cabeceras acordes al dominio principal; (4) ejecutar
``python3 infrastructure_sync.py`` antes de operación. Máxima seguridad: nunca claves
reales en código.

Ejecución::

  python3 infrastructure_sync.py
  python3 infrastructure_sync.py --base https://tryonyou.app
  python3 infrastructure_sync.py --fatality   # además: snapshot master_fatality (local)

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import httpx

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

_DEFAULT_UA = "TryOnYou-infrastructure-sync/1.0"


def _normalize_base(raw: str) -> str:
    u = (raw or "").strip().rstrip("/")
    if not u:
        return ""
    if not u.startswith(("http://", "https://")):
        u = "https://" + u.lstrip("/")
    return u


def resolve_public_base() -> str:
    """Prioridad: INFRA_SYNC_BASE_URL → TRYONYOU_PUBLIC_DOMAIN → tryonyou.app."""
    explicit = _normalize_base(os.environ.get("INFRA_SYNC_BASE_URL") or "")
    if explicit:
        return explicit
    domain = (os.environ.get("TRYONYOU_PUBLIC_DOMAIN") or "tryonyou.app").strip()
    return _normalize_base(domain) or "https://tryonyou.app"


def _cors_summary(headers: httpx.Headers) -> dict[str, str]:
    out: dict[str, str] = {}
    for key in (
        "access-control-allow-origin",
        "access-control-allow-methods",
        "access-control-allow-headers",
    ):
        v = headers.get(key)
        if v:
            out[key] = v
    return out


def probe_get(client: httpx.Client, url: str) -> dict[str, Any]:
    try:
        r = client.get(url, headers={"User-Agent": _DEFAULT_UA})
        body_preview = (r.text or "")[:400]
        return {
            "url": url,
            "status_code": r.status_code,
            "ok_http": 200 <= r.status_code < 300,
            "cors": _cors_summary(r.headers),
            "body_preview": body_preview if r.headers.get("content-type", "").startswith("application/json") else None,
        }
    except httpx.HTTPError as e:
        return {"url": url, "ok_http": False, "error": str(e)}
    except OSError as e:
        return {"url": url, "ok_http": False, "error": str(e)}


def probe_options_checkout(client: httpx.Client, base: str) -> dict[str, Any]:
    """Simula preflight CORS del navegador hacia inauguración (alineado con paymentService)."""
    url = f"{base}/api/stripe_inauguration_checkout"
    origin = _normalize_base(os.environ.get("GOOGLE_STUDIO_ALLOWED_ORIGIN") or base)
    try:
        r = client.request(
            "OPTIONS",
            url,
            headers={
                "User-Agent": _DEFAULT_UA,
                "Origin": origin,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            },
            timeout=20.0,
        )
        return {
            "url": url,
            "simulated_origin": origin,
            "status_code": r.status_code,
            "preflight_ok": r.status_code in (200, 204),
            "cors": _cors_summary(r.headers),
        }
    except (httpx.HTTPError, OSError) as e:
        return {"url": url, "preflight_ok": False, "error": str(e)}


def probe_post_checkout_no_body(client: httpx.Client, base: str) -> dict[str, Any]:
    """
    POST vacío como el front: puede devolver 200 + JSON, 4xx o 402 (FinancialGuard).
    Cualquier respuesta HTTP estructurada indica que el endpoint existe (no DNS rotos).
    """
    url = f"{base}/api/stripe_inauguration_checkout"
    origin = _normalize_base(os.environ.get("GOOGLE_STUDIO_ALLOWED_ORIGIN") or base)
    try:
        r = client.post(
            url,
            headers={
                "User-Agent": _DEFAULT_UA,
                "Origin": origin,
                "Content-Type": "application/json",
            },
            content="{}",
            timeout=25.0,
        )
        try:
            data = r.json()
        except json.JSONDecodeError:
            data = {"_raw": (r.text or "")[:300]}
        return {
            "url": url,
            "origin": origin,
            "status_code": r.status_code,
            "reachable": True,
            "json_keys": list(data.keys()) if isinstance(data, dict) else None,
            "payment_required": r.status_code == 402,
            "cors": _cors_summary(r.headers),
        }
    except (httpx.HTTPError, OSError) as e:
        return {"url": url, "reachable": False, "error": str(e)}


def run_sync(base: str, include_fatality: bool) -> dict[str, Any]:
    base = _normalize_base(base)
    report: dict[str, Any] = {
        "patent": "PCT/EP2025/067317",
        "base_url": base,
        "checks": {},
    }
    timeout = httpx.Timeout(25.0)
    with httpx.Client(timeout=timeout, follow_redirects=True) as client:
        report["checks"]["health"] = probe_get(client, f"{base}/api/health")
        report["checks"]["sovereignty_guard_status"] = probe_get(
            client, f"{base}/api/sovereignty_guard_status"
        )
        report["checks"]["stripe_inauguration_options"] = probe_options_checkout(client, base)
        report["checks"]["stripe_inauguration_post"] = probe_post_checkout_no_body(client, base)

    report["env_hints"] = {
        "front_api_origin": "VITE_STRIPE_CHECKOUT_API_ORIGIN (debe coincidir con el host que sirve /api/*)",
        "stripe_server": "STRIPE_SECRET_KEY_FR + STRIPE_WEBHOOK_SECRET_FR (servidor)",
        "google_studio": "GOOGLE_STUDIO_API_KEY (scripts / agentes; no volcar en repo)",
        "sync_base_override": "INFRA_SYNC_BASE_URL",
        "allowed_origin_doc": "GOOGLE_STUDIO_ALLOWED_ORIGIN (origen simulado en probes CORS)",
    }

    if include_fatality:
        try:
            from master_fatality import consolidate_report

            report["master_fatality_local"] = consolidate_report()
        except Exception as e:
            report["master_fatality_local"] = {"ok": False, "error": str(e)}

    # Resumen simple para CI
    h = report["checks"].get("health") or {}
    post = report["checks"].get("stripe_inauguration_post") or {}
    opt = report["checks"].get("stripe_inauguration_options") or {}
    report["summary"] = {
        "health_ok": bool(h.get("ok_http")),
        "checkout_reachable": bool(post.get("reachable")),
        "cors_preflight": bool(opt.get("preflight_ok")),
        "liquidity_block_402_on_checkout": bool(post.get("payment_required")),
    }
    return report


def main() -> int:
    ap = argparse.ArgumentParser(description="Ping de infraestructura TryOnYou (dominio + API).")
    ap.add_argument(
        "--base",
        default="",
        help="URL base (default: INFRA_SYNC_BASE_URL o TRYONYOU_PUBLIC_DOMAIN)",
    )
    ap.add_argument(
        "--fatality",
        action="store_true",
        help="Incluir consolidate_report() de master_fatality.py (requiere env local)",
    )
    args = ap.parse_args()
    base = _normalize_base(args.base) if args.base else resolve_public_base()
    out = run_sync(base, include_fatality=args.fatality)
    print(json.dumps(out, indent=2, ensure_ascii=False))
    s = out.get("summary") or {}
    ok = bool(s.get("health_ok") and s.get("checkout_reachable") and s.get("cors_preflight"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
