"""
Paso 1: engines Node en package.json + npm lock-only + git acotado (opcional).

- Raíz: E50_PROJECT_ROOT (por defecto ~/Projects/22TRYONYOU).
- package.json: lectura/escritura completa (sin r+ truncate).
- Git: E50_GIT_PUSH=1; nunca `git add .`; commit con rutas explícitas.
- core.autocrlf: solo si E50_GIT_AUTOCRLF=1 (Windows/CRLF).

Ejecutar: python3 bunker_master_fix.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

ROOT = os.path.abspath(
    os.environ.get("E50_PROJECT_ROOT", os.path.expanduser("~/Projects/22TRYONYOU"))
)

GIT_PATHS = [
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
]


def _run(argv: list[str], *, cwd: str) -> int:
    try:
        return subprocess.run(argv, cwd=cwd, check=False).returncode
    except OSError as e:
        print(f"❌ {e}")
        return 1


def _git_on() -> bool:
    return os.environ.get("E50_GIT_PUSH", "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


def _autocrlf_on() -> bool:
    return os.environ.get("E50_GIT_AUTOCRLF", "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


def bunker_master_fix() -> int:
    print("🛠️ Paso 1: Forzando configuración de producción (seguro)...")

    os.makedirs(ROOT, exist_ok=True)
    os.chdir(ROOT)

    pkg = os.path.join(ROOT, "package.json")
    if not os.path.isfile(pkg):
        print(f"❌ No hay package.json en {ROOT}")
        return 1

    with open(pkg, encoding="utf-8") as f:
        data = json.load(f)
    if "engines" not in data or not isinstance(data.get("engines"), dict):
        data["engines"] = {}
    data["engines"]["node"] = ">=20.0.0"
    with open(pkg, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("✅ package.json → engines.node >=20.0.0")

    if _run(["npm", "install", "--package-lock-only"], cwd=ROOT) != 0:
        print("⚠️  npm install --package-lock-only devolvió error")
    else:
        print("✅ npm install --package-lock-only")

    if not _git_on():
        print("ℹ️  Sin E50_GIT_PUSH=1 no se ejecuta git.")
        return 0

    if not os.path.isdir(os.path.join(ROOT, ".git")):
        print("ℹ️  No hay .git en ROOT.")
        return 0

    if _autocrlf_on():
        if _run(["git", "config", "core.autocrlf", "false"], cwd=ROOT) == 0:
            print("✅ git config core.autocrlf false")
        else:
            print("⚠️  git config core.autocrlf falló")

    exist = [p for p in GIT_PATHS if os.path.exists(os.path.join(ROOT, p))]
    if not exist:
        print("⚠️  Nada que añadir con git (revisa GIT_PATHS)")
        return 0

    if _run(["git", "add", *exist], cwd=ROOT) != 0:
        print("❌ git add falló")
        return 1

    rc = _run(
        [
            "git",
            "commit",
            "-m",
            "FIX: Node engine and environment sync for Paris Deploy",
        ],
        cwd=ROOT,
    )
    if rc == 0:
        print("✅ git commit")
    elif rc == 1:
        print("ℹ️  git commit: sin cambios o ya commiteado")
    else:
        print("❌ git commit falló")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(bunker_master_fix())
