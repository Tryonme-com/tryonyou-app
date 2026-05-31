"""
Despliegue «victoria»: commit + push acotado (sin git add . ni shell).

- Raíz: E50_PROJECT_ROOT (por defecto ~/Projects/22TRYONYOU).
- E50_GIT_PUSH=1 obligatorio. E50_FORCE_PUSH=1 para --force.
- E50_VICTORIA_PATHS='a,b,c' sustituye la lista por defecto.
- E50_GIT_COMMIT_MSG sobrescribe el mensaje (por defecto GOLDEN_PEACOCK…).

Ejecutar: E50_GIT_PUSH=1 python3 despliegue_victoria_safe.py
"""

from __future__ import annotations

import os
import subprocess
import sys

ROOT = os.path.abspath(
    os.environ.get("E50_PROJECT_ROOT", os.path.expanduser("~/Projects/22TRYONYOU"))
)

DEFAULT_PATHS = [
    "vercel.json",
    "api/index.py",
    "src/lib/licence_check.ts",
    "src/lib/constants.ts",
    "src/lib/patent_guard.ts",
    "src/lib/instantPay.ts",
    "src/components/LicenceGuard.tsx",
    "src/config/pricing.json",
    "src/config/pricing_logic.json",
    "src/config/security_audit.json",
    "src/data/bunker_radar_sync.json",
    "src/lib/pilot/lafayetteEngine.ts",
    "src/locales/fr_luxe.ts",
    "src/lib/utils/qrGenerator.ts",
]


def _run(argv: list[str], *, cwd: str) -> int:
    try:
        return subprocess.run(argv, cwd=cwd, check=False).returncode
    except OSError as e:
        print(f"❌ {e}")
        return 1


def _on(x: str) -> bool:
    return os.environ.get(x, "").strip().lower() in ("1", "true", "yes", "on")


def _paths() -> list[str]:
    raw = os.environ.get("E50_VICTORIA_PATHS", "").strip()
    if raw:
        return [p.strip() for p in raw.split(",") if p.strip()]
    return list(DEFAULT_PATHS)


def _commit_msg() -> str:
    return (
        os.environ.get("E50_GIT_COMMIT_MSG", "").strip()
        or "GOLDEN_PEACOCK: Final operational bunker - Paris Ready"
    )


def despliegue_victoria_safe() -> int:
    print("🚀 Paso 44: Lanzando despliegue de victoria a París (git acotado)...")

    os.makedirs(ROOT, exist_ok=True)
    os.chdir(ROOT)

    if not _on("E50_GIT_PUSH"):
        print("ℹ️  Define E50_GIT_PUSH=1 para ejecutar git.")
        return 0

    if not os.path.isdir(os.path.join(ROOT, ".git")):
        print("ℹ️  No hay .git en ROOT.")
        return 0

    candidates = _paths()
    exist = [p for p in candidates if os.path.exists(os.path.join(ROOT, p))]
    if not exist:
        print("⚠️  Ninguna ruta de la lista existe. Ajusta E50_VICTORIA_PATHS o genera archivos.")
        print(f"   Buscadas: {', '.join(candidates)}")
        return 1

    if _on("E50_GIT_AUTOCRLF"):
        _run(["git", "config", "core.autocrlf", "false"], cwd=ROOT)

    if _run(["git", "add", *exist], cwd=ROOT) != 0:
        print("❌ git add falló")
        return 1

    rc = _run(["git", "commit", "-m", _commit_msg()], cwd=ROOT)
    if rc not in (0, 1):
        print("❌ git commit falló")
        return 1

    cmd = ["git", "push", "origin", "main"]
    if _on("E50_FORCE_PUSH"):
        cmd.append("--force")
    if _run(cmd, cwd=ROOT) != 0:
        print("❌ git push falló")
        return 1

    print("\n🔥 Push completado. Revisa Vercel.")
    return 0


if __name__ == "__main__":
    sys.exit(despliegue_victoria_safe())
