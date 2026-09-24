"""
Genera invoice_98k.json (metadatos de factura 98.000 EUR) bajo el proyecto.

- Raíz: E50_PROJECT_ROOT (por defecto ~/Projects/22TRYONYOU).
- JSON UTF-8, ensure_ascii=False.

Ejecutar: python3 generar_invoice_98k.py
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.abspath(
    os.environ.get("E50_PROJECT_ROOT", os.path.expanduser("~/Projects/22TRYONYOU"))
)


def generar_invoice_98k() -> int:
    print("💼 Paso 17: generando factura de implantación (98.000€)...")

    os.makedirs(ROOT, exist_ok=True)
    os.chdir(ROOT)

    invoice_data = {
        "concept": "Initial Set-up & Invisible Adjustment Algorithm License",
        "client": "Luxury Brand Group (LVMH/Balmain)",
        "amount": 98000,
        "currency": "EUR",
        "terms": "Net 30",
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "status": "PENDING_SIGNATURE",
    }

    rel = os.path.join("src", "data", "contracts", "invoice_98k.json")
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(invoice_data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"✅ {rel}")
    return 0


if __name__ == "__main__":
    sys.exit(generar_invoice_98k())
