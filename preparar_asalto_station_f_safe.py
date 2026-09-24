"""
Escribe src/components/special/StationFWelcome.tsx (bannière UI, pas géolocalisation réelle).

Git opcional: solo ese archivo (sin git add . ni shell).

- Raíz: E50_PROJECT_ROOT (por defecto ~/Projects/22TRYONYOU).
- E50_GIT_PUSH=1, E50_FORCE_PUSH=1 opcional.

Ejecutar: python3 preparar_asalto_station_f_safe.py
"""

from __future__ import annotations

import os
import subprocess
import sys

ROOT = os.path.abspath(
    os.environ.get("E50_PROJECT_ROOT", os.path.expanduser("~/Projects/22TRYONYOU"))
)

STATION_F_WELCOME_TSX = """/**
 * Bannière marketing. La géofence réelle nécessite géoloc / IP / réseau côté app ou serveur.
 */
export function StationFWelcome() {
  return (
    <div className="bg-[#E2001A] text-white p-4 text-center font-bold animate-pulse">
      BIENVENUE STATION F - PRÉCISION BIOMÉTRIQUE DISPONIBLE POUR LE LUXE
    </div>
  );
}
"""

GIT_PATHS = [
    "src/components/special/StationFWelcome.tsx",
]


def _run(argv: list[str], *, cwd: str) -> int:
    try:
        return subprocess.run(argv, cwd=cwd, check=False).returncode
    except OSError as e:
        print(f"❌ {e}")
        return 1


def _on(x: str) -> bool:
    return os.environ.get(x, "").strip().lower() in ("1", "true", "yes", "on")


def preparar_asalto_station_f_safe() -> int:
    print("🗼 Paso 47: Hook UI STATION F (sin geofencing magique en este archivo)...")

    os.makedirs(ROOT, exist_ok=True)
    os.chdir(ROOT)

    spec = os.path.join(ROOT, "src", "components", "special")
    os.makedirs(spec, exist_ok=True)
    path = os.path.join(spec, "StationFWelcome.tsx")
    with open(path, "w", encoding="utf-8") as f:
        f.write(STATION_F_WELCOME_TSX)

    print(f"✅ {os.path.relpath(path, ROOT)}")

    if not _on("E50_GIT_PUSH"):
        print("ℹ️  Sin E50_GIT_PUSH=1 no se ejecuta git.")
        return 0

    if not os.path.isdir(os.path.join(ROOT, ".git")):
        print("ℹ️  No hay .git en ROOT.")
        return 0

    exist = [p for p in GIT_PATHS if os.path.exists(os.path.join(ROOT, p))]
    if not exist:
        return 1

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
            "STRATEGY: Station F specialized landing hook active",
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

    print("\n🔥 Push completado. Monta <StationFWelcome /> donde corresponda.")
    return 0


if __name__ == "__main__":
    sys.exit(preparar_asalto_station_f_safe())
