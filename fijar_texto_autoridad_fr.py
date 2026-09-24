"""
Escribe src/data/authority_fr.ts (copy autoridad FR para el frontend).

- Raíz: E50_PROJECT_ROOT (por defecto ~/Projects/22TRYONYOU).

Ejecutar: python3 fijar_texto_autoridad_fr.py
"""

from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(
    os.environ.get("E50_PROJECT_ROOT", os.path.expanduser("~/Projects/22TRYONYOU"))
)

AUTHORITY_FR_TS = """/**
 * Copy de marca (FR); validar con legal/compliance antes de uso amplio.
 */
export const AuthorityFR = {
  title: "L'Infrastructure de Précision TryOnYou",
  concept:
    "Nous ne vendons pas des vêtements, nous vendons la certitude physique du Double Numérique.",
  why_us:
    "Alors que le marché tâtonne avec la 2D, notre algorithme impose la réalité biométrique.",
  cta_enterprise:
    "Demander une licence d'exploitation - 98.000 € (Implantation et Certification)",
} as const;

export type AuthorityFRManifest = typeof AuthorityFR;
"""


def fijar_texto_autoridad_fr() -> int:
    print("🇫🇷 Paso 31: Inyectando autoridad francesa en el búnker...")

    os.makedirs(ROOT, exist_ok=True)
    os.chdir(ROOT)

    data_dir = os.path.join(ROOT, "src", "data")
    os.makedirs(data_dir, exist_ok=True)
    path = os.path.join(data_dir, "authority_fr.ts")
    with open(path, "w", encoding="utf-8") as f:
        f.write(AUTHORITY_FR_TS)

    print(f"✅ {os.path.relpath(path, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(fijar_texto_autoridad_fr())
