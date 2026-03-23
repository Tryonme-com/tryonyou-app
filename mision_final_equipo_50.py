"""
Misión final equipo 50: engines Node ≥20, LITIGIO_STATUS.json, npm lock-only, git opcional.

⚠️  Git solo con E50_GIT_PUSH=1; add acotado (nunca `git add .`).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime

ROOT = os.environ.get("E50_PROJECT_ROOT", os.path.expanduser("~/Projects/22TRYONYOU"))


def _run(argv: list[str]) -> bool:
    try:
        return subprocess.run(argv, cwd=ROOT, check=False).returncode == 0
    except OSError as e:
        print(f"❌ {e}")
        return False


def mision_final_equipo_50() -> None:
    print("🚀 EQUIPO 50: Iniciando suma estratégica Jules + 70 + Copilot + Vercel...")

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
        print("✅ Jules: Motor Node fijado para GitHub/Vercel (≥20).")
    else:
        print("ℹ️  Sin package.json en ROOT; se omite engines.")

    status_litis = {
        "equipo": "50_AGENTS",
        "radar": "LVMH_CHANEL_DIOR_CONNECTED",
        "status": "OPERATIONAL_BUNKER",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "deploy_token": "E50_ULTIMATUM_FORCE",
    }
    litis_path = os.path.join(ROOT, "LITIGIO_STATUS.json")
    with open(litis_path, "w", encoding="utf-8") as f:
        json.dump(status_litis, f, indent=4, ensure_ascii=False)
        f.write("\n")
    print("✅ 70: Radar de litigio inyectado y sincronizado.")

    if os.path.isfile(pkg_path):
        print("🧹 npm install --package-lock-only...")
        if not _run(["npm", "install", "--package-lock-only"]):
            print("❌ npm install --package-lock-only falló.")
            sys.exit(1)
    else:
        print("ℹ️  Sin package.json; se omite npm.")

    if os.environ.get("E50_GIT_PUSH", "").strip().lower() not in ("1", "true", "yes", "on"):
        print("ℹ️  Sin E50_GIT_PUSH=1 no se ejecuta git.")
        print("🔥 Misión local completada (sin push).")
        return

    print("🧹 Cursor: git add acotado, commit, push --force main...")
    paths = [
        os.path.join(ROOT, "package.json"),
        os.path.join(ROOT, "package-lock.json"),
        os.path.join(ROOT, "LITIGIO_STATUS.json"),
        os.path.join(ROOT, ".gitignore"),
        os.path.join(ROOT, "src"),
    ]
    add_args = ["git", "add", *[p for p in paths if os.path.exists(p)]]
    if len(add_args) <= 1:
        print("❌ No hay archivos rastreables para git add.")
        sys.exit(1)
    _run(add_args)
    _run(
        [
            "git",
            "commit",
            "-m",
            "MISIÓN FINAL: Suma Total Equipo 50 - Búnker Activo y Node Fix",
        ]
    )
    if _run(["git", "push", "origin", "main", "--force"]):
        print("\n🔥 ÉXITO ABSOLUTO. El búnker está en el aire.")
        print("👉 Revisa Vercel / GitHub para el estado del deploy.")
    else:
        print("❌ Push falló.")
        sys.exit(1)


if __name__ == "__main__":
    mision_final_equipo_50()
