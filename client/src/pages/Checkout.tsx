/**
 * TRYONYOU — /checkout
 *
 * Fetches a Stripe PaymentIntent client_secret from the backend, then renders
 * the <Elements> provider and <CheckoutForm> for secure card tokenisation.
 *
 * Style: Maison Couture Nocturne — graphite #0A0807 + or #C9A84C.
 */

import { useEffect, useState } from "react";
import { loadStripe } from "@stripe/stripe-js";
import { Elements } from "@stripe/react-stripe-js";
import { useLocation } from "wouter";

import SiteHeader from "@/components/sections/SiteHeader";
import SiteFooter from "@/components/sections/SiteFooter";
import CheckoutForm from "@/components/CheckoutForm";

// Publishable key — safe in the browser bundle (VITE_ prefix exposes it).
const stripePromise = loadStripe(
  import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY as string
);

const STRIPE_APPEARANCE = {
  theme: "night" as const,
  variables: {
    colorPrimary: "#C9A84C",
    colorBackground: "#0A0807",
    colorText: "#F5EFE0",
    colorDanger: "#e57373",
    fontFamily: "Inter, sans-serif",
    borderRadius: "2px",
  },
};

interface PaymentState {
  clientSecret: string | null;
  error: string | null;
  loading: boolean;
}

export default function Checkout() {
  const [location] = useLocation();
  const params = new URLSearchParams(location.split("?")[1] ?? "");
  const orderId = params.get("order_id") ?? "";
  // Amount is read from the URL and passed to the backend.
  // In production the backend should look up the canonical amount from its
  // order DB using order_id instead of trusting this value directly.
  const amountCents = parseInt(params.get("amount_cents") ?? "0", 10);

  const [state, setState] = useState<PaymentState>({
    clientSecret: null,
    error: null,
    loading: true,
  });

  useEffect(() => {
    document.title = "Paiement sécurisé · TRYONYOU";

    if (!orderId || amountCents <= 0) {
      setState({ clientSecret: null, error: "Paramètres de commande invalides.", loading: false });
      return;
    }

    fetch("/api/create-payment-intent", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ order_id: orderId, amount_cents: amountCents }),
    })
      .then(async (res) => {
        const data = await res.json();
        if (!res.ok) throw new Error(data.error ?? "Erreur serveur");
        return data.client_secret as string;
      })
      .then((clientSecret) => setState({ clientSecret, error: null, loading: false }))
      .catch((err: Error) =>
        setState({ clientSecret: null, error: err.message, loading: false })
      );
  }, [orderId, amountCents]);

  const returnUrl = `${window.location.origin}/checkout/confirmation?order_id=${orderId}`;

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

            <h1
              className="text-2xl font-light tracking-[0.2em] uppercase mb-1"
              style={{ fontFamily: "Playfair Display, serif", fontStyle: "italic" }}
            >
              Paiement
            </h1>
            <div className="h-px bg-[var(--color-or)]/40 mb-6" />

            {state.loading && (
              <p className="text-sm text-[#F5EFE0]/50 tracking-widest uppercase animate-pulse">
                Initialisation…
              </p>
            )}

            {state.error && (
              <p className="text-sm text-red-400 border border-red-400/30 rounded px-3 py-2">
                {state.error}
              </p>
            )}

            {state.clientSecret && (
              <Elements
                stripe={stripePromise}
                options={{ clientSecret: state.clientSecret, appearance: STRIPE_APPEARANCE }}
              >
                <CheckoutForm returnUrl={returnUrl} />
              </Elements>
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
