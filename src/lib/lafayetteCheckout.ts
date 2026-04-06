/**
 * Contrato Lafayette — URL de pago Stripe (Payment Link / Checkout público).
 * Prioridad: VITE_LAFAYETTE_STRIPE_CHECKOUT_URL → enlaces soberanía existentes.
 */
export function getLafayetteStripeCheckoutUrl(): string {
  const e = import.meta.env;
  const candidates = [
    e.VITE_LAFAYETTE_STRIPE_CHECKOUT_URL,
    e.VITE_STRIPE_LINK_SOVEREIGNTY_4_5M,
    e.VITE_STRIPE_CHECKOUT_URL,
    e.VITE_STRIPE_LINK_SOVEREIGNTY_98K,
  ];
  for (const v of candidates) {
    const s = (v as string | undefined)?.trim();
    if (s) return s;
  }
  return "";
}
