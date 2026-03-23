"""
Inyección controlada de claves Stripe/plan (desde el entorno, no desde el código).

- Raíz: E50_PROJECT_ROOT (por defecto ~/Projects/22TRYONYOU).
- Valores: exporta antes de ejecutar, por ejemplo:
    export INJECT_VITE_STRIPE_PUBLIC_KEY='pk_live_...'
    export INJECT_STRIPE_SECRET_KEY='sk_live_...'
    export INJECT_VITE_PLAN_100_ID='price_...'
  (también acepta prefijo E50_* para la misma clave.)
- Escribe/actualiza .env local con merge (sin duplicar claves).
- NUNCA hace git add de .env.
- Git solo con E50_GIT_PUSH=1; rutas explícitas; push --force solo con E50_FORCE_PUSH=1.

Ejecutar: python3 inyectar_claves_intelligence.py
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

# (canónico .env, nombres alternativos en os.environ)
INJECT_ALIASES: list[tuple[str, tuple[str, ...]]] = [
    ("VITE_STRIPE_PUBLIC_KEY", ("INJECT_VITE_STRIPE_PUBLIC_KEY", "E50_VITE_STRIPE_PUBLIC_KEY")),
    ("STRIPE_SECRET_KEY", ("INJECT_STRIPE_SECRET_KEY", "E50_STRIPE_SECRET_KEY")),
    ("VITE_PLAN_100_ID", ("INJECT_VITE_PLAN_100_ID", "E50_VITE_PLAN_100_ID")),
]

EXAMPLE_MARK = "# --- Intelligence / Stripe (inyectar_claves_intelligence) ---\n"


def _collect() -> dict[str, str]:
    out: dict[str, str] = {}
    for canonical, alts in INJECT_ALIASES:
        for name in alts:
            v = os.environ.get(name, "").strip()
            if v:
                out[canonical] = v
                break
    return out


def _merge_dotenv(path: str, updates: dict[str, str]) -> None:
    lines: list[str] = []
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
    done: set[str] = set()
    new_lines: list[str] = []
    for ln in lines:
        s = ln.strip()
        if s and not s.startswith("#") and "=" in s:
            k = s.split("=", 1)[0].strip()
            if k in updates:
                new_lines.append(f"{k}={updates[k]}")
                done.add(k)
                continue
        new_lines.append(ln)
    for k, v in updates.items():
        if k not in done:
            if new_lines and new_lines[-1].strip():
                new_lines.append("")
            new_lines.append(f"# Jules / Intelligence merge ({k})")
            new_lines.append(f"{k}={v}")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines).rstrip() + "\n")


def _ensure_env_example(path: str) -> None:
    if not os.path.isfile(path):
        return
    with open(path, encoding="utf-8") as f:
        text = f.read()
    if "VITE_PLAN_100_ID" in text and EXAMPLE_MARK.strip() in text:
        return
    block = (
        "\n"
        + EXAMPLE_MARK
        + "# Plan Stripe (100 EUR/mes) — ID de Price del Dashboard\n"
        + "VITE_PLAN_100_ID=TU_PRICE_ID_STRIPE\n"
        + "# Secreto solo servidor (nunca VITE_); Vercel / API Python\n"
        + "STRIPE_SECRET_KEY=TU_STRIPE_SECRET_KEY\n"
    )
    with open(path, "a", encoding="utf-8") as f:
        f.write(block)


def _run(argv: list[str], *, cwd: str) -> int:
    try:
        return subprocess.run(argv, cwd=cwd, check=False).returncode
    except OSError as e:
        print(f"❌ {e}")
        return 1


def _git_on() -> bool:
    v = os.environ.get("E50_GIT_PUSH", "").strip().lower()
    return v in ("1", "true", "yes", "on")


def _force_push_on() -> bool:
    v = os.environ.get("E50_FORCE_PUSH", "").strip().lower()
    return v in ("1", "true", "yes", "on")


def inyectar_claves_intelligence() -> int:
    print("🛠️ Jules: Intelligence System — inyección controlada (claves solo desde entorno).")

    os.makedirs(ROOT, exist_ok=True)
    os.chdir(ROOT)

    updates = _collect()
    env_path = os.path.join(ROOT, ".env")
    example_path = os.path.join(ROOT, ".env.example")

    if updates:
        _merge_dotenv(env_path, updates)
        print(f"📦 .env actualizado en {env_path} ({len(updates)} clave(s)).")
    else:
        print(
            "⚠️  Ninguna clave en el entorno. Exporta INJECT_VITE_STRIPE_PUBLIC_KEY, "
            "INJECT_STRIPE_SECRET_KEY, INJECT_VITE_PLAN_100_ID (o E50_*). No se escribió .env."
        )

    _ensure_env_example(example_path)
    if os.path.isfile(example_path):
        print("📄 .env.example revisado (bloque Stripe/plan).")

    sync = {
        "source": "intelligence_system",
        "firebase_project_id": "gen-lang-client-0091228222",
        "keys_injected": list(updates.keys()),
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": "LINKED" if updates else "PENDING_ENV",
    }
    sync_path = os.path.join(ROOT, "INTELLIGENCE_SYNC.json")
    with open(sync_path, "w", encoding="utf-8") as f:
        json.dump(sync, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"✅ {sync_path}")

    if not _git_on():
        print("ℹ️  Sin E50_GIT_PUSH=1 no se ejecuta git (.env nunca se añade).")
        return 0

    if not os.path.isdir(os.path.join(ROOT, ".git")):
        print("ℹ️  No hay .git en ROOT.")
        return 0

    to_add = [p for p in (sync_path, example_path) if os.path.isfile(p)]
    if _run(["git", "add", *to_add], cwd=ROOT) != 0:
        print("❌ git add falló")
        return 1

    rc = _run(
        [
            "git",
            "commit",
            "-m",
            "INTEGRATION: Intelligence sync marker + .env.example (Stripe plan)",
        ],
        cwd=ROOT,
    )
    if rc not in (0, 1):
        print("❌ git commit falló")
        return 1

    push = ["git", "push", "origin", "main"]
    if _force_push_on():
        push.append("--force")
    if _run(push, cwd=ROOT) != 0:
        print("❌ git push falló")
        return 1

    print("\n✅ Sincronización registrada. .env sigue fuera de Git; Vercel debe tener las mismas vars.")
    return 0


if __name__ == "__main__":
    sys.exit(inyectar_claves_intelligence())
