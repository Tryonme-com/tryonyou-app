"""
Jules + 70: engines.node en package.json, npm install, git opcional.

⚠️  subprocess con lista + shell=True es incorrecto.
⚠️  Git (add/commit/push) solo con E50_GIT_PUSH=1; add acotado, no `git add .`.
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


def ejecucion_equipo_50() -> None:
    os.makedirs(ROOT, exist_ok=True)
    os.chdir(ROOT)

    pkg_path = os.path.join(ROOT, "package.json")
    if not os.path.isfile(pkg_path):
        print(f"❌ No existe {pkg_path}")
        sys.exit(1)

    print("🛠️ Jules: engines.node = 20.x en package.json...")
    with open(pkg_path, encoding="utf-8") as f:
        data = json.load(f)
    data["engines"] = {"node": "20.x"}
    with open(pkg_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print("🛡️ Agente 70: npm install...")
    if not _run(["npm", "install"]):
        print("❌ npm install falló.")
        sys.exit(1)

    if os.environ.get("E50_GIT_PUSH", "").strip().lower() not in ("1", "true", "yes", "on"):
        print("ℹ️  Sin E50_GIT_PUSH=1 no se ejecuta git.")
        return

    print("🚀 Equipo 50: git add acotado, commit, push --force...")
    _run(["git", "add", "package.json", "package-lock.json", "src/", ".gitignore"])
    _run(["git", "commit", "-m", "LITIGIO_TOTAL: Jules & 70 Takeover - Fix Error 50"])
    if _run(["git", "push", "origin", "main", "--force"]):
        print("🔥 Push enviado. Revisa GitHub/Vercel.")
    else:
        print("❌ Push falló.")
        sys.exit(1)


if __name__ == "__main__":
    ejecucion_equipo_50()
