"""
Genera OFFRE_COMPLIANCE_LUXE.json (metadatos de oferta; no es documento legal).

- Raíz: E50_PROJECT_ROOT (por defecto ~/Projects/22TRYONYOU).
- JSON UTF-8, ensure_ascii=False, fecha UTC opcional en el objeto.

Ejecutar: python3 generar_oferta_cumplimiento.py
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.abspath(
    os.environ.get("E50_PROJECT_ROOT", os.path.expanduser("~/Projects/22TRYONYOU"))
)


def generar_oferta_cumplimiento() -> int:
    print("⚖️ Paso 26: Generando oferta de cumplimiento (JSON metadatos)...")

    os.makedirs(ROOT, exist_ok=True)
    os.chdir(ROOT)

    oferta = {
        "asunto": "Regularización de Licencia - Tecnología Biométrica TryOnYou",
        "canon_entrada": "98.000 € (Pago único)",
        "licencia_mensual": "9.900 € / mes por terminal",
        "royalty_ventas": "5% sobre transacciones validadas",
        "validez": "15 días naturales",
        "nota": "Esta oferta evita el inicio de acciones legales por infracción de propiedad intelectual.",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    rel = os.path.join("src", "data", "OFFRE_COMPLIANCE_LUXE.json")
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(oferta, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"✅ {rel}")
    print("ℹ️  Es un archivo de datos en el repo; el cierre legal lo firma un abogado en el formato oficial.")
    return 0


if __name__ == "__main__":
    sys.exit(generar_oferta_cumplimiento())
