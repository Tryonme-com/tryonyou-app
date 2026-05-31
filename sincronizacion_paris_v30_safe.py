"""
Paso 30: escribe src/data/paris_sync.json (copy autoridad FR); git opcional y acotado.

- Raíz: E50_PROJECT_ROOT (por defecto ~/Projects/22TRYONYOU).
- Git: E50_GIT_PUSH=1, solo paris_sync.json; E50_FORCE_PUSH=1 para --force.

Ejecutar: python3 sincronizacion_paris_v30_safe.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

ROOT = os.path.abspath(
    os.environ.get("E50_PROJECT_ROOT", os.path.expanduser("~/Projects/22TRYONYOU"))
)

CONTENT_FR = {
    "hero_title": "L'Infrastructure de Précision pour le Retail de Luxe",
    "sub_text": "Pourquoi nous? Parce que le luxe ne tolère pas l'approximation.",
    "logic_point": (
        "Zéro Retour: Notre algorithme biométrique dépasse les limites du 2D."
    ),
    "cta_enterprise": (
        "Licence d'Exploitation: 98.000€ (Contactez notre département technique)"
    ),
}

GIT_PATHS = [
    "src/data/paris_sync.json",
]


def _run(argv: list[str], *, cwd: str) -> int:
    try:
        return subprocess.run(argv, cwd=cwd, check=False).returncode
    except OSError as e:
        print(f"❌ {e}")
        return 1


def _on(x: str) -> bool:
    return os.environ.get(x, "").strip().lower() in ("1", "true", "yes", "on")


def sincronizacion_paris_v30_safe() -> int:
    print("🚀 Ejecutando Paso 30: Sincronización de autoridad con París (seguro)...")

    os.makedirs(ROOT, exist_ok=True)
    os.chdir(ROOT)

    data_dir = os.path.join(ROOT, "src", "data")
    os.makedirs(data_dir, exist_ok=True)
    path = os.path.join(data_dir, "paris_sync.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(CONTENT_FR, f, indent=4, ensure_ascii=False)
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
            "STRATEGY: Step 30 - Paris Authority Sync",
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

    print("\n🔥 Push completado. Vercel desplegará según tu proyecto.")
    return 0


if __name__ == "__main__":
    sys.exit(sincronizacion_paris_v30_safe())
