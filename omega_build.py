#!/usr/bin/env python3
"""
Build Omega: instala deps del backend (pip) y construye la SPA Vite en la raíz (npm run build).

  python3 omega_build.py

Variables: E50_PROJECT_ROOT (opcional), E50_SKIP_NPM=1 para solo pip.

En macOS/Homebrew, pip al Python del sistema suele fallar (PEP 668). Este script
crea o usa `.venv/` en la raíz del repo para instalar `backend/requirements.txt`.

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

# @lo+erestu : mezcla a propósito; el sello es el guiño, no suena a dictado ni a “français parfait”.
TY_LO_PLUS_TU = "lo + eres tú"
TY_LO_PLUS_FR = "le plus c'est toi"


def _run(argv: list[str], *, cwd: Path) -> int:
    print("+", " ".join(argv))
    return subprocess.run(argv, cwd=str(cwd), check=False).returncode


def _venv_python(venv_dir: Path) -> Path | None:
    for rel in ("bin/python3", "bin/python"):
        p = venv_dir / rel
        if p.is_file():
            return p
    return None


def _ensure_project_venv(root: Path) -> Path:
    """Python dentro de `.venv` para `pip install` sin conflicto PEP 668."""
    vdir = root / ".venv"
    py = _venv_python(vdir)
    if py:
        return py
    print("[omega_build] Creando .venv (pip compatible con PEP 668)…")
    if _run([sys.executable, "-m", "venv", str(vdir)], cwd=root) != 0:
        print(
            "No se pudo crear .venv. Prueba: python3 -m venv .venv",
            file=sys.stderr,
        )
        raise SystemExit(1)
    py = _venv_python(vdir)
    if not py:
        print(".venv creado pero no se encontró python.", file=sys.stderr)
        raise SystemExit(1)
    return py


def main() -> int:
    print(f"[omega_build] ROOT={ROOT}")
    print(f"[omega_build] {TY_LO_PLUS_TU} · {TY_LO_PLUS_FR} · @lo+erestu")

    req = ROOT / "backend" / "requirements.txt"
    if req.is_file():
        pip_py = _ensure_project_venv(ROOT)
        if _run([str(pip_py), "-m", "pip", "install", "-r", str(req)], cwd=ROOT) != 0:
            print("pip install backend fallo.", file=sys.stderr)
            return 1
    else:
        print("Aviso: no hay backend/requirements.txt")

    if os.environ.get("E50_SKIP_NPM", "").strip().lower() in ("1", "true", "yes", "on"):
        print("E50_SKIP_NPM=1: omitiendo npm run build.")
        return 0

    ui = ROOT
    pkg = ui / "package.json"
    if not pkg.is_file():
        print("Aviso: no hay package.json en la raíz; nada que construir con npm.")
        return 0

    if _run(["npm", "install"], cwd=ui) != 0:
        print("npm install fallo.", file=sys.stderr)
        return 1
    if _run(["npm", "run", "build"], cwd=ui) != 0:
        print("npm run build fallo.", file=sys.stderr)
        return 1

    print(f"[omega_build] OK — dist/ · {TY_LO_PLUS_TU} ({TY_LO_PLUS_FR})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
