/**
 * Service de paiement — uniquement passerelle Stripe verifiee Paris (EUR, FR).
 * LiveitFashion / abvetos : pas de routage vers compte US bloque.
 */
import {
  getInaugurationStripeCheckoutUrl,
  openPaymentUrl,
} from "../lib/lafayetteCheckout";
import {
  STRIPE_DEFAULT_COUNTRY,
  STRIPE_DEFAULT_CURRENCY,
  STRIPE_DEFAULT_LOCALE,
  getStripePublishableKeyParis,
} from "./stripeParisConfig";

export type ParisTransactionDefaults = {
  country: typeof STRIPE_DEFAULT_COUNTRY;
  currency: typeof STRIPE_DEFAULT_CURRENCY;
  locale: typeof STRIPE_DEFAULT_LOCALE;
};

export function getDefaultStripeTransactionDefaults(): ParisTransactionDefaults {
  return {
    country: STRIPE_DEFAULT_COUNTRY,
    currency: STRIPE_DEFAULT_CURRENCY,
    locale: STRIPE_DEFAULT_LOCALE,
  };
}

export { getStripePublishableKeyParis };

function inaugurationCheckoutEndpoint(): string {
  const configured = (
    import.meta.env.VITE_STRIPE_CHECKOUT_API_ORIGIN as string | undefined
  )?.trim();
  const base = (
    configured ||
    (typeof window !== "undefined" ? window.location.origin : "") ||
    ""
  ).replace(/\/$/, "");
  return `${base}/api/stripe_inauguration_checkout`;
}

export async function fetchParisInaugurationCheckoutUrl(): Promise<string | undefined> {
  const endpoint = inaugurationCheckoutEndpoint();
  if (!endpoint.startsWith("http")) return undefined;
  try {
    const res = await fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(typeof window !== "undefined" && window.location?.origin
          ? { Origin: window.location.origin }
          : {}),
      },
      body: "{}",
    });
    const data = (await res.json()) as { status?: string; url?: string };
    if (data?.status === "ok" && data?.url) return data.url;
  } catch {
    /* ignore */
  }
  return undefined;
}

export async function architectOpenVerifiedParisCheckout(): Promise<boolean> {
  const fromEnv = getInaugurationStripeCheckoutUrl().trim();
  if (fromEnv) {
    openPaymentUrl(fromEnv);
    return true;
  }
  const fromApi = await fetchParisInaugurationCheckoutUrl();
  if (fromApi) {
    openPaymentUrl(fromApi);
    return true;
  }
  return false;
}
