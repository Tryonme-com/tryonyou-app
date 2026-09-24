"""
Protocolo señal verde: engines Node ≥20, npm lock-only, git opcional, pausa de consola.

⚠️  Git solo con E50_GIT_PUSH=1; add acotado (nunca `git add .`).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time

ROOT = os.environ.get("E50_PROJECT_ROOT", os.path.expanduser("~/Projects/22TRYONYOU"))


def _run(argv: list[str]) -> bool:
    try:
        return subprocess.run(argv, cwd=ROOT, check=False).returncode == 0
    except OSError as e:
        print(f"❌ {e}")
        return False


def check_status() -> None:
    os.makedirs(ROOT, exist_ok=True)
    os.chdir(ROOT)

    pkg_path = os.path.join(ROOT, "package.json")
    if os.path.isfile(pkg_path):
        with open(pkg_path, encoding="utf-8") as f:
            data = json.load(f)
        data["engines"] = {"node": ">=20.x"}
        with open(pkg_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print("✅ engines.node fijado (≥20.x).")
    else:
        print("ℹ️  Sin package.json en ROOT.")

    if os.path.isfile(pkg_path):
        print("📦 npm install --package-lock-only...")
        if not _run(["npm", "install", "--package-lock-only"]):
            print("❌ npm falló.")
            sys.exit(1)

    if os.environ.get("E50_GIT_PUSH", "").strip().lower() not in ("1", "true", "yes", "on"):
        print("ℹ️  Sin E50_GIT_PUSH=1 no se ejecuta git.")
    else:
        paths = [
            os.path.join(ROOT, "package.json"),
            os.path.join(ROOT, "package-lock.json"),
            os.path.join(ROOT, ".gitignore"),
            os.path.join(ROOT, "src"),
        ]
        add_args = ["git", "add", *[p for p in paths if os.path.exists(p)]]
        if len(add_args) <= 2:
            print("❌ Nada que añadir con git add acotado.")
            sys.exit(1)
        _run(add_args)
        if not _run(["git", "commit", "-m", "E50_GREEN_LIGHT_PROTOCOL"]):
            print("❌ git commit falló.")
            sys.exit(1)
        if not _run(["git", "push", "origin", "main", "--force"]):
            print("❌ git push falló.")
            sys.exit(1)
        print("✅ Push enviado.")

    print("⏳ Despliegue en curso... Esperando señal verde de Vercel.")
    time.sleep(5)


if __name__ == "__main__":
    check_status()
