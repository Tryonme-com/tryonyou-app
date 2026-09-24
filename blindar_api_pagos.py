"""
Fusiona cabeceras de seguridad en vercel.json sin borrar builds/routes existentes.

- HSTS en rutas /api/*
- CORS solo si defines E50_CORS_ALLOW_ORIGIN (origen concreto; no uses * en pagos reales).

No añade rewrites a archivos inexistentes (tu API actual es Python en api/index.py).

- Raíz: E50_PROJECT_ROOT (por defecto ~/Projects/22TRYONYOU).

Ejecutar: python3 blindar_api_pagos.py
"""

from __future__ import annotations

import json
import os
import sys

ROOT = os.path.abspath(
    os.environ.get("E50_PROJECT_ROOT", os.path.expanduser("~/Projects/22TRYONYOU"))
)

API_SOURCE = "/api/(.*)"


def _api_header_block(cors_origin: str | None) -> dict:
    hdrs: list[dict[str, str]] = [
        {
            "key": "Strict-Transport-Security",
            "value": "max-age=63072000; includeSubDomains; preload",
        },
    ]
    if cors_origin:
        hdrs.insert(
            0,
            {"key": "Access-Control-Allow-Origin", "value": cors_origin},
        )
    return {"source": API_SOURCE, "headers": hdrs}


def blindar_api_pagos() -> int:
    print("🔒 Paso 43: Blindando cabeceras de API en vercel.json (merge)...")

    os.makedirs(ROOT, exist_ok=True)
    os.chdir(ROOT)

    path = os.path.join(ROOT, "vercel.json")
    if not os.path.isfile(path):
        print(f"❌ No existe {path}")
        return 1

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    cors = os.environ.get("E50_CORS_ALLOW_ORIGIN", "").strip() or None
    if not cors:
        print(
            "ℹ️  Sin E50_CORS_ALLOW_ORIGIN: no se añade Access-Control-Allow-Origin "
            "(recomendado: un origen fijo, p. ej. https://tu-dominio.com)."
        )

    block = _api_header_block(cors)
    headers = data.get("headers")
    if not isinstance(headers, list):
        headers = []

    replaced = False
    out_headers: list[dict] = []
    for h in headers:
        if isinstance(h, dict) and h.get("source") == API_SOURCE:
            out_headers.append(block)
            replaced = True
        else:
            out_headers.append(h)
    if not replaced:
        out_headers.append(block)

    data["headers"] = out_headers

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"✅ {os.path.relpath(path, ROOT)} (HSTS en {API_SOURCE})")
    print(
        "ℹ️  El checkout debe vivir en tu stack (p. ej. otra función serverless); "
        "no se ha tocado builds/routes."
    )
    return 0


if __name__ == "__main__":
    sys.exit(blindar_api_pagos())
