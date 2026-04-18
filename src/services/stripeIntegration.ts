/**
 * Punto único de entrada para Stripe en front (Paris / EUR).
 * Reexporta configuración y flujos de checkout; no llama a /v1/prices ni /v1/products.
 */
export {
  STRIPE_DEFAULT_COUNTRY,
  STRIPE_DEFAULT_CURRENCY,
  STRIPE_DEFAULT_LOCALE,
  getStripePublishableKeyParis,
} from "./stripeParisConfig";
export {
  architectOpenVerifiedParisCheckout,
  fetchParisInaugurationCheckoutUrl,
  getDefaultStripeTransactionDefaults,
  type ParisTransactionDefaults,
} from "./paymentService";
