"""
Activa el flujo de cobro (plan 100€): comprueba vars en entorno, merge seguro en .env, git acotado.

- Raíz: E50_PROJECT_ROOT (por defecto ~/Projects/22TRYONYOU).
- Plan ID: exporta INJECT_VITE_PLAN_100_ID o E50_VITE_PLAN_100_ID (nunca hardcodees price_* en código).
- Claves Stripe: comprueba VITE_STRIPE_PUBLIC_KEY / INJECT_VITE_STRIPE_PUBLIC_KEY y STRIPE_SECRET_KEY / INJECT_*.
- .env: solo merge; nunca se hace git add de .env.
- Git: E50_GIT_PUSH=1; rutas explícitas; --force solo con E50_FORCE_PUSH=1.

Ejecutar: python3 activar_flujo_dinero.py
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


def _get(name: str, *alts: str) -> str:
    for n in (name,) + alts:
        v = os.environ.get(n, "").strip()
        if v:
            return v
    return ""


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
            new_lines.append(f"# activar_flujo_dinero ({k})")
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


def activar_flujo_dinero() -> int:
    print("🚀 Verificando conexión con la pasarela (entorno + merge local)...")

    os.makedirs(ROOT, exist_ok=True)
    os.chdir(ROOT)

    pk = _get("VITE_STRIPE_PUBLIC_KEY", "INJECT_VITE_STRIPE_PUBLIC_KEY", "E50_VITE_STRIPE_PUBLIC_KEY")
    sk = _get("STRIPE_SECRET_KEY", "INJECT_STRIPE_SECRET_KEY", "E50_STRIPE_SECRET_KEY")
    plan = _get("VITE_PLAN_100_ID", "INJECT_VITE_PLAN_100_ID", "E50_VITE_PLAN_100_ID")

    if pk:
        print("✅ Clave publicable Stripe: presente en entorno.")
    else:
        print("⚠️  Falta clave publicable (VITE_STRIPE_PUBLIC_KEY o INJECT_VITE_STRIPE_PUBLIC_KEY).")

    if sk:
        print("✅ Secreto Stripe: presente en entorno (solo servidor / Vercel).")
    else:
        print("⚠️  Falta STRIPE_SECRET_KEY en entorno local (puede estar solo en Vercel).")

    if not plan:
        print(
            "❌ Falta ID del plan de 100€. Exporta INJECT_VITE_PLAN_100_ID=price_... "
            "(el real del Dashboard de Stripe)."
        )
        return 1

    print("✅ VITE_PLAN_100_ID recibido desde el entorno (no se usa un price inventado en código).")

    updates = {"VITE_PLAN_100_ID": plan}
    if pk:
        updates["VITE_STRIPE_PUBLIC_KEY"] = pk
    if sk:
        updates["STRIPE_SECRET_KEY"] = sk

    env_path = os.path.join(ROOT, ".env")
    _merge_dotenv(env_path, updates)
    print(f"📦 .env actualizado (merge) en {env_path}")

    state = {
        "flow": "MONEY_100EUR_PARIS",
        "plan_id_configured": True,
        "publishable_in_env": bool(pk),
        "secret_in_env": bool(sk),
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "reminder": "Replica VITE_* y STRIPE_SECRET_KEY en Vercel; no subas .env.",
    }
    out_json = os.path.join(ROOT, "MONEY_FLOW_ACTIVATION.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"✅ {out_json}")

    if not _git_on():
        print("ℹ️  Sin E50_GIT_PUSH=1 no se ejecuta git (.env no se versiona).")
        print("\n✅ Listo en local. Configura las mismas variables en Vercel para tráfico real.")
        return 0

    if not os.path.isdir(os.path.join(ROOT, ".git")):
        print("ℹ️  No hay .git en ROOT.")
        return 0

    candidates = [
        "MONEY_FLOW_ACTIVATION.json",
        "MONEY_FLOW.json",
        "src/lib/stripe.ts",
        "STRIPE_ACTIVE_PLAN.json",
        "package.json",
        "package-lock.json",
        ".env.example",
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
            "MONEY: Activating 100EUR payment flow marker (no secrets)",
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

    print("\n✅ Cambios seguros subidos. El cobro real depende de Vercel + sesión Checkout en backend.")
    return 0


if __name__ == "__main__":
    sys.exit(activar_flujo_dinero())
