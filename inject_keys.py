"""Merge claves de pago en .env desde el entorno; constants.ts sin secretos. python3 inject_keys.py"""
from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(
    os.environ.get("E50_PROJECT_ROOT", os.path.expanduser("~/Projects/22TRYONYOU"))
)

TS = """// inject_keys.py — no commitees claves; VITE_* en .env / Vercel (Paris: *_FR)
export const PLAN_100_PRICE_ID = import.meta.env.VITE_PLAN_100_ID ?? '';
const _pk =
  import.meta.env.VITE_STRIPE_PUBLIC_KEY_FR || import.meta.env.VITE_STRIPE_PUBLIC_KEY;
export const STRIPE_PUBLISHABLE_READY = Boolean(_pk && String(_pk).length > 0);
"""


def _g(*names: str) -> str:
    for n in names:
        v = os.environ.get(n, "").strip()
        if v:
            return v
    return ""


def _merge(path: str, u: dict[str, str]) -> None:
    lines: list[str] = []
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
    done: set[str] = set()
    out: list[str] = []
    for ln in lines:
        s = ln.strip()
        if s and not s.startswith("#") and "=" in s:
            k = s.split("=", 1)[0].strip()
            if k in u:
                out.append(f"{k}={u[k]}")
                done.add(k)
                continue
        out.append(ln)
    for k, v in u.items():
        if k not in done:
            if out and out[-1].strip():
                out.append("")
            out.append(f"# inject_keys ({k})")
            out.append(f"{k}={v}")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out).rstrip() + "\n")


def inject_keys() -> int:
    print("💰 Paso 2: inyectando desde entorno (merge .env)...")
    os.makedirs(ROOT, exist_ok=True)
    os.chdir(ROOT)
    u: dict[str, str] = {}
    x = _g(
        "VITE_STRIPE_PUBLIC_KEY_FR",
        "INJECT_VITE_STRIPE_PUBLIC_KEY_FR",
        "E50_VITE_STRIPE_PUBLIC_KEY_FR",
        "VITE_STRIPE_PUBLIC_KEY",
        "INJECT_VITE_STRIPE_PUBLIC_KEY",
        "E50_VITE_STRIPE_PUBLIC_KEY",
    )
    if x:
        u["VITE_STRIPE_PUBLIC_KEY_FR"] = x
    x = _g(
        "STRIPE_SECRET_KEY_FR",
        "INJECT_STRIPE_SECRET_KEY_FR",
        "E50_STRIPE_SECRET_KEY_FR",
        "STRIPE_SECRET_KEY",
        "INJECT_STRIPE_SECRET_KEY",
        "E50_STRIPE_SECRET_KEY",
    )
    if x:
        u["STRIPE_SECRET_KEY_FR"] = x
    x = _g("VITE_PLAN_100_ID", "INJECT_VITE_PLAN_100_ID", "E50_VITE_PLAN_100_ID")
    if x:
        u["VITE_PLAN_100_ID"] = x
    if u and os.environ.get("E50_SKIP_NODE_DOTENV", "").lower() not in ("1", "true", "yes", "on"):
        u["NODE_VERSION"] = os.environ.get("E50_NODE_DOTENV", "20.x").strip() or "20.x"
    if not u:
        print("⚠️  Exporta INJECT_* o E50_* para Stripe/plan.")
    else:
        _merge(os.path.join(ROOT, ".env"), u)
        print("✅ .env merge:", ", ".join(sorted(u.keys())))
    d = os.path.join(ROOT, "src", "lib")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, "constants.ts")
    with open(p, "w", encoding="utf-8") as f:
        f.write(TS)
    print("✅ src/lib/constants.ts (solo import.meta.env)")
    return 0


if __name__ == "__main__":
    sys.exit(inject_keys())
