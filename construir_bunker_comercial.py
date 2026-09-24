"""
Construye pricing.json + LicenceGuard.tsx + patent_guard.ts; opcionalmente git acotado.

- Raíz: E50_PROJECT_ROOT (por defecto ~/Projects/22TRYONYOU).
- Ajusta engines.node en package.json (>=20.0.0) sin sed frágil.
- Git: E50_GIT_PUSH=1, rutas explícitas, sin .env; E50_FORCE_PUSH=1 para --force.

Ejecutar: python3 construir_bunker_comercial.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

ROOT = os.path.abspath(
    os.environ.get("E50_PROJECT_ROOT", os.path.expanduser("~/Projects/22TRYONYOU"))
)

PRICING_LOGIC = {
    "LICENCE_ENTRY": {
        "name": "Licence d'Implantation Luxe",
        "amount": 98000,
        "required": True,
        "type": "ONE_TIME",
    },
    "MAINTENANCE": {
        "name": "Support & Cloud SaaS",
        "amount": 100,
        "required_licence": "LICENCE_ENTRY",
        "type": "MONTHLY",
    },
}

# Resumen numérico (equivalente útil al pricing_logic.json del bash)
PRICING_FLAT = {
    "LICENCE_ENTRY": 98000,
    "MAINTENANCE_MONTHLY": 100,
    "ROYALTY_PERCENTAGE": 0.05,
    "CURRENCY": "EUR",
    "STATUS": "CONFIG_LOCAL",
}

LICENCE_GUARD_TSX = """/**
 * UI: licencePaid debe venir del backend / webhooks Stripe, no confiar solo en el cliente.
 */
import type { ReactNode } from 'react';

type Props = { licencePaid: boolean; children: ReactNode };

export function LicenceGuard({ licencePaid, children }: Props) {
  if (!licencePaid) {
    return (
      <div className="bg-red-950 text-white p-10 border-2 border-red-600 rounded-lg">
        <h2 className="text-3xl font-black mb-4">ACCÈS RESTREINT</h2>
        <p className="text-xl mb-6">Votre licence de 98.000€ n&apos;est pas activée.</p>
        <button
          type="button"
          className="bg-red-600 px-8 py-3 font-bold uppercase hover:bg-red-700 transition"
        >
          Régulariser ma Licence (98.000€)
        </button>
      </div>
    );
  }
  return <>{children}</>;
}
"""

PATENT_GUARD_TS = """/**
 * Metadatos de flujo; la autorización real debe validarse en servidor.
 */
export const PATENT_ACCESS_DENIED = "ACCÈS REFUSÉ: Licence de 98.000€ requise.";

export function checkPatentAccess(hasPaid98k: boolean): string {
  if (!hasPaid98k) return "DENIED";
  return "ACCESS_GRANTED_MAINTENANCE_100_ACTIVE";
}
"""

GIT_PATHS = [
    "package.json",
    "package-lock.json",
    ".gitignore",
    ".env.example",
    "vercel.json",
    "src/config/pricing.json",
    "src/config/pricing_logic.json",
    "src/components/LicenceGuard.tsx",
    "src/lib/patent_guard.ts",
]


def _run(argv: list[str], *, cwd: str) -> int:
    try:
        return subprocess.run(argv, cwd=cwd, check=False).returncode
    except OSError as e:
        print(f"❌ {e}")
        return 1


def _on(x: str) -> bool:
    return os.environ.get(x, "").strip().lower() in ("1", "true", "yes", "on")


def construir_bunker_comercial() -> int:
    print("🏗️  Construcción del búnker comercial (archivos + motores Node)...")

    os.makedirs(ROOT, exist_ok=True)
    os.chdir(ROOT)

    pkg = os.path.join(ROOT, "package.json")
    if os.path.isfile(pkg):
        with open(pkg, encoding="utf-8") as f:
            data = json.load(f)
        if "engines" not in data or not isinstance(data.get("engines"), dict):
            data["engines"] = {}
        data["engines"]["node"] = ">=20.0.0"
        with open(pkg, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print("✅ package.json → engines.node >=20.0.0")

    cfg = os.path.join(ROOT, "src", "config")
    os.makedirs(cfg, exist_ok=True)
    p1 = os.path.join(cfg, "pricing.json")
    with open(p1, "w", encoding="utf-8") as f:
        json.dump(PRICING_LOGIC, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("✅ src/config/pricing.json")

    p2 = os.path.join(cfg, "pricing_logic.json")
    with open(p2, "w", encoding="utf-8") as f:
        json.dump(PRICING_FLAT, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("✅ src/config/pricing_logic.json")

    comp = os.path.join(ROOT, "src", "components")
    os.makedirs(comp, exist_ok=True)
    lg = os.path.join(comp, "LicenceGuard.tsx")
    with open(lg, "w", encoding="utf-8") as f:
        f.write(LICENCE_GUARD_TSX)
    print("✅ src/components/LicenceGuard.tsx")

    lib = os.path.join(ROOT, "src", "lib")
    os.makedirs(lib, exist_ok=True)
    pg = os.path.join(lib, "patent_guard.ts")
    with open(pg, "w", encoding="utf-8") as f:
        f.write(PATENT_GUARD_TS)
    print("✅ src/lib/patent_guard.ts")

    if not _on("E50_GIT_PUSH"):
        print("ℹ️  Sin E50_GIT_PUSH=1 no se ejecuta git.")
        return 0

    if not os.path.isdir(os.path.join(ROOT, ".git")):
        print("ℹ️  No hay .git en ROOT.")
        return 0

    if _on("E50_GIT_AUTOCRLF"):
        _run(["git", "config", "core.autocrlf", "false"], cwd=ROOT)

    exist = [p for p in GIT_PATHS if os.path.exists(os.path.join(ROOT, p))]
    if not exist:
        print("⚠️  Nada que añadir con git")
        return 0

    if _run(["git", "add", *exist], cwd=ROOT) != 0:
        print("❌ git add falló")
        return 1

    rc = _run(
        [
            "git",
            "commit",
            "-m",
            "FINAL: High-Ticket Licensing (98k) and Maintenance (100) Integrated",
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

    print("\n🔥 Push completado. Revisa GitHub y el despliegue en Vercel.")
    return 0


if __name__ == "__main__":
    sys.exit(construir_bunker_comercial())
