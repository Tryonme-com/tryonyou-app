"""
Node ≥20, FINAL_SYNC.json, npm lock, comprobación de remoto y push opcional (E50_GIT_PUSH).

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


def ensure_node_20() -> None:
    pkg_path = os.path.join(ROOT, "package.json")
    if os.path.isfile(pkg_path):
        with open(pkg_path, encoding="utf-8") as f:
            data = json.load(f)
        data["engines"] = {"node": ">=20.x"}
        with open(pkg_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
    print("✅ Motor Node 20 configurado.")


def final_sync_files() -> None:
    status = {
        "status": "GREEN_TARGET",
        "team": "50_AGENTS",
        "deployment": "FORCED",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    out = os.path.join(ROOT, "FINAL_SYNC.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(status, f, indent=4, ensure_ascii=False)
        f.write("\n")
    print("✅ Archivos de estado sincronizados.")


def check_git_remote() -> None:
    print("📡 git remote -v")
    subprocess.run(["git", "-C", ROOT, "remote", "-v"], check=False)


def push_to_green() -> None:
    pkg_path = os.path.join(ROOT, "package.json")
    if os.path.isfile(pkg_path):
        print("📦 npm install --package-lock-only...")
        if not _run(["npm", "install", "--package-lock-only"]):
            print("❌ npm falló.")
            sys.exit(1)

    if os.environ.get("E50_GIT_PUSH", "").strip().lower() not in ("1", "true", "yes", "on"):
        print("ℹ️  Sin E50_GIT_PUSH=1 no se ejecuta push.")
        return

    paths = [
        os.path.join(ROOT, "package.json"),
        os.path.join(ROOT, "package-lock.json"),
        os.path.join(ROOT, "FINAL_SYNC.json"),
        os.path.join(ROOT, ".gitignore"),
        os.path.join(ROOT, "src"),
    ]
    add_args = ["git", "add", *[p for p in paths if os.path.exists(p)]]
    if len(add_args) <= 1:
        print("❌ Nada que añadir con git add acotado.")
        sys.exit(1)
    _run(add_args)
    if not _run(["git", "commit", "-m", "E50: FINAL_ATTACK_TO_GREEN"]):
        print("❌ git commit falló.")
        sys.exit(1)
    if not _run(["git", "push", "origin", "main", "--force"]):
        print("❌ git push falló.")
        sys.exit(1)
    print("🚀 Push final ejecutado. Esperando despliegue de Vercel.")


if __name__ == "__main__":
    os.makedirs(ROOT, exist_ok=True)
    os.chdir(ROOT)
    ensure_node_20()
    final_sync_files()
    check_git_remote()
    push_to_green()
