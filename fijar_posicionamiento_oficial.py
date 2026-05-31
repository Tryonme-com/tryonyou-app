"""
Escribe src/data/brand_position.ts (manifesto de posicionamiento).

- Raíz: E50_PROJECT_ROOT (por defecto ~/Projects/22TRYONYOU).

Ejecutar: python3 fijar_posicionamiento_oficial.py
"""

from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(
    os.environ.get("E50_PROJECT_ROOT", os.path.expanduser("~/Projects/22TRYONYOU"))
)

BRAND_POSITION_TS = """/**
 * Copy de marca; revisar con legal/compliance antes de uso público amplio.
 */
export const BrandPosition = {
  statement:
    "TryOnYou n'est pas une application, c'est une infrastructure de précision.",
  philosophy:
    "Le luxe ne tolère pas l'approximation. Nous transformons la biométrie en certitude d'achat.",
  legal_status:
    "Propriété intellectuelle protégée. Licence d'exploitation requise pour toute intégration retail.",
  message_to_market:
    "Si vous vendez du prestige, ne l'affichez pas avec des filtres 2D. Utilisez la physique.",
} as const;

export type BrandPositionManifest = typeof BrandPosition;
"""


def fijar_posicionamiento_oficial() -> int:
    print("🚀 Paso 28: Fijando posicionamiento de autoridad...")

    os.makedirs(ROOT, exist_ok=True)
    os.chdir(ROOT)

    data_dir = os.path.join(ROOT, "src", "data")
    os.makedirs(data_dir, exist_ok=True)
    path = os.path.join(data_dir, "brand_position.ts")
    with open(path, "w", encoding="utf-8") as f:
        f.write(BRAND_POSITION_TS)

    print(f"✅ {os.path.relpath(path, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(fijar_posicionamiento_oficial())
