"""Despliegue Vercel — token solo en entorno VERCEL_TOKEN; sin os.system.

Actualiza production_manifest.json y ejecuta la CLI de Vercel con subprocess.

Patente: PCT/EP2025/067317
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "production_manifest.json"
VAULT = ROOT / "master_omega_vault.json"


def deploy_sovereign_network() -> int:
    print("--- INICIANDO DESPLIEGUE VERCEL (Omega) ---")

    if not VAULT.exists():
        print("Error: master_omega_vault.json no encontrado.", file=sys.stderr)
        return 1

    token = os.environ.get("VERCEL_TOKEN", "").strip()
    if not token:
        print(
            "Define VERCEL_TOKEN en el entorno (revoca el token si llegó a filtrarse).",
            file=sys.stderr,
        )
        return 1

    if not MANIFEST.exists():
        print(f"Aviso: {MANIFEST.name} no existe; solo despliego.", file=sys.stderr)
    else:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        data["deployment"] = {
            "verified_domains": [
                "abvetos.com",
                "tryonme.com",
                "tryonme.app",
                "tryonme.org",
            ],
            "hosting": "Vercel",
            "status": "LIVE",
        }
        MANIFEST.write_text(
            json.dumps(data, indent=4, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    print("Ejecutando: vercel --prod --yes")
    proc = subprocess.run(
        ["vercel", "--token", token, "--prod", "--yes"],
        cwd=ROOT,
    )
    if proc.returncode != 0:
        print(f"vercel terminó con código {proc.returncode}.", file=sys.stderr)
        return proc.returncode

    print("--- Despliegue Vercel completado (código 0). ---")
    return 0


if __name__ == "__main__":
    raise SystemExit(deploy_sovereign_network())
