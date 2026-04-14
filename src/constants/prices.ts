/**
 * Canonical Stripe price catalogue — TryOnYou V10.
 *
 * CRITICAL: Stripe requires amounts in the smallest currency unit.
 * For EUR that means **cents** (1 € = 100 cents).
 *
 * 27 500,00 € → 2_750_000 cents
 * 22 500,00 € → 2_250_000 cents
 * 12 500,00 € →   1_250_000 cents (inauguration pack)
 *
 * The `currency` field MUST be the lowercase ISO 4217 code (`'eur'`).
 * Stripe rejects requests where `currency` is missing, uppercase, or
 * where the amount is a float instead of an integer.
 */

export const STRIPE_CURRENCY = "eur" as const;

export const SIREN = "943 610 196" as const;
export const PATENT = "PCT/EP2025/067317" as const;

export interface StripePrice {
  /** Human-readable label (never sent to Stripe). */
  label: string;
  /** Amount in cents (integer). Stripe rejects floats. */
  amountCents: number;
  /** ISO 4217 currency code, lowercase. */
  currency: typeof STRIPE_CURRENCY;
  /** Optional Stripe Price ID (price_…) when already created in Dashboard. */
  stripePriceId?: string;
}

export const PRICES: Record<string, StripePrice> = {
  sovereign_full: {
    label: "Licence Souveraineté Complète",
    amountCents: 2_750_000,
    currency: STRIPE_CURRENCY,
  },
  sovereign_standard: {
    label: "Licence Souveraineté Standard",
    amountCents: 2_250_000,
    currency: STRIPE_CURRENCY,
  },
  inauguration: {
    label: "Pack Inauguration",
    amountCents: 1_250_000,
    currency: STRIPE_CURRENCY,
  },
  maison_rive_gauche: {
    label: "Pack Maison Rive Gauche",
    amountCents: 10_990_000,
    currency: STRIPE_CURRENCY,
  },
  plan_100: {
    label: "Plan Mensuel 100 €",
    amountCents: 10_000,
    currency: STRIPE_CURRENCY,
  },
  setup_fee: {
    label: "Setup Fee (Activation Commerciale)",
    amountCents: 1_250_000,
    currency: STRIPE_CURRENCY,
  },
  exclusivity: {
    label: "Exclusivité Rive Gauche",
    amountCents: 1_500_000,
    currency: STRIPE_CURRENCY,
  },
  total_immediate: {
    label: "Total Immédiat (Setup + Exclusivité)",
    amountCents: 2_750_000,
    currency: STRIPE_CURRENCY,
  },
} as const;

/**
 * Legal metadata injected into every PaymentIntent and Invoice so that
 * Stripe Support (Isabella) can trace each transaction back to the
 * legal entity.
 */
export const LEGAL_METADATA: Record<string, string> = {
  siren: SIREN,
  patent: PATENT,
  platform: "TryOnYou_V10",
};
