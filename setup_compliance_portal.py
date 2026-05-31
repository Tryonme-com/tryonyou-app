"""
Escribe src/components/ComplianceSection.tsx bajo el proyecto (UI; no es aviso legal).

- Raíz: E50_PROJECT_ROOT (por defecto ~/Projects/22TRYONYOU).

Ejecutar: python3 setup_compliance_portal.py
"""

from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(
    os.environ.get("E50_PROJECT_ROOT", os.path.expanduser("~/Projects/22TRYONYOU"))
)

COMPLIANCE_TSX = """/**
 * Texto de interfaz de demostración. No sustituye asesoramiento legal ni un acto procesal.
 */
import React from 'react';

export const ComplianceSection = () => {
  return (
    <div className="bg-red-950 text-white p-12 border-t-4 border-red-600">
      <h2 className="text-3xl font-serif mb-6 uppercase tracking-tighter">Avis d&apos;Infraction de Brevet</h2>
      <p className="mb-8 text-lg text-gray-300">
        Si votre système utilise la biométrie pour l&apos;ajustement de vêtements sans licence TryOnYou,
        vous êtes en violation de la propriété intellectuelle déposée.
      </p>
      <div className="bg-black p-8 border border-red-800">
        <h3 className="text-xl font-bold mb-4">RÉGULARISATION IMMÉDIATE</h3>
        <ul className="space-y-4 mb-8">
          <li>• Canon de Licence: <strong>98.000 €</strong></li>
          <li>• Maintenance Systèmes: <strong>100 € / mois</strong></li>
          <li>• Protection Juridique Incluse</li>
        </ul>
        <button type="button" className="w-full bg-red-600 hover:bg-red-700 py-4 font-black uppercase">
          Régulariser ma Licence
        </button>
      </div>
    </div>
  );
};
"""


def setup_compliance_portal() -> int:
    print("⚖️ Paso 27: Configurando el Portal de Cumplimiento (componente React)...")

    os.makedirs(ROOT, exist_ok=True)
    os.chdir(ROOT)

    comp = os.path.join(ROOT, "src", "components")
    os.makedirs(comp, exist_ok=True)
    path = os.path.join(comp, "ComplianceSection.tsx")
    with open(path, "w", encoding="utf-8") as f:
        f.write(COMPLIANCE_TSX)

    print(f"✅ {os.path.relpath(path, ROOT)}")
    print("ℹ️  Importa <ComplianceSection /> donde quieras mostrarlo (p. ej. App o una ruta /compliance).")
    return 0


if __name__ == "__main__":
    sys.exit(setup_compliance_portal())
