/**
 * Utilidades Stripe + alineación checkout Shopify (abvetos.com / LiveitFashion → Paris EUR).
 * Prioridad enlaces Stripe: inauguración → Lafayette → soberanía legada.
 */
import {
  ABVETOS_LIVE_SHOP_VARIANT_ID,
  getDivineoCheckoutUrl,
} from "../divineo/envBootstrap";
import {
  STRIPE_DEFAULT_COUNTRY,
  STRIPE_DEFAULT_CURRENCY,
  STRIPE_DEFAULT_LOCALE,
  getStripePublishableKeyParis,
} from "../services/stripeParisConfig";

export { ABVETOS_LIVE_SHOP_VARIANT_ID };
export {
  STRIPE_DEFAULT_COUNTRY,
  STRIPE_DEFAULT_CURRENCY,
  STRIPE_DEFAULT_LOCALE,
  getStripePublishableKeyParis,
};

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

/** Solo `VITE_INAUGURATION_STRIPE_CHECKOUT_URL` (build / Vercel). */
export function getInaugurationStripeEnvUrl(): string {
  return (
    import.meta.env.VITE_INAUGURATION_STRIPE_CHECKOUT_URL as string | undefined
  )?.trim() || "";
}

/** Inauguración 12.500 € — primero env inaugural; respaldos Lafayette / soberanía (liquidez). */
export function getInaugurationStripeCheckoutUrl(): string {
  const direct = getInaugurationStripeEnvUrl();
  if (direct) return direct;
  return getLafayetteStripeCheckoutUrl();
}

/**
 * Variante Shopify usada en cobros: env primero, si no el SKU LIVE abvetos (53412065182103).
 */
export function resolveShopifyVariantIdForPayments(): string {
  const fromEnv = (import.meta.env.VITE_SHOP_VARIANT as string | undefined)?.trim();
  return fromEnv || ABVETOS_LIVE_SHOP_VARIANT_ID;
}

/**
 * URL de carrito abvetos.com acorde a `getDivineoCheckoutUrl()` (variant ya fijado por env o ID soberano).
 */
export function getAbvetosSovereignPaymentUrl(): string {
  return getDivineoCheckoutUrl();
}

/**
 * Abre un enlace de pago en nueva pestaña (Stripe Payment Link o URL externa).
 */
export function openPaymentUrl(url: string): void {
  const u = url.trim();
  if (!u) return;
  window.open(u, "_blank", "noopener,noreferrer");
}

/**
 * Cobro inaugural: prioridad absoluta `VITE_INAUGURATION_STRIPE_CHECKOUT_URL`.
 * Sin validación Shopify ni pasos extra que bloqueen (Firebase puede seguir sincronizando).
 */
export function openInaugurationStripeLiquidity(): void {
  const url = getInaugurationStripeCheckoutUrl();
  if (!url) return;
  openPaymentUrl(url);
}
