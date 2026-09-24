/** Checkout Divineo V11: base abvetos.com + VITE_SHOP_VARIANT. Pagos: EUR / cuenta Stripe Paris (VITE_STRIPE_PUBLIC_KEY_FR). */

/** Variante Shopify LIVE en abvetos.com (SKU real soberano). */
export const ABVETOS_LIVE_SHOP_VARIANT_ID = "53412065182103" as const;

export function getDivineoCheckoutUrl(): string {
  const base = (import.meta.env.VITE_DIVINEO_CHECKOUT_BASE || "https://abvetos.com").replace(
    /\/$/,
    "",
  );
  const variant = (
    import.meta.env.VITE_SHOP_VARIANT || ABVETOS_LIVE_SHOP_VARIANT_ID
  ).trim();
  let url = base.includes("://") ? base : `https://${base}`;
  if (variant) {
    const u = new URL(url);
    u.searchParams.set("variant", variant);
    url = u.toString();
  }
  return url;
}

if (typeof window !== "undefined") {
  window.__DIVINEO_CHECKOUT_URL__ = getDivineoCheckoutUrl();
}
