"""
Paso 19: commit + push acotado (flujo metadatos 98k / radar / cobros en repo).

- Sin shell=True, sin git add ., sin .env.
- E50_GIT_PUSH=1; E50_FORCE_PUSH=1 para --force.
- Raíz: E50_PROJECT_ROOT (por defecto ~/Projects/22TRYONYOU).

Ejecutar: python3 closure_98k.py
"""

from __future__ import annotations

import os
import subprocess
import sys

ROOT = os.path.abspath(
    os.environ.get("E50_PROJECT_ROOT", os.path.expanduser("~/Projects/22TRYONYOU"))
)

PATHS = [
    "package.json",
    "package-lock.json",
    ".gitignore",
    ".env.example",
    "vercel.json",
    "index.html",
    "vite.config.ts",
    "vite.config.js",
    "tailwind.config.js",
    "tsconfig.json",
    "src",
    "public",
    "api",
    "src/data/contracts/invoice_98k.json",
    "src/data/radar_config.json",
    "STRIPE_ACTIVE_PLAN.json",
    "MONEY_FLOW.json",
    "MONEY_FLOW_ACTIVATION.json",
    "INTELLIGENCE_SYNC.json",
    "LITIGIO_STATUS.json",
    "MISSION_CONTROL.json",
    "STUDIO_SYNC.json",
    "FINAL_SYNC.json",
    "JULES_TEAM_STATUS.json",
    "DEPLOY_SUCCESS.json",
]


def _run(argv: list[str], *, cwd: str) -> int:
    try:
        return subprocess.run(argv, cwd=cwd, check=False).returncode
    except OSError as e:
        print(f"❌ {e}")
        return 1


def _on(x: str) -> bool:
    return os.environ.get(x, "").strip().lower() in ("1", "true", "yes", "on")


def closure_98k() -> int:
    print("🚀 Paso 19: cierre 98k — commit/push acotado (metadatos en repo)...")

    os.makedirs(ROOT, exist_ok=True)
    os.chdir(ROOT)

    if not _on("E50_GIT_PUSH"):
        print("ℹ️  E50_GIT_PUSH=1 para git.")
        return 0

    if not os.path.isdir(os.path.join(ROOT, ".git")):
        print(f"❌ Sin .git en {ROOT}")
        return 1

    exist = [p for p in PATHS if os.path.exists(os.path.join(ROOT, p))]
    if not exist:
        print("❌ Ninguna ruta de PATHS existe; genera invoice/radar o ajusta la lista.")
        return 1

    if _run(["git", "add", *exist], cwd=ROOT) != 0:
        print("❌ git add falló")
        return 1

    rc = _run(
        [
            "git",
            "commit",
            "-m",
            "ENTERPRISE: High-ticket 98k contract flow activated",
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

    print("\n🔥 Push completado. Los JSON en repo son metadatos; cobros reales = Stripe + Vercel + backend.")
    return 0


if __name__ == "__main__":
    sys.exit(closure_98k())
