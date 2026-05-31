/**
 * Pasarela Stripe — cuenta verificada Paris / EUR (abvetos.com, LiveitFashion).
 * Usar con Payment Element o enlaces generados por el backend (/api/stripe_*).
 */
export const STRIPE_DEFAULT_COUNTRY = "FR" as const;
export const STRIPE_DEFAULT_CURRENCY = "eur" as const;
export const STRIPE_DEFAULT_LOCALE = "fr" as const;

/** Clave publicable LIVE Paris: VITE_STRIPE_PUBLIC_KEY_FR o legado VITE_STRIPE_PUBLIC_KEY */
export function getStripePublishableKeyParis(): string {
  const e = import.meta.env;
  const fr = (e.VITE_STRIPE_PUBLIC_KEY_FR as string | undefined)?.trim();
  if (fr) return fr;
  return ((e.VITE_STRIPE_PUBLIC_KEY as string | undefined) || "").trim();
}
