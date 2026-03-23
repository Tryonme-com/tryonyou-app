"""
Jules + Google AI Studio: engines Node ≥20, STUDIO_CONFIG.json, npm lock-only, git opcional.

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


def ejecucion_final_jules_studio() -> None:
    print("🚀 JULES: Iniciando ejecución en Google AI Studio...")

    os.makedirs(ROOT, exist_ok=True)
    os.chdir(ROOT)

    pkg_path = os.path.join(ROOT, "package.json")
    if os.path.isfile(pkg_path):
        print("🛠️ Jules: Fix Error 50 — engines.node ≥20...")
        with open(pkg_path, encoding="utf-8") as f:
            data = json.load(f)
        data["engines"] = {"node": ">=20.0.0"}
        with open(pkg_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
    else:
        print("ℹ️  Sin package.json en ROOT; se omite ajuste de engines.")

    print("📓 Sincronización NotebookLM / memoria (STUDIO_CONFIG.json)...")
    config_studio = {
        "executor": "Jules",
        "memory_source": "NotebookLM",
        "platform": "Google AI Studio",
        "status": "FINAL_BUILD",
    }
    studio_path = os.path.join(ROOT, "STUDIO_CONFIG.json")
    with open(studio_path, "w", encoding="utf-8") as f:
        json.dump(config_studio, f, indent=4, ensure_ascii=False)
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
        print("🔥 Build local listo (Studio config + lock).")
        return

    print("🚀 Empuje final: git add acotado, commit, push --force main...")
    paths = [
        os.path.join(ROOT, "package.json"),
        os.path.join(ROOT, "package-lock.json"),
        os.path.join(ROOT, "STUDIO_CONFIG.json"),
        os.path.join(ROOT, ".gitignore"),
        os.path.join(ROOT, "src"),
    ]
    add_args = ["git", "add", *[p for p in paths if os.path.exists(p)]]
    if len(add_args) <= 2:
        print("❌ No hay archivos rastreables para git add.")
        sys.exit(1)
    _run(add_args)
    _run(
        [
            "git",
            "commit",
            "-m",
            "JULES: Final Studio Build - Notebook Memory Sync",
        ]
    )
    if _run(["git", "push", "origin", "main", "--force"]):
        print("🔥 BÚNKER CERRADO. Todo está en Google Studio. Ya puedes descansar.")
    else:
        print("❌ Push falló.")
        sys.exit(1)


if __name__ == "__main__":
    ejecucion_final_jules_studio()
