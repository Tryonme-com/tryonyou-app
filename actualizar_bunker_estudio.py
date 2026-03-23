"""
Sincronización búnker / Google Studio: engines Node ≥20, STUDIO_SYNC.json, npm lock-only, git opcional.

⚠️  Git solo con E50_GIT_PUSH=1; add acotado (nunca `git add .`).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

from google_studio import studio_link_fields

ROOT = os.environ.get("E50_PROJECT_ROOT", os.path.expanduser("~/Projects/22TRYONYOU"))


def _run(argv: list[str]) -> bool:
    try:
        return subprocess.run(argv, cwd=ROOT, check=False).returncode == 0
    except OSError as e:
        print(f"❌ {e}")
        return False


def actualizar_bunker_estudio() -> None:
    print("🚀 Sincronizando Google Studio con el Equipo de los 50...")

    os.makedirs(ROOT, exist_ok=True)
    os.chdir(ROOT)

    pkg_path = os.path.join(ROOT, "package.json")
    if os.path.isfile(pkg_path):
        with open(pkg_path, encoding="utf-8") as f:
            data = json.load(f)
        data["engines"] = {"node": ">=20.0.0"}
        with open(pkg_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print("✅ Motores alineados con Google Studio (Node ≥20).")
    else:
        print("ℹ️  Sin package.json en ROOT; se omite engines.")

    litis = {
        "studio_update": "LATEST",
        "team": "50_AGENTS",
        "status": "CONNECTED",
        "radar": "ACTIVE",
        **studio_link_fields(),
    }
    sync_path = os.path.join(ROOT, "STUDIO_SYNC.json")
    with open(sync_path, "w", encoding="utf-8") as f:
        json.dump(litis, f, indent=4, ensure_ascii=False)
        f.write("\n")

    if os.path.isfile(pkg_path):
        print("🧹 npm install --package-lock-only...")
        if not _run(["npm", "install", "--package-lock-only"]):
            print("❌ npm install --package-lock-only falló.")
            sys.exit(1)
    else:
        print("ℹ️  Sin package.json; se omite npm.")

    if os.environ.get("E50_GIT_PUSH", "").strip().lower() not in ("1", "true", "yes", "on"):
        print("ℹ️  Sin E50_GIT_PUSH=1 no se ejecuta git.")
        print("🔥 STUDIO_SYNC y lock listos en ROOT (sin push).")
        return

    print("🧹 git add acotado, commit, push --force main...")
    paths = [
        os.path.join(ROOT, "package.json"),
        os.path.join(ROOT, "package-lock.json"),
        os.path.join(ROOT, "STUDIO_SYNC.json"),
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
            "UPDATE: Google Studio Sync & Node 20 Fix",
        ]
    )
    if _run(["git", "push", "origin", "main", "--force"]):
        print("\n🔥 TODO ACTUALIZADO. El búnker está en línea con Google Studio.")
        print("👉 Revisa Vercel / GitHub para confirmar el deploy.")
    else:
        print("❌ Push falló.")
        sys.exit(1)


if __name__ == "__main__":
    actualizar_bunker_estudio()
