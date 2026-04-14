/** Checkout Divineo V11: base abvetos.com + VITE_SHOP_VARIANT. */

/** Variante Shopify LIVE en abvetos.com (SKU real soberano). */
export const ABVETOS_LIVE_SHOP_VARIANT_ID = "53412065182103" as const;
export const DIVINEO_CHECKOUT_SAFE_BASE = "https://abvetos.com" as const;

const DIVINEO_ALLOWED_HOST_SUFFIXES = ["abvetos.com"] as const;
const DIVINEO_ALLOWED_LOCAL_HOSTS = new Set(["localhost", "127.0.0.1"]);

function normalizeBaseUrl(rawBase?: string): string {
  const cleanBase = (rawBase || DIVINEO_CHECKOUT_SAFE_BASE).trim().replace(/\/$/, "");
  return cleanBase.includes("://") ? cleanBase : `https://${cleanBase}`;
}

function isAllowedDivineoHost(hostname: string): boolean {
  const host = hostname.toLowerCase();
  if (DIVINEO_ALLOWED_LOCAL_HOSTS.has(host)) return true;
  return DIVINEO_ALLOWED_HOST_SUFFIXES.some(
    (suffix) => host === suffix || host.endsWith(`.${suffix}`),
  );
}

export function isDivineoCheckoutUrlAllowed(rawUrl: string): boolean {
  try {
    const url = new URL(rawUrl);
    return isAllowedDivineoHost(url.hostname);
  } catch {
    return false;
  }
}

export function getDivineoCheckoutUrl(): string {
  const baseCandidate = normalizeBaseUrl(import.meta.env.VITE_DIVINEO_CHECKOUT_BASE);
  const base = isDivineoCheckoutUrlAllowed(baseCandidate)
    ? baseCandidate
    : DIVINEO_CHECKOUT_SAFE_BASE;
  const variant = (
    import.meta.env.VITE_SHOP_VARIANT || ABVETOS_LIVE_SHOP_VARIANT_ID
  ).trim();
  let url = base;
  if (variant) {
    const u = new URL(url);
    u.searchParams.set("variant", variant);
    url = u.toString();
  }
  return url;
}

if (typeof window !== "undefined") {
  const candidate = normalizeBaseUrl(import.meta.env.VITE_DIVINEO_CHECKOUT_BASE);
  window.__DIVINEO_CHECKOUT_BLOCKED__ = !isDivineoCheckoutUrlAllowed(candidate);
  window.__DIVINEO_CHECKOUT_URL__ = getDivineoCheckoutUrl();
}
