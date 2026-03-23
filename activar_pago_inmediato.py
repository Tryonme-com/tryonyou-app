"""
Escribe src/lib/instantPay.ts (checkout inmediato vía sesión Stripe).

Requiere en el backend una ruta POST /api/create-checkout-session coherente con el body.
En el frontend: npm install @stripe/stripe-js

- Raíz: E50_PROJECT_ROOT (por defecto ~/Projects/22TRYONYOU).

Ejecutar: python3 activar_pago_inmediato.py
"""

from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(
    os.environ.get("E50_PROJECT_ROOT", os.path.expanduser("~/Projects/22TRYONYOU"))
)

INSTANT_PAY_TS = """import { loadStripe } from "@stripe/stripe-js";

/** amount en céntimos (p. ej. 10000 = 100,00 EUR); el servidor debe validar precios. */
export async function forceInstantPay(): Promise<void> {
  const pk = import.meta.env.VITE_STRIPE_PUBLIC_KEY;
  if (!pk) {
    console.error("VITE_STRIPE_PUBLIC_KEY no configurada");
    return;
  }
  console.log("Iniciando cobro de validación técnica (100 EUR)...");
  const res = await fetch("/api/create-checkout-session", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ amount: 10000 }),
  });
  if (!res.ok) {
    console.error("create-checkout-session falló:", await res.text());
    return;
  }
  const data = (await res.json()) as { id?: string };
  if (!data.id) {
    console.error("Respuesta sin session id");
    return;
  }
  const stripe = await loadStripe(pk);
  if (!stripe) {
    console.error("Stripe.js no cargó");
    return;
  }
  const { error } = await stripe.redirectToCheckout({ sessionId: data.id });
  if (error) {
    console.error(error.message);
  }
}
"""


def activar_pago_inmediato() -> int:
    print("💰 Paso 39: Activando gatillo de pago real...")

    os.makedirs(ROOT, exist_ok=True)
    os.chdir(ROOT)

    lib = os.path.join(ROOT, "src", "lib")
    os.makedirs(lib, exist_ok=True)
    path = os.path.join(lib, "instantPay.ts")
    with open(path, "w", encoding="utf-8") as f:
        f.write(INSTANT_PAY_TS)

    print(f"✅ {os.path.relpath(path, ROOT)}")
    print("ℹ️  Implementa POST /api/create-checkout-session e instala @stripe/stripe-js.")
    return 0


if __name__ == "__main__":
    sys.exit(activar_pago_inmediato())
