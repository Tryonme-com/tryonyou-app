"""
Paso 3: git push a la rama activa, sin shell=True y sin force-push a main.

- Raíz: E50_PROJECT_ROOT (por defecto ~/Projects/22TRYONYOU).
- E50_GIT_PUSH=1 obligatorio.
- Empuja origin/<rama-actual> con -u. Nunca `git push origin main --force`.
- E50_FORCE_PUSH=1 solo se admite en ramas que no sean main/master.

Ejecutar: python3 asalto_final.py
"""

from __future__ import annotations

import os
import subprocess
import sys

PROTECTED_BRANCHES = {"main", "master"}


def _root() -> str:
    return os.path.abspath(
        os.environ.get("E50_PROJECT_ROOT", os.path.expanduser("~/Projects/22TRYONYOU"))
    )


def _run(argv: list[str], *, cwd: str) -> int:
    try:
        return subprocess.run(argv, cwd=cwd, check=False).returncode
    except OSError as e:
        print(f"❌ {e}")
        return 1


def _on(x: str, env: dict[str, str] | None = None) -> bool:
    source = env if env is not None else os.environ
    return source.get(x, "").strip().lower() in ("1", "true", "yes", "on")


def _current_branch(cwd: str) -> str:
    try:
        completed = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return ""
    if completed.returncode != 0:
        return ""
    return completed.stdout.strip()


def build_push_command(branch: str, env: dict[str, str] | None = None) -> list[str]:
    cmd = ["git", "push", "-u", "origin", branch]
    if _on("E50_FORCE_PUSH", env):
        if branch in PROTECTED_BRANCHES:
            raise ValueError("E50_FORCE_PUSH no se aplica a main/master.")
        cmd.append("--force")
    return cmd


def asalto_final() -> int:
    print("🚀 Paso 3: push a remoto (git sin shell)...")

    root = _root()
    os.makedirs(root, exist_ok=True)
    os.chdir(root)

    if not _on("E50_GIT_PUSH"):
        print("ℹ️  E50_GIT_PUSH=1 para ejecutar push.")
        return 0

    if not os.path.isdir(os.path.join(root, ".git")):
        print(f"❌ Sin .git en {root}")
        return 1

    branch = _current_branch(root)
    if not branch:
        print("❌ Rama detached; no se hace push.")
        return 1

    try:
        cmd = build_push_command(branch)
    except ValueError as exc:
        print(f"❌ {exc}")
        return 1

    rc = _run(cmd, cwd=root)
    if rc != 0:
        print(f"❌ git push falló (código {rc}). Revisa remoto, rama y credenciales.")
        return 1

    print(f"\n🔥 Push no destructivo completado hacia origin/{branch}.")
    return 0


if __name__ == "__main__":
    sys.exit(asalto_final())
