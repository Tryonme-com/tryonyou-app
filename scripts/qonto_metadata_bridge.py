#!/usr/bin/env python3
"""
Metadata Bridge — facturas cliente Qonto importadas (borrador) → datos obligatorios.

Rellena vía API (PATCH /v2/client_invoices/{id}) campos típicos que faltan en
«Importada — Faltan datos»: fecha de vencimiento, cabecera/pie con proveedor y
categoría, e IVA en líneas cuando el borrador lo permite.

Requisitos:
  - QONTO_API_KEY (misma cabecera Authorization que usa api/core_engine.py).
  - Alcance API: client_invoices.read + client_invoice.write.

Variables opcionales:
  QONTO_BRIDGE_SUPPLIER_LABEL=TRYONYOU
  QONTO_BRIDGE_CATEGORY_LABEL=Software/Lujo
  QONTO_BRIDGE_DUE_DATE=2026-06-30
  QONTO_BRIDGE_VAT_RATE=20   (porcentaje FR estándar; string en payload Qonto)
  QONTO_BRIDGE_CLIENT_INVOICE_IDS=id1,id2   (si se omite, lista borradores importados)

Uso:
  python3 scripts/qonto_metadata_bridge.py --dry-run
  python3 scripts/qonto_metadata_bridge.py

Patente: PCT/EP2025/067317 — Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

try:
    import requests
except ImportError as e:
    print("Instala requests: pip install requests", file=sys.stderr)
    raise SystemExit(1) from e

BASE = "https://thirdparty.qonto.com"


def _env(name: str, default: str = "") -> str:
    return (os.getenv(name) or default).strip()


def _auth_headers() -> dict[str, str]:
    token = _env("QONTO_API_KEY") or _env("QONTO_AUTHORIZATION_KEY")
    if not token:
        print("Falta QONTO_API_KEY (o QONTO_AUTHORIZATION_KEY).", file=sys.stderr)
        raise SystemExit(2)
    return {
        "Authorization": token,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def _list_draft_imported_invoices(session: requests.Session) -> list[dict[str, Any]]:
    """Lista borradores incluyendo importados (exclude_imported=false)."""
    params: dict[str, str | bool | int] = {
        "exclude_imported": False,
        "filter[status]": "draft",
        "per_page": 100,
        "page": 1,
    }
    r = session.get(f"{BASE}/v2/client_invoices", params=params, timeout=60)
    r.raise_for_status()
    data = r.json()
    rows = data.get("client_invoices")
    return rows if isinstance(rows, list) else []


def _get_invoice(session: requests.Session, inv_id: str) -> dict[str, Any]:
    r = session.get(f"{BASE}/v2/client_invoices/{inv_id}", timeout=60)
    r.raise_for_status()
    body = r.json()
    ci = body.get("client_invoice")
    return ci if isinstance(ci, dict) else {}


def _build_patch_body(
    invoice: dict[str, Any],
    *,
    supplier: str,
    category: str,
    due_date: str,
    vat_rate: str,
) -> dict[str, Any]:
    header = (
        f"Proveedor: {supplier} | Catégorie: {category} | Réf. contrat: "
        f"{_env('QONTO_CONTRACT_REFERENCE', 'DIVINEO-V10-PCT2025-067317')}"
    )
    footer = (
        f"TryOnYou — F-2026-001 | TVA article: {vat_rate}% (logiciel / luxe). "
        "Métadonnées injectées via scripts/qonto_metadata_bridge.py"
    )
    existing_h = str(invoice.get("header") or "").strip()
    merged_header = f"{existing_h} | {header}" if existing_h else header
    payload: dict[str, Any] = {
        "due_date": due_date,
        "header": merged_header[:500],
        "footer": footer[:525],
    }
    items = invoice.get("items")
    if isinstance(items, list) and items:
        new_items: list[dict[str, Any]] = []
        for it in items:
            if not isinstance(it, dict):
                continue
            row = dict(it)
            if not str(row.get("vat_rate") or "").strip():
                row["vat_rate"] = vat_rate
            if not str(row.get("title") or "").strip():
                row["title"] = (category or "Prestation")[:40]
            new_items.append(row)
        payload["items"] = new_items
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Qonto client invoice metadata bridge")
    parser.add_argument("--dry-run", action="store_true", help="Solo listar IDs, sin PATCH")
    args = parser.parse_args()

    supplier = _env("QONTO_BRIDGE_SUPPLIER_LABEL", "TRYONYOU")
    category = _env("QONTO_BRIDGE_CATEGORY_LABEL", "Software/Lujo")
    due_date = _env("QONTO_BRIDGE_DUE_DATE", "2026-06-30")
    vat_rate = _env("QONTO_BRIDGE_VAT_RATE", "20")

    session = requests.Session()
    session.headers.update(_auth_headers())

    explicit = _env("QONTO_BRIDGE_CLIENT_INVOICE_IDS")
    if explicit:
        ids = [x.strip() for x in explicit.split(",") if x.strip()]
    else:
        rows = _list_draft_imported_invoices(session)
        ids = [str(r.get("id") or "").strip() for r in rows if r.get("id")]

    if not ids:
        print(json.dumps({"ok": False, "message": "no_client_invoice_candidates"}, indent=2))
        return 3

    results: list[dict[str, Any]] = []
    for inv_id in ids:
        if args.dry_run:
            results.append({"id": inv_id, "dry_run": True})
            continue
        inv = _get_invoice(session, inv_id)
        if str(inv.get("status") or "").lower() != "draft":
            results.append(
                {
                    "id": inv_id,
                    "skipped": True,
                    "reason": "not_draft_only_patch_supported",
                    "status": inv.get("status"),
                }
            )
            continue
        body = _build_patch_body(inv, supplier=supplier, category=category, due_date=due_date, vat_rate=vat_rate)
        pr = session.patch(f"{BASE}/v2/client_invoices/{inv_id}", data=json.dumps(body), timeout=90)
        try:
            out = pr.json()
        except ValueError:
            out = {"raw": pr.text[:500]}
        results.append(
            {
                "id": inv_id,
                "http_status": pr.status_code,
                "ok": pr.status_code == 200,
                "response": out,
            }
        )

    summary = {
        "ok": all(r.get("ok") for r in results if "ok" in r),
        "count": len(results),
        "dry_run": args.dry_run,
        "results": results,
        "hint": (
            "Tras PATCH, valide las facturas en la app Qonto para pasar a «unpaid» "
            "si el flujo lo requiere (solo borradores son actualizables por API)."
        ),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["ok"] or args.dry_run else 1


if __name__ == "__main__":
    repo = Path(__file__).resolve().parents[1]
    # Carga .env local si existe (no versionado).
    env_file = repo / ".env"
    if env_file.is_file():
        for line in env_file.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            k, v = k.strip(), v.strip().strip('"').strip("'")
            if k and k not in os.environ:
                os.environ[k] = v
    raise SystemExit(main())
