"""
Equipo 51: engines Node ≥20, MISSION_CONTROL.json, npm lock-only, git opcional.

⚠️  Git solo con E50_GIT_PUSH=1; add acotado (nunca `git add .`).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

ROOT = os.environ.get("E50_PROJECT_ROOT", os.path.expanduser("~/Projects/22TRYONYOU"))


def _run(argv: list[str]) -> bool:
    try:
        return subprocess.run(argv, cwd=ROOT, check=False).returncode == 0
    except OSError as e:
        print(f"❌ {e}")
        return False


def ejecucion_total_equipo_51() -> None:
    print("🚀 EQUIPO 51: Iniciando despliegue masivo en Google AI Studio...")

    os.makedirs(ROOT, exist_ok=True)
    os.chdir(ROOT)

    pkg_path = os.path.join(ROOT, "package.json")
    if os.path.isfile(pkg_path):
        print("🛠️ Jules & Cursor: Node 20 Fix — engines en package.json...")
        with open(pkg_path, encoding="utf-8") as f:
            data = json.load(f)
        data["engines"] = {"node": ">=20.0.0"}
        with open(pkg_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
    else:
        print("ℹ️  Sin package.json en ROOT; se omite ajuste de engines.")

    print("🛡️ Agente 70 & Manus: MISSION_CONTROL.json...")
    status_final = {
        "ejecutor": "Jules",
        "equipo": "51_AGENTS",
        "inteligencia": "Agente_70_Manus",
        "fuente": "NotebookLM",
        "plataforma": "Google_AI_Studio",
        "litis_status": "TOTAL_WAR_READY",
    }
    mission_path = os.path.join(ROOT, "MISSION_CONTROL.json")
    with open(mission_path, "w", encoding="utf-8") as f:
        json.dump(status_final, f, indent=4, ensure_ascii=False)
        f.write("\n")

    if os.path.isfile(pkg_path):
        print("📦 npm install --package-lock-only...")
        if not _run(["npm", "install", "--package-lock-only"]):
            print("❌ npm install --package-lock-only falló.")
            sys.exit(1)
    else:
        print("ℹ️  Sin package.json; se omite npm.")

    if os.environ.get("E50_GIT_PUSH", "").strip().lower() not in ("1", "true", "yes", "on"):
        print("ℹ️  Sin E50_GIT_PUSH=1 no se ejecuta git.")
        print("🔥 Misión local lista (MISSION_CONTROL + lock).")
        return

    print("🚀 Push crítico: git add acotado, commit, push --force main...")
    paths = [
        os.path.join(ROOT, "package.json"),
        os.path.join(ROOT, "package-lock.json"),
        os.path.join(ROOT, "MISSION_CONTROL.json"),
        os.path.join(ROOT, ".gitignore"),
        os.path.join(ROOT, "src"),
    ]
    add_args = ["git", "add", *[p for p in paths if os.path.exists(p)]]
    if len(add_args) <= 1:
        print("❌ No hay archivos rastreables para git add.")
        sys.exit(1)
    if not _run(add_args):
        print("❌ git add falló.")
        sys.exit(1)
    commit_rc = subprocess.run(
        [
            "git",
            "commit",
            "-m",
            "EQUIPO 51: Ejecución Total Jules/70/Manus - Studio Build",
        ],
        cwd=ROOT,
        check=False,
    ).returncode
    if commit_rc not in (0, 1):
        print("❌ git commit falló.")
        sys.exit(1)
    if _run(["git", "push", "origin", "main", "--force"]):
        print("🔥 BÚNKER BLINDADO. El equipo de los 51 ha tomado el control. Fin de la operación.")
    else:
        print("❌ Push falló.")
        sys.exit(1)


if __name__ == "__main__":
    ejecucion_total_equipo_51()
