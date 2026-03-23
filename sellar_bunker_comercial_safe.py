"""
Versión segura del flujo «sellar búnker»: merge .env desde el entorno (sin placeholders),
licence_check.ts sin URLs inventadas, git solo con flags y rutas explícitas (sin .env).

Antes de ejecutar (ejemplo):
  export E50_PROJECT_ROOT='/Users/mac/tryonyou-app'
  export INJECT_VITE_STRIPE_PUBLIC_KEY='pk_live_...'
  export INJECT_VITE_PRODUCT_98K_ID='prod_...'
  export INJECT_VITE_PRICE_98K_ID='price_...'
  export INJECT_VITE_PRICE_100_ID='price_...'
  # opcional: enlace de pago 98k (Payment Link / Checkout)
  export INJECT_VITE_STRIPE_CHECKOUT_98K_URL='https://buy.stripe.com/...'

Git (opcional): E50_GIT_PUSH=1, E50_FORCE_PUSH=1 solo si lo necesitas de verdad.

Ejecutar: python3 sellar_bunker_comercial_safe.py
"""

from __future__ import annotations

import os
import subprocess
import sys

ROOT = os.path.abspath(
    os.environ.get("E50_PROJECT_ROOT", os.path.expanduser("~/Projects/22TRYONYOU"))
)

LICENCE_CHECK_TS = """/**
 * Muro de acceso (cliente): la URL de pago viene de VITE_STRIPE_CHECKOUT_98K_URL.
 * Autorización real: backend + webhooks Stripe.
 */
const checkout98k = import.meta.env.VITE_STRIPE_CHECKOUT_98K_URL ?? "";

export type AccessState =
  | { status: "LOCKED"; required: string; action: string }
  | { status: "ACTIVE"; fee: string };

export function checkAccess(hasPaid98k: boolean): AccessState {
  if (!hasPaid98k) {
    return {
      status: "LOCKED",
      required: "98.000€ Licence Fee",
      action: checkout98k,
    };
  }
  return { status: "ACTIVE", fee: "100€/month" };
}
"""

GIT_PATHS = [
    "src/lib/licence_check.ts",
]


def _run(argv: list[str], *, cwd: str) -> int:
    try:
        return subprocess.run(argv, cwd=cwd, check=False).returncode
    except OSError as e:
        print(f"❌ {e}")
        return 1


def _on(x: str) -> bool:
    return os.environ.get(x, "").strip().lower() in ("1", "true", "yes", "on")


def _core_stripe_env_ok(keys_module) -> bool:
    """Exige las 4 claves núcleo en el entorno (no placeholders en el repo)."""
    for canonical, alts in keys_module.KEYS[:4]:
        if not any(os.environ.get(n, "").strip() for n in alts):
            print(f"⚠️  Falta en el entorno: {canonical} (INJECT_* / E50_* / VITE_*).")
            return False
    return True


def sellar_bunker_comercial_safe() -> int:
    print("🛠️  Sellado búnker (seguro): Stripe desde entorno + licence_check.ts...")

    os.makedirs(ROOT, exist_ok=True)
    os.chdir(ROOT)

    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)

    import inject_keys
    import vincular_stripe_validado as vs

    if not _core_stripe_env_ok(vs):
        return 1

    rc = vs.vincular_stripe_validado()
    if rc != 0:
        return rc

    if os.environ.get("E50_SKIP_NODE_DOTENV", "").lower() not in ("1", "true", "yes", "on"):
        nv = os.environ.get("E50_NODE_DOTENV", "20.x").strip() or "20.x"
        inject_keys._merge(os.path.join(ROOT, ".env"), {"NODE_VERSION": nv})

    lib = os.path.join(ROOT, "src", "lib")
    os.makedirs(lib, exist_ok=True)
    lc = os.path.join(lib, "licence_check.ts")
    with open(lc, "w", encoding="utf-8") as f:
        f.write(LICENCE_CHECK_TS)
    print("✅ src/lib/licence_check.ts")

    if not _on("E50_GIT_PUSH"):
        print("ℹ️  Sin E50_GIT_PUSH=1 no se ejecuta git (.env no se commitea).")
        return 0

    if not os.path.isdir(os.path.join(ROOT, ".git")):
        print("ℹ️  No hay .git en ROOT.")
        return 0

    exist = [p for p in GIT_PATHS if os.path.exists(os.path.join(ROOT, p))]
    if not exist:
        print("⚠️  Nada que añadir con git")
        return 0

    if _run(["git", "add", *exist], cwd=ROOT) != 0:
        print("❌ git add falló")
        return 1

    cr = _run(
        [
            "git",
            "commit",
            "-m",
            "CORE: licence_check + Stripe env (98k/100); sin secretos en repo",
        ],
        cwd=ROOT,
    )
    if cr not in (0, 1):
        print("❌ git commit falló")
        return 1

    cmd = ["git", "push", "origin", "main"]
    if _on("E50_FORCE_PUSH"):
        cmd.append("--force")
    if _run(cmd, cwd=ROOT) != 0:
        print("❌ git push falló")
        return 1

    print("\n🔥 Push completado. Revisa Vercel y variables VITE_* allí.")
    return 0


if __name__ == "__main__":
    sys.exit(sellar_bunker_comercial_safe())
