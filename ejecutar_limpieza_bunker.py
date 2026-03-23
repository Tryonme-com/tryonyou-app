"""
Diagnóstico rápido + purga opcional de __pycache__ / .pytest_cache bajo el proyecto.

  E50_PROJECT_ROOT — raíz (por defecto ~/Projects/22TRYONYOU)
  E50_PURGE_CACHE=1 — borra __pycache__, *.pyc sueltos y .pytest_cache bajo ROOT
  E50_STRICT=1 — exit 1 si falta STRIPE_SECRET_KEY (o alias) cuando pides purga o siempre? Solo si E50_STRICT=1 y falta alguna de EMAIL_USER, EMAIL_PASS, STRIPE_SECRET_KEY

Variables comprobadas: EMAIL_USER/EMAIL_PASS, STRIPE_SECRET_KEY (+ INJECT_* / E50_* donde aplica).

python3 ejecutar_limpieza_bunker.py
"""

from __future__ import annotations

import logging
import os
import shutil
import sys
import time

ROOT = os.path.abspath(
    os.environ.get("E50_PROJECT_ROOT", os.path.expanduser("~/Projects/22TRYONYOU"))
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | [SYSTEM_CHECK] | %(message)s",
    stream=sys.stdout,
)


def _on(x: str) -> bool:
    return os.environ.get(x, "").strip().lower() in ("1", "true", "yes", "on")


def _g(*names: str) -> str:
    for n in names:
        v = os.environ.get(n, "").strip()
        if v:
            return v
    return ""


def _check_env() -> list[str]:
    missing: list[str] = []
    if not _g("EMAIL_USER", "E50_SMTP_USER"):
        missing.append("EMAIL_USER")
    if not _g("EMAIL_PASS", "E50_SMTP_PASS"):
        missing.append("EMAIL_PASS")
    if not _g("STRIPE_SECRET_KEY", "INJECT_STRIPE_SECRET_KEY", "E50_STRIPE_SECRET_KEY"):
        missing.append("STRIPE_SECRET_KEY")
    return missing


def _purge_python_caches() -> tuple[int, int]:
    """Devuelve (dirs_borrados, archivos_pyc_borrados)."""
    rm_dirs = 0
    rm_files = 0
    if not os.path.isdir(ROOT):
        return 0, 0
    for dirpath, dirnames, filenames in os.walk(ROOT, topdown=False):
        base = os.path.basename(dirpath)
        if base == "__pycache__":
            try:
                shutil.rmtree(dirpath)
                rm_dirs += 1
                logging.info("Eliminado: %s", dirpath)
            except OSError as e:
                logging.warning("No se pudo borrar %s: %s", dirpath, e)
            continue
        if base == ".pytest_cache" and dirpath.endswith(".pytest_cache"):
            try:
                shutil.rmtree(dirpath)
                rm_dirs += 1
                logging.info("Eliminado: %s", dirpath)
            except OSError as e:
                logging.warning("No se pudo borrar %s: %s", dirpath, e)
        for fn in filenames:
            if fn.endswith(".pyc"):
                fp = os.path.join(dirpath, fn)
                try:
                    os.remove(fp)
                    rm_files += 1
                except OSError as e:
                    logging.warning("No se pudo borrar %s: %s", fp, e)
    return rm_dirs, rm_files


def ejecutar_limpieza_bunker() -> int:
    logging.info("Inicio diagnóstico (ROOT=%s)", ROOT)
    logging.info("Comprobación entorno (sin imprimir secretos)...")
    time.sleep(0.3)

    missing = _check_env()
    for key in ("EMAIL_USER", "EMAIL_PASS", "STRIPE_SECRET_KEY"):
        if key in missing:
            logging.warning("Variable %s: no detectada", key)
        else:
            logging.info("Variable %s: presente", key)

    if _on("E50_PURGE_CACHE"):
        logging.info("E50_PURGE_CACHE=1 — purgando cachés Python bajo ROOT...")
        d, f = _purge_python_caches()
        logging.info("Purge hecho: %d carpetas, %d ficheros .pyc", d, f)
    else:
        logging.info("Sin E50_PURGE_CACHE=1 no se borra disco (solo diagnóstico).")

    print("\n" + "—" * 60)
    print("PYTHON DIAGNOSTICS: OK")
    print("ROOT:", ROOT)
    print("—" * 60)

    if _on("E50_STRICT") and missing:
        logging.error("E50_STRICT=1 y faltan variables: %s", ", ".join(missing))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(ejecutar_limpieza_bunker())
