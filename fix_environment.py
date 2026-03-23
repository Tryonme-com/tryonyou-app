"""
Alinea engines Node en package.json y regenera package-lock (opcionalmente limpia node_modules).

- Raíz: E50_PROJECT_ROOT (por defecto ~/Projects/22TRYONYOU).
- Motor Node: E50_NODE_ENGINE (ej. >=20.x); por defecto >=20.0.0.
- Limpieza profunda (rm node_modules + package-lock.json): solo con E50_DEEP_CLEAN=1.
- Sin shell=True; package.json se reescribe completo (sin r+ truncate).

Ejecutar: python3 fix_environment.py
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys

ROOT = os.path.abspath(
    os.environ.get("E50_PROJECT_ROOT", os.path.expanduser("~/Projects/22TRYONYOU"))
)


def _deep_clean_on() -> bool:
    return os.environ.get("E50_DEEP_CLEAN", "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


def _run(argv: list[str], *, cwd: str) -> int:
    try:
        return subprocess.run(argv, cwd=cwd, check=False).returncode
    except OSError as e:
        print(f"❌ {e}")
        return 1


def fix_environment() -> int:
    print("🛠️ Paso 1: Alineando motores...")

    os.makedirs(ROOT, exist_ok=True)
    os.chdir(ROOT)

    pkg_path = os.path.join(ROOT, "package.json")
    if not os.path.isfile(pkg_path):
        print(f"❌ No hay package.json en {ROOT}")
        return 1

    with open(pkg_path, encoding="utf-8") as f:
        data = json.load(f)

    if "engines" not in data or not isinstance(data.get("engines"), dict):
        data["engines"] = {}
    # Por defecto >=20.0.0 (CI); para coincidir con tu snippet: E50_NODE_ENGINE='>=20.x'
    node_engine = os.environ.get("E50_NODE_ENGINE", ">=20.0.0").strip() or ">=20.0.0"
    data["engines"]["node"] = node_engine

    with open(pkg_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    if _deep_clean_on():
        nm = os.path.join(ROOT, "node_modules")
        lock = os.path.join(ROOT, "package-lock.json")
        if os.path.isdir(nm):
            shutil.rmtree(nm, ignore_errors=False)
        if os.path.isfile(lock):
            os.remove(lock)
        print("🧹 E50_DEEP_CLEAN=1: node_modules y package-lock.json eliminados.")
    else:
        print(
            "ℹ️  Sin borrar node_modules (exporta E50_DEEP_CLEAN=1 para limpieza profunda como en tu script original)."
        )

    if _run(["npm", "install", "--package-lock-only"], cwd=ROOT) != 0:
        print("❌ npm install --package-lock-only falló")
        return 1

    print(f"✅ Entorno alineado (engines.node={node_engine!r}, lockfile actualizado).")
    return 0


if __name__ == "__main__":
    sys.exit(fix_environment())
