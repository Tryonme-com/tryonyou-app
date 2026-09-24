"""
Paso 32: radar + claves reales (merge .env); JSON público para la UI; git acotado (sin .env).

- RADAR_STATUS: variable de entorno RADAR_STATUS o E50_RADAR_STATUS; si vacío, valor por defecto no secreto.
- VITE_PLAN_98K_ID: solo si exportas INJECT_VITE_PLAN_98K_ID / E50_* / VITE_PLAN_98K_ID (nunca placeholders en código).
- Raíz: E50_PROJECT_ROOT (por defecto ~/Projects/22TRYONYOU).
- Git: E50_GIT_PUSH=1, solo src/data/bunker_radar_sync.json; E50_FORCE_PUSH=1 opcional.

Ejecutar: python3 sincronizar_bunker_total_safe.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone

ROOT = os.path.abspath(
    os.environ.get("E50_PROJECT_ROOT", os.path.expanduser("~/Projects/22TRYONYOU"))
)

DEFAULT_RADAR = "ACTIVE_LITIGATION_MONITORING_PARIS"

GIT_PATHS = [
    "src/data/bunker_radar_sync.json",
]


def _g(*names: str) -> str:
    for n in names:
        v = os.environ.get(n, "").strip()
        if v:
            return v
    return ""


def _run(argv: list[str], *, cwd: str) -> int:
    try:
        return subprocess.run(argv, cwd=cwd, check=False).returncode
    except OSError as e:
        print(f"❌ {e}")
        return 1


def _on(x: str) -> bool:
    return os.environ.get(x, "").strip().lower() in ("1", "true", "yes", "on")


def sincronizar_bunker_total_safe() -> int:
    print("🚀 Paso 32: Sincronizando radar y claves (modo seguro)...")

    os.makedirs(ROOT, exist_ok=True)
    os.chdir(ROOT)

    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)
    import inject_keys

    radar = _g("RADAR_STATUS", "E50_RADAR_STATUS") or DEFAULT_RADAR
    updates: dict[str, str] = {"RADAR_STATUS": radar}

    plan98 = _g(
        "VITE_PLAN_98K_ID",
        "INJECT_VITE_PLAN_98K_ID",
        "E50_VITE_PLAN_98K_ID",
    )
    if plan98:
        updates["VITE_PLAN_98K_ID"] = plan98
    else:
        print(
            "ℹ️  Sin VITE_PLAN_98K_ID en el entorno: no se escribe ningún price ID "
            "(exporta el price real de Stripe si lo necesitas en .env)."
        )

    env_path = os.path.join(ROOT, ".env")
    inject_keys._merge(env_path, updates)
    print(f"✅ .env merge: {', '.join(sorted(updates.keys()))}")

    data_dir = os.path.join(ROOT, "src", "data")
    os.makedirs(data_dir, exist_ok=True)
    public_path = os.path.join(data_dir, "bunker_radar_sync.json")
    payload = {
        "radar_status": radar,
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    with open(public_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"✅ {os.path.relpath(public_path, ROOT)} (apt para commit; sin secretos)")

    if not _on("E50_GIT_PUSH"):
        print("ℹ️  Sin E50_GIT_PUSH=1 no se ejecuta git (.env no se sube).")
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
            "FINAL DELIVERY: Authority, Revenue Flow 98k/100, and Paris Radar Active",
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

    print("\n🔥 Push completado. Replica RADAR_STATUS / VITE_* en Vercel.")
    return 0


if __name__ == "__main__":
    sys.exit(sincronizar_bunker_total_safe())
