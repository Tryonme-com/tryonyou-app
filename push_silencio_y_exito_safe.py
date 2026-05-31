"""
Commit + push acotado: posicionamiento de marca + manifiesto técnico (sin git add .).

Rutas por defecto: brand_position.ts, logic_manifest.ts (generados por otros pasos).
- Raíz: E50_PROJECT_ROOT (por defecto ~/Projects/22TRYONYOU).
- Obligatorio: E50_GIT_PUSH=1. Opcional: E50_FORCE_PUSH=1, E50_GIT_AUTOCRLF=1.

Opcional: E50_AUTHORITY_PATHS='ruta1,ruta2' (relativas a ROOT) sustituye la lista.

Ejecutar: E50_GIT_PUSH=1 python3 push_silencio_y_exito_safe.py
"""

from __future__ import annotations

import os
import subprocess
import sys

ROOT = os.path.abspath(
    os.environ.get("E50_PROJECT_ROOT", os.path.expanduser("~/Projects/22TRYONYOU"))
)

DEFAULT_PATHS = [
    "src/data/brand_position.ts",
    "src/data/logic_manifest.ts",
]


def _run(argv: list[str], *, cwd: str) -> int:
    try:
        return subprocess.run(argv, cwd=cwd, check=False).returncode
    except OSError as e:
        print(f"❌ {e}")
        return 1


def _on(x: str) -> bool:
    return os.environ.get(x, "").strip().lower() in ("1", "true", "yes", "on")


def _git_paths() -> list[str]:
    extra = os.environ.get("E50_AUTHORITY_PATHS", "").strip()
    if extra:
        return [p.strip() for p in extra.split(",") if p.strip()]
    return list(DEFAULT_PATHS)


def push_silencio_y_exito_safe() -> int:
    print("🚀 Paso 29: Subiendo la versión final de autoridad (git acotado)...")

    os.makedirs(ROOT, exist_ok=True)
    os.chdir(ROOT)

    if not _on("E50_GIT_PUSH"):
        print("ℹ️  Define E50_GIT_PUSH=1 para ejecutar git (evita pushes accidentales).")
        return 0

    if not os.path.isdir(os.path.join(ROOT, ".git")):
        print("ℹ️  No hay .git en ROOT.")
        return 0

    paths = _git_paths()
    exist = [p for p in paths if os.path.exists(os.path.join(ROOT, p))]
    if not exist:
        print("⚠️  Ninguna de las rutas existe aún. Genera los archivos o ajusta E50_AUTHORITY_PATHS.")
        print(f"   Buscadas: {', '.join(paths)}")
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
            "AUTHORITY: Formalizing brand position and technical superiority",
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

    print("\n🔥 Push completado (rutas explícitas, sin add .).")
    return 0


if __name__ == "__main__":
    sys.exit(push_silencio_y_exito_safe())
