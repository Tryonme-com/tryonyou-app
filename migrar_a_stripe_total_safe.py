"""
Escribe src/config/payment_settings.ts (Stripe como proveedor; importes y URL vía env).

No incrustes enlaces de checkout en el repo: usa VITE_STRIPE_CHECKOUT_URL (o la que ya uses).

- Raíz: E50_PROJECT_ROOT (por defecto ~/Projects/22TRYONYOU).
- Git: E50_GIT_PUSH=1, solo payment_settings.ts; E50_FORCE_PUSH=1 opcional.

Ejecutar: python3 migrar_a_stripe_total_safe.py
"""

from __future__ import annotations

import os
import subprocess
import sys

ROOT = os.path.abspath(
    os.environ.get("E50_PROJECT_ROOT", os.path.expanduser("~/Projects/22TRYONYOU"))
)

PAYMENT_SETTINGS_TS = """/**
 * Proveedor Stripe; estado y enlace reales desde variables Vite / Vercel.
 * Importe 141.986 EUR = cifra de negocio documentada; validar en backend al cobrar.
 */
export const PAYMENT_CONFIG = {
  provider: "STRIPE" as const,
  accountStatus:
    (import.meta.env.VITE_PAYMENT_ACCOUNT_STATUS as string | undefined) ?? "UNKNOWN",
  enterpriseInvoiceEur: 141_986,
  currency: "EUR" as const,
  stripeCheckoutUrl:
    (import.meta.env.VITE_STRIPE_CHECKOUT_URL as string | undefined) ??
    (import.meta.env.VITE_STRIPE_CHECKOUT_98K_URL as string | undefined) ??
    "",
  revolutBackup: false as const,
} as const;
"""

GIT_PATHS = [
    "src/config/payment_settings.ts",
]


def _run(argv: list[str], *, cwd: str) -> int:
    try:
        return subprocess.run(argv, cwd=cwd, check=False).returncode
    except OSError as e:
        print(f"❌ {e}")
        return 1


def _on(x: str) -> bool:
    return os.environ.get(x, "").strip().lower() in ("1", "true", "yes", "on")


def migrar_a_stripe_total_safe() -> int:
    print("🔄 Paso 46: Migrando configuración de pagos hacia Stripe (modo seguro)...")

    os.makedirs(ROOT, exist_ok=True)
    os.chdir(ROOT)

    cfg = os.path.join(ROOT, "src", "config")
    os.makedirs(cfg, exist_ok=True)
    path = os.path.join(cfg, "payment_settings.ts")
    with open(path, "w", encoding="utf-8") as f:
        f.write(PAYMENT_SETTINGS_TS)

    print(f"✅ {os.path.relpath(path, ROOT)}")
    print(
        "🤖 Jules: define VITE_STRIPE_CHECKOUT_URL (o VITE_STRIPE_CHECKOUT_98K_URL) "
        "y VITE_PAYMENT_ACCOUNT_STATUS en Vercel."
    )

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
            "PAYMENT: Revolut bypass - Stripe direct flow activated for 141k",
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

    print("\n✅ Push completado. El cobro real sigue dependiendo de Checkout/PI en servidor.")
    return 0


if __name__ == "__main__":
    sys.exit(migrar_a_stripe_total_safe())
