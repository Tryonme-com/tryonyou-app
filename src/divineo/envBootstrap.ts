/** Checkout Divineo V11: base abvetos.com + VITE_SHOP_VARIANT. */

export function getDivineoCheckoutUrl(): string {
  const base = (import.meta.env.VITE_DIVINEO_CHECKOUT_BASE || "https://abvetos.com").replace(
    /\/$/,
    "",
  );
  const variant = (import.meta.env.VITE_SHOP_VARIANT || "").trim();
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
