"""Paso 4: git add acotado, sin shell. E50_GIT_PUSH=1 obligatorio. E50_FORCE_PUSH=1 para --force."""
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
    "index.html",
    "vite.config.ts",
    "vite.config.js",
    "tailwind.config.js",
    "postcss.config.js",
    "tsconfig.json",
    "tsconfig.node.json",
    "vercel.json",
    "src",
    "public",
    "api",
    "STRIPE_ACTIVE_PLAN.json",
    "MONEY_FLOW.json",
    "MONEY_FLOW_ACTIVATION.json",
    "INTELLIGENCE_SYNC.json",
    "DEPLOY_SUCCESS.json",
    "LITIGIO_STATUS.json",
    "MISSION_CONTROL.json",
    "STUDIO_SYNC.json",
    "FINAL_SYNC.json",
    "JULES_TEAM_STATUS.json",
]


def _run(argv: list[str], cwd: str) -> int:
    try:
        return subprocess.run(argv, cwd=cwd, check=False).returncode
    except OSError as e:
        print(f"❌ {e}")
        return 1


def _on(x: str) -> bool:
    return os.environ.get(x, "").strip().lower() in ("1", "true", "yes", "on")


def final_deploy() -> int:
    print("🚀 Paso 4: push final (git acotado, sin .env).")
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
        print("❌ Ninguna ruta de PATHS existe; edita final_deploy.py")
        return 1
    if _run(["git", "add", *exist], ROOT) != 0:
        return 1
    rc = _run(
        [
            "git",
            "commit",
            "-m",
            "FINAL_TAKEOVER: Búnker operativo, cobros activos y radar sincronizado",
        ],
        ROOT,
    )
    if rc not in (0, 1):
        return 1
    cmd = ["git", "push", "origin", "main"]
    if _on("E50_FORCE_PUSH"):
        cmd.append("--force")
    if _run(cmd, ROOT) != 0:
        print("❌ git push falló")
        return 1
    print("\n🔥 Push hecho. Vercel despliega desde el remoto.")
    return 0


if __name__ == "__main__":
    sys.exit(final_deploy())
