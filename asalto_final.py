"""
Paso 3: git push a main (opcionalmente --force), sin shell=True.

- Raíz: E50_PROJECT_ROOT (por defecto ~/Projects/22TRYONYOU).
- E50_GIT_PUSH=1 obligatorio.
- --force solo con E50_FORCE_PUSH=1 (tu script original forzaba siempre).

Ejecutar: python3 asalto_final.py
"""

from __future__ import annotations

import os
import subprocess
import sys

ROOT = os.path.abspath(
    os.environ.get("E50_PROJECT_ROOT", os.path.expanduser("~/Projects/22TRYONYOU"))
)


def _run(argv: list[str], *, cwd: str) -> int:
    try:
        return subprocess.run(argv, cwd=cwd, check=False).returncode
    except OSError as e:
        print(f"❌ {e}")
        return 1


def _on(x: str) -> bool:
    return os.environ.get(x, "").strip().lower() in ("1", "true", "yes", "on")


def asalto_final() -> int:
    print("🚀 Paso 3: push a remoto (git sin shell)...")

    os.makedirs(ROOT, exist_ok=True)
    os.chdir(ROOT)

    if not _on("E50_GIT_PUSH"):
        print("ℹ️  E50_GIT_PUSH=1 para ejecutar push.")
        return 0

    if not os.path.isdir(os.path.join(ROOT, ".git")):
        print(f"❌ Sin .git en {ROOT}")
        return 1

    cmd = ["git", "push", "origin", "main"]
    if _on("E50_FORCE_PUSH"):
        cmd.append("--force")

    rc = _run(cmd, cwd=ROOT)
    if rc != 0:
        print(f"❌ git push falló (código {rc}). Revisa remoto, rama y credenciales.")
        return 1

    print("\n🔥 Push completado. Revisa GitHub y el despliegue en Vercel.")
    return 0


if __name__ == "__main__":
    sys.exit(asalto_final())
