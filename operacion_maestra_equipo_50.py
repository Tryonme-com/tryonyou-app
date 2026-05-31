"""
Operación maestra Equipo 50: engines Node ≥20, LITIGIO_STATUS.json en el proyecto,
npm lock-only, git opcional.

⚠️  Git (add/commit/push) solo con E50_GIT_PUSH=1; paths acotados, nunca `git add .`.
    `verificar_litis.py` en este repo escribe otro esquema JSON en tryonyou-app; no se
    encadena aquí para no pisar LITIGIO_STATUS del búnker (E50_PROJECT_ROOT).
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


def operacion_maestra_equipo_50() -> None:
    # 1. JULES: Corrección de motor y entorno (Error 50 Fix)
    os.makedirs(ROOT, exist_ok=True)
    os.chdir(ROOT)

    pkg_path = os.path.join(ROOT, "package.json")
    if os.path.isfile(pkg_path):
        print("🛠️ Jules: Forzando Node ≥20 y limpiando definición de engines...")
        with open(pkg_path, encoding="utf-8") as f:
            data = json.load(f)
        data["engines"] = {"node": ">=20.0.0"}
        with open(pkg_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
    else:
        print("ℹ️  Sin package.json en ROOT; se omite ajuste de engines.")

    # 2. AGENTE 70: Estatus de litigio para el build (búnker / proyecto ROOT)
    print("🛡️ Agente 70: Generando LITIGIO_STATUS.json en el proyecto...")
    litis_status = {
        "marcas": ["LVMH", "Chanel", "Dior", "Balmain", "Hermès"],
        "status": "RADAR_CONNECTED",
        "timestamp": date.today().isoformat(),
    }
    litis_path = os.path.join(ROOT, "LITIGIO_STATUS.json")
    with open(litis_path, "w", encoding="utf-8") as f:
        json.dump(litis_status, f, indent=4, ensure_ascii=False)
        f.write("\n")

    # 3. npm: solo lockfile (como en tu borrador)
    if os.path.isfile(pkg_path):
        print("🚀 npm install --package-lock-only...")
        if not _run(["npm", "install", "--package-lock-only"]):
            print("❌ npm install --package-lock-only falló.")
            sys.exit(1)
    else:
        print("ℹ️  Sin package.json; se omite npm.")

    # 4. CURSOR: consolidación y push crítico (opt-in)
    if os.environ.get("E50_GIT_PUSH", "").strip().lower() not in ("1", "true", "yes", "on"):
        print("ℹ️  Sin E50_GIT_PUSH=1 no se ejecuta git.")
        print("🔥 Equipo conectado (sin push). Radar y lock listos en ROOT.")
        return

    print("🚀 Cursor: git add acotado, commit, push --force main...")
    paths = [
        os.path.join(ROOT, "package.json"),
        os.path.join(ROOT, "package-lock.json"),
        os.path.join(ROOT, "LITIGIO_STATUS.json"),
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
            "EQUIPO_50_TOTAL_TAKEOVER: Fix Node Version & Radar Sync",
        ]
    )
    if _run(["git", "push", "origin", "main", "--force"]):
        print("🔥 TODO EL EQUIPO CONECTADO. El búnker está en el aire.")
    else:
        print("❌ Push falló.")
        sys.exit(1)


if __name__ == "__main__":
    operacion_maestra_equipo_50()
