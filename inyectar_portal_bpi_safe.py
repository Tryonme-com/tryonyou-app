"""
Escribe src/components/BpiAdminPortal.tsx (maqueta UI estilo dossier; no es envío real a Bpifrance).

Git opcional y acotado (solo ese archivo).

- Raíz: E50_PROJECT_ROOT (por defecto ~/Projects/22TRYONYOU).
- E50_GIT_PUSH=1, E50_FORCE_PUSH=1 opcional.

Ejecutar: python3 inyectar_portal_bpi_safe.py
"""

from __future__ import annotations

import os
import subprocess
import sys

ROOT = os.path.abspath(
    os.environ.get("E50_PROJECT_ROOT", os.path.expanduser("~/Projects/22TRYONYOU"))
)

BPI_PORTAL_TSX = """import React from "react";

/**
 * Maquette UI uniquement. Les statuts affichés ne valent pas dossier Bpifrance ni PI.
 */
export function BpiAdminPortal() {
  return (
    <div className="p-10 bg-white text-blue-900 font-sans border-4 border-blue-900">
      <h1 className="text-3xl font-black italic">BPIFRANCE - DOSSIER INNOVATION</h1>
      <p className="mt-4">
        Statut : <strong>PRÊT POUR SOUMISSION</strong>{" "}
        <span className="text-sm font-normal text-gray-600">(démo)</span>
      </p>
      <div className="mt-6 bg-gray-100 p-4 border border-blue-300">
        <p>
          Certificat de Brevet : <strong>À REMPLACER PAR VOS PIÈCES</strong>
        </p>
        <p>
          Impact Carbone : <strong>INDICATEUR PLACEHOLDER</strong>
        </p>
      </div>
      <p className="mt-4 text-xs text-gray-500 max-w-xl">
        Cette interface ne transmet rien à Bpifrance. Reliez le bouton à votre
        flux documentaire / contact officiel.
      </p>
      <button
        type="button"
        className="mt-6 bg-blue-900 text-white py-4 px-8 font-bold hover:bg-blue-700"
      >
        ENVOYER À BPIFRANCE
      </button>
    </div>
  );
}
"""

GIT_PATHS = [
    "src/components/BpiAdminPortal.tsx",
]


def _run(argv: list[str], *, cwd: str) -> int:
    try:
        return subprocess.run(argv, cwd=cwd, check=False).returncode
    except OSError as e:
        print(f"❌ {e}")
        return 1


def _on(x: str) -> bool:
    return os.environ.get(x, "").strip().lower() in ("1", "true", "yes", "on")


def inyectar_portal_bpi_safe() -> int:
    print("🚀 Paso 49: Sincronizando maqueta portal Bpifrance (modo seguro)...")

    os.makedirs(ROOT, exist_ok=True)
    os.chdir(ROOT)

    comp = os.path.join(ROOT, "src", "components")
    os.makedirs(comp, exist_ok=True)
    path = os.path.join(comp, "BpiAdminPortal.tsx")
    with open(path, "w", encoding="utf-8") as f:
        f.write(BPI_PORTAL_TSX)

    print(f"✅ {os.path.relpath(path, ROOT)}")

    if not _on("E50_GIT_PUSH"):
        print("ℹ️  Sin E50_GIT_PUSH=1 no se ejecuta git.")
        return 0

    if not os.path.isdir(os.path.join(ROOT, ".git")):
        print("ℹ️  No hay .git en ROOT.")
        return 0

    exist = [p for p in GIT_PATHS if os.path.exists(os.path.join(ROOT, p))]
    if not exist:
        return 1

    if _on("E50_GIT_AUTOCRLF"):
        _run(["git", "config", "core.autocrlf", "false"], cwd=ROOT)

    if _run(["git", "add", *exist], cwd=ROOT) != 0:
        print("❌ git add falló")
        return 1

    rc = _run(
        [
            "git",
            "commit",
            "-m",
            "LEGAL: Bpifrance submission module ready",
        ],
        cwd=ROOT,
    )
    if rc not in (0, 1):
        print("❌ git commit falló")
        return 1

    cmd = ["git", "push", "origin", "main"]
    if _on("E50_FORCE_PUSH"):
        cmd.append("--force")
    if _run(cmd, cwd=ROOT) != 0:
        print("❌ git push falló")
        return 1

    print("\n🔥 Push completado.")
    return 0


if __name__ == "__main__":
    sys.exit(inyectar_portal_bpi_safe())
