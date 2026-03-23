#!/usr/bin/env python3
"""
Build Omega: instala deps del backend (pip) y construye mirror_ui (npm run build).

  python3 omega_build.py

Variables: E50_PROJECT_ROOT (opcional), E50_SKIP_NPM=1 para solo pip.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(os.environ.get("E50_PROJECT_ROOT", Path(__file__).resolve().parent)).resolve()


def _run(argv: list[str], *, cwd: Path) -> int:
    print("+", " ".join(argv))
    return subprocess.run(argv, cwd=str(cwd), check=False).returncode


def main() -> int:
    print(f"[omega_build] ROOT={ROOT}")

    req = ROOT / "backend" / "requirements.txt"
    if req.is_file():
        if _run([sys.executable, "-m", "pip", "install", "-r", str(req)], cwd=ROOT) != 0:
            print("pip install backend fallo.", file=sys.stderr)
            return 1
    else:
        print("Aviso: no hay backend/requirements.txt")

    if os.environ.get("E50_SKIP_NPM", "").strip().lower() in ("1", "true", "yes", "on"):
        print("E50_SKIP_NPM=1: omitiendo npm run build.")
        return 0

    ui = ROOT / "mirror_ui"
    pkg = ui / "package.json"
    if not pkg.is_file():
        print("Aviso: no hay mirror_ui/package.json; nada que construir con npm.")
        return 0

    if _run(["npm", "install"], cwd=ui) != 0:
        print("npm install fallo.", file=sys.stderr)
        return 1
    if _run(["npm", "run", "build"], cwd=ui) != 0:
        print("npm run build fallo.", file=sys.stderr)
        return 1

    print("[omega_build] OK — salida en mirror_ui/dist/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
