/**
 * TRYONYOU — /checkout/confirmation
 *
 * Stripe redirects here after a payment attempt with:
 *   ?payment_intent=pi_...
 *   &payment_intent_client_secret=pi_..._secret_...
 *   &redirect_status=succeeded|processing|requires_payment_method
 *   &order_id=<orderId>   (appended by Checkout.tsx)
 *
 * Style: Maison Couture Nocturne — graphite #0A0807 + or #C9A84C.
 */

import { useEffect, useState } from "react";
import { loadStripe, type Stripe } from "@stripe/stripe-js";
import { Link, useLocation } from "wouter";
import SiteHeader from "@/components/sections/SiteHeader";
import SiteFooter from "@/components/sections/SiteFooter";

const stripePromise: Promise<Stripe | null> = loadStripe(
  import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY as string
);

type PaymentStatus = "loading" | "succeeded" | "processing" | "failed";

function GoldRule({ className = "" }: { className?: string }) {
  return <div className={`h-px bg-[var(--color-or)]/40 ${className}`} />;
}

export default function CheckoutConfirmation() {
  const [location] = useLocation();
  const params = new URLSearchParams(location.split("?")[1] ?? "");

  const clientSecret = params.get("payment_intent_client_secret") ?? "";
  const redirectStatus = params.get("redirect_status") ?? "";
  const orderId = params.get("order_id") ?? "";

  const [status, setStatus] = useState<PaymentStatus>("loading");
  const [paymentIntentId, setPaymentIntentId] = useState<string>("");

  useEffect(() => {
    document.title = "Confirmation de paiement · TRYONYOU";

    // Fast path — Stripe already tells us the redirect_status in the URL.
    if (redirectStatus === "succeeded") {
      setPaymentIntentId(params.get("payment_intent") ?? "");
      setStatus("succeeded");
      return;
    }
    if (redirectStatus === "processing") {
      setStatus("processing");
      return;
    }
    if (redirectStatus === "requires_payment_method") {
      setStatus("failed");
      return;
    }

    // Fallback: retrieve PaymentIntent directly to get a definitive status.
    if (!clientSecret) {
      setStatus("failed");
      return;
    }

    let cancelled = false;
    (async () => {
      try {
        const stripe = await stripePromise;
        if (!stripe || cancelled) return;
        const { paymentIntent } = await stripe.retrievePaymentIntent(clientSecret);
        if (cancelled) return;
        if (!paymentIntent) { setStatus("failed"); return; }
        setPaymentIntentId(paymentIntent.id);
        if (paymentIntent.status === "succeeded") setStatus("succeeded");
        else if (paymentIntent.status === "processing") setStatus("processing");
        else setStatus("failed");
      } catch {
        if (!cancelled) setStatus("failed");
      }
    })();
    return () => { cancelled = true; };
  }, [clientSecret, redirectStatus, params]);

  return (
    <div className="min-h-screen flex flex-col bg-[#0A0807] text-[#F5EFE0]">
      <SiteHeader />

      <main className="flex-1 flex items-center justify-center px-4 py-16">
        <div className="w-full max-w-md">
          {/* Gold hairline frame */}
          <div className="relative border border-[var(--color-or)]/25 p-8">
            <div className="absolute -top-1 -left-1 w-4 h-4 border-t border-l border-[var(--color-or)]" />
            <div className="absolute -top-1 -right-1 w-4 h-4 border-t border-r border-[var(--color-or)]" />
            <div className="absolute -bottom-1 -left-1 w-4 h-4 border-b border-l border-[var(--color-or)]" />
            <div className="absolute -bottom-1 -right-1 w-4 h-4 border-b border-r border-[var(--color-or)]" />

            {status === "loading" && (
              <>
                <h1
                  className="text-2xl font-light tracking-[0.2em] uppercase mb-1"
                  style={{ fontFamily: "Playfair Display, serif", fontStyle: "italic" }}
                >
                  Vérification
                </h1>
                <GoldRule className="mb-6" />
                <p className="text-sm text-[#F5EFE0]/50 tracking-widest uppercase animate-pulse">
                  Confirmation en cours…
                </p>
              </>
            )}

            {status === "succeeded" && (
              <>
                <p className="text-xs tracking-[0.3em] uppercase text-[var(--color-or)] mb-2">
                  I — Confirmation
                </p>
                <h1
                  className="text-2xl font-light tracking-[0.2em] uppercase mb-1"
                  style={{ fontFamily: "Playfair Display, serif", fontStyle: "italic" }}
                >
                  Paiement accepté
                </h1>
                <GoldRule className="mb-6" />

                <p className="text-sm text-[#F5EFE0]/80 leading-relaxed mb-4">
                  Votre paiement a bien été enregistré. Notre équipe traitera votre commande
                  dans les plus brefs délais.
                </p>

                {orderId && (
                  <p className="text-xs text-[#F5EFE0]/40 tracking-widest mb-1">
                    Référence commande :{" "}
                    <span className="text-[#F5EFE0]/70">{orderId}</span>
                  </p>
                )}
                {paymentIntentId && (
                  <p className="text-xs text-[#F5EFE0]/40 tracking-widest mb-6">
                    Référence Stripe :{" "}
                    <span className="text-[#F5EFE0]/70 font-mono text-[10px]">
                      {paymentIntentId}
                    </span>
                  </p>
                )}

                <GoldRule className="mb-6" />
                <Link
                  href="/"
                  className="inline-block text-xs tracking-[0.25em] uppercase text-[var(--color-or)] hover:opacity-75 transition-opacity"
                >
                  ← Retour à l'accueil
                </Link>
              </>
            )}

            {status === "processing" && (
              <>
                <p className="text-xs tracking-[0.3em] uppercase text-[var(--color-or)] mb-2">
                  I — En cours
                </p>
                <h1
                  className="text-2xl font-light tracking-[0.2em] uppercase mb-1"
                  style={{ fontFamily: "Playfair Display, serif", fontStyle: "italic" }}
                >
                  Traitement en cours
                </h1>
                <GoldRule className="mb-6" />
                <p className="text-sm text-[#F5EFE0]/80 leading-relaxed mb-6">
                  Votre paiement est en cours de traitement. Vous recevrez une confirmation
                  par e-mail dès qu'il sera validé.
                </p>
                {orderId && (
                  <p className="text-xs text-[#F5EFE0]/40 tracking-widest mb-6">
                    Référence commande :{" "}
                    <span className="text-[#F5EFE0]/70">{orderId}</span>
                  </p>
                )}
                <Link
                  href="/"
                  className="inline-block text-xs tracking-[0.25em] uppercase text-[var(--color-or)] hover:opacity-75 transition-opacity"
                >
                  ← Retour à l'accueil
                </Link>
              </>
            )}

            {status === "failed" && (
              <>
                <p className="text-xs tracking-[0.3em] uppercase text-red-400/80 mb-2">
                  Paiement non abouti
                </p>
                <h1
                  className="text-2xl font-light tracking-[0.2em] uppercase mb-1"
                  style={{ fontFamily: "Playfair Display, serif", fontStyle: "italic" }}
                >
                  Échec du paiement
                </h1>
                <GoldRule className="mb-6" />
                <p className="text-sm text-[#F5EFE0]/80 leading-relaxed mb-6">
                  Le paiement n'a pas pu être finalisé. Veuillez réessayer ou contacter
                  notre équipe à{" "}
                  <a
                    href="mailto:admin@tryonyou.app"
                    className="text-[var(--color-or)] hover:opacity-75 transition-opacity"
                  >
                    admin@tryonyou.app
                  </a>
                  .
                </p>
                {orderId && (
                  <Link
                    href={`/checkout?order_id=${orderId}`}
                    className="inline-block text-xs tracking-[0.25em] uppercase text-[var(--color-or)] hover:opacity-75 transition-opacity mr-6"
                  >
                    ↺ Réessayer
                  </Link>
                )}
                <Link
                  href="/"
                  className="inline-block text-xs tracking-[0.25em] uppercase text-[#F5EFE0]/40 hover:opacity-75 transition-opacity"
                >
                  ← Accueil
                </Link>
              </>
            )}
          </div>

          <p className="mt-4 text-center text-xs text-[#F5EFE0]/30 tracking-widest">
            Paiement sécurisé par Stripe · TLS 1.3
          </p>
        </div>
      </main>

      <SiteFooter />
    </div>
  );
}
