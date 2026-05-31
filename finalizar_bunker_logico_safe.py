"""
Escribe src/data/logic_manifest.ts (manifiesto «Zéro Retour»); git opcional y acotado.

- Raíz: E50_PROJECT_ROOT (por defecto ~/Projects/22TRYONYOU).
- Git: E50_GIT_PUSH=1, solo rutas listadas (no .env); E50_FORCE_PUSH=1 para --force.

No uses git add . ni push --force a ciegas: mezcla secretos y reescribe main.

Ejecutar: python3 finalizar_bunker_logico_safe.py
"""

from __future__ import annotations

import os
import subprocess
import sys

ROOT = os.path.abspath(
    os.environ.get("E50_PROJECT_ROOT", os.path.expanduser("~/Projects/22TRYONYOU"))
)

LOGIC_MANIFEST_TS = """/**
 * Copy de posicionamiento; cifras son messaging — validar claims con legal/compliance.
 */
export const LogicData = {
  competencia: "Estimación visual basada en fotos",
  tryonyou: "Simulación biométrica con caída de tejido real",
  error_margin: "Mercado: 15% | TryOnYou: <0.3%",
  value_proposition: "Dejar de vender ropa para vender certezas",
} as const;

export type LogicManifest = typeof LogicData;
"""

GIT_PATHS = [
    "src/data/logic_manifest.ts",
]


def _run(argv: list[str], *, cwd: str) -> int:
    try:
        return subprocess.run(argv, cwd=cwd, check=False).returncode
    except OSError as e:
        print(f"❌ {e}")
        return 1


def _on(x: str) -> bool:
    return os.environ.get(x, "").strip().lower() in ("1", "true", "yes", "on")


def finalizar_bunker_logico_safe() -> int:
    print("🚀 Paso 27: Inyectando la lógica final «Zéro Retour» (manifiesto)...")

    os.makedirs(ROOT, exist_ok=True)
    os.chdir(ROOT)

    data_dir = os.path.join(ROOT, "src", "data")
    os.makedirs(data_dir, exist_ok=True)
    path = os.path.join(data_dir, "logic_manifest.ts")
    with open(path, "w", encoding="utf-8") as f:
        f.write(LOGIC_MANIFEST_TS)

    print(f"✅ {os.path.relpath(path, ROOT)}")

    if not _on("E50_GIT_PUSH"):
        print("ℹ️  Sin E50_GIT_PUSH=1 no se ejecuta git.")
        return 0

    if not os.path.isdir(os.path.join(ROOT, ".git")):
        print("ℹ️  No hay .git en ROOT.")
        return 0

    exist = [p for p in GIT_PATHS if os.path.exists(os.path.join(ROOT, p))]
    if not exist:
        print("⚠️  Nada que añadir con git")
        return 0

    if _on("E50_GIT_AUTOCRLF"):
        _run(["git", "config", "core.autocrlf", "false"], cwd=ROOT)

    if _run(["git", "add", *exist], cwd=ROOT) != 0:
        print("❌ git add falló")
        return 1

    rc = _run(
        [
            "git",
            "commit",
            "-m",
            "FINAL ARCHITECTURE: Logic-driven deployment for Paris HQ",
        ],
        cwd=ROOT,
    )
    if rc not in (0, 1):
        print("❌ git commit falló")
        return 1

    cmd = ["git", "push", "origin", "main"]
    if _on("E50_FORCE_PUSH"):
        cmd.append("--force")
    if _run(cmd, cwd=ROOT) != 0:
        print("❌ git push falló")
        return 1

    print("\n🔥 Push completado. Revisa GitHub y Vercel.")
    return 0


if __name__ == "__main__":
    sys.exit(finalizar_bunker_logico_safe())
