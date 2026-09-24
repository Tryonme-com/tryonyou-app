"""
Auditoría heurística en src/ (TS/TSX/PY): busca cadenas asociadas a bypass / demo.

Muchos matches son falsos positivos (p. ej. "free" en texto). Revisa cada hallazgo.

  E50_PROJECT_ROOT — raíz del proyecto
  E50_GIT_PUSH=1 — tras auditar, git add + commit solo src/data/mesa_listos_audit.json
  E50_GIT_COMMIT_MSG — mensaje (opcional)

python3 auditar_mesa_de_los_listos.py
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

ROOT = os.path.abspath(
    os.environ.get("E50_PROJECT_ROOT", os.path.expanduser("~/Projects/22TRYONYOU"))
)

SKIP_DIR_NAMES = frozenset(
    {
        "node_modules",
        ".git",
        "__pycache__",
        ".venv",
        "venv",
        "dist",
        "build",
        ".tox",
    }
)

# Límites de palabra para reducir ruido; ajusta según tu codebase.
PATRONES = [
    (r"\bfree\b", "free"),
    (r"\bdemo_unlocked\b", "demo_unlocked"),
    (r"\bbypass_payment\b", "bypass_payment"),
    (r"\btest_user\b", "test_user"),
]


def _on(x: str) -> bool:
    return os.environ.get(x, "").strip().lower() in ("1", "true", "yes", "on")


def _run(argv: list[str], *, cwd: str) -> int:
    try:
        return subprocess.run(argv, cwd=cwd, check=False).returncode
    except OSError as e:
        print(f"❌ {e}")
        return 1


def auditar_mesa_de_los_listos() -> int:
    print("💎 Auditoría «Mesa de los Listos» (heurística, revisar manualmente)...")

    src = os.path.join(ROOT, "src")
    if not os.path.isdir(src):
        print(f"⚠️  No existe {src} — nada que auditar.")
        return 0

    hallazgos: list[dict[str, str]] = []
    for dirpath, dirnames, filenames in os.walk(src, topdown=True):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIR_NAMES]
        for fn in filenames:
            if not fn.endswith((".tsx", ".ts", ".py")):
                continue
            ruta = os.path.join(dirpath, fn)
            try:
                with open(ruta, encoding="utf-8") as f:
                    contenido = f.read()
            except OSError as e:
                print(f"⚠️  No se pudo leer {ruta}: {e}")
                continue
            for rx, nombre in PATRONES:
                if re.search(rx, contenido, re.IGNORECASE):
                    rel = os.path.relpath(ruta, ROOT)
                    hallazgos.append({"file": rel, "pattern": nombre})
                    print(f"⚠️  Posible punto a revisar: {rel} (patrón: {nombre})")

    report_path = os.path.join(ROOT, "src", "data", "mesa_listos_audit.json")
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    payload = {
        "_note": "Heurística; cada match puede ser falso positivo (comentarios, i18n, etc.).",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "root": ROOT,
        "findings_count": len(hallazgos),
        "findings": hallazgos,
    }
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"\n📄 Informe: {os.path.relpath(report_path, ROOT)}")

    if not hallazgos:
        print("✅ Ningún patrón coincidente (con estos regex). El código puede seguir teniendo otras fugas.")
    else:
        print(f"❌ ATENCIÓN: {len(hallazgos)} coincidencias (revisar manualmente).")

    if not _on("E50_GIT_PUSH"):
        print("ℹ️  Sin E50_GIT_PUSH=1 no se ejecuta git (no se usa git add .).")
        return 0

    if not os.path.isdir(os.path.join(ROOT, ".git")):
        print("ℹ️  No hay .git en ROOT.")
        return 0

    msg = (
        os.environ.get("E50_GIT_COMMIT_MSG", "").strip()
        or f"CONSOLIDATION: Table of the Wise Protocol {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%MZ')}"
    )
    rel_report = os.path.relpath(report_path, ROOT)
    if _on("E50_GIT_AUTOCRLF"):
        _run(["git", "config", "core.autocrlf", "false"], cwd=ROOT)
    if _run(["git", "add", rel_report], cwd=ROOT) != 0:
        print("❌ git add falló")
        return 1
    rc = _run(["git", "commit", "-m", msg], cwd=ROOT)
    if rc not in (0, 1):
        print("❌ git commit falló")
        return 1
    print("🏛️  Commit creado (solo mesa_listos_audit.json).")
    return 0


if __name__ == "__main__":
    sys.exit(auditar_mesa_de_los_listos())
