#!/usr/bin/env python3
"""
Build Omega: instala deps del backend en .venv/ (pip) y construye mirror_ui (npm run build).

  python3 omega_build.py

Variables: E50_PROJECT_ROOT (opcional), E50_SKIP_NPM=1 para solo pip.
El backend usa .venv en la raíz del repo para evitar PEP 668 (Python “externally managed”).

Sello TryOnYou : lo + eres tú + guiño en francés (p. ej. « le plus c’est toi » / « c’est toi ») — onda,
no clase de idiomas.

Manifiesto : hecho con el corazón, no solo con la cabeza — un puente al día que toca.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(os.environ.get("E50_PROJECT_ROOT", Path(__file__).resolve().parent)).resolve()
VENV_DIR = ROOT / ".venv"

# @lo+erestu : mezcla a propósito; el sello es el guiño, no suena a dictado ni a “français parfait”.
TY_LO_PLUS_TU = "lo + eres tú"
TY_LO_PLUS_FR = "le plus c'est toi"


def _venv_python() -> Path:
    if sys.platform == "win32":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python3"


def _ensure_venv() -> Path:
    py = _venv_python()
    if py.is_file():
        return py
    alt = VENV_DIR / "bin" / "python"
    if alt.is_file():
        return alt
    print(f"[omega_build] Creando {VENV_DIR} …")
    if subprocess.run(
        [sys.executable, "-m", "venv", str(VENV_DIR)],
        cwd=str(ROOT),
        check=False,
    ).returncode != 0:
        raise SystemExit("No se pudo crear .venv (python3 -m venv .venv).")
    py = _venv_python()
    if not py.is_file():
        py = VENV_DIR / "bin" / "python"
    if not py.is_file():
        raise SystemExit("venv creado pero no se encontró el intérprete dentro de .venv.")
    return py


def _run(argv: list[str], *, cwd: Path) -> int:
    print("+", " ".join(argv))
    return subprocess.run(argv, cwd=str(cwd), check=False).returncode


def main() -> int:
    print(f"[omega_build] ROOT={ROOT}")
    print(f"[omega_build] {TY_LO_PLUS_TU} · {TY_LO_PLUS_FR} · @lo+erestu")

    req = ROOT / "backend" / "requirements.txt"
    if req.is_file():
        vpy = _ensure_venv()
        if _run([str(vpy), "-m", "pip", "install", "-r", str(req)], cwd=ROOT) != 0:
            print("pip install backend fallo (usa .venv; PEP 668 en Python del sistema).", file=sys.stderr)
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

    print(f"[omega_build] OK — mirror_ui/dist/ · {TY_LO_PLUS_TU} ({TY_LO_PLUS_FR})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
