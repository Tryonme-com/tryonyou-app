/**
 * Cobros marca ABVETOS / boutique — séparer panier Shopify et encaissement Stripe Paris.
 * Les ordres de débit (« Architecte ») passent uniquement par `architectOpenVerifiedParisCheckout`.
 */
import { getAbvetosSovereignPaymentUrl, openPaymentUrl } from "../lib/lafayetteCheckout";
import { architectOpenVerifiedParisCheckout } from "./paymentService";

/** Ouvre uniquement la pasarela Stripe vérifiée (FR / EUR), jamais un tubo US. */
export function openAbvetosVerifiedStripeOnly(): void {
  void architectOpenVerifiedParisCheckout();
}

/** Panier produits abvetos.com (Shopify) — ne remplace pas l’encaissement inaugural Stripe. */
export function openAbvetosShopifyCart(): void {
  openPaymentUrl(getAbvetosSovereignPaymentUrl());
}
