"""
Paso 37: vincula IDs Stripe en .env solo desde variables de entorno (merge, sin placeholders).

- Raíz: E50_PROJECT_ROOT (por defecto ~/Projects/22TRYONYOU).
- Exporta valores reales antes de ejecutar, por ejemplo:
    export INJECT_VITE_STRIPE_PUBLIC_KEY='pk_live_...'
    export INJECT_VITE_PRODUCT_98K_ID='prod_...'
    export INJECT_VITE_PRICE_98K_ID='price_...'
    export INJECT_VITE_PRICE_100_ID='price_...'
  (también acepta E50_* o las claves VITE_* ya definidas.)

Ejecutar: python3 vincular_stripe_validado.py
"""

from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(
    os.environ.get("E50_PROJECT_ROOT", os.path.expanduser("~/Projects/22TRYONYOU"))
)

# (clave en .env, nombres a buscar en os.environ)
KEYS: list[tuple[str, tuple[str, ...]]] = [
    ("VITE_STRIPE_PUBLIC_KEY", ("VITE_STRIPE_PUBLIC_KEY", "INJECT_VITE_STRIPE_PUBLIC_KEY", "E50_VITE_STRIPE_PUBLIC_KEY")),
    ("VITE_PRODUCT_98K_ID", ("VITE_PRODUCT_98K_ID", "INJECT_VITE_PRODUCT_98K_ID", "E50_VITE_PRODUCT_98K_ID")),
    ("VITE_PRICE_98K_ID", ("VITE_PRICE_98K_ID", "INJECT_VITE_PRICE_98K_ID", "E50_VITE_PRICE_98K_ID")),
    ("VITE_PRICE_100_ID", ("VITE_PRICE_100_ID", "INJECT_VITE_PRICE_100_ID", "E50_VITE_PRICE_100_ID")),
    (
        "VITE_STRIPE_CHECKOUT_98K_URL",
        (
            "VITE_STRIPE_CHECKOUT_98K_URL",
            "INJECT_VITE_STRIPE_CHECKOUT_98K_URL",
            "E50_VITE_STRIPE_CHECKOUT_98K_URL",
        ),
    ),
]


def _collect() -> dict[str, str]:
    out: dict[str, str] = {}
    for canonical, alts in KEYS:
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
            new_lines.append(f"# vincular_stripe_validado ({k})")
            new_lines.append(f"{k}={v}")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines).rstrip() + "\n")


def vincular_stripe_validado() -> int:
    print("🔗 Paso 37: Vinculando IDs Stripe validados desde el entorno (merge .env)...")

    os.makedirs(ROOT, exist_ok=True)
    os.chdir(ROOT)

    u = _collect()
    if not u:
        print(
            "⚠️  No hay IDs en el entorno. Exporta INJECT_VITE_STRIPE_PUBLIC_KEY, "
            "INJECT_VITE_PRODUCT_98K_ID, INJECT_VITE_PRICE_98K_ID, INJECT_VITE_PRICE_100_ID "
            "(opcional INJECT_VITE_STRIPE_CHECKOUT_98K_URL; o E50_* / VITE_*)."
        )
        return 1

    env_path = os.path.join(ROOT, ".env")
    _merge_dotenv(env_path, u)
    print("✅ .env actualizado:", ", ".join(sorted(u.keys())))
    print("ℹ️  Replica las mismas VITE_* en Vercel; el botón solo cobra si el checkout/backend usa esos price IDs.")
    return 0


if __name__ == "__main__":
    sys.exit(vincular_stripe_validado())
