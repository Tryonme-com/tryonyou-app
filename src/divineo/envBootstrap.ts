const base = (import.meta.env.VITE_DIVINEO_CHECKOUT_BASE || "https://abvetos.com").replace(
  /\/$/,
  "",
);
const variant = (import.meta.env.VITE_SHOP_VARIANT || "").trim();

let url = base;
if (variant) {
  const u = new URL(base.includes("://") ? base : `https://${base}`);
  u.searchParams.set("variant", variant);
  url = u.toString();
}

window.__DIVINEO_CHECKOUT_URL__ = url;
