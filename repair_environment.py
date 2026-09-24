"""
Protocolo de sincronización local: Git + Python + plantilla .env (sin secretos en código).

Patente: PCT/EP2025/067317 — @CertezaAbsoluta @lo+erestu
Bajo Protocolo de Soberanía V10 - Founder: Rubén
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


def _run(cmd: list[str], *, cwd: Path) -> tuple[bool, str]:
    try:
        r = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
            cwd=str(cwd),
        )
        if r.returncode != 0:
            return False, (r.stderr or r.stdout or "").strip()
        return True, (r.stdout or "").strip()
    except OSError as e:
        return False, str(e)


def repair_environment() -> int:
    root = Path(__file__).resolve().parent
    os.chdir(root)
    print("--- Iniciando protocolo de sincronización ---")

    print("Git: gc --prune=now...")
    ok, err = _run(["git", "gc", "--prune=now"], cwd=root)
    if not ok:
        print(f"  (aviso) git gc: {err or 'sin detalle'}")

    print("Git: pull origin main...")
    ok, err = _run(["git", "pull", "origin", "main"], cwd=root)
    if not ok:
        print(f"  (aviso) git pull: {err or 'fallo'} — revisa rama/remoto.")

    req = root / "requirements.txt"
    if req.is_file():
        print("Python: pip install -r requirements.txt...")
        py_ok, py_err = _run(
            [sys.executable, "-m", "pip", "install", "-r", str(req)],
            cwd=root,
        )
        if not py_ok:
            print(f"  (aviso) pip: {py_err}")

    env_file = root / ".env"
    example = root / ".env.example"
    if not env_file.is_file():
        print("ADVERTENCIA: .env no detectado.")
        if example.is_file():
            shutil.copy(example, env_file)
            print(f"[OK] Copiado {example.name} -> .env (completa valores sensibles).")
        else:
            env_file.write_text(
                "# Plantilla mínima — usa .env.example si existe\n"
                "GOOGLE_STUDIO_KEY=\n"
                "VERCEL_TOKEN=\n",
                encoding="utf-8",
            )
            print("[OK] Creado .env mínimo; añade claves reales sin subirlas a git.")

    print("--- Entorno verificado (revisar avisos de git/pip) ---")
    return 0


if __name__ == "__main__":
    raise SystemExit(repair_environment())
