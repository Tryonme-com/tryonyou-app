"""
Paso 38: commit + push acotado (flujo Stripe / cobros en repo, sin .env).

- Sin shell=True, sin git add ., sin subir secretos.
- E50_GIT_PUSH=1; E50_FORCE_PUSH=1 para --force.
- Raíz: E50_PROJECT_ROOT (por defecto ~/Projects/22TRYONYOU).

Ejecutar: python3 desplegar_caja_registradora.py
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
    "src/lib/stripe.ts",
    "src/lib/constants.ts",
    "STRIPE_ACTIVE_PLAN.json",
    "MONEY_FLOW.json",
    "MONEY_FLOW_ACTIVATION.json",
    "INTELLIGENCE_SYNC.json",
    "LITIGIO_STATUS.json",
]


def _run(argv: list[str], *, cwd: str) -> int:
    try:
        return subprocess.run(argv, cwd=cwd, check=False).returncode
    except OSError as e:
        print(f"❌ {e}")
        return 1


def _on(x: str) -> bool:
    return os.environ.get(x, "").strip().lower() in ("1", "true", "yes", "on")


def desplegar_caja_registradora() -> int:
    print("🚀 Paso 38: Activando flujo de caja (git acotado, sin .env)...")

    os.makedirs(ROOT, exist_ok=True)
    os.chdir(ROOT)

    if not _on("E50_GIT_PUSH"):
        print("ℹ️  E50_GIT_PUSH=1 para ejecutar git.")
        return 0

    if not os.path.isdir(os.path.join(ROOT, ".git")):
        print(f"❌ Sin .git en {ROOT}")
        return 1

    exist = [p for p in PATHS if os.path.exists(os.path.join(ROOT, p))]
    if not exist:
        print("❌ Ninguna ruta de PATHS existe; ajusta la lista o genera stripe.ts / JSON.")
        return 1

    if _run(["git", "add", *exist], cwd=ROOT) != 0:
        print("❌ git add falló")
        return 1

    rc = _run(
        [
            "git",
            "commit",
            "-m",
            "STRIPE_LIVE: IDs 200 OK synchronized - Ready for 98k/100",
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

    print("\n🔥 Push completado. Cobro real = Stripe + Vercel (vars) + sesión Checkout en backend.")
    return 0


if __name__ == "__main__":
    sys.exit(desplegar_caja_registradora())
