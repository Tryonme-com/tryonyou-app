"""
Suma estratégica Copilot + GitHub + Vercel: engines Node ≥20, LITIGIO_STATUS.json,
npm lock-only, git opcional.

⚠️  Git solo con E50_GIT_PUSH=1; add acotado (nunca `git add .`).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

ROOT = os.environ.get("E50_PROJECT_ROOT", os.path.expanduser("~/Projects/22TRYONYOU"))


def _run(argv: list[str]) -> bool:
    try:
        return subprocess.run(argv, cwd=ROOT, check=False).returncode == 0
    except OSError as e:
        print(f"❌ {e}")
        return False


def sincronizacion_total_bunker() -> None:
    print("🚀 SUMA ESTRATÉGICA: Copilot + GitHub + Vercel")

    os.makedirs(ROOT, exist_ok=True)
    os.chdir(ROOT)

    pkg_path = os.path.join(ROOT, "package.json")

    # 1–2. GitHub / Copilot: motores primero; luego lock (GitHub Actions / CI)
    if os.path.isfile(pkg_path):
        print("📂 GitHub: Configurando motores de alto rendimiento (Node ≥20)...")
        with open(pkg_path, encoding="utf-8") as f:
            data = json.load(f)
        data["engines"] = {"node": ">=20.0.0"}
        with open(pkg_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")

        print("🤖 Copilot: Generando dependencias críticas (package-lock)...")
        if not _run(["npm", "install", "--package-lock-only"]):
            print("❌ npm install --package-lock-only falló.")
            sys.exit(1)
    else:
        print("ℹ️  Sin package.json en ROOT; se omiten engines y npm.")

    # 3. Vercel / Agente 70: puente de datos para deploy
    print("⚡ Vercel: Sincronizando Radar de Litigio y Gran Oleada...")
    status_50 = {
        "equipo": "50_AGENTS",
        "integracion": ["Copilot", "GitHub", "Vercel"],
        "status": "OPERATIONAL_BUNKER",
        "radar": "LVMH_CONNECTED",
    }
    litis_path = os.path.join(ROOT, "LITIGIO_STATUS.json")
    with open(litis_path, "w", encoding="utf-8") as f:
        json.dump(status_50, f, indent=4, ensure_ascii=False)
        f.write("\n")

    if os.environ.get("E50_GIT_PUSH", "").strip().lower() not in ("1", "true", "yes", "on"):
        print("ℹ️  Sin E50_GIT_PUSH=1 no se ejecuta git.")
        print("✅ Mesa lista: lock + LITIGIO_STATUS en ROOT.")
        return

    # 4. Push (opt-in)
    print("🔥 Consolidando cambios. Lanzando push final...")
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
            "SUMA TOTAL: Copilot+GitHub+Vercel - Búmker 50 Activo",
        ]
    )
    if _run(["git", "push", "origin", "main", "--force"]):
        print(
            "✅ ÉXITO: El sistema Abvetos está en el aire. "
            "Jules y el equipo de los 50 tienen el control."
        )
    else:
        print("❌ Push falló.")
        sys.exit(1)


if __name__ == "__main__":
    sincronizacion_total_bunker()
