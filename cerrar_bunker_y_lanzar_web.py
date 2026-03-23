"""
Cierre búnker y deploy: engines Node ≥20, LITIGIO_STATUS.json, npm lock-only, git opcional.

⚠️  Git solo con E50_GIT_PUSH=1; add acotado (nunca `git add .`).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import date

ROOT = os.environ.get("E50_PROJECT_ROOT", os.path.expanduser("~/Projects/22TRYONYOU"))


def _run(argv: list[str]) -> bool:
    try:
        return subprocess.run(argv, cwd=ROOT, check=False).returncode == 0
    except OSError as e:
        print(f"❌ {e}")
        return False


def cerrar_bunker_y_lanzar_web() -> None:
    print("🚀 SUMA ESTRATÉGICA FINAL: JULES + 70 + COPILOT + VERCEL")

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
        print("✅ Jules: Versión de Node fijada para CI (≥20).")
    else:
        print("ℹ️  Sin package.json en ROOT; se omite engines.")

    litis_data = {
        "equipo": "50_AGENTS",
        "status": "RADAR_CONNECTED",
        "targets": ["LVMH", "Chanel", "Dior", "Balmain", "Hermès"],
        "timestamp": date.today().isoformat(),
    }
    litis_path = os.path.join(ROOT, "LITIGIO_STATUS.json")
    with open(litis_path, "w", encoding="utf-8") as f:
        json.dump(litis_data, f, indent=4, ensure_ascii=False)
        f.write("\n")
    print("✅ 70: Radar de marcas sincronizado.")

    if os.path.isfile(pkg_path):
        print("🧹 npm install --package-lock-only...")
        if not _run(["npm", "install", "--package-lock-only"]):
            print("❌ npm install --package-lock-only falló.")
            sys.exit(1)
    else:
        print("ℹ️  Sin package.json; se omite npm.")

    if os.environ.get("E50_GIT_PUSH", "").strip().lower() not in ("1", "true", "yes", "on"):
        print("ℹ️  Sin E50_GIT_PUSH=1 no se ejecuta git.")
        print("🔥 Búnker listo en disco (sin push).")
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
            "FINAL_TAKEOVER: Búnker 50 Activo - Fix Node 20",
        ]
    )
    if _run(["git", "push", "origin", "main", "--force"]):
        print("\n🔥 ÉXITO: El búnker está en el aire.")
        print("👉 Revisa Vercel / GitHub Actions para confirmar el deploy.")
    else:
        print("❌ Push falló.")
        sys.exit(1)


if __name__ == "__main__":
    cerrar_bunker_y_lanzar_web()
