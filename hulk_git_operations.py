"""
hulk_git_operations — Limpieza de artefactos + push seguro a Git.

Uso básico:
    hulk_clean_everything()
    print(push_to_git())

Variables de entorno:
    E50_GIT_PUSH=1       — requerido para ejecutar el push (evita pushes accidentales).
    E50_FORCE_PUSH=1     — añade --force al git push.
    E50_GIT_REMOTE       — remoto (por defecto "origin").
    E50_GIT_BRANCH       — rama (por defecto rama actual activa).
    E50_PROJECT_ROOT     — raíz del repositorio (por defecto directorio del script).

Flujo:
    1. hulk_clean_everything() purga .next, node_modules/.cache, __pycache__ y temp_logs.
    2. push_to_git() solo procede si:
         a. hulk_clean_everything() fue llamado en esta sesión, Y
         b. el árbol de trabajo Git está limpio (sin cambios sin confirmar), Y
         c. E50_GIT_PUSH=1 está definido.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from bunker_cleaner_v10 import BunkerCleaner

# ---------------------------------------------------------------------------
# Estado interno de sesión
# ---------------------------------------------------------------------------

_cleaned: bool = False  # Bandera: se activa tras hulk_clean_everything()


def _root() -> Path:
    return Path(
        os.environ.get("E50_PROJECT_ROOT", str(Path(__file__).resolve().parent))
    ).resolve()


def _on(var: str) -> bool:
    return os.environ.get(var, "").strip().lower() in ("1", "true", "yes", "on")


def _run(argv: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, cwd=str(cwd), capture_output=True, text=True, check=False)


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------


def hulk_clean_everything() -> str:
    """Purga artefactos de compilación del repositorio.

    Elimina .next, node_modules/.cache, __pycache__ (recursivo) y temp_logs.
    Marca la sesión como limpia para que push_to_git() pueda proceder.

    Returns:
        Mensaje de confirmación de limpieza.
    """
    global _cleaned

    cleaner = BunkerCleaner()
    result = cleaner.ejecutar_limpieza()
    _cleaned = True
    return result


def push_to_git() -> str:
    """Realiza git push solo si el repositorio está limpio.

    Condiciones necesarias:
        1. hulk_clean_everything() debe haberse ejecutado en esta sesión.
        2. El árbol de trabajo Git no debe tener cambios sin confirmar.
        3. La variable E50_GIT_PUSH=1 debe estar definida.

    Returns:
        Cadena de texto describiendo el resultado de la operación.
    """
    if not _cleaned:
        return (
            "⛔ push_to_git() cancelado: ejecuta hulk_clean_everything() primero."
        )

    if not _on("E50_GIT_PUSH"):
        return "ℹ️  Define E50_GIT_PUSH=1 para habilitar el push (evita envíos accidentales)."

    root = _root()

    if not (root / ".git").is_dir():
        return f"ℹ️  No se encontró repositorio Git en {root}."

    # Verificar que el árbol de trabajo está limpio (sin cambios sin confirmar)
    status = _run(["git", "status", "--porcelain"], cwd=root)
    if status.returncode != 0:
        return f"❌ git status falló: {status.stderr.strip()}"

    if status.stdout.strip():
        return (
            "⚠️  El árbol de trabajo no está limpio. Confirma o descarta los cambios antes de hacer push.\n"
            + status.stdout.strip()
        )

    remote = os.environ.get("E50_GIT_REMOTE", "origin").strip() or "origin"

    # Obtener rama activa si no se especifica
    branch_env = os.environ.get("E50_GIT_BRANCH", "").strip()
    if branch_env:
        branch = branch_env
    else:
        rev = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=root)
        if rev.returncode != 0:
            return f"❌ No se pudo determinar la rama activa: {rev.stderr.strip()}"
        branch = rev.stdout.strip()

    cmd: list[str] = ["git", "push", remote, branch]
    if _on("E50_FORCE_PUSH"):
        cmd.append("--force")

    push = _run(cmd, cwd=root)
    if push.returncode != 0:
        return f"❌ git push falló:\n{push.stderr.strip()}"

    return f"✅ Push completado: {remote}/{branch}"


# ---------------------------------------------------------------------------
# Ejecución directa
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    hulk_clean_everything()
    print(push_to_git())
