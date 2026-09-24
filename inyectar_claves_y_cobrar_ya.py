"""
Equipo 50: merge de claves Stripe/plan en .env local + marcador de flujo de cobro.

⚠️  NUNCA hagas `git add .env`: subiría secretos al remoto.
⚠️  No uses `open(".env", "w")` sin merge: borraría Firebase, ABVET, etc.

- Raíz: E50_PROJECT_ROOT (por defecto ~/Projects/22TRYONYOU).
- Claves (mismo criterio que inyectar_claves_intelligence.py):
    INJECT_VITE_STRIPE_PUBLIC_KEY, INJECT_STRIPE_SECRET_KEY, INJECT_VITE_PLAN_100_ID
    (o equivalentes E50_*).
- NODE_VERSION en .env: por defecto 20.x (merge); desactiva con E50_SKIP_NODE_DOTENV=1.
- Git solo con E50_GIT_PUSH=1; rutas explícitas; .env excluido; --force con E50_FORCE_PUSH=1.

Ejecutar desde cualquier sitio:
  python3 /Users/mac/tryonyou-app/inyectar_claves_y_cobrar_ya.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone

# Mismo directorio que inyectar_claves_intelligence.py
try:
    from inyectar_claves_intelligence import ROOT, _collect, _merge_dotenv
except ImportError:
    ROOT = os.path.abspath(
        os.environ.get("E50_PROJECT_ROOT", os.path.expanduser("~/Projects/22TRYONYOU"))
    )

    def _collect() -> dict[str, str]:
        out: dict[str, str] = {}
        pairs = [
            ("VITE_STRIPE_PUBLIC_KEY", ("INJECT_VITE_STRIPE_PUBLIC_KEY", "E50_VITE_STRIPE_PUBLIC_KEY")),
            ("STRIPE_SECRET_KEY", ("INJECT_STRIPE_SECRET_KEY", "E50_STRIPE_SECRET_KEY")),
            ("VITE_PLAN_100_ID", ("INJECT_VITE_PLAN_100_ID", "E50_VITE_PLAN_100_ID")),
        ]
        for canonical, alts in pairs:
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
                new_lines.append(f"# merge ({k})")
                new_lines.append(f"{k}={v}")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(new_lines).rstrip() + "\n")


def _run(argv: list[str], *, cwd: str) -> int:
    try:
        return subprocess.run(argv, cwd=cwd, check=False).returncode
    except OSError as e:
        print(f"❌ {e}")
        return 1


def _git_on() -> bool:
    return os.environ.get("E50_GIT_PUSH", "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


def _force_push_on() -> bool:
    return os.environ.get("E50_FORCE_PUSH", "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


def inyectar_claves_y_cobrar_ya() -> int:
    print("🚀 EQUIPO 50: extrayendo claves del entorno (Intelligence / CI), merge en .env local.")

    os.makedirs(ROOT, exist_ok=True)
    os.chdir(ROOT)

    updates = _collect()

    if not updates.get("VITE_STRIPE_PUBLIC_KEY") or not updates.get("STRIPE_SECRET_KEY"):
        print("⚠️  Advertencia: faltan INJECT_VITE_STRIPE_PUBLIC_KEY y/o INJECT_STRIPE_SECRET_KEY.")
        print("🛠️  Jules: modo merge — el resto del .env no se toca; solo se actualizan claves presentes.")

    # NODE_VERSION solo si ya hay algo que inyectar (evita tocar .env al ejecutar sin claves).
    if updates and os.environ.get("E50_SKIP_NODE_DOTENV", "").strip().lower() not in (
        "1",
        "true",
        "yes",
        "on",
    ):
        updates["NODE_VERSION"] = os.environ.get("E50_NODE_DOTENV", "20.x").strip() or "20.x"

    env_path = os.path.join(ROOT, ".env")
    if updates:
        _merge_dotenv(env_path, updates)
        print(f"📦 .env actualizado (merge) en {env_path}")
    else:
        print("⚠️  Nada que escribir en .env: exporta al menos una clave INJECT_* o E50_*.")

    marker = {
        "flow": "MONEY_FLOW_100EUR",
        "status": "ACTIVE" if updates.get("VITE_PLAN_100_ID") else "PENDING_PRICE_ID",
        "has_publishable": bool(updates.get("VITE_STRIPE_PUBLIC_KEY")),
        "has_secret": bool(updates.get("STRIPE_SECRET_KEY")),
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "note": "STRIPE_SECRET_KEY solo servidor; configura el mismo valor en Vercel. No subas .env.",
    }
    marker_path = os.path.join(ROOT, "MONEY_FLOW.json")
    with open(marker_path, "w", encoding="utf-8") as f:
        json.dump(marker, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"✅ {marker_path}")

    print("🧹 Producción: Vercel usa variables del dashboard; el push solo lleva código + marcadores seguros.")

    if not _git_on():
        print("ℹ️  Sin E50_GIT_PUSH=1 no se ejecuta git (recomendado: nunca añadir .env).")
        print("\n💰 Local: con claves en .env, Vite puede usar VITE_*; cobro real exige Checkout en backend.")
        return 0

    if not os.path.isdir(os.path.join(ROOT, ".git")):
        print("ℹ️  No hay .git en ROOT.")
        return 0

    candidates = [
        "MONEY_FLOW.json",
        "INTELLIGENCE_SYNC.json",
        "STRIPE_ACTIVE_PLAN.json",
        "src/lib/stripe.ts",
        "package.json",
        "package-lock.json",
        ".env.example",
        ".gitignore",
    ]
    to_add = [p for p in candidates if os.path.exists(os.path.join(ROOT, p))]

    if _run(["git", "add", *to_add], cwd=ROOT) != 0:
        print("❌ git add falló")
        return 1

    rc = _run(
        [
            "git",
            "commit",
            "-m",
            "MONEY_FLOW: Active 100EUR plan marker (no secrets in repo)",
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

    print("\n💰 Marcador de flujo subido. Configura las mismas vars en Vercel para cobro en producción.")
    return 0


if __name__ == "__main__":
    sys.exit(inyectar_claves_y_cobrar_ya())
