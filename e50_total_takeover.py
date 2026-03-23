"""
fix_engines + STUDIO_SYNC + npm lock; git opcional con E50_GIT_PUSH=1 (add acotado, sin `git add .`).
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


def fix_engines() -> None:
    pkg_path = os.path.join(ROOT, "package.json")
    if not os.path.isfile(pkg_path):
        print("ℹ️  Sin package.json en ROOT; se omite fix_engines.")
        return
    with open(pkg_path, encoding="utf-8") as f:
        data = json.load(f)
    data["engines"] = {"node": ">=20.x"}
    with open(pkg_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("✅ engines.node actualizado.")


def sync_studio() -> None:
    litis = {
        "status": "OPERATIONAL",
        "team": "50_AGENTS",
        "node": "20.x",
        "radar": "ACTIVE",
    }
    sync_path = os.path.join(ROOT, "STUDIO_SYNC.json")
    with open(sync_path, "w", encoding="utf-8") as f:
        json.dump(litis, f, indent=4, ensure_ascii=False)
        f.write("\n")
    print("✅ STUDIO_SYNC.json escrito.")


def deploy_force() -> None:
    pkg_path = os.path.join(ROOT, "package.json")
    if os.path.isfile(pkg_path):
        print("📦 npm install --package-lock-only...")
        if not _run(["npm", "install", "--package-lock-only"]):
            print("❌ npm falló.")
            sys.exit(1)
    else:
        print("ℹ️  Sin package.json; se omite npm.")

    if os.environ.get("E50_GIT_PUSH", "").strip().lower() not in ("1", "true", "yes", "on"):
        print("ℹ️  Sin E50_GIT_PUSH=1 no se ejecuta git.")
        return

    paths = [
        os.path.join(ROOT, "package.json"),
        os.path.join(ROOT, "package-lock.json"),
        os.path.join(ROOT, "STUDIO_SYNC.json"),
        os.path.join(ROOT, ".gitignore"),
        os.path.join(ROOT, "src"),
    ]
    add_args = ["git", "add", *[p for p in paths if os.path.exists(p)]]
    if len(add_args) <= 2:
        print("❌ Nada que añadir con git add acotado.")
        sys.exit(1)
    _run(add_args)
    if not _run(["git", "commit", "-m", "E50_TOTAL_TAKEOVER"]):
        print("❌ git commit falló (¿sin cambios o repo no inicializado?).")
        sys.exit(1)
    if not _run(["git", "push", "origin", "main", "--force"]):
        print("❌ git push falló.")
        sys.exit(1)
    print("🔥 Push enviado.")


if __name__ == "__main__":
    os.makedirs(ROOT, exist_ok=True)
    os.chdir(ROOT)
    fix_engines()
    sync_studio()
    deploy_force()
