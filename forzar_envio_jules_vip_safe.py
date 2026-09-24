"""
Git acotado para manifiesto VIP + maqueta Bpifrance (sin git add . ni shell).

No envía correos ni notifica a Bpifrance: solo sube archivos del repo.

- Raíz: E50_PROJECT_ROOT (por defecto ~/Projects/22TRYONYOU).
- E50_GIT_PUSH=1 obligatorio. E50_FORCE_PUSH=1 opcional.
- E50_JULES_FORCE_PATHS='a,b,c' sustituye la lista.

Ejecutar: E50_GIT_PUSH=1 python3 forzar_envio_jules_vip_safe.py
"""

from __future__ import annotations

import os
import subprocess
import sys

ROOT = os.path.abspath(
    os.environ.get("E50_PROJECT_ROOT", os.path.expanduser("~/Projects/22TRYONYOU"))
)

DEFAULT_PATHS = [
    "src/data/vip_access_list.json",
    "src/components/BpiAdminPortal.tsx",
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
    raw = os.environ.get("E50_JULES_FORCE_PATHS", "").strip()
    if raw:
        return [p.strip() for p in raw.split(",") if p.strip()]
    return list(DEFAULT_PATHS)


def _commit_msg() -> str:
    return (
        os.environ.get("E50_GIT_COMMIT_MSG", "").strip()
        or "JULES_FORCE: VIP Tokens dispatched to LVMH, Balmain, Kering & Bpifrance targets"
    )


def forzar_envio_jules_vip_safe() -> int:
    print("🤖 Jules: Push acotado (VIP + portal Bpifrance maqueta)...")

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
        print("⚠️  Ninguna ruta existe. Ejecuta jules_envio_vip / inyectar_portal_bpi_safe o ajusta E50_JULES_FORCE_PATHS.")
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

    print("\n🔥 Push completado. Invitaciones reales = backend + email/CRM, no git.")
    return 0


if __name__ == "__main__":
    sys.exit(forzar_envio_jules_vip_safe())
