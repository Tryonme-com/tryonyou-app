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

/** Evita ráfagas POST /api/stripe_inauguration_checkout entre montajes y clics (TTL corto). */
const PARIS_CHECKOUT_URL_CACHE_MS = 90_000;
let _parisCheckoutUrlCache: { value: string; ts: number } | null = null;

let _inflightParisCheckout: Promise<string | undefined> | null = null;

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
  const now = Date.now();
  if (
    _parisCheckoutUrlCache &&
    now - _parisCheckoutUrlCache.ts < PARIS_CHECKOUT_URL_CACHE_MS
  ) {
    return _parisCheckoutUrlCache.value;
  }
  if (!_inflightParisCheckout) {
    const work = (async () => {
      const endpoint = inaugurationCheckoutEndpoint();
      if (!endpoint.startsWith("http")) {
        return undefined;
      }
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
        const data = (await res.json()) as {
          status?: string;
          url?: string;
          message?: string;
        };
        if (data?.status === "ok" && data?.url) {
          _parisCheckoutUrlCache = { value: data.url, ts: Date.now() };
          return data.url;
        }
        if (data?.status === "error" || !res.ok) {
          console.warn(
            "[paymentService] inauguration checkout",
            res.status,
            data?.message ?? "",
          );
        }
      } catch (e) {
        console.warn("[paymentService] fetchParisInaugurationCheckoutUrl", e);
      }
      return undefined;
    })();
    // Una sola promesa en vuelo: limpiar al settled, no en el finally del primer await
    // (evita ventanas donde otro caller ve null y duplica el POST).
    _inflightParisCheckout = work.finally(() => {
      _inflightParisCheckout = null;
    });
  }
  return _inflightParisCheckout;
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
