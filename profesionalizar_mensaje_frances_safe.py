"""
Escribe src/data/message_fr.json (copy enterprise FR); git opcional y acotado.

- Raíz: E50_PROJECT_ROOT (por defecto ~/Projects/22TRYONYOU).
- Git: E50_GIT_PUSH=1, solo message_fr.json; E50_FORCE_PUSH=1 para --force.

Ejecutar: python3 profesionalizar_mensaje_frances_safe.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

ROOT = os.path.abspath(
    os.environ.get("E50_PROJECT_ROOT", os.path.expanduser("~/Projects/22TRYONYOU"))
)

MESSAGE_FR = {
    "titre": "L'Infrastructure de Précision pour le Luxe",
    "accroche": (
        "Le futur du retail ne se joue pas sur des photos, "
        "mais sur la physique biométrique."
    ),
    "valeur": (
        "Nous éliminons 98% des retours grâce à notre algorithme "
        "d'ajustement invisible."
    ),
    "appel_action": (
        "Contactez notre département Enterprise pour une licence "
        "d'exploitation (98.000€)."
    ),
}

GIT_PATHS = [
    "src/data/message_fr.json",
]


def _run(argv: list[str], *, cwd: str) -> int:
    try:
        return subprocess.run(argv, cwd=cwd, check=False).returncode
    except OSError as e:
        print(f"❌ {e}")
        return 1


def _on(x: str) -> bool:
    return os.environ.get(x, "").strip().lower() in ("1", "true", "yes", "on")


def profesionalizar_mensaje_frances_safe() -> int:
    print("🚀 Paso 30: Blindando el mensaje profesional en francés...")

    os.makedirs(ROOT, exist_ok=True)
    os.chdir(ROOT)

    data_dir = os.path.join(ROOT, "src", "data")
    os.makedirs(data_dir, exist_ok=True)
    path = os.path.join(data_dir, "message_fr.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(MESSAGE_FR, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"✅ {os.path.relpath(path, ROOT)}")

    if not _on("E50_GIT_PUSH"):
        print("ℹ️  Sin E50_GIT_PUSH=1 no se ejecuta git.")
        return 0

    if not os.path.isdir(os.path.join(ROOT, ".git")):
        print("ℹ️  No hay .git en ROOT.")
        return 0

    exist = [p for p in GIT_PATHS if os.path.exists(os.path.join(ROOT, p))]
    if not exist:
        print("⚠️  Nada que añadir con git")
        return 0

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
            "STRATEGY: Synchronizing web copy with Paris LinkedIn traffic",
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

    print("✅ Push completado. Replica el copy en el frontend si aún no lo importas.")
    return 0


if __name__ == "__main__":
    sys.exit(profesionalizar_mensaje_frances_safe())
