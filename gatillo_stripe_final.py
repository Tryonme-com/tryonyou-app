"""
Escribe src/components/StripePayButton.tsx (CTA pago; URL solo desde env Vite).

Usa VITE_STRIPE_CHECKOUT_URL o VITE_STRIPE_CHECKOUT_98K_URL (mismo criterio que payment_settings).

- Raíz: E50_PROJECT_ROOT (por defecto ~/Projects/22TRYONYOU).

Ejecutar: python3 gatillo_stripe_final.py
"""

from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(
    os.environ.get("E50_PROJECT_ROOT", os.path.expanduser("~/Projects/22TRYONYOU"))
)

STRIPE_PAY_BUTTON_TSX = """import React from "react";

function checkoutUrl(): string {
  return (
    (import.meta.env.VITE_STRIPE_CHECKOUT_URL as string | undefined) ??
    (import.meta.env.VITE_STRIPE_CHECKOUT_98K_URL as string | undefined) ??
    ""
  );
}

export function StripePayButton() {
  const url = checkoutUrl();
  return (
    <div className="mt-10 p-6 border-2 border-red-600 bg-zinc-900 text-center">
      <h3 className="text-white text-xl font-bold mb-4">RÉGULARISATION URGENTE</h3>
      <p className="text-red-500 mb-6">Échéance : Lundi 23 Mars - 09:00 AM</p>
      {!url ? (
        <p className="text-amber-400 text-sm mb-4">
          Configure VITE_STRIPE_CHECKOUT_URL (o VITE_STRIPE_CHECKOUT_98K_URL) en Vercel.
        </p>
      ) : null}
      <button
        type="button"
        disabled={!url}
        onClick={() => {
          if (url) window.location.assign(url);
        }}
        className="bg-green-600 hover:bg-green-500 disabled:opacity-40 disabled:cursor-not-allowed text-white font-black py-4 px-10 rounded-full text-2xl shadow-2xl"
      >
        PAYER 141.986 € MAINTENANT
      </button>
    </div>
  );
}
"""


def gatillo_stripe_final() -> int:
    print("⚡ Paso 47: Inyectando botón de pago Stripe en el Salón VIP...")

    os.makedirs(ROOT, exist_ok=True)
    os.chdir(ROOT)

    comp = os.path.join(ROOT, "src", "components")
    os.makedirs(comp, exist_ok=True)
    path = os.path.join(comp, "StripePayButton.tsx")
    with open(path, "w", encoding="utf-8") as f:
        f.write(STRIPE_PAY_BUTTON_TSX)

    print(f"✅ {os.path.relpath(path, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(gatillo_stripe_final())
