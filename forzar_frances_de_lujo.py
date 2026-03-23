"""
Escribe src/locales/fr_luxe.ts (copy UI piloto Lafayette, francés luxe).

- Raíz: E50_PROJECT_ROOT (por defecto ~/Projects/22TRYONYOU).

Ejecutar: python3 forzar_frances_de_lujo.py
"""

from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(
    os.environ.get("E50_PROJECT_ROOT", os.path.expanduser("~/Projects/22TRYONYOU"))
)

FR_LUXE_TS = """/**
 * Cadenas UI Lafayette (FR); revisar con producto/legal antes de producción.
 */
export const LafayetteUI = {
  header: {
    title: "Le Miroir Digital TryOnYou",
    subtitle: "Précision Biométrique. Zéro Retour.",
  },
  pilot_buttons: {
    selection: "Ma Sélection Parfaite",
    reserve: "Réserver en Cabine (QR Code)",
    combinations: "Voir Combinaisons Alternative",
    save: "Sauvegarder ma Silhouette",
    share: "Partager mon Look",
  },
  pricing: {
    enterprise: "Licence d'Implantation - 98.000 €",
    maintenance: "Support et Maintenance - 100 € / mois",
  },
  messages: {
    scanning: "Analyse de la physique du tissu en cours...",
    success: "Ajustement invisible validé. Prêt pour l'essayage.",
  },
} as const;

export type LafayetteUILocale = typeof LafayetteUI;
"""


def forzar_frances_de_lujo() -> int:
    print("🇫🇷 Paso 42: Blindando la interfaz en francés de alta gama...")

    os.makedirs(ROOT, exist_ok=True)
    os.chdir(ROOT)

    loc = os.path.join(ROOT, "src", "locales")
    os.makedirs(loc, exist_ok=True)
    path = os.path.join(loc, "fr_luxe.ts")
    with open(path, "w", encoding="utf-8") as f:
        f.write(FR_LUXE_TS)
    print(f"✅ {os.path.relpath(path, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(forzar_frances_de_lujo())
