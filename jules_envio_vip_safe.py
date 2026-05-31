"""
Genera src/data/vip_access_list.json (manifiesto demo de marcas); git opcional y acotado.

Los slugs en cliente no son secretos: la autorización real debe ser en servidor.

- Raíz: E50_PROJECT_ROOT (por defecto ~/Projects/22TRYONYOU).
- Git: E50_GIT_PUSH=1, solo vip_access_list.json; E50_FORCE_PUSH=1 opcional.

Ejecutar: python3 jules_envio_vip_safe.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

ROOT = os.path.abspath(
    os.environ.get("E50_PROJECT_ROOT", os.path.expanduser("~/Projects/22TRYONYOU"))
)

INVITADOS = [
    "LVMH",
    "Kering",
    "Balmain",
    "Chanel",
    "Dior",
    "Hermès",
    "Lafayette",
    "Printemps",
    "Farfetch",
    "Zalando",
    "Le Bon Marché",
    "Vivienne",
]

GIT_PATHS = [
    "src/data/vip_access_list.json",
]


def _run(argv: list[str], *, cwd: str) -> int:
    try:
        return subprocess.run(argv, cwd=cwd, check=False).returncode
    except OSError as e:
        print(f"❌ {e}")
        return 1


def _on(x: str) -> bool:
    return os.environ.get(x, "").strip().lower() in ("1", "true", "yes", "on")


def jules_envio_vip_safe() -> int:
    print("🤖 Jules: Procesando invitaciones VIP para las 12 corporaciones (modo seguro)...")

    os.makedirs(ROOT, exist_ok=True)
    os.chdir(ROOT)

    invitation_slugs: dict[str, str] = {}
    for company in INVITADOS:
        slug_key = (
            company.upper()
            .replace("È", "E")
            .replace("É", "E")
            .replace("Ê", "E")
            .replace("'", "")
            .replace(" ", "_")
        )
        invitation_slugs[company] = f"VIP_ACCESS_{slug_key}_2026"

    payload = {
        "_meta": {
            "warning": (
                "Solo datos de UI/demo visibles en el cliente. "
                "No usar estos slugs como tokens de autenticación; validar en backend."
            ),
            "version": 1,
        },
        "invitations": invitation_slugs,
    }

    data_dir = os.path.join(ROOT, "src", "data")
    os.makedirs(data_dir, exist_ok=True)
    path = os.path.join(data_dir, "vip_access_list.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        f.write("\n")

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
            "JULES: VIP Friends access tokens deployed for 12 Target Companies",
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

    print(f"\n✅ Push completado. {len(INVITADOS)} marcas en el manifiesto (revisa backend).")
    return 0


if __name__ == "__main__":
    sys.exit(jules_envio_vip_safe())
