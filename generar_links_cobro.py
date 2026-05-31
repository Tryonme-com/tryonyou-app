"""
Genera src/constants/stripe_links.ts y src/components/SubscriptionPanel.tsx.

Los Payment Links reales van en Vite/Vercel (no en código):
  VITE_STRIPE_LINK_MAINTENANCE_100
  VITE_STRIPE_LINK_ENTERPRISE_141K

- Raíz: E50_PROJECT_ROOT (por defecto ~/Projects/22TRYONYOU).

Ejecutar: python3 generar_links_cobro.py
"""

from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(
    os.environ.get("E50_PROJECT_ROOT", os.path.expanduser("~/Projects/22TRYONYOU"))
)

STRIPE_LINKS_TS = """/**
 * URLs de Payment Link / Checkout; definir en .env / Vercel (VITE_*).
 */
const maintenance =
  (import.meta.env.VITE_STRIPE_LINK_MAINTENANCE_100 as string | undefined) ?? "";
const enterprise =
  (import.meta.env.VITE_STRIPE_LINK_ENTERPRISE_141K as string | undefined) ?? "";

export const STRIPE_LINKS = {
  MAINTENANCE_100: maintenance,
  ENTERPRISE_141K: enterprise,
  currency: "EUR" as const,
} as const;
"""

SUBSCRIPTION_PANEL_TSX = """import React from "react";
import { STRIPE_LINKS } from "../constants/stripe_links";

export function SubscriptionPanel() {
  const hasMaintenance = STRIPE_LINKS.MAINTENANCE_100.length > 0;
  const hasEnterprise = STRIPE_LINKS.ENTERPRISE_141K.length > 0;

  return (
    <div className="bg-black text-white p-10 border-2 border-amber-500 shadow-2xl">
      <h2 className="text-2xl font-serif mb-6 text-center">
        ACCÈS INFRASTRUCTURE TRYONYOU
      </h2>
      {!hasMaintenance && !hasEnterprise ? (
        <p className="text-center text-amber-200 text-sm mb-6">
          Configure VITE_STRIPE_LINK_MAINTENANCE_100 et
          VITE_STRIPE_LINK_ENTERPRISE_141K (Vercel).
        </p>
      ) : null}
      <div className="flex flex-col gap-6">
        <a
          href={hasMaintenance ? STRIPE_LINKS.MAINTENANCE_100 : undefined}
          aria-disabled={!hasMaintenance}
          className={
            "py-4 text-center font-bold transition " +
            (hasMaintenance
              ? "bg-white text-black hover:bg-gray-200"
              : "bg-gray-700 text-gray-400 pointer-events-none cursor-not-allowed")
          }
        >
          S&apos;ABONNER AU MAINTIEN (100 € / mois)
        </a>
        <a
          href={hasEnterprise ? STRIPE_LINKS.ENTERPRISE_141K : undefined}
          aria-disabled={!hasEnterprise}
          className={
            "py-4 text-center font-black transition " +
            (hasEnterprise
              ? "bg-amber-500 text-black hover:bg-amber-400"
              : "bg-gray-700 text-gray-400 pointer-events-none cursor-not-allowed")
          }
        >
          RÉGULARISER LICENCE LUXE (141.986 €)
        </a>
      </div>
    </div>
  );
}
"""


def generar_links_cobro() -> int:
    print("🚀 Paso 50: Generando infraestructura de links Stripe (env-driven)...")

    os.makedirs(ROOT, exist_ok=True)
    os.chdir(ROOT)

    const_dir = os.path.join(ROOT, "src", "constants")
    os.makedirs(const_dir, exist_ok=True)
    p1 = os.path.join(const_dir, "stripe_links.ts")
    with open(p1, "w", encoding="utf-8") as f:
        f.write(STRIPE_LINKS_TS)

    comp = os.path.join(ROOT, "src", "components")
    os.makedirs(comp, exist_ok=True)
    p2 = os.path.join(comp, "SubscriptionPanel.tsx")
    with open(p2, "w", encoding="utf-8") as f:
        f.write(SUBSCRIPTION_PANEL_TSX)

    print(f"✅ {os.path.relpath(p1, ROOT)}")
    print(f"✅ {os.path.relpath(p2, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(generar_links_cobro())
